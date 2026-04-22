from dataclasses import dataclass
import json
from pathlib import Path


@dataclass
class PluginConfig:
    enabled: bool = True
    settings: dict = None
    permissions: dict = None

    def __post_init__(self):
        if self.settings is None:
            self.settings = {}
        if self.permissions is None:
            self.permissions = {}


class PluginConfigManager:
    CONFIG_FILE = "data/plugins_config.json"

    def __init__(self):
        self.configs: dict[str, PluginConfig] = {}
        self._load()

    def _load(self):
        path = Path(self.CONFIG_FILE)
        if path.exists():
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for name, cfg in data.items():
                        self.configs[name] = PluginConfig(**cfg)
            except Exception as e:
                print(f"{e}")

    def _save(self):
        Path(self.CONFIG_FILE).parent.mkdir(parents=True, exist_ok=True)
        data = {name: {
            'enabled': cfg.enabled,
            'settings': cfg.settings,
            'permissions': cfg.permissions
        } for name, cfg in self.configs.items()}

        with open(self.CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def get(self, plugin_name: str) -> PluginConfig:
        if plugin_name not in self.configs:
            self.configs[plugin_name] = PluginConfig()
        return self.configs[plugin_name]

    def set_enabled(self, plugin_name: str, enabled: bool):
        cfg = self.get(plugin_name)
        cfg.enabled = enabled
        self._save()

    def is_enabled(self, plugin_name: str) -> bool:
        return self.get(plugin_name).enabled
