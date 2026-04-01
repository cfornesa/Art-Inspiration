import { config } from "../config.js";
import type { ChatMessage } from "../types.js";

interface AgentCompletionResponse {
  choices?: Array<{
    message?: {
      content?: string;
    };
  }>;
}

export async function generateAgentReply(messages: ChatMessage[]): Promise<string> {
  if (!config.MISTRAL_API_KEY) {
    throw new Error("MISTRAL_API_KEY not configured.");
  }

  if (!config.AGENT_ID) {
    throw new Error("AGENT_ID not configured.");
  }

  const response = await fetch("https://api.mistral.ai/v1/agents/completions", {
    method: "POST",
    headers: {
      Authorization: `Bearer ${config.MISTRAL_API_KEY}`,
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      agent_id: config.AGENT_ID,
      messages
    })
  });

  if (!response.ok) {
    const body = await response.text();
    throw new Error(`Mistral API error (${response.status}): ${body}`);
  }

  const data = (await response.json()) as AgentCompletionResponse;
  const reply = data.choices?.[0]?.message?.content?.trim();

  if (!reply) {
    throw new Error("Empty response from agent.");
  }

  return reply;
}
