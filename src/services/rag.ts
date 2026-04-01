import fs from "node:fs/promises";
import path from "node:path";
import { config } from "../config.js";
import type { RagIndex, RagItem } from "../types.js";
import { embedText } from "./embeddings.js";

let cache: { mtimeMs: number; index: RagIndex } | null = null;

function cosineSimilarity(a: number[], b: number[]): number {
  if (a.length !== b.length || a.length === 0) {
    return -1;
  }

  let dot = 0;
  let normA = 0;
  let normB = 0;

  for (let i = 0; i < a.length; i += 1) {
    dot += a[i] * b[i];
    normA += a[i] * a[i];
    normB += b[i] * b[i];
  }

  if (normA === 0 || normB === 0) {
    return -1;
  }

  return dot / (Math.sqrt(normA) * Math.sqrt(normB));
}

async function loadIndex(): Promise<RagIndex | null> {
  const absolute = path.resolve(config.RAG_INDEX_PATH);
  try {
    const stats = await fs.stat(absolute);
    if (cache && cache.mtimeMs === stats.mtimeMs) {
      return cache.index;
    }

    const raw = await fs.readFile(absolute, "utf8");
    const parsed = JSON.parse(raw) as RagIndex;
    cache = { mtimeMs: stats.mtimeMs, index: parsed };
    return parsed;
  } catch {
    return null;
  }
}

export async function getArtContext(query: string): Promise<string> {
  const index = await loadIndex();
  if (!index || index.items.length === 0) {
    return "";
  }

  const queryEmbedding = await embedText(query);

  const scored = index.items
    .map((item: RagItem) => ({
      item,
      score: cosineSimilarity(queryEmbedding, item.embedding)
    }))
    .filter((entry) => entry.score > 0)
    .sort((a, b) => b.score - a.score)
    .slice(0, config.RAG_TOP_K);

  if (scored.length === 0) {
    return "";
  }

  return scored
    .map((entry) => `[Source: ${entry.item.source}]\n${entry.item.text}`)
    .join("\n\n---\n\n");
}
