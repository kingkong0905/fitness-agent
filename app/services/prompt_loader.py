from dataclasses import dataclass
from pathlib import Path

import yaml
from jinja2 import BaseLoader, Environment


@dataclass(frozen=True)
class PromptConfig:
    version: str
    description: str
    model: str
    max_tokens: int
    system: str
    user_template: str


class PromptLoader:
    def __init__(self, prompts_dir: Path):
        self._prompts_dir = prompts_dir
        self._cache: dict[str, PromptConfig] = {}
        self._jinja_env = Environment(loader=BaseLoader(), keep_trailing_newline=True)

    def load(self, name: str, version: str) -> PromptConfig:
        cache_key = f"{name}/{version}"
        if cache_key not in self._cache:
            path = self._prompts_dir / name / f"{version}.yaml"
            if not path.exists():
                raise FileNotFoundError(f"Prompt not found: {path}")
            raw = yaml.safe_load(path.read_text())
            self._cache[cache_key] = PromptConfig(
                version=raw["version"],
                description=raw.get("description", ""),
                model=raw["model"],
                max_tokens=raw["max_tokens"],
                system=raw["system"].strip(),
                user_template=raw["user_template"],
            )
        return self._cache[cache_key]

    def render_user(self, prompt_name: str, prompt_version: str, **variables) -> str:
        template_str = self.load(prompt_name, prompt_version).user_template
        template = self._jinja_env.from_string(template_str)
        return template.render(**variables).strip()


_loader: PromptLoader | None = None


def get_prompt_loader() -> PromptLoader:
    global _loader
    if _loader is None:
        prompts_dir = Path(__file__).parent.parent.parent / "prompts"
        _loader = PromptLoader(prompts_dir)
    return _loader
