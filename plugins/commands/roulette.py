from plugins.base import BasePlugin, PluginContext, PluginResponse
import random


class RoulettePlugin(BasePlugin):
    name = "roulette"
    description = "Рулетка с наградами или наказаниями"
    version = "1.0.0"
    cooldown = 10

    commands = {
        'roulette': 'Рулетка: /roulette <reward|punish> <вариант1> <вариант2> ... [до 15]',
        'spin': 'Короткая команда для /roulette',
        'rol' : 'Вариант короткой команды'
    }

    def execute(self, command: str, args: list[str], ctx: PluginContext) -> PluginResponse:
        if len(args) < 3:
            return PluginResponse.error(
                "Используйте: /roulette <reward|punish> <вариант1> <вариант2> ...\n"
                "Минимум 2 варианта, максимум 15"
            )

        mode = args[0].lower()
        options = args[1:]

        if mode not in ['reward', 'punish', 'награда', 'наказание']:
            return PluginResponse.error("Режим: reward (награда) или punish (наказание)")

        if len(options) < 2:
            return PluginResponse.error("Минимум 2 варианта")
        if len(options) > 15:
            return PluginResponse.error("Максимум 15 вариантов")

        is_reward = mode in ['reward', 'награда']
        emoji = "🎁" if is_reward else "💀"
        title = "РУЛЕТКА НАГРАД" if is_reward else "РУЛЕТКА НАКАЗАНИЙ"

        result = random.choice(options)

        final_msg = f"{emoji} {title}\n\n"
        final_msg += "барабан остановился...\n\n"
        final_msg += f"Результат:\n"
        final_msg += f"└─ {result}\n\n"

        final_msg += f"Всего вариантов: {len(options)}\n"

        shown_options = options[:5]
        for i, opt in enumerate(shown_options, 1):
            prefix = "├─" if i < len(shown_options) else "└─"
            final_msg += f"{prefix} {opt}\n"

        if len(options) > 5:
            final_msg += f"\n_... и ещё {len(options) - 5} вариантов_"

        return PluginResponse.ok(final_msg)