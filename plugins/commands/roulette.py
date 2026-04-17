from plugins import BasePlugin, PluginContext, PluginResponse
import random
import math
import re
import hashlib
import time
import json


class RoulettePlugin(BasePlugin):
    name = "roulette"
    description = "Анимированная рулетка с колесом"
    version = "2.3.0"
    cooldown = 10
    author = "Nexus team"

    commands = {
        'roulette': 'Колесо фортуны: /roulette <reward|punish> <вариант1> ...',
        'rol': 'Короткая команда для roulette',
        'spin': '/spin 0g 1b 2r для casino mode'
    }

    def execute(self, command: str, args: list[str], ctx: PluginContext) -> PluginResponse:
        casino_pattern = re.compile(r'^\d+[rgb]$', re.IGNORECASE)
        spin_id = hashlib.md5(f"{ctx.user_id}{time.time()}{random.random()}".encode()).hexdigest()[:8]

        if all(casino_pattern.match(arg) for arg in args):
            return self._run_casino(args, spin_id)
        else:
            mode = args[0].lower()
            options = args[1:] if mode in ['reward', 'punish', 'награда', 'наказание', 'r', 'p'] else args
            if len(options) < 2:
                return PluginResponse.error("Минимум 2 варианта")
            if len(options) > 15:
                return PluginResponse.error("Максимум 15 вариантов")

            is_reward = mode in ['reward', 'награда', 'r']
            title = "РУЛЕТКА НАГРАД" if is_reward else "РУЛЕТКА НАКАЗАНИЙ"
            accent = "#FFD700" if is_reward else "#FF4444"
            winner = random.choice(options)

            return PluginResponse.ok(self.gen_standard_html(options, winner, title, accent, spin_id))

    def _run_casino(self, args, spin_id):
        items = [{'num': a[:-1], 'color': a[-1].lower()} for a in args]
        cmap = {
            'g': {'bg': '#22c55e', 'label': 'ЗЕРО'},
            'r': {'bg': '#ef4444', 'label': 'КРАСНОЕ'},
            'b': {'bg': '#1e293b', 'label': 'ЧЁРНОЕ'}
        }
        winner = random.choice(items)
        return PluginResponse.ok(self.gen_casino_html(items, winner, cmap, spin_id))

    @staticmethod
    def gen_standard_html(options, winner, title, accent, spin_id):
        n, ang = len(options), 360 / len(options)
        w_idx = options.index(winner)
        target = 360 * 5 - (w_idx * ang + ang / 2)
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8', '#F7DC6F', '#BB8FCE', '#85C1E9', '#F8B500',
                  '#6C5CE7', '#A29BFE', '#FD79A8', '#00B894', '#E17055', '#74B9FF']

        svg = []
        for i, opt in enumerate(options):
            sa, ea = i * ang - 90, (i + 1) * ang - 90
            sr, er = math.radians(sa), math.radians(ea)
            x1, y1 = 150 + 135 * math.cos(sr), 150 + 135 * math.sin(sr)
            x2, y2 = 150 + 135 * math.cos(er), 150 + 135 * math.sin(er)
            la = 1 if ang > 180 else 0
            svg.append(
                f'<path d="M 150 150 L {x1} {y1} A 135 135 0 {la} 1 {x2} {y2} Z" fill="{colors[i % 15]}" stroke="#1a1a2e" stroke-width="2"/>')
            mid = math.radians(sa + ang / 2)
            tx, ty = 150 + 95 * math.cos(mid), 150 + 95 * math.sin(mid)
            rot = sa + ang / 2 + 90
            lbl = opt[:14] + ('…' if len(opt) > 14 else '')
            svg.append(
                f'<text x="{tx}" y="{ty}" fill="white" font-size="11" font-weight="bold" text-anchor="middle" dominant-baseline="middle" transform="rotate({rot}, {tx}, {ty})">{lbl}</text>')
        svg.append(
            '<circle cx="150" cy="150" r="28" fill="#1a1a2e" stroke="var(--accent)" stroke-width="4"/><circle cx="150" cy="150" r="18" fill="var(--accent)"/><polygon points="150,142 143,156 157,156" fill="#1a1a2e"/>')

        return f"""<div id="wheel-{spin_id}" data-options='{json.dumps(options)}' data-winner="{winner}" data-type="standard" style="--spin-angle: {target}deg; --accent: {accent}; font-family: system-ui, sans-serif; max-width: 380px; width: 100%; margin: 0 auto; background: linear-gradient(145deg, #1e1b4b, #312e81); border-radius: 16px; padding: 16px; border: 2px solid #4f46e5; box-shadow: 0 10px 30px rgba(0,0,0,0.4); box-sizing: border-box;">
        <div style="text-align:center; font-size:28px; font-weight:800; color:var(--accent); margin-bottom:12px; text-transform:uppercase;">{title}</div>
        <div style="position:relative; width:100%; max-width:300px; aspect-ratio:1/1; margin:0 auto;">
            <div style="position:absolute; top:-8px; left:50%; transform:translateX(-50%); z-index:10; width:20px; height:20px;">
                <div style="width:3px; height:10px; background:#fbbf24; margin:0 auto; border-radius:2px;"></div>
            </div>
            <div class="rw" style="width:100%; height:100%; border-radius:50%; overflow:hidden; box-shadow:0 0 20px rgba(0,0,0,0.5); animation: spin 4s cubic-bezier(0.25,0.1,0.25,1) forwards;">
                <svg width="300" height="300" viewBox="0 0 300 300" style="width:100%; height:100%;">{''.join(svg)}</svg>
            </div>
        </div>
        <div class="rr" style="margin-top:16px; background:rgba(0,0,0,0.3); border-radius:12px; padding:14px; text-align:center; border:1px solid var(--accent); animation: fadeIn 0.6s 4s forwards; opacity:0;">
            <div style="font-size:22px; font-weight:bold; color:var(--accent); margin-bottom:6px;">WINNER!</div>
            <div style="font-size:24px; font-weight:700; color:white; background:rgba(255,255,255,0.1); padding:10px; border-radius:8px; word-break:break-word;">{winner}</div>
        </div>
        <button class="roulette-reroll-btn" style="margin-top:10px; width:100%; padding:10px; background:var(--accent); color:#1e1b4b; font-weight:bold; border:none; border-radius:8px; cursor:pointer; font-size:14px; opacity:0; animation: fadeIn 0.5s 4.2s forwards;">Крутить снова (убрать '{winner[:20]}{"..." if len(winner) > 20 else ""}')</button>
    </div>
    <style>@keyframes spin{{from{{transform:rotate(0)}}to{{transform:rotate(var(--spin-angle))}}}}@keyframes fadeIn{{from{{opacity:0;transform:translateY(10px)}}to{{opacity:1;transform:translateY(0)}}}}.rw{{transform:rotate(0)}}</style>"""

    @staticmethod
    def gen_casino_html(options, winner, cmap, spin_id):
        n, ang = len(options), 360 / len(options)
        w_idx = options.index(winner)
        target = 360 * 5 - (w_idx * ang + ang / 2)
        svg = []
        for i, it in enumerate(options):
            sa, ea = i * ang - 90, (i + 1) * ang - 90
            sr, er = math.radians(sa), math.radians(ea)
            x1, y1 = 150 + 135 * math.cos(sr), 150 + 135 * math.sin(sr)
            x2, y2 = 150 + 135 * math.cos(er), 150 + 135 * math.sin(er)
            la = 1 if ang > 180 else 0
            fl = cmap[it['color']]['bg']
            svg.append(
                f'<path d="M 150 150 L {x1} {y1} A 135 135 0 {la} 1 {x2} {y2} Z" fill="{fl}" stroke="#fff" stroke-width="1.5"/>')
            mid = math.radians(sa + ang / 2)
            tx, ty = 150 + 95 * math.cos(mid), 150 + 95 * math.sin(mid)
            rot = sa + ang / 2 + 90
            svg.append(
                f'<text x="{tx}" y="{ty}" fill="white" font-size="12" font-weight="bold" text-anchor="middle" dominant-baseline="middle" transform="rotate({rot}, {tx}, {ty})">{it["num"]}</text>')
        svg.append(
            '<circle cx="150" cy="150" r="28" fill="#1a1a2e" stroke="#fbbf24" stroke-width="4"/><circle cx="150" cy="150" r="18" fill="#fbbf24"/><polygon points="150,142 143,156 157,156" fill="#1a1a2e"/>')

        win_info = cmap[winner['color']]
        return f"""<div id="wheel-{spin_id}" data-options='{json.dumps(options)}' data-winner="{winner['num']}" data-type="casino" style="--spin: {target}deg; max-width: 380px; width: 100%; margin: 0 auto; background: #0f172a; border-radius: 16px; padding: 16px; border: 3px solid #fbbf24; box-shadow: 0 10px 30px rgba(0,0,0,0.5); font-family: system-ui, sans-serif; box-sizing: border-box;">
        <div style="text-align:center; font-size:28px; font-weight:800; color:#fbbf24; margin-bottom:12px; text-transform:uppercase;">CASINO</div>
        <div style="position:relative; width:100%; max-width:300px; aspect-ratio:1/1; margin:0 auto;">
            <div style="position:absolute; top:-8px; left:50%; transform:translateX(-50%); z-index:10; width:20px; height:20px;">
                <div style="width:2px; height:8px; background:#fbbf24; margin:0 auto; border-radius:1px;"></div>
            </div>
            <div id="rw-{spin_id}" style="width:100%; height:100%; border-radius:50%; overflow:hidden; box-shadow:0 0 20px rgba(0,0,0,0.5); border:3px solid #fbbf24; transform:rotate(0deg);">
                <svg width="300" height="300" viewBox="0 0 300 300" style="width:100%; height:100%; display:block;">{''.join(svg)}</svg>
            </div>
        </div>
        <div class="rr" style="margin-top:16px; background:rgba(255,255,255,0.05); border-radius:12px; padding:14px; text-align:center; border:1px solid #fbbf24; animation: fadeIn 0.6s 4s forwards; opacity:0;">
            <div style="font-size:22px; font-weight:bold; color:#fbbf24; margin-bottom:6px; text-transform:uppercase;">WINNER!</div>
            <div style="font-size:28px; font-weight:900; color:#fff; text-shadow:0 2px 12px rgba(0,0,0,0.9); margin:4px 0;">{winner['num']}</div>
            <div style="display:inline-block; padding:4px 12px; border-radius:16px; background:{win_info['bg']}; color:white; font-weight:bold; font-size:13px;">{win_info['label']}</div>
        </div>
        <button class="roulette-reroll-btn" style="margin-top:10px; width:100%; padding:10px; background:#fbbf24; color:#0f172a; font-weight:bold; border:none; border-radius:8px; cursor:pointer; font-size:14px; opacity:0; animation: fadeIn 0.5s 4.2s forwards;">Крутить снова (убрать {winner['num']})</button>
    </div>
    <style>
    @keyframes spin{{from{{transform:rotate(0)}}to{{transform:rotate(var(--spin))}}}}
    @keyframes fadeIn{{from{{opacity:0;transform:translateY(10px)}}to{{opacity:1;transform:translateY(0)}}}}
    #rw-{spin_id}{{animation:spin 4s cubic-bezier(0.25,0.1,0.25,1) forwards;transform:rotate(0deg)}}
    </style>
    """

    @staticmethod
    def help() -> str:
        return (
            "Колесо Фортуны\n\n"
            "Анимированная рулетка с двумя режимами работы.\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "Стандартный режим:\n"
            "\n"
            "/roulette <режим> <вариант1> <вариант2> ...\n"
            "/rol <режим> <вариант1> <вариант2> ...\n"
            "\n\n"
            "Режимы:\n"
            "reward / награда / r — рулетка наград\n"
            "punish / наказание / p — рулетка наказаний\n"
            "Без режима — случайный выбор из вариантов\n\n"
            "Примеры:\n"
            "/roulette reward Пицца Суши Бургер\n"
            "/rol punish Правда Действие\n"
            "/roulette Вариант1 Вариант2 Вариант3\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "Casino режим:\n"
            "\n"
            "/spin <число><цвет> ...\n"
            "\n\n"
            "Цвета:\n"
            "g — зелёное (зеро)\n"
            "r — красное\n"
            "b — чёрное\n\n"
            "Примеры:\n"
            "  /spin 0g 1r 2b 3r\n"
            "  /spin 7r 17b 23r\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "Ограничения:\n"
            "Минимум вариантов: 2\n"
            "Максимум вариантов: 15\n"
            "Длина текста: до 14 символов в секторе\n\n"
            "Кулдаун: 10 секунд\n\n"
            "Особенности:\n"
            "Плавная анимация вращения\n"
            "Автоматическое определение победителя\n"
            "Кнопка \"Крутить снова\"\n"
            "Уникальный ID для каждого спина"
        )