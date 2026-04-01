import path from "node:path";
import express from "express";
import cors from "cors";
import helmet from "helmet";
import rateLimit from "express-rate-limit";
import { config } from "./config.js";
import { chatRouter } from "./routes/chat.js";

export function createApp() {
  const app = express();

  app.use(helmet({ contentSecurityPolicy: false }));
  app.use(
    cors({
      origin: config.APP_URL ? [config.APP_URL] : true,
      methods: ["GET", "POST"],
      allowedHeaders: ["Content-Type"]
    })
  );
  app.use(express.json({ limit: "1mb" }));
  app.use(
    rateLimit({
      windowMs: 60 * 1000,
      max: 60,
      standardHeaders: true,
      legacyHeaders: false
    })
  );

  const publicPath = path.resolve("public");
  app.use("/public", express.static(publicPath, { maxAge: "1d" }));
  app.use("/static", express.static(publicPath, { maxAge: "1d" }));

  app.get("/", (_req, res) => {
    res.sendFile(path.join(publicPath, "index.html"));
  });

  app.get("/health", (_req, res) => {
    res.json({
      status: "online",
      agent: "Art Inspiration Agent",
      version: "1.0",
      features: ["pii_redaction", "preference_fine_tuning", "local_rag_embeddings", "mistral_agent"]
    });
  });

  app.use(chatRouter);

  return app;
}
