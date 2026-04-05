from plugins.base import BasePlugin, PluginContext, PluginResponse
from plugins.games.base_game import BaseGame
import random


class TicTacToeGame(BaseGame):

    name = "tictactoe"
    description = "Крестики-нолики в чате"

    def __init__(self):
        super().__init__()
        self.board = [' '] * 9
        self.current_player = 'X'
        self.winner = None

    def render_board(self) -> str:
        lines = []
        for i in range(0, 9, 3):
            row = self.board[i:i + 3]
            lines.append(f" {row[0]} │ {row[1]} │ {row[2]} ")
            if i < 6:
                lines.append("───┼───┼───")
        return "\n".join(lines)

    def make_move(self, position: int, player: str) -> bool:
        if position < 0 or position > 8 or self.board[position] != ' ':
            return False
        self.board[position] = player
        return True

    def check_winner(self) -> str | None:
        wins = [
            [0, 1, 2], [3, 4, 5], [6, 7, 8],
            [0, 3, 6], [1, 4, 7], [2, 5, 8],
            [0, 4, 8], [2, 4, 6]
        ]
        for combo in wins:
            if self.board[combo[0]] == self.board[combo[1]] == self.board[combo[2]] != ' ':
                return self.board[combo[0]]
        if ' ' not in self.board:
            return 'draw'
        return None

    def get_state(self) -> dict:
        return {
            'board': self.board.copy(),
            'current_player': self.current_player,
            'winner': self.winner
        }

    def load_state(self, state: dict):
        self.board = state.get('board', [' '] * 9)
        self.current_player = state.get('current_player', 'X')
        self.winner = state.get('winner')


class TicTacToePlugin(BasePlugin):
    name = "tictactoe"
    description = "Игра в крестики-нолики"
    version = "1.0.0"

    commands = {
        'game': 'Запустить игру: /game tictactoe [action] [args]'
    }

    _games: dict[int, dict[int, TicTacToeGame]] = {}

    async def execute(self, command: str, args: list[str], ctx: PluginContext) -> PluginResponse | None:
        if not args or args[0].lower() != 'tictactoe':
            return

        chat_id = ctx.chat_id or 0

        if chat_id not in self._games:
            self._games[chat_id] = {}

        user_games = self._games[chat_id]

        if len(args) < 2:
            if ctx.user_id in user_games:
                return PluginResponse.error(
                    "У вас уже есть активная игра. Завершите её или сдайтесь: `/game tictactoe resign`")

            game = TicTacToeGame()
            user_games[ctx.user_id] = game

            return PluginResponse.ok(
                f"🎮 Новая игра в крестики-нолики!\n\n"
                f"Ходят крестики (X). Ваш ход: `/game tictactoe move <1-9>`\n\n"
                f"Поле:\n```\n{game.render_board()}```\n\n"
                f"Номера ячеек:\n`1│2│3` `4│5│6` `7│8│9`",
                data={'game_started': True, 'player': 'X'}
            )

        subcommand = args[1].lower()
        game = user_games.get(ctx.user_id)

        if subcommand == 'move' and game and not game.winner:
            if len(args) < 3:
                return PluginResponse.error("Укажите номер ячейки: `/game tictactoe move 5`")

            try:
                position = int(args[2]) - 1  # 1-9 -> 0-8
                if not game.make_move(position, game.current_player):
                    return PluginResponse.error("Ячейка занята или неверный номер (1-9)")

                winner = game.check_winner()
                if winner:
                    game.winner = winner
                    result = "Ничья!" if winner == 'draw' else f"Победили {'крестики' if winner == 'X' else 'нолики'}!"
                    del user_games[ctx.user_id]
                    return PluginResponse.ok(f"{result}\n\nФинальное поле:\n```\n{game.render_board()}```")

                if game.current_player == 'X':
                    game.current_player = 'O'
                    empty = [i for i, v in enumerate(game.board) if v == ' ']
                    if empty:
                        bot_move = random.choice(empty)
                        game.make_move(bot_move, 'O')
                        winner = game.check_winner()
                        if winner:
                            game.winner = winner
                            result = "Ничья!" if winner == 'draw' else f"Бот победил!"
                            del user_games[ctx.user_id]
                            return PluginResponse.ok(f"{result}\n\n```\n{game.render_board()}```")
                    game.current_player = 'X'

                return PluginResponse.ok(
                    f"Ход принят! Ваш следующий ход: `/game tictactoe move <1-9>`\n\n"
                    f"Поле:\n```\n{game.render_board()}```",
                    data={'move_made': True}
                )

            except ValueError:
                return PluginResponse.error("Укажите число от 1 до 9")

        elif subcommand == 'resign':
            if ctx.user_id in user_games:
                del user_games[ctx.user_id]
                return PluginResponse.ok("Вы сдались. Игра завершена.")
            return PluginResponse.error("У вас нет активной игры")

        elif subcommand == 'status':
            if ctx.user_id not in user_games:
                return PluginResponse.error("У вас нет активной игры. Начните: `/game tictactoe`")
            game = user_games[ctx.user_id]
            return PluginResponse.ok(
                f"Ваша игра в прогрессе:\n```\n{game.render_board()}```\n\n"
                f"Сейчас ходят: {'крестики (вы)' if game.current_player == 'X' else 'нолики (бот)'}"
            )

        return PluginResponse.error(
            f"Неизвестная подкоманда. Используйте: `/game tictactoe`, `move`, `status`, `resign`")