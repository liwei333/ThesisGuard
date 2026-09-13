import { mkdtempSync, rmSync, writeFileSync } from 'node:fs'
import { join } from 'node:path'
import { tmpdir } from 'node:os'

import {
  canonicalOpenApiPath,
  compareArtifacts,
  exportCurrentOpenApi,
  generateClient,
  generatedDir,
} from './openapi-tools.mjs'

const tempRoot = mkdtempSync(join(tmpdir(), 'thesisguard-api-check-'))
const tempOpenApi = join(tempRoot, 'openapi.json')
const tempGenerated = join(tempRoot, 'generated')

try {
  exportCurrentOpenApi(tempOpenApi)
  generateClient(tempOpenApi, tempGenerated)

  if (process.env.THESISGUARD_API_CHECK_INJECT_DRIFT === '1') {
    writeFileSync(join(tempGenerated, '__drift_probe.ts'), 'export const drift = true\n')
  }

  const errors = compareArtifacts(canonicalOpenApiPath, generatedDir, tempOpenApi, tempGenerated)
  if (errors.length) {
    console.error('OpenAPI generated client drift detected:')
    for (const error of errors) {
      console.error(`- ${error}`)
    }
    process.exitCode = 1
  } else {
    console.log('OpenAPI generated client is current.')
  }
} finally {
  rmSync(tempRoot, { recursive: true, force: true })
}
