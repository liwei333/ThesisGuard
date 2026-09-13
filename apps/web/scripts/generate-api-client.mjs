import { canonicalOpenApiPath, exportCurrentOpenApi, generateClient, generatedDir } from './openapi-tools.mjs'

exportCurrentOpenApi(canonicalOpenApiPath)
generateClient(canonicalOpenApiPath, generatedDir)

console.log(`Generated OpenAPI artifact: ${canonicalOpenApiPath}`)
console.log(`Generated TypeScript client: ${generatedDir}`)
