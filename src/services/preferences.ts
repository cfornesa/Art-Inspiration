import type { UserPreferences } from "../types.js";

export function buildPreferenceContext(preferences?: UserPreferences | null): string {
  if (!preferences) {
    return "";
  }

  const lines: string[] = ["USER PREFERENCES (apply to this and all subsequent responses):"];

  if (preferences.style) {
    lines.push(`- Artistic Style: Prioritize ${preferences.style} aesthetics and historical references.`);
  }
  if (preferences.medium) {
    lines.push(`- Medium Focus: Tailor all technical advice specifically to ${preferences.medium}.`);
  }
  if (preferences.skill_level) {
    const level = preferences.skill_level.toLowerCase();
    if (level === "beginner") {
      lines.push("- Skill Level: Use accessible language; avoid jargon; explain fundamentals first.");
    } else if (level === "intermediate") {
      lines.push("- Skill Level: Assume foundational knowledge; introduce nuanced techniques.");
    } else if (level === "advanced") {
      lines.push("- Skill Level: Use professional terminology; focus on refinement and mastery.");
    } else {
      lines.push(`- Skill Level: Calibrate for a ${preferences.skill_level} practitioner.`);
    }
  }
  if (preferences.focus) {
    lines.push(`- Topic Focus: Emphasize ${preferences.focus} in both conceptual and technical guidance.`);
  }

  return lines.length > 1 ? lines.join("\n") : "";
}
