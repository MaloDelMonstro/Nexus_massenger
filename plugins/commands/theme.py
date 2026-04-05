from plugins.base import BasePlugin, PluginContext, PluginResponse
from plugins.security import SecurityPolicy


class ThemePlugin(BasePlugin):
    name = "theme"
    description = "Смена темы оформления чата"
    version = "1.0.0"

    commands = {
        'theme': 'Сменить тему: /theme <название> или /theme reset'
    }

    THEMES = {
        'default': {'bg': '#1f2937', 'text': '#ffffff', 'accent': '#6366f1'},
        'dark': {'bg': '#111827', 'text': '#f3f4f6', 'accent': '#8b5cf6'},
        'light': {'bg': '#f9fafb', 'text': '#1f2937', 'accent': '#4f46e5'},
        'matrix': {'bg': '#000000', 'text': '#00ff00', 'accent': '#00cc00'},
        'sunset': {'bg': '#1e1b4b', 'text': '#fef3c7', 'accent': '#f97316'},
    }

    async def execute(self, command: str, args: list[str], ctx: PluginContext) -> PluginResponse:
        if not args:
            themes_list = ', '.join(f"`{t}`" for t in self.THEMES.keys())
            return PluginResponse.ok(f"Доступные темы: {themes_list}\n\nИспользуйте `/theme <название>` для применения")

        theme_name = args[0].lower()

        if theme_name == 'reset':
            return PluginResponse.ok("Тема сброшена на стандартную", data={'theme': 'default'})

        if not SecurityPolicy.is_safe_theme_name(theme_name):
            return PluginResponse.error("Недопустимое название темы")

        if theme_name in self.THEMES:
            theme_data = self.THEMES[theme_name]
            return PluginResponse.ok(
                f"Тема изменена на `{theme_name}` ✨",
                data={'theme': theme_name, 'colors': theme_data}
            )

        return PluginResponse.error(f"Тема `{theme_name}` не найдена. Доступные: {', '.join(self.THEMES.keys())}")