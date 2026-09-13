import { artifactHash, canonicalOpenApiPath, generatedDir } from './openapi-tools.mjs'

console.log(artifactHash(canonicalOpenApiPath, generatedDir))
