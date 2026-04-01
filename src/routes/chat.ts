import { Router } from "express";
import { z } from "zod";
import { getArtContext } from "../services/rag.js";
import { redactPii } from "../services/pii.js";
import { buildPreferenceContext } from "../services/preferences.js";
import { generateAgentReply } from "../services/mistral.js";
import { stripMarkdown } from "../services/format.js";
import type { ChatMessage } from "../types.js";

const chatSchema = z.object({
  message: z.string().min(1),
  history: z.array(z.object({ role: z.enum(["user", "assistant"]), content: z.string() })).default([]),
  preferences: z
    .object({
      style: z.string().nullable().optional(),
      medium: z.string().nullable().optional(),
      skill_level: z.string().nullable().optional(),
      focus: z.string().nullable().optional()
    })
    .nullable()
    .optional()
});

export const chatRouter = Router();

chatRouter.post("/chat", async (req, res) => {
  const parsed = chatSchema.safeParse(req.body);
  if (!parsed.success) {
    return res.status(400).json({ reply: "Error: Invalid request payload." });
  }

  try {
    const { message, history, preferences } = parsed.data;
    const artContext = await getArtContext(message);
    const augmentedInput = artContext
      ? `[Retrieved Reference Material]\n${artContext}\n\n[User Message]\n${message}`
      : message;

    const safeInput = redactPii(augmentedInput);
    const preferenceContext = buildPreferenceContext(preferences ?? undefined);
    const userContent = preferenceContext ? `${preferenceContext}\n\n${safeInput}` : safeInput;

    const inputs: ChatMessage[] = [...history, { role: "user", content: userContent }];
    const reply = await generateAgentReply(inputs);

    return res.json({
      reply: stripMarkdown(reply),
      metadata: { status: "success" }
    });
  } catch (error) {
    const message = error instanceof Error ? error.message : "Unknown system error.";
    return res.status(500).json({ reply: `System Error: ${message}` });
  }
});
