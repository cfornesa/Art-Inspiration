import fs from "node:fs/promises";
import path from "node:path";
import dotenv from "dotenv";
import fg from "fast-glob";
import mammoth from "mammoth";
import pdfParse from "pdf-parse";
import { config } from "../config.js";
import type { RagIndex, RagItem } from "../types.js";
import { embedText } from "../services/embeddings.js";

dotenv.config();

const chunkSize = Number(process.env.RAG_CHUNK_SIZE ?? 1000);
const chunkOverlap = Number(process.env.RAG_CHUNK_OVERLAP ?? 150);

function splitText(text: string): string[] {
  const clean = text.replace(/\s+/g, " ").trim();
  if (!clean) {
    return [];
  }

  const chunks: string[] = [];
  let start = 0;

  while (start < clean.length) {
    const end = Math.min(start + chunkSize, clean.length);
    chunks.push(clean.slice(start, end));
    if (end >= clean.length) {
      break;
    }
    start = Math.max(0, end - chunkOverlap);
  }

  return chunks;
}

async function extractText(filePath: string): Promise<string> {
  if (filePath.toLowerCase().endsWith(".pdf")) {
    const buffer = await fs.readFile(filePath);
    const parsed = await pdfParse(buffer);
    return parsed.text ?? "";
  }

  if (filePath.toLowerCase().endsWith(".docx")) {
    const parsed = await mammoth.extractRawText({ path: filePath });
    return parsed.value ?? "";
  }

  return "";
}

async function run() {
  const docsRoot = path.resolve(config.DOCUMENTS_DIR);
  const files = await fg(["**/*.pdf", "**/*.docx"], { cwd: docsRoot, absolute: true });

  if (files.length === 0) {
    console.error(`No PDF or DOCX files found in ${docsRoot}.`);
    process.exit(1);
  }

  const items: RagItem[] = [];

  for (const file of files) {
    const source = path.relative(process.cwd(), file);
    const text = await extractText(file);
    const chunks = splitText(text);

    for (let i = 0; i < chunks.length; i += 1) {
      const chunk = chunks[i];
      const embedding = await embedText(chunk);
      items.push({
        id: `${source}#${i}`,
        source,
        chunkIndex: i,
        text: chunk,
        embedding
      });
    }

    console.log(`Indexed ${source} -> ${chunks.length} chunks`);
  }

  const outputPath = path.resolve(config.RAG_INDEX_PATH);
  await fs.mkdir(path.dirname(outputPath), { recursive: true });

  const index: RagIndex = {
    metadata: {
      createdAt: new Date().toISOString(),
      model: config.EMBEDDING_MODEL,
      chunkSize,
      chunkOverlap,
      documentsCount: files.length,
      chunksCount: items.length
    },
    items
  };

  await fs.writeFile(outputPath, JSON.stringify(index), "utf8");
  console.log(`Saved local RAG index to ${outputPath}`);
}

run().catch((error) => {
  console.error(error);
  process.exit(1);
});
