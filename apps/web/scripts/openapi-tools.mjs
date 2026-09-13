import { createHash } from 'node:crypto'
import { existsSync, mkdirSync, readdirSync, readFileSync, rmSync, statSync, writeFileSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { dirname, join, relative, resolve } from 'node:path'
import { spawnSync } from 'node:child_process'
import { fileURLToPath } from 'node:url'

const scriptDir = dirname(fileURLToPath(import.meta.url))
export const webRoot = resolve(scriptDir, '..')
export const repoRoot = resolve(webRoot, '../..')
export const canonicalOpenApiPath = resolve(webRoot, 'openapi.json')
export const generatedDir = resolve(webRoot, 'src/api/generated')

const pythonCandidates = [
  process.env.PYTHON,
  '/opt/homebrew/opt/python@3.12/bin/python3.12',
  'python3.12',
  'python3',
  'python',
].filter(Boolean)

function run(command, args, options = {}) {
  const result = spawnSync(command, args, {
    cwd: options.cwd ?? webRoot,
    env: options.env ?? process.env,
    encoding: 'utf-8',
    stdio: options.stdio ?? 'pipe',
  })
  if (result.status !== 0) {
    const details = [
      result.stdout?.trim(),
      result.stderr?.trim(),
    ].filter(Boolean).join('\n')
    throw new Error(`${command} ${args.join(' ')} failed with exit ${result.status}\n${details}`)
  }
  return result.stdout
}

export function exportCurrentOpenApi(destinationPath = canonicalOpenApiPath) {
  const pythonCode = [
    'import json',
    'from apps.api.main import create_app',
    'print(json.dumps(create_app().openapi(), ensure_ascii=False, sort_keys=True, separators=(\",\", \":\")))',
  ].join('\n')

  let lastError = null
  for (const python of pythonCandidates) {
    const result = spawnSync(python, ['-c', pythonCode], {
      cwd: repoRoot,
      env: {
        ...process.env,
        PYTHONPATH: repoRoot,
      },
      encoding: 'utf-8',
      stdio: 'pipe',
    })
    if (result.status === 0) {
      const canonical = result.stdout.trim()
      mkdirSync(dirname(destinationPath), { recursive: true })
      writeFileSync(destinationPath, `${canonical}\n`)
      return JSON.parse(canonical)
    }
    lastError = `${python}: ${result.stderr || result.stdout}`
  }
  throw new Error(`Unable to export OpenAPI from create_app().openapi()\n${lastError}`)
}

export function generateClient(inputPath = canonicalOpenApiPath, outputDir = generatedDir) {
  rmSync(outputDir, { recursive: true, force: true })
  mkdirSync(outputDir, { recursive: true })
  run(
    resolve(webRoot, 'node_modules/.bin/openapi'),
    [
      '--input', inputPath,
      '--output', outputDir,
      '--client', 'axios',
      '--useOptions',
      '--exportCore', 'true',
      '--exportServices', 'true',
      '--exportModels', 'true',
      '--exportSchemas', 'false',
    ],
    { stdio: 'pipe' },
  )
  patchGeneratedClient(outputDir)
}

function replaceOnce(filePath, expected, replacement) {
  const source = readFileSync(filePath, 'utf-8')
  if (!source.includes(expected)) {
    throw new Error(`Generated client patch anchor was not found in ${filePath}`)
  }
  writeFileSync(filePath, source.replace(expected, replacement))
}

export function patchGeneratedClient(outputDir = generatedDir) {
  const apiErrorPath = join(outputDir, 'core/ApiError.ts')
  const apiResultPath = join(outputDir, 'core/ApiResult.ts')
  const openApiPath = join(outputDir, 'core/OpenAPI.ts')
  const requestPath = join(outputDir, 'core/request.ts')
  const indexPath = join(outputDir, 'index.ts')

  replaceOnce(
    apiResultPath,
    'export type ApiResult = {\n',
    'export type ApiResult<TBody = unknown> = {\n',
  )
  replaceOnce(
    apiResultPath,
    '    readonly body: any;\n',
    '    readonly body: TBody;\n',
  )

  replaceOnce(
    apiErrorPath,
    'export class ApiError extends Error {\n',
    'export class ApiError<TBody = unknown> extends Error {\n',
  )
  replaceOnce(
    apiErrorPath,
    '    public readonly body: any;\n',
    '    public readonly body: TBody;\n',
  )
  replaceOnce(
    apiErrorPath,
    '    constructor(request: ApiRequestOptions, response: ApiResult, message: string) {\n',
    '    constructor(request: ApiRequestOptions, response: ApiResult<TBody>, message: string) {\n',
  )

  replaceOnce(
    openApiPath,
    "import type { ApiRequestOptions } from './ApiRequestOptions';\n",
    "import type { AxiosInstance } from 'axios';\nimport type { ApiRequestOptions } from './ApiRequestOptions';\n",
  )
  replaceOnce(
    openApiPath,
    '    ENCODE_PATH?: ((path: string) => string) | undefined;\n',
    '    AXIOS?: AxiosInstance | undefined;\n    ENCODE_PATH?: ((path: string) => string) | undefined;\n',
  )
  replaceOnce(
    openApiPath,
    '    HEADERS: undefined,\n    ENCODE_PATH: undefined,\n',
    '    HEADERS: undefined,\n    AXIOS: undefined,\n    ENCODE_PATH: undefined,\n',
  )

  replaceOnce(
    requestPath,
    'export const getResponseBody = (response: AxiosResponse<any>): any => {\n',
    'export const getResponseBody = <T>(response: AxiosResponse<T>): T | undefined => {\n',
  )
  replaceOnce(
    requestPath,
    '    body: any,\n',
    '    body: unknown,\n',
  )
  replaceOnce(
    requestPath,
    'export const catchErrorCodes = (options: ApiRequestOptions, result: ApiResult): void => {\n',
    'export const catchErrorCodes = <TBody = unknown>(options: ApiRequestOptions, result: ApiResult<TBody>): void => {\n',
  )
  replaceOnce(
    requestPath,
    'export const request = <T>(config: OpenAPIConfig, options: ApiRequestOptions, axiosClient: AxiosInstance = axios): CancelablePromise<T> => {\n',
    'export const request = <T>(config: OpenAPIConfig, options: ApiRequestOptions, axiosClient: AxiosInstance = config.AXIOS ?? axios): CancelablePromise<T> => {\n',
  )
  replaceOnce(
    requestPath,
    '                const result: ApiResult = {\n',
    '                const result: ApiResult<unknown> = {\n',
  )
  replaceOnce(
    requestPath,
    '                resolve(result.body);\n',
    '                resolve(result.body as T);\n',
  )

  replaceOnce(
    indexPath,
    "export { ApiError } from './core/ApiError';\n",
    "export { ApiError } from './core/ApiError';\nexport type { ApiResult } from './core/ApiResult';\n",
  )

  for (const filePath of listFiles(outputDir)) {
    if (filePath.endsWith('.ts')) {
      const source = readFileSync(filePath, 'utf-8')
      writeFileSync(filePath, `${source.trimEnd()}\n`)
    }
  }
}

function stableStringify(value) {
  if (Array.isArray(value)) {
    return `[${value.map(stableStringify).join(',')}]`
  }
  if (value && typeof value === 'object') {
    return `{${Object.keys(value).sort().map((key) => `${JSON.stringify(key)}:${stableStringify(value[key])}`).join(',')}}`
  }
  return JSON.stringify(value)
}

export function writeCanonicalJson(destinationPath, value) {
  mkdirSync(dirname(destinationPath), { recursive: true })
  writeFileSync(destinationPath, `${stableStringify(value)}\n`)
}

export function listFiles(rootDir) {
  if (!existsSync(rootDir)) {
    return []
  }
  const files = []
  function visit(dir) {
    for (const entry of readdirSync(dir).sort()) {
      const path = join(dir, entry)
      const stats = statSync(path)
      if (stats.isDirectory()) {
        visit(path)
      } else if (stats.isFile()) {
        files.push(path)
      }
    }
  }
  visit(rootDir)
  return files
}

export function artifactHash(openApiPath = canonicalOpenApiPath, clientDir = generatedDir) {
  const hash = createHash('sha256')
  hash.update('openapi.json\0')
  hash.update(readFileSync(openApiPath))
  for (const file of listFiles(clientDir)) {
    const relativePath = relative(clientDir, file)
    hash.update('\0')
    hash.update(relativePath)
    hash.update('\0')
    hash.update(readFileSync(file))
  }
  return hash.digest('hex')
}

export function compareArtifacts(
  expectedOpenApiPath,
  expectedClientDir,
  actualOpenApiPath,
  actualClientDir,
) {
  const expectedOpenApi = JSON.parse(readFileSync(expectedOpenApiPath, 'utf-8'))
  const actualOpenApi = JSON.parse(readFileSync(actualOpenApiPath, 'utf-8'))
  const errors = []

  if (stableStringify(expectedOpenApi) !== stableStringify(actualOpenApi)) {
    errors.push('canonical OpenAPI artifact differs from current FastAPI OpenAPI')
  }

  const expectedFiles = listFiles(expectedClientDir).map((path) => relative(expectedClientDir, path))
  const actualFiles = listFiles(actualClientDir).map((path) => relative(actualClientDir, path))
  if (JSON.stringify(expectedFiles) !== JSON.stringify(actualFiles)) {
    errors.push('generated client file list differs')
  }

  for (const relativePath of expectedFiles) {
    const expectedPath = join(expectedClientDir, relativePath)
    const actualPath = join(actualClientDir, relativePath)
    if (!existsSync(actualPath)) {
      continue
    }
    if (readFileSync(expectedPath, 'utf-8') !== readFileSync(actualPath, 'utf-8')) {
      errors.push(`generated client file differs: ${relativePath}`)
    }
  }

  return errors
}

export function createTempWorkspace() {
  return tmpdir()
}

export { stableStringify }
