from plugins.base import BasePlugin, PluginContext, PluginResponse
import random
import math


class RoulettePlugin(BasePlugin):
    name = "roulette"
    description = "Анимированная рулетка с колесом"
    version = "2.0.1"
    cooldown = 10
    author = "Nexus team"

    commands = {
        'roulette': 'Колесо фортуны: /roulette <reward|punish> <вариант1> <вариант2> ... до 15 вариантов',
        'rol': 'Короткая команда для roulette',
        'spin': 'Короткая команда для roulette'
    }

    def execute(self, command: str, args: list[str], ctx: PluginContext) -> PluginResponse:
        if len(args) < 3:
            return PluginResponse.error(
                "Используйте: /roulette <reward|punish> <вариант1> <вариант2> ...\n"
                "Минимум 2 варианта, максимум 15"
            )

        mode = args[0].lower()
        options = args[1:]

        if mode not in ['reward', 'punish', 'награда', 'наказание', 'r', 'p']:
            return PluginResponse.error("Режим: reward (награда) или punish (наказание)")

        if len(options) < 2:
            return PluginResponse.error("Минимум 2 варианта")
        if len(options) > 15:
            return PluginResponse.error("Максимум 15 вариантов")

        is_reward = mode in ['reward', 'награда', 'r']
        title = "РУЛЕТКА НАГРАД" if is_reward else "РУЛЕТКА НАКАЗАНИЙ"
        accent_color = "#FFD700" if is_reward else "#FF4444"

        winner_index = random.randint(0, len(options) - 1)
        winner = options[winner_index]

        html_code = self._create_wheel_html(options, winner_index, title, winner, accent_color, is_reward)
        return PluginResponse.ok(html_code)

    def _create_wheel_html(self, options, winner_index, title, winner, accent_color, is_reward):
        n = len(options)
        segment_angle = 360 / n
        target_rotation = 360 * 5 - (winner_index * segment_angle + segment_angle / 2)

        colors = [
            '#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8', '#F7DC6F',
            '#BB8FCE', '#85C1E9', '#F8B500', '#6C5CE7', '#A29BFE', '#FD79A8',
            '#00B894', '#E17055', '#74B9FF'
        ]

        svg_segments = []
        for i in range(n):
            start_angle = i * segment_angle - 90
            end_angle = start_angle + segment_angle

            start_rad = math.radians(start_angle)
            end_rad = math.radians(end_angle)

            x1 = 150 + 135 * math.cos(start_rad)
            y1 = 150 + 135 * math.sin(start_rad)
            x2 = 150 + 135 * math.cos(end_rad)
            y2 = 150 + 135 * math.sin(end_rad)

            large_arc = 1 if segment_angle > 180 else 0
            color = colors[i % len(colors)]

            svg_segments.append(
                f'<path d="M 150 150 L {x1} {y1} A 135 135 0 {large_arc} 1 {x2} {y2} Z" '
                f'fill="{color}" stroke="#1a1a2e" stroke-width="2"/>'
            )

            mid_angle = math.radians(start_angle + segment_angle / 2)
            tx = 150 + 95 * math.cos(mid_angle)
            ty = 150 + 95 * math.sin(mid_angle)
            text_angle = (start_angle + segment_angle / 2) + 90

            label = options[i][:14] + ('…' if len(options[i]) > 14 else '')
            svg_segments.append(
                f'<text x="{tx}" y="{ty}" fill="white" font-size="11" font-weight="bold" '
                f'text-anchor="middle" dominant-baseline="middle" '
                f'transform="rotate({text_angle}, {tx}, {ty})">{label}</text>'
            )

        return f"""
<div class="roulette-card" style="--spin-angle: {target_rotation}deg; --accent: {accent_color}; font-family: system-ui, -apple-system, sans-serif; max-width: 420px; margin: 0 auto; background: linear-gradient(145deg, #1e1b4b, #312e81); border-radius: 16px; padding: 20px; border: 2px solid #4f46e5; box-shadow: 0 10px 30px rgba(0,0,0,0.4);">
    <div style="text-align: center; font-size: 35px; font-weight: 800; color: var(--accent); margin-bottom: 15px; text-transform: uppercase; letter-spacing: 1px;">
        {title}
    </div>

    <div style="position: relative; width: 300px; height: 300px; margin: 0 auto;">
        <div style="position: absolute; top: -12px; left: 50%; transform: translateX(-50%); z-index: 10; font-size: 28px; filter: drop-shadow(0 4px 6px rgba(0,0,0,0.5));">⤵</div>

        <div class="roulette-wheel" style="width: 100%; height: 100%; border-radius: 50%; overflow: hidden; box-shadow: 0 0 20px rgba(0,0,0,0.5); animation: spin 4s cubic-bezier(0.25, 0.1, 0.25, 1) forwards;">
            <svg width="300" height="300" viewBox="0 0 300 300" style="width: 100%; height: 100%;">
                {''.join(svg_segments)}
                <circle cx="150" cy="150" r="28" fill="#1a1a2e" stroke="var(--accent)" stroke-width="4"/>
                <circle cx="150" cy="150" r="18" fill="var(--accent)"/>
                <polygon points="150,142 143,156 157,156" fill="#1a1a2e"/>
            </svg>
        </div>
    </div>

    <div class="roulette-result" style="margin-top: 20px; background: rgba(0,0,0,0.3); border-radius: 12px; padding: 16px; text-align: center; border: 1px solid var(--accent); animation: fadeIn 0.6s 4s forwards; opacity: 0;">
        <div style="font-size: 26px; font-weight: bold; color: var(--accent); margin-bottom: 8px;">WINNER!</div>
        <div style="font-size: 24px; font-weight: 700; color: white; background: rgba(255,255,255,0.1); padding: 12px; border-radius: 8px; word-break: break-word;">
            {winner}
        </div>
    </div>
</div>

<style>
@keyframes spin {{
    from {{ transform: rotate(0deg); }}
    to {{ transform: rotate(var(--spin-angle)); }}
}}
@keyframes fadeIn {{
    from {{ opacity: 0; transform: translateY(10px); }}
    to {{ opacity: 1; transform: translateY(0); }}
}}
.roulette-wheel {{
    transform: rotate(0deg);
}}
</style>
"""