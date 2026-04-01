# Documents Folder

This folder holds the **generated local RAG embeddings index** at `embeddings/art-index.json`.

## How It Works

Your actual document sources are in `../art_documents/` (PDF and DOCX files). The index is built **locally** from those documents:

```bash
npm run build:index
```

This command:
1. Reads all PDFs and DOCX from `../art_documents/`
2. Splits them into 1000-character chunks with 150-char overlap
3. Generates embeddings locally (using Xenova/all-MiniLM-L6-v2)
4. Saves the resulting index to `embeddings/art-index.json`

## Deployment

The `art-index.json` file is committed to git and deployed with your app. No server-side index generation needed.

## Updating the Index

When you add new documents:

```bash
# Add new files to ../art_documents/
npm run build:index
git add embeddings/art-index.json
git commit -m "Rebuild index with new documents"
```

The index is deterministic, so you can safely version it.
