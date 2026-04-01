export function stripMarkdown(text: string): string {
  let result = text;
  result = result.replace(/#{1,6}\s*/g, "");
  result = result.replace(/\*{1,3}([^*]+)\*{1,3}/g, "$1");
  result = result.replace(/_{1,2}([^_]+)_{1,2}/g, "$1");
  result = result.replace(/[\u2013\u2014]/g, "-");
  result = result.replace(/[\u2600-\u27BF]/g, "");
  result = result.replace(/[\u{1F000}-\u{1FFFF}]/gu, "");
  result = result.replace(/\n{3,}/g, "\n\n");
  return result.trim();
}
