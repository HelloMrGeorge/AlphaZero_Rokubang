import copy
import numpy as np
from roku_game import Board

MAX_SCORE = 10000
# # 第一手评分
# SCORES_1 = {'h5': MAX_SCORE, 'm5': MAX_SCORE, 'h4': 40, 'm4': 10, 'h3': 10, 'm3': 5, 'h2': 5, 'm2': 1}
# # 第零手评分,非当前玩家
# SCORES_0 = {'h5': MAX_SCORE, 'm5': MAX_SCORE, 'h4': MAX_SCORE, 'm4': MAX_SCORE, 'h3': 50, 'm3': 10, 'h2': 10, 'm2': 1}
# # 第二手评分
# SCORES_2 = {'h5': 40, 'm5': 20, 'h4': 40, 'm4': 20, 'h3': 10, 'm3': 2, 'h2': 2, 'm2': 1}
# 第零手评分,非当前玩家
SCORES_0 = {'h5': MAX_SCORE, 'm5': MAX_SCORE, 'h4': MAX_SCORE, 'm4': MAX_SCORE, 'h3': 100, 'm3': 15, 'h2': 15, 'm2': 1}
# 第二手评分
SCORES_2 = {'h5': 80, 'm5': 10, 'h4': 100, 'm4': 10, 'h3': 20, 'm3': 2, 'h2': 2, 'm2': 1}


def add_score(h, w, direction, board, player, score, table):
    square = board.square
    oppo_player = 3 - player
    connect_num = 0  # 连珠的棋子数
    origin = -1  # 区间的起点，从盘边缘开始
    flag_blocked = False
    if direction == (0, 1):  # 搜索到棋盘边缘
        length = board.width
    elif direction == (1, 0):
        length = board.height
    elif direction == (1, 1):
        length = min(board.height - h, board.width - w)
    else:
        length = min(h + 1, board.width - w)

    for i in range(length):
        if i <= origin:
            continue
        if square[h + (i * direction[0]), w + (i * direction[1])] == player:
            connect_num += 1
        else:
            # 遇到空位或者对手棋子，开始判定棋形
            chess_num = potential_num = connect_num
            for j in range(board.n_in_row - connect_num):
                try:
                    loc_j = square[h + (origin - j) * direction[0], w + (origin - j) * direction[1]]  # 处理超出棋盘的情况
                except IndexError:
                    loc_j = oppo_player

                # global global_flag
                # if global_flag:
                #     print(square)
                #     global_flag = False
                # if connect_num == 4 and print_flag and player == 1:
                #     print(square)
                #     print_flag = False

                if loc_j != oppo_player:
                    potential_num += 1
                    if loc_j == player:
                        chess_num += 1
                else:
                    flag_blocked = True
                    break

            origin = i  # 推进区间
            for j in range(board.n_in_row - connect_num):
                try:
                    loc_j = square[h + (i + j) * direction[0], w + (i + j) * direction[1]]  # 处理超出棋盘的情况
                except IndexError:
                    loc_j = oppo_player
                if loc_j != oppo_player:
                    potential_num += 1
                    if loc_j == player:
                        chess_num += 1
                else:
                    if connect_num != 0:  # 如果没有形成连珠，则不能推进区间，一旦形成连珠，不到最后一颗是不会进入这里的
                        origin = i + j  # 推进区间
                    flag_blocked = True
                    break

            # if connect_num == 4:
            #     print(potential_num, (old_origin, origin), (h + (i * direction[0]), w + (i * direction[1])), player)

            if potential_num >= 6:
                # 小于6的都是死棋
                if chess_num > connect_num:
                    score += table.get(f'm{chess_num}', 0)
                if flag_blocked:
                    # 有一面阻挡的情况就会是眠形
                    score += table.get(f'm{connect_num}', 0)
                    # if table.get(f'm{connect_num}', 0) >= 5:
                    #     print(f'm{connect_num}')
                    flag_blocked = False
                else:
                    score += table.get(f'h{connect_num}', 0)
                    # if table.get(f'h{connect_num}', 0) >= 5:
                    #     print(f'h{connect_num}')
            connect_num = 0
    return score


class MaxTree:

    def __init__(self, player):
        self.player = player

    def evaluate(self, board: Board):
        player = self.player
        oppo_player = 3 - player

        # 对结束棋局的走法剪枝
        end, winner = board.game_end()
        if end:
            del board
            if winner == -1:
                return 0
            elif winner == player:
                return np.inf
            else:
                return -np.inf

        oppo_table = SCORES_0
        my_table = SCORES_2

        my_score_sum = 0
        oppo_score_sum = 0
        for h in range(board.height):
            my_score_sum = add_score(h, 0, (0, 1), board, player, my_score_sum, my_table)
            oppo_score_sum = add_score(h, 0, (0, 1), board, oppo_player, oppo_score_sum, oppo_table)

        for w in range(board.width):
            my_score_sum = add_score(0, w, (1, 0), board, player, my_score_sum, my_table)
            oppo_score_sum = add_score(0, w, (1, 0), board, oppo_player, oppo_score_sum, oppo_table)

        for h in range(board.height - board.n_in_row + 1):
            my_score_sum = add_score(h, 0, (1, 1), board, player, my_score_sum, my_table)
            oppo_score_sum = add_score(h, 0, (1, 1), board, oppo_player, oppo_score_sum, oppo_table)

        for w in range(1, board.width - board.n_in_row + 1):  # 从1开始，避免重复记分
            my_score_sum = add_score(0, w, (1, 1), board, player, my_score_sum, my_table)
            oppo_score_sum = add_score(0, w, (1, 1), board, oppo_player, oppo_score_sum, oppo_table)

        for h in range(board.height - 1, board.n_in_row - 2, -1):
            my_score_sum = add_score(h, 0, (-1, 1), board, player, my_score_sum, my_table)
            oppo_score_sum = add_score(h, 0, (-1, 1), board, oppo_player, oppo_score_sum, oppo_table)

        for w in range(1, board.width - board.n_in_row + 1):
            my_score_sum = add_score(board.height - 1, w, (-1, 1), board, player, my_score_sum, my_table)
            oppo_score_sum = add_score(board.height - 1, w, (-1, 1), board, oppo_player, oppo_score_sum, oppo_table)

        del board
        return my_score_sum - oppo_score_sum

    def get_move(self, board: Board):
        best_first_action = None
        best_next_action = None
        best_score = -np.inf
        action_list = []
        for first_action in board.neighbor:
            first_board = copy.deepcopy(board)
            first_board.do_move(first_action)

            for next_action in first_board.neighbor:
                next_board = copy.deepcopy(first_board)
                next_board.do_move(next_action)

                score = self.evaluate(next_board)
                if score >= best_score:
                    best_score = score
                    best_first_action = first_action
                    best_next_action = next_action

                action_list.append((first_action, next_action, score))
            action_list.sort(key=lambda x: x[2], reverse=True)

        return action_list


class MTEngine:
    """
    AI player based on MMT for SAU
    """

    def __init__(self, name="MTEngine"):
        self.player = None
        self.name = name
        self.mt = None
        self.mt_oppo = None
        self.first_turn = False  # 首回合落子在天元
        self.chess = 2
        self.next_action = None

    def set_player_ind(self, p):
        self.player = p
        self.mt = MaxTree(self.player)
        self.mt_oppo = MaxTree(3 - self.player)
        if self.player == 1:
            self.first_turn = True

    def get_action(self, board):
        if self.first_turn:
            self.first_turn = False
            return 180  # 9 + 19 * 9
        if self.chess == 1:
            self.chess = 2
            return self.next_action

        if len(board.availables) > 0:
            action_list = self.mt.get_move(board)
            if len(action_list) >= 3:
                action_list = action_list[:3]
            best_score = np.inf
            for first_action, next_action, _ in action_list:
                oppo_board = copy.deepcopy(board)
                oppo_board.do_move(first_action)
                oppo_board.do_move(next_action)
                end, winner = board.game_end()
                if end:
                    action, self.next_action, _ = action_list[0]
                    break
                oppo_action_list = self.mt_oppo.get_move(oppo_board)
                score = oppo_action_list[0][2]
                if best_score >= score:
                    action = first_action
                    self.next_action = next_action
                    best_score = score
            self.chess = 1
            return action
        else:
            print("WARNING: the board is full")

    def __str__(self):
        return "Engine MT {}".format(self.player)
