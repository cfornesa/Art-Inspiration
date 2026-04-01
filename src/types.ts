export type ChatRole = "user" | "assistant";

export interface ChatMessage {
  role: ChatRole;
  content: string;
}

export interface UserPreferences {
  style?: string | null;
  medium?: string | null;
  skill_level?: string | null;
  focus?: string | null;
}

export interface RagItem {
  id: string;
  source: string;
  chunkIndex: number;
  text: string;
  embedding: number[];
}

export interface RagIndex {
  metadata: {
    createdAt: string;
    model: string;
    chunkSize: number;
    chunkOverlap: number;
    documentsCount: number;
    chunksCount: number;
  };
  items: RagItem[];
}
