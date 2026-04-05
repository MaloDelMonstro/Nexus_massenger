from plugins.base import BasePlugin, PluginContext, PluginResponse


class DoomStubPlugin(BasePlugin):
    """
    Заглушка для DOOM 2
    """

    name = "doom"
    description = "DOOM 2 в чате (заглушка)"
    version = "0.1.0"
    required_role = 'admin'

    commands = {
        'game': 'Запустить DOOM: /game doom [action]'
    }

    async def execute(self, command: str, args: list[str], ctx: PluginContext) -> PluginResponse:
        if not args or args[0].lower() != 'doom':
            return None

        if len(args) < 2:
            return PluginResponse.ok(
                " **DOOM 2 Stub**\n\n"
                "Это демонстрационный плагин. В полной версии:\n"
                "• Запуск игрового сервера\n"
                "• Стриминг видео в чат через WebRTC\n"
                "• Управление персонажем командами: `/doom move forward`, `/doom shoot`\n\n"
                "Для разработки: реализуйте интеграцию с PrBoom+ или Chocolate Doom"
            )

        action = args[1].lower()

        if action == 'start':
            return PluginResponse.ok(
                "Запуск DOOM 2...\n\n"
                "```\nDOOM Shareware Registered v1.9\nBuild 1234567\n"
                "Loading IWAD: doom.wad\n"
                "Initializing graphics... OK\n"
                "Initializing sound... OK\n\n"
                "Game started! Use `/doom move <direction>` to play.\n```",
                data={'game_session': 'stub_12345'}
            )

        elif action == 'move':
            direction = args[2] if len(args) > 2 else 'forward'
            return PluginResponse.ok(
                f"Вы двигаетесь: `{direction}`\n\n*(в реальной версии здесь был бы кадр из игры)*")

        elif action == 'shoot':
            return PluginResponse.ok("💥 БА-БАХ! Враг повержен!\n\n*(демо-режим: +10 очков)*", data={'score': 10})

        elif action == 'status':
            return PluginResponse.ok(
                "Статус DOOM 2:\n"
                "• Сессия: stub_12345\n"
                "• FPS: 60 (эмуляция)\n"
                "• Счёт: 0\n"
                "• Уровень: E1M1 - Hangar"
            )

        return PluginResponse.error(f"Неизвестная команда: `/doom {action}`")