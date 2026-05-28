import yaml
from pathlib import Path

CONFIG_DIR = Path.home() / ".config" / "ai-token-bar"
CONFIG_PATH = CONFIG_DIR / "config.yaml"


def load_config() -> dict:
    if not CONFIG_PATH.exists():
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        _write_default_config()
        return {}
    with open(CONFIG_PATH) as f:
        return yaml.safe_load(f) or {}


def _write_default_config():
    example = Path(__file__).parent / "config.example.yaml"
    if example.exists():
        CONFIG_PATH.write_text(example.read_text())
