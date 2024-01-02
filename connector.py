from loguru import logger

from roku_game import Board, Game
# from roku_mcts import MCTSEngine
# from roku_RL import RLEngine
# from roku_MMT import MMTEngine
from roku_MT import MTEngine

# from policy_value_net_pytorch import PolicyValueNet  # Pytorch


CHAR_MAP = {
    'A': '00', 'B': '01', 'C': '02', 'D': '03', 'E': '04',
    'F': '05', 'G': '06', 'H': '07', 'I': '08', 'J': '09',
    'K': '10', 'L': '11', 'M': '12', 'N': '13', 'O': '14',
    'P': '15', 'Q': '16', 'R': '17', 'S': '18', '@': '-1'
}
CHAR_MAP = str.maketrans(CHAR_MAP)

NUMBER_MAP = {
    0: 'A', 1: 'B', 2: 'C', 3: 'D', 4: 'E', 5: 'F',
    6: 'G', 7: 'H', 8: 'I', 9: 'J', 10: 'K', 11: 'L',
    12: 'M', 13: 'N', 14: 'O', 15: 'P', 16: 'Q', 17: 'R', 18: 'S'
}


class ServerPlayer:
    """
    SAU服务端的玩家
    """

    def __init__(self):
        self.player = None
        self.locations = None

    def set_player_ind(self, p):
        self.player = p

    def get_action(self, board):
        try:
            move = board.location_to_move(self.locations[0:2])
            self.locations = self.locations[2:]
        except Exception:
            move = -1
            if move == -1 or move not in board.availables:
                raise Exception("invalid move")
            else:
                raise Exception("unknown exception")
        return move

    def parse_move(self, moves: str):
        self.locations = moves.translate(CHAR_MAP)
        self.locations = [int(self.locations[i:i + 2]) for i in range(0, 8, 2)]

    def __str__(self):
        return "Human {}".format(self.player)


class LocalServer:
    """
    在本地构建一个与SAU同步的服务器
    """

    def __init__(self, engine, width=19, height=19):
        self.server = ServerPlayer()
        self.engine = engine
        self.board = None
        self.game = None
        self.width = width
        self.height = height
        self.first_turn = False

    def parse_command(self, command):
        command = command.strip()
        logger.info(f'command: {command}')
        command_parts = command.split(' ')
        command_word = command_parts[0]

        if command_word == "name?":
            self.board = Board(width=self.width, height=self.height, n_in_row=6)
            self.game = Game(self.board)
            response = "name " + self.engine.name
            return response

        elif command_word == "new":
            side = command_parts[1]
            self.board.init_board()  # 默认0号玩家开局
            p1, p2 = self.board.players
            if side == 'black':
                self.server.set_player_ind(p2)
                self.engine.set_player_ind(p1)
                move = self.engine.get_action(self.board)
                self.board.do_move(move)
                response = "move JJ@@\n"
            else:
                self.server.set_player_ind(p1)
                self.engine.set_player_ind(p2)
                self.first_turn = True
                response = "wait for black\n"
            logger.info(f'response: {response}')
            return response

        elif command_word == "move":
            self.server.parse_move(command_parts[1])
            move = self.server.get_action(self.board)
            self.board.do_move(move)
            if self.first_turn:
                self.first_turn = False
            else:
                move = self.server.get_action(self.board)
                self.board.do_move(move)

            response = ""
            move = self.engine.get_action(self.board)
            self.board.do_move(move)
            response += ''.join([NUMBER_MAP[i] for i in self.board.move_to_location(move)])
            move = self.engine.get_action(self.board)
            self.board.do_move(move)
            response += ''.join([NUMBER_MAP[i] for i in self.board.move_to_location(move)])
            response = "move " + response
            logger.info(f'response: {response}')
            return response

        elif command_word == "end":
            response = "end\n"
            logger.info(f'response: {response}')
            return response

        elif command_word == "quit":
            response = "quit\n"
            logger.info(f'response: {response}')
            quit()

        elif command_word == "error":
            response = "error\n"
            logger.info(f'response: {response}')
            return response

        else:
            response = "unknown command"
            logger.info(f'response: {response}')
            return response


if __name__ == '__main__':

    logger.remove(handler_id=None)
    log_file = logger.add('test.log', level='INFO')
    # MCTS Engine
    # engine = MCTSEngine(c_puct=5, n_playout=400, name="Engine2")

    # RL Engine
    # model_file = './engine.model'
    # best_policy = PolicyValueNet(19, 19, model_file=model_file)
    # engine = RLEngine(best_policy, c_puct=5, n_playout=400, name="Engine3")

    # MMT Engine
    engine = MTEngine(name="Engine4")

    local_server = LocalServer(engine)
    # 主程序循环读取指令并处理
    while True:
        command = input()
        response = local_server.parse_command(command)
        if response:
            print(response)
