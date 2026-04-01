import { createServer } from "node:http";
import dotenv from "dotenv";
import { createApp } from "./src/app.js";

dotenv.config();

const port = Number(process.env.PORT ?? 5000);
const app = createApp();
const server = createServer(app);

server.listen(port, "0.0.0.0", () => {
  console.log(`Art Inspiration Agent listening on port ${port}`);
});
