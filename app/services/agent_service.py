import json
import re
from datetime import date

import anthropic
from fastapi import HTTPException

from app.config import settings
from app.models.profile import MemberProfile
from app.services.prompt_loader import get_prompt_loader


class AgentService:
    async def generate_weekly_plan(
        self,
        profile: MemberProfile,
        week_start: date,
        extra_notes: str | None = None,
    ) -> dict:
        loader = get_prompt_loader()
        prompt = loader.load(settings.PROMPT_NAME, settings.PROMPT_VERSION)

        bmi = round(profile.weight_kg / ((profile.height_cm / 100) ** 2), 1)
        user_message = loader.render_user(
            prompt_name=settings.PROMPT_NAME,
            prompt_version=settings.PROMPT_VERSION,
            full_name=profile.full_name,
            age=profile.age,
            gender=profile.gender,
            weight_kg=profile.weight_kg,
            height_cm=profile.height_cm,
            bmi=bmi,
            fitness_level=profile.fitness_level,
            goals=profile.goals,
            available_days=profile.available_days,
            equipment=profile.equipment,
            health_notes=profile.health_notes,
            week_start=week_start.strftime("%A, %B %d, %Y"),
            extra_notes=extra_notes,
        )

        client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)

        try:
            response = client.messages.create(
                model=prompt.model,
                max_tokens=prompt.max_tokens,
                system=[
                    {
                        "type": "text",
                        "text": prompt.system,
                        "cache_control": {"type": "ephemeral"},
                    }
                ],
                messages=[{"role": "user", "content": user_message}],
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
