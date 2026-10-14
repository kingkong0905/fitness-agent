import json
import re
from datetime import date

import anthropic
from fastapi import HTTPException

from app.config import settings
from app.models.profile import MemberProfile

SYSTEM_PROMPT = """You are an elite certified personal trainer and sports nutritionist with 15+ years of experience designing personalized training programs. Your expertise spans strength training, cardiovascular conditioning, flexibility, and functional fitness.

When creating weekly training plans, you always:
- Prioritize safety and proper form above all else
- Apply progressive overload principles to drive adaptation
- Balance workout intensity with adequate recovery and rest days
- Tailor programs to the member's exact fitness level, equipment, and goals
- Account for any health conditions, injuries, or physical limitations
- Include proper warm-up and cool-down protocols
- Provide actionable technique cues for each exercise
- Distribute muscle group work to avoid overtraining

You respond ONLY with a valid JSON object — no markdown, no explanation, no preamble. The JSON must strictly follow the schema provided."""


def _build_user_prompt(profile: MemberProfile, week_start: date, extra_notes: str | None) -> str:
    bmi = round(profile.weight_kg / ((profile.height_cm / 100) ** 2), 1)
    lines = [
        "Create a personalized weekly training plan for the following member.",
        "",
        "MEMBER PROFILE:",
        f"- Name: {profile.full_name}",
        f"- Age: {profile.age} years old",
        f"- Gender: {profile.gender}",
        f"- Weight: {profile.weight_kg} kg",
        f"- Height: {profile.height_cm} cm (BMI: {bmi})",
        f"- Fitness Level: {profile.fitness_level}",
        f"- Goals: {profile.goals}",
        f"- Available Training Days: {profile.available_days}",
        f"- Available Equipment: {profile.equipment}",
        f"- Health Notes / Limitations: {profile.health_notes or 'None'}",
        f"- Week Starting: {week_start.strftime('%A, %B %d, %Y')}",
    ]
    if extra_notes:
        lines.append(f"- Additional Notes: {extra_notes}")

    lines += [
        "",
        "Return a JSON object with this exact structure:",
        """{
  "week_summary": "<brief 2-3 sentence overview of the week's training focus and goals>",
  "days": [
    {
      "day": "<day name e.g. Monday>",
      "focus": "<primary training focus e.g. Upper Body Strength>",
      "duration_minutes": <integer>,
      "warmup": ["<exercise or activity>", ...],
      "exercises": [
        {
          "name": "<exercise name>",
          "sets": <integer>,
          "reps": "<e.g. 8-10 or 30 seconds>",
          "rest_seconds": <integer>,
          "notes": "<brief technique cue>"
        }
      ],
      "cooldown": ["<stretch or activity>", ...],
      "calories_estimate": <integer>
    }
  ],
  "weekly_tips": ["<actionable tip>", ...],
  "nutrition_note": "<brief nutrition guidance aligned with the member's goals>"
}""",
        "",
        f"Only include days from the member's available training days. Include appropriate rest days. Ensure the plan is safe, effective, and achievable for a {profile.fitness_level} level member.",
    ]
    return "\n".join(lines)


class AgentService:
    async def generate_weekly_plan(
        self,
        profile: MemberProfile,
        week_start: date,
        extra_notes: str | None = None,
    ) -> dict:
        client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)

        try:
            response = client.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=4096,
                system=[
                    {
                        "type": "text",
                        "text": SYSTEM_PROMPT,
                        "cache_control": {"type": "ephemeral"},
                    }
                ],
                messages=[
                    {
                        "role": "user",
                        "content": _build_user_prompt(profile, week_start, extra_notes),
                    }
                ],
            )

            raw = response.content[0].text.strip()
            raw = re.sub(r"^```(?:json)?\s*", "", raw)
            raw = re.sub(r"\s*```$", "", raw)
            return json.loads(raw)

        except json.JSONDecodeError as exc:
            raise HTTPException(
                status_code=503, detail=f"Agent returned malformed JSON: {exc}"
            ) from exc
        except Exception as exc:
            raise HTTPException(status_code=503, detail=f"AI service unavailable: {exc}") from exc
