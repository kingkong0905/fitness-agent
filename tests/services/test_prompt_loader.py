from pathlib import Path

import pytest
import yaml

from app.services.prompt_loader import PromptConfig, PromptLoader, get_prompt_loader

REAL_PROMPTS_DIR = Path(__file__).parent.parent.parent / "prompts"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _write_prompt(tmp_path: Path, name: str, version: str, data: dict) -> Path:
    prompt_dir = tmp_path / name
    prompt_dir.mkdir(parents=True, exist_ok=True)
    path = prompt_dir / f"{version}.yaml"
    path.write_text(yaml.dump(data))
    return path


MINIMAL_YAML = {
    "version": "v1",
    "description": "Test prompt",
    "model": "claude-sonnet-4-6",
    "max_tokens": 1024,
    "system": "You are a test assistant.",
    "user_template": "Hello {{ name }}!",
}

CONDITIONAL_YAML = {
    **MINIMAL_YAML,
    "user_template": (
        "Name: {{ name }}\n"
        "{% if extra %}"
        "Extra: {{ extra }}\n"
        "{% endif %}"
        "End"
    ),
}

RAW_BLOCK_YAML = {
    **MINIMAL_YAML,
    "user_template": 'Before {% raw %}{"key": "{{ value }}"}{% endraw %} After',
}

DEFAULT_FILTER_YAML = {
    **MINIMAL_YAML,
    "user_template": "Notes: {{ notes or 'None' }}",
}


# ---------------------------------------------------------------------------
# PromptLoader.load()
# ---------------------------------------------------------------------------

class TestPromptLoaderLoad:
    def test_load_returns_prompt_config(self, tmp_path):
        _write_prompt(tmp_path, "plan", "v1", MINIMAL_YAML)
        loader = PromptLoader(tmp_path)
        config = loader.load("plan", "v1")
        assert isinstance(config, PromptConfig)

    def test_load_fields_mapped_correctly(self, tmp_path):
        _write_prompt(tmp_path, "plan", "v1", MINIMAL_YAML)
        config = PromptLoader(tmp_path).load("plan", "v1")
        assert config.version == "v1"
        assert config.description == "Test prompt"
        assert config.model == "claude-sonnet-4-6"
        assert config.max_tokens == 1024
        assert config.system == "You are a test assistant."
        assert "{{ name }}" in config.user_template

    def test_load_description_defaults_to_empty_string(self, tmp_path):
        data = {k: v for k, v in MINIMAL_YAML.items() if k != "description"}
        _write_prompt(tmp_path, "plan", "v1", data)
        config = PromptLoader(tmp_path).load("plan", "v1")
        assert config.description == ""

    def test_load_system_prompt_is_stripped(self, tmp_path):
        data = {**MINIMAL_YAML, "system": "\n\n  You are neat.  \n\n"}
        _write_prompt(tmp_path, "plan", "v1", data)
        config = PromptLoader(tmp_path).load("plan", "v1")
        assert config.system == "You are neat."

    def test_load_raises_for_unknown_prompt_name(self, tmp_path):
        loader = PromptLoader(tmp_path)
        with pytest.raises(FileNotFoundError):
            loader.load("nonexistent", "v1")

    def test_load_raises_for_unknown_version(self, tmp_path):
        _write_prompt(tmp_path, "plan", "v1", MINIMAL_YAML)
        loader = PromptLoader(tmp_path)
        with pytest.raises(FileNotFoundError):
            loader.load("plan", "v99")

    def test_load_caches_result(self, tmp_path):
        _write_prompt(tmp_path, "plan", "v1", MINIMAL_YAML)
        loader = PromptLoader(tmp_path)
        first = loader.load("plan", "v1")
        second = loader.load("plan", "v1")
        assert first is second

    def test_load_different_versions_are_independent(self, tmp_path):
        v1 = {**MINIMAL_YAML, "version": "v1", "model": "model-a", "max_tokens": 100}
        v2 = {**MINIMAL_YAML, "version": "v2", "model": "model-b", "max_tokens": 200}
        _write_prompt(tmp_path, "plan", "v1", v1)
        _write_prompt(tmp_path, "plan", "v2", v2)
        loader = PromptLoader(tmp_path)
        assert loader.load("plan", "v1").model == "model-a"
        assert loader.load("plan", "v2").model == "model-b"


# ---------------------------------------------------------------------------
# PromptLoader.render_user()
# ---------------------------------------------------------------------------

class TestPromptLoaderRenderUser:
    def test_renders_variable(self, tmp_path):
        _write_prompt(tmp_path, "plan", "v1", MINIMAL_YAML)
        result = PromptLoader(tmp_path).render_user("plan", "v1", name="Alice")
        assert result == "Hello Alice!"

    def test_conditional_included_when_truthy(self, tmp_path):
        _write_prompt(tmp_path, "plan", "v1", CONDITIONAL_YAML)
        result = PromptLoader(tmp_path).render_user("plan", "v1", name="Bob", extra="bonus")
        assert "Extra: bonus" in result

    def test_conditional_excluded_when_none(self, tmp_path):
        _write_prompt(tmp_path, "plan", "v1", CONDITIONAL_YAML)
        result = PromptLoader(tmp_path).render_user("plan", "v1", name="Bob", extra=None)
        assert "Extra" not in result

    def test_conditional_excluded_when_not_provided(self, tmp_path):
        _write_prompt(tmp_path, "plan", "v1", CONDITIONAL_YAML)
        result = PromptLoader(tmp_path).render_user("plan", "v1", name="Bob")
        assert "Extra" not in result

    def test_raw_block_preserves_curly_braces(self, tmp_path):
        _write_prompt(tmp_path, "plan", "v1", RAW_BLOCK_YAML)
        result = PromptLoader(tmp_path).render_user("plan", "v1")
        assert '{"key": "{{ value }}"}' in result

    def test_default_filter_for_none_value(self, tmp_path):
        _write_prompt(tmp_path, "plan", "v1", DEFAULT_FILTER_YAML)
        result = PromptLoader(tmp_path).render_user("plan", "v1", notes=None)
        assert "Notes: None" in result

    def test_default_filter_uses_actual_value(self, tmp_path):
        _write_prompt(tmp_path, "plan", "v1", DEFAULT_FILTER_YAML)
        result = PromptLoader(tmp_path).render_user("plan", "v1", notes="knee pain")
        assert "Notes: knee pain" in result

    def test_output_is_stripped(self, tmp_path):
        data = {**MINIMAL_YAML, "user_template": "  hello  "}
        _write_prompt(tmp_path, "plan", "v1", data)
        result = PromptLoader(tmp_path).render_user("plan", "v1")
        assert result == "hello"


# ---------------------------------------------------------------------------
# Real YAML files — v1 and v2
# ---------------------------------------------------------------------------

class TestRealPromptFiles:
    def test_v1_loads_all_fields(self):
        loader = PromptLoader(REAL_PROMPTS_DIR)
        config = loader.load("weekly_plan", "v1")
        assert config.version == "v1"
        assert config.model == "claude-sonnet-4-6"
        assert config.max_tokens == 4096
        assert len(config.system) > 50
        assert "{{ full_name }}" in config.user_template

    def test_v2_loads_all_fields(self):
        loader = PromptLoader(REAL_PROMPTS_DIR)
        config = loader.load("weekly_plan", "v2")
        assert config.version == "v2"
        assert config.model == "claude-opus-4-7"
        assert config.max_tokens == 8000
        assert len(config.system) > 50
        assert "{{ full_name }}" in config.user_template

    def test_v2_max_tokens_greater_than_v1(self):
        loader = PromptLoader(REAL_PROMPTS_DIR)
        assert loader.load("weekly_plan", "v2").max_tokens > loader.load("weekly_plan", "v1").max_tokens

    def test_v1_render_includes_profile_variables(self):
        loader = PromptLoader(REAL_PROMPTS_DIR)
        result = loader.render_user(
            "weekly_plan", "v1",
            full_name="Jane Doe", age=28, gender="female",
            weight_kg=65.0, height_cm=168.0, bmi=23.0,
            fitness_level="intermediate", goals="lose weight",
            available_days="Monday,Wednesday,Friday",
            equipment="dumbbells", health_notes=None,
            week_start="Monday, October 14, 2026", extra_notes=None,
        )
        assert "Jane Doe" in result
        assert "intermediate" in result
        assert "lose weight" in result
        assert "Monday,Wednesday,Friday" in result

    def test_v1_render_includes_extra_notes_when_provided(self):
        loader = PromptLoader(REAL_PROMPTS_DIR)
        result = loader.render_user(
            "weekly_plan", "v1",
            full_name="Jane", age=28, gender="female",
            weight_kg=65.0, height_cm=168.0, bmi=23.0,
            fitness_level="beginner", goals="fitness",
            available_days="Monday", equipment="bodyweight",
            health_notes=None, week_start="Monday, October 14, 2026",
            extra_notes="Focus on form this week",
        )
        assert "Focus on form this week" in result

    def test_v1_render_excludes_extra_notes_when_absent(self):
        loader = PromptLoader(REAL_PROMPTS_DIR)
        result = loader.render_user(
            "weekly_plan", "v1",
            full_name="Jane", age=28, gender="female",
            weight_kg=65.0, height_cm=168.0, bmi=23.0,
            fitness_level="beginner", goals="fitness",
            available_days="Monday", equipment="bodyweight",
            health_notes=None, week_start="Monday, October 14, 2026",
            extra_notes=None,
        )
        assert "Additional Notes" not in result

    def test_v1_render_preserves_json_schema_braces(self):
        loader = PromptLoader(REAL_PROMPTS_DIR)
        result = loader.render_user(
            "weekly_plan", "v1",
            full_name="Jane", age=28, gender="female",
            weight_kg=65.0, height_cm=168.0, bmi=23.0,
            fitness_level="beginner", goals="fitness",
            available_days="Monday", equipment="bodyweight",
            health_notes=None, week_start="Monday, October 14, 2026",
            extra_notes=None,
        )
        assert '"week_summary"' in result
        assert '"exercises"' in result


# ---------------------------------------------------------------------------
# get_prompt_loader() singleton
# ---------------------------------------------------------------------------

class TestGetPromptLoaderSingleton:
    def test_returns_prompt_loader_instance(self):
        loader = get_prompt_loader()
        assert isinstance(loader, PromptLoader)

    def test_returns_same_instance_on_repeated_calls(self):
        assert get_prompt_loader() is get_prompt_loader()
