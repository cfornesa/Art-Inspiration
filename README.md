# Art Inspiration Agent (Node.js + Express)

This project is the Node.js conversion of the original Python application and is designed for Hostinger Node.js deployment.

## Runtime and Build Requirements

- Node version: `20.x`
- Root directory: `/`
- Package manager: `npm`
- Build command: `npm run build`
- Entry file: `server.bundle.js`
- Output directory: none

## Environment Variables

Required:

- `NODE_ENV` (`development` or `production`)
- `MISTRAL_API_KEY`
- `AGENT_ID`

Optional:

- `APP_URL` (restricts CORS to one frontend origin)
- `PORT` (defaults to `5000`)
- `DOCUMENTS_DIR` (defaults to `art_documents`)
- `RAG_INDEX_PATH` (defaults to `documents/embeddings/art-index.json`)
- `RAG_TOP_K` (defaults to `4`)
- `RAG_CHUNK_SIZE` (defaults to `1000`)
- `RAG_CHUNK_OVERLAP` (defaults to `150`)
- `EMBEDDING_MODEL` (defaults to `Xenova/all-MiniLM-L6-v2`)

Use `.env.example` as your template.

## Commands

- `npm install`
- `npm run build`
- `npm start`

For local development:

- `npm run dev`

To generate local RAG embeddings index:

- `npm run build:index`

## Architecture

- `server.ts`: server entrypoint
- `src/app.ts`: Express app, security middleware, routes, static hosting
- `src/routes/chat.ts`: `/chat` endpoint with validation and orchestration
- `src/services/mistral.ts`: Mistral agent API integration (uses `MISTRAL_API_KEY`, `AGENT_ID`)
- `src/services/rag.ts`: local index retrieval with cosine similarity
- `src/services/embeddings.ts`: local embedding generation using `@xenova/transformers`
- `src/scripts/build-index.ts`: document ingestion and index build script
- `public/`: frontend assets

## Local RAG Storage Scheme

This implementation uses on-disk JSON vector storage:

- The indexing script reads files from `DOCUMENTS_DIR` (`PDF` and `DOCX`)
- Text is chunked and embedded locally
- Embeddings are saved to `documents/embeddings/art-index.json`
- Query-time retrieval computes cosine similarity against local vectors

This is fully local storage and does not require external vector databases.

### Adding New Documents

When you find new art resources to add:

1. **Place the file** in `art_documents/` (PDF or DOCX)
2. **Rebuild the index** locally:
   ```bash
   npm run build:index
   ```
3. **Commit both** the new document and the updated index:
   ```bash
   git add art_documents/ documents/embeddings/art-index.json
   git commit -m "Add new art resource and rebuild index"
   ```
4. **Deploy normally** to Hostinger—no extra steps needed

The index is deterministic (same documents always produce the same embeddings), so you can safely version it in git.

## Security and Quality Controls

- `helmet` for hardening headers
- Request body size limit
- `express-rate-limit` for abuse protection
- Request validation with `zod`
- Basic PII redaction before model submission
- Strict TypeScript mode
