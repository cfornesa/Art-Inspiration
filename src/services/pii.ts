const piiPatterns: Record<string, RegExp> = {
  EMAIL: /[\w.-]+@[\w.-]+\.\w+/gi,
  PHONE: /\+?\d{1,4}?[-.\s]?\(?\d{1,3}?\)?[-.\s]?\d{1,4}[-.\s]?\d{1,4}[-.\s]?\d{1,9}/g,
  SSN: /\b(?!666|000|9\d{2})\d{3}[- ]?(?!00)\d{2}[- ]?(?!0000)\d{4}\b/g,
  ADDRESS: /\d{1,5}\s\w+.\s(\b\w+\b\s){1,2}\w+,\s\w+,\s[A-Z]{2}\s\d{5}/gi
};

export function redactPii(text: string): string {
  let redacted = text;
  for (const [label, pattern] of Object.entries(piiPatterns)) {
    redacted = redacted.replace(pattern, `[${label}_REDACTED]`);
  }
  return redacted;
}
