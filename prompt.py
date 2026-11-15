import tomllib
from collections.abc import Callable
from pathlib import Path


PROMPTS_PATH = Path(__file__).with_name("config") / "prompts.toml"


def decide_action(page: str, complete: Callable[[str, str], str], *, language: str = "ja") -> str:
    with PROMPTS_PATH.open("rb") as config:
        prompts = tomllib.load(config)
    instruction = prompts.get(language)
    if not isinstance(instruction, str) or not instruction.strip():
        raise ValueError(f"Missing prompt for language: {language}")
    instruction = instruction.strip()
    return complete(instruction, page)
