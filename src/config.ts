import dotenv from "dotenv";
import { z } from "zod";

dotenv.config();

const envSchema = z.object({
  NODE_ENV: z.enum(["development", "production"]).default("development"),
  PORT: z.coerce.number().default(5000),
  MISTRAL_API_KEY: z.string().optional().default(""),
  AGENT_ID: z.string().optional().default(""),
  APP_URL: z.string().url().optional().or(z.literal("")),
  DOCUMENTS_DIR: z.string().default("art_documents"),
  RAG_INDEX_PATH: z.string().default("documents/embeddings/art-index.json"),
  RAG_TOP_K: z.coerce.number().int().positive().default(4),
  EMBEDDING_MODEL: z.string().default("Xenova/all-MiniLM-L6-v2")
});

const parsed = envSchema.safeParse(process.env);

if (!parsed.success) {
  const issues = parsed.error.issues.map((issue) => `${issue.path.join(".")}: ${issue.message}`).join("; ");
  throw new Error(`Invalid environment configuration: ${issues}`);
}

export const config = {
  ...parsed.data,
  APP_URL: parsed.data.APP_URL || undefined
};
