# -*- coding: utf-8 -*-
import numpy as np
import copy


class Board:
    """board for the game"""

    def __init__(self, **kwargs):
        self.last_move = None
        self.availables = None
        self.current_player = None
        self.neighbor: set = set()  # 保存邻近格点，包括棋子周围的8格
        self.width = int(kwargs.get('width', 8))
        self.height = int(kwargs.get('height', 8))
        # 字典的方式存储state, key: move, value: player
        self.states = {}
        # 一行几个子赢棋
        self.n_in_row = int(kwargs.get('n_in_row', 6))
        self.players = [1, 2]  # player1 and player2
        self.chesses = 1  # 初始只能下一个棋
        self.last_moves = []  # 上回合下的所有棋
        self.curr_moves = []  # 这回合下的所有棋
        self.square = np.zeros((self.height, self.width))  # 新增一个表格形式的棋盘状态，0表示无棋子，1表示玩家1的棋子，2表示玩家2的棋子

    def init_board(self, start_player=0):
        if self.width < self.n_in_row or self.height < self.n_in_row:
            raise Exception('board width and height can not be '
                            'less than {}'.format(self.n_in_row))
        self.current_player = self.players[start_player]  # 开始的玩家
        # 把可以走的步数存在一个list中
        self.availables = list(range(self.width * self.height))
        self.states = {}
        self.last_move = -1
        self.square = np.zeros((self.height, self.width))

    def move_to_location(self, move):
        """
        3*3 的棋盘 moves 长这样:
        6 7 8
        3 4 5
        0 1 2
         move 5的 位置就是(1,2)
        """
        h = move // self.width
        w = move % self.width
        return [h, w]

    def location_to_move(self, location):
        if len(location) != 2:
            return -1
        h = location[0]
        w = location[1]
        move = h * self.width + w
        if move not in range(self.width * self.height):
            return -1
        return move

    def current_state(self):
        """返回当前玩家视角下的棋局状态state.
        state 形状: 4*width*height，4个二值特征平面
        """

        square_state = np.zeros((4, self.width, self.height))
        if self.states:
            moves, players = np.array(list(zip(*self.states.items())))
            move_curr = moves[players == self.current_player]
            move_oppo = moves[players != self.current_player]
            square_state[0][move_curr // self.height,
                            move_curr % self.height] = 1.0
            square_state[1][move_oppo // self.height,
                            move_oppo % self.height] = 1.0
            for move in self.last_moves:
                square_state[2][move // self.height, move % self.height] = 1.0
            for move in self.curr_moves:
                square_state[3][move // self.height, move % self.height] = 1.0
        return square_state[:, ::-1, :]

    def do_move(self, move):
        """下一个棋子"""
        self.states[move] = self.current_player
        h, w = self.move_to_location(move)
        self.square[h, w] = self.current_player
        self.availables.remove(move)
        self._update_neighbor(move)
        self.last_move = move
        self.curr_moves.append(move)
        self.chesses -= 1
        if self.chesses == 0:
            self._change_turn()
            self.chesses = 2
        return self.chesses

    def _change_turn(self):
        """交换下棋的权利"""
        self.current_player = (
            self.players[0] if self.current_player == self.players[1]
            else self.players[1]
        )
        """ 当前玩家走的两颗棋子做一份深拷贝赋值给last_moves"""
        self.last_moves = copy.deepcopy(self.curr_moves)
        self.curr_moves.clear()

    # def has_a_winner(self):
    #     """判断当前是否有赢家了"""
    #     width = self.width
    #     height = self.height
    #     states = self.states
    #     n = self.n_in_row
    #
    #     moved = list(set(range(width * height)) - set(self.availables))
    #     if len(moved) < self.n_in_row + 2:
    #         return False, -1
    #
    #     for m in moved:
    #         h = m // width
    #         w = m % width
    #         player = states[m]
    #
    #         if (w in range(width - n + 1) and
    #                 len(set(states.get(i, -1) for i in range(m, m + n))) == 1):  # 如果自[h,w]起，横排n个元素的颜色只有一种
    #             return True, player  # 则游戏结束，返回赢家
    #
    #         if (h in range(height - n + 1) and
    #                 len(set(states.get(i, -1) for i in range(m, m + n * width, width))) == 1):
    #             return True, player
    #
    #         if (w in range(width - n + 1) and h in range(height - n + 1) and
    #                 len(set(states.get(i, -1) for i in range(m, m + n * (width + 1), width + 1))) == 1):
    #             return True, player
    #
    #         if (w in range(n - 1, width) and h in range(height - n + 1) and
    #                 len(set(states.get(i, -1) for i in range(m, m + n * (width - 1), width - 1))) == 1):
    #             return True, player
    #
    #     return False, -1
    #
    # def game_end(self):
    #     """检查游戏有没有结束"""
    #     win, winner = self.has_a_winner()
    #     if win:
    #         return True, winner  # 某个玩家胜利
    #     elif not len(self.availables):
    #         return True, -1  # 平局
    #     return False, -1  # 游戏尚未结束

    def game_end(self):
        """
        使用square，快速判赢，只需要判别最后一次行棋周围的5格，只存在平局和自己赢的情况，不存在自己下完，对手赢棋的情况
        """
        h, w = self.move_to_location(self.last_move)
        player = self.states[self.last_move]

        if len(self.availables) > self.width * self.height - self.n_in_row * 2 + 1:
            # 最快后手第三手赢棋
            return False, -1

        for direction in [(1, 0), (0, 1), (1, 1), (-1, 1)]:
            # 方向为横向、纵向、斜右、斜左
            win = self.connect_n(h, w, direction, player)
            if win:
                # print(self.square)
                return win, player

        if len(self.availables) == 0:
            return True, -1  # 平局

        return False, -1  # 游戏尚未结束

    def connect_n(self, h, w, direction, player):
        n = self.n_in_row
        connect_num = 0
        for i in range(-n + 1, n):
            # 需要从倒退五格开始，防止漏算最后一手棋在中间形成连珠的情况
            try:
                if self.square[h + (i * direction[0]), w + (i * direction[1])] == player:
                    connect_num = connect_num + 1
                else:
                    connect_num = 0
                if connect_num >= n:
                    return True
            except IndexError:
                continue
        return False

    def get_current_player(self):
        return self.current_player

    def is_start(self):
        """判断游戏是否为开局"""
        return len(self.availables) == (self.width * self.height)

    def _update_neighbor(self, move):
        """
        更新棋盘与棋子相邻的格点
        """
        width = self.width
        candidates = [
            move + 1, move - 1,
            move + width - 1, move + width, move + width + 1,
            move - width - 1, move - width, move - width + 1
        ]
        for candidate in candidates:
            if candidate not in self.availables:
                continue  # 排除已经下过的格点
            if abs((candidate // width) - (move // width)) > 1:
                continue  # 排除非斜对角格点
            if ((move % width) == 0) and ((candidate % width) == width - 1):
                continue  # 排除超出左界的格点
            if ((move % width) == width - 1) and ((candidate % width) == 0):
                continue  # 排除超出右界的格点
            self.neighbor.add(candidate)
        self.neighbor.discard(move)

    def __str__(self):
        return str(self.height) + "_" + str(self.width) + "_" + str(self.n_in_row)


class Game(object):
    """game server"""

    def __init__(self, board):
        self.board = board

    @staticmethod
    def graphic(board, player1, player2):
        """Draw the board and show game info"""
        width = board.width
        height = board.height

        print("Player", player1, "with X".rjust(3))
        print("Player", player2, "with O".rjust(3))
        print()
        for x in range(width):
            print("{0:8}".format(x), end='')
        print('\r\n')
        for i in range(height - 1, -1, -1):
            print("{0:4d}".format(i), end='')
            for j in range(width):
                loc = i * width + j
                p = board.states.get(loc, -1)
                if p == player1:
                    print('X'.center(8), end='')
                elif p == player2:
                    print('O'.center(8), end='')
                else:
                    print('_'.center(8), end='')
            print('\r\n\r\n')

    def start_play(self, player1, player2, start_player=0, is_shown=1):
        """两个玩家之间的对战，或者玩家对战AI"""
        if start_player not in (0, 1):
            raise Exception('start_player should be either 0 (player1 first) '
                            'or 1 (player2 first)')
        self.board.init_board(start_player)
        p1, p2 = self.board.players
        player1.set_player_ind(p1)
        player2.set_player_ind(p2)
        players = {p1: player1, p2: player2}
        if is_shown:
            self.graphic(self.board, player1.player, player2.player)
        while True:
            current_player = self.board.get_current_player()
            player_in_turn = players[current_player]
            move = player_in_turn.get_action(self.board)
            self.board.do_move(move)
            if is_shown:
                self.graphic(self.board, player1.player, player2.player)
            end, winner = self.board.game_end()
            if end:
                if is_shown:
                    if winner != -1:
                        print("Game end. Winner is", players[winner])
                    else:
                        print("Game end. Tie")
                return winner

    def start_self_play(self, player, is_shown=0, temp=1e-3):
        """ 使用 MCTS player开始一次自对弈, reuse the search tree,
         存储 self-play 的数据: (state, mcts_probs, z)
        """
        # 初始化棋盘
        self.board.init_board()
        p1, p2 = self.board.players  # p1 =1，p2 =2
        states, mcts_probs, current_players, is_need_changes = [], [], [], []
        while True:
            # 获取可行的步数和每一步的胜率 , return_prob=1代表返回move的同时也返回胜率
            move, move_probs = player.get_action(self.board,
                                                 temp=temp,
                                                 return_prob=1)
            # #存储数据（每一步走完之后的盘面信息，该步的胜率，走棋的玩家）
            states.append(self.board.current_state())
            mcts_probs.append(move_probs)
            current_players.append(self.board.current_player)
            # 将移动表现出来
            is_need_change = self.board.do_move(move)
            # 存储下一步是否需要交换玩家
            is_need_changes.append(is_need_change)
            if is_shown:
                self.graphic(self.board, p1, p2)
            end, winner = self.board.game_end()  # 判断游戏是否结束
            if end:
                # 当前玩家视角下的winner ，他还是我
                winners_z = np.zeros(len(current_players))
                if winner != -1:
                    winners_z[np.array(current_players) == winner] = 1.0  # 赢了这个人走的那一步就是正反馈
                    winners_z[np.array(current_players) != winner] = -1.0  # 输了就是负反馈
                # 重置根节点
                player.reset_player()
                if is_shown:
                    if winner != -1:
                        print("Game end. Winner is player:", winner)
                    else:
                        print("Game end. Tie")
                return winner, zip(states, mcts_probs, winners_z)  # 返回每一步，每步的先验概率，每步的反馈
