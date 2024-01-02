import copy
import numpy as np
from roku_game import Board

MAX_SCORE = 10000
# 第零手评分,非当前玩家
SCORES_0 = {'h5': MAX_SCORE, 'm5': MAX_SCORE, 'h4': MAX_SCORE, 'm4': MAX_SCORE, 'h3': 10, 'm3': 5, 'h2': 2, 'm2': 1}
# 第一手评分
SCORES_1 = {'h5': MAX_SCORE, 'm5': MAX_SCORE, 'h4': 10, 'm4': 7, 'h3': 7, 'm3': 4, 'h2': 4, 'm2': 1}
# 第二手评分
SCORES_2 = {'h5': 10, 'm5': 7, 'h4': 7, 'm4': 4, 'h3': 4, 'm3': 2, 'h2': 2, 'm2': 1}


def evaluate_rand(node, player):
    return np.random.randint(-100, 100)


# def evaluate_roku(node, player):
#     board: Board = node.board
#     current_player = board.get_current_player()
#     board.do_move(node.action)
#     next_player = board.get_current_player()
#     end, winner = board.game_end()
#     oppo_player = 3 - player  # 3-2=1 3-1=2
#
#     if end:
#         del board
#         if winner == -1:
#             return 0
#         elif winner == player:
#             return MAX_SCORE
#         else:
#             return -MAX_SCORE
#
#     if current_player == next_player:
#         my_table = SCORES_1
#     else:
#         my_table = SCORES_2
#     oppo_table = SCORES_0
#
#     # 每一行、列、斜对角都只保留最好的一个棋形
#     my_score_sum = 0
#     oppo_score_sum = 0
#     for h in range(board.height):
#         my_add_score = 0
#         oppo_add_score = 0
#         for w in range(board.width - board.n_in_row + 1):
#             my_temp_score = my_table.get(get_form(h, w, (0, 1), board, player), 0)
#             oppo_temp_score = oppo_table.get(get_form(h, w, (0, 1), board, oppo_player), 0)
#             if my_temp_score > my_add_score:
#                 my_add_score = my_temp_score
#             if oppo_temp_score > oppo_add_score:
#                 oppo_add_score = oppo_temp_score
#         my_score_sum += my_add_score
#         oppo_score_sum += oppo_add_score
#
#     for w in range(board.width):
#         my_add_score = 0
#         oppo_add_score = 0
#         for h in range(board.height - board.n_in_row + 1):
#             my_temp_score = my_table.get(get_form(h, w, (1, 0), board, player), 0)
#             oppo_temp_score = oppo_table.get(get_form(h, w, (1, 0), board, oppo_player), 0)
#             if my_temp_score > my_add_score:
#                 my_add_score = my_temp_score
#             if oppo_temp_score > oppo_add_score:
#                 oppo_add_score = oppo_temp_score
#         my_score_sum += my_add_score
#         oppo_score_sum += oppo_add_score
#
#     for h in range(board.height - board.n_in_row + 1):
#         my_add_score = 0
#         oppo_add_score = 0
#         for w in range(board.width - board.n_in_row + 1):
#             my_temp_score = my_table.get(get_form(h, w, (1, 1), board, player), 0)
#             oppo_temp_score = oppo_table.get(get_form(h, w, (1, 1), board, oppo_player), 0)
#             if my_temp_score > my_add_score:
#                 my_add_score = my_temp_score
#             if oppo_temp_score > oppo_add_score:
#                 oppo_add_score = oppo_temp_score
#         my_score_sum += my_add_score
#         oppo_score_sum += oppo_add_score
#
#     for h in range(board.height - 1, board.n_in_row - 2, -1):
#         my_add_score = 0
#         oppo_add_score = 0
#         for w in range(board.width - board.n_in_row + 1):
#             my_temp_score = my_table.get(get_form(h, w, (-1, 1), board, player), 0)
#             oppo_temp_score = oppo_table.get(get_form(h, w, (-1, 1), board, oppo_player), 0)
#             if my_temp_score > my_add_score:
#                 my_add_score = my_temp_score
#             if oppo_temp_score > oppo_add_score:
#                 oppo_add_score = oppo_temp_score
#         my_score_sum += my_add_score
#         oppo_score_sum += oppo_add_score
#     return my_score_sum - oppo_score_sum
#
#
# def get_form(h, w, direction, board, player):
#     square = board.square
#     best_connect_num = chess_num = block_num = 0  # 保存最长连的棋子数、我方棋子的总数
#     flag_oppo = False  # 保存是否有对手棋子的特征
#     connect_num = 0
#     origin = (h - direction[0], w - direction[1])
#     for i in range(board.n_in_row):
#         # 构建一个6格的滑动窗口
#         # print(direction)
#         if square[h + (i * direction[0]), w + (i * direction[1])] == player:
#             connect_num += 1
#             chess_num += 1  # 保存我方棋子的总数
#         else:
#             if connect_num > best_connect_num:
#                 block_num = 0
#                 best_connect_num = connect_num
#                 if (origin[0] < 0) or (origin[1] < 0) or (square[origin] != 0):
#                     block_num += 1
#                 if square[h + (i * direction[0]), w + (i * direction[1])] != 0:
#                     block_num += 1
#             if (not flag_oppo) and square[h + (i * direction[0]), w + (i * direction[1])] != 0:
#                 flag_oppo = True
#             origin = (h + (i * direction[0]), w + (i * direction[1]))
#             connect_num = 0
#
#     if (best_connect_num < chess_num) and (not flag_oppo):
#         # 因为棋形是断开的，且没有对手的棋子，所以必定是眠形
#         return f'm{chess_num}'
#     else:
#         if block_num == 0:
#             return f'h{best_connect_num}'
#         if block_num == 1:
#             return f'm{best_connect_num}'
#         else:
#             return "default"

def evaluate_roku(node, player):
    board: Board = node.board
    board.do_move(node.action)
    end, winner = board.game_end()
    oppo_player = 3 - player  # 3-2=1 3-1=2

    if end:
        del board
        if winner == -1:
            return 0
        elif winner == player:
            return MAX_SCORE
        else:
            return -MAX_SCORE

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

    for w in range(board.width - board.n_in_row + 1):
        my_score_sum = add_score(0, w, (1, 1), board, player, my_score_sum, my_table)
        oppo_score_sum = add_score(0, w, (1, 1), board, oppo_player, oppo_score_sum, oppo_table)

    for h in range(board.height - 1, board.n_in_row - 2, -1):
        my_score_sum = add_score(h, 0, (-1, 1), board, player, my_score_sum, my_table)
        oppo_score_sum = add_score(h, 0, (-1, 1), board, oppo_player, oppo_score_sum, oppo_table)

    for w in range(board.width - board.n_in_row + 1):
        my_score_sum = add_score(board.height - 1, w, (-1, 1), board, player, my_score_sum, my_table)
        oppo_score_sum = add_score(board.height - 1, w, (-1, 1), board, oppo_player, oppo_score_sum, oppo_table)

    return my_score_sum - oppo_score_sum


def add_score(h, w, direction, board, player, score, table):
    square = board.square
    oppo_player = 3 - player
    connect_num = 0  # 连珠的棋子数
    # origin = (h - direction[0], w - direction[1])  # 区间的起点，从盘边缘开始
    origin = -1
    flag_blocked = False
    if direction == (0, 1):  # 搜索到棋盘边缘
        length = board.width
    elif direction == (1, 0):
        length = board.height
    elif direction == (1, 1):
        length = min(board.height - h, board.width - w)
    else:
        length = min(h + 1, board.width - w)
    print_flag = True
    for i in range(length):
        if i <= origin:
            continue
        if square[h + (i * direction[0]), w + (i * direction[1])] == player:
            connect_num += 1
        else:
            # 遇到空位或者对手棋子，开始判定棋形
            potential_num = connect_num
            for j in range(board.n_in_row - connect_num):
                try:
                    loc_j = square[h + (origin - j) * direction[0], w + (origin - j) * direction[1]]  # 处理超出棋盘的情况
                except IndexError:
                    loc_j = oppo_player
                if connect_num == 4 and print_flag and player == 1:
                    print(square)
                    print_flag = False
                if loc_j != oppo_player:
                    potential_num += 1
                else:
                    flag_blocked = True
                    break
            old_origin = origin
            origin = i  # 推进区间
            for j in range(board.n_in_row - connect_num):
                try:
                    loc_j = square[h + (i + j) * direction[0], w + (i + j) * direction[1]]  # 处理超出棋盘的情况
                except IndexError:
                    loc_j = oppo_player
                if loc_j != oppo_player:
                    potential_num += 1
                else:
                    origin = i + j  # 推进区间
                    flag_blocked = True
                    break

            if connect_num == 4:
                print(potential_num, (old_origin, origin), (h + (i * direction[0]), w + (i * direction[1])), player)
            if potential_num >= 6:
                # 小于6的都是死棋
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


class Node:

    def __init__(self, board, action, depth):
        self.board: Board = board  # 设置棋盘属性
        self.action = action  # 节点的动作是节点与父节点连线上的动作
        self.depth = depth


class MinMaxTree:

    def __init__(self, evaluate_fn, player, depth=3):
        self.depth = depth  # 设置深度属性
        self.evaluate_fn = evaluate_fn
        self.player = player

    def evaluate(self, node, a=-MAX_SCORE, b=MAX_SCORE):
        board = node.board
        current_player = board.get_current_player()  # 正准备下棋的玩家

        # 处理叶子节点的情况
        if node.depth == self.depth:
            score = self.evaluate_fn(node, self.player)
            del board
            return score, node.action

        board.do_move(node.action)
        next_player = board.get_current_player()  # 换手后的玩家

        # 对结束棋局的走法剪枝
        end, winner = board.game_end()
        if end:
            del board
            if winner == -1:
                return 0, node.action
            elif winner == self.player:
                return MAX_SCORE, node.action
            else:
                return -MAX_SCORE, node.action

        best_action = None
        # is_prune = (next_player != current_player)
        #
        # # 搜索子节点
        # if current_player == self.player:
        #     best_score = -MAX_SCORE
        #     for action in board.neighbor:
        #         child = Node(copy.deepcopy(board), action, node.depth + 1)
        #         score, _ = self.evaluate(child, a, b)
        #         if score >= best_score:
        #             best_score = score
        #             best_action = action
        #         # if is_prune and (best_score < a):
        #         #     # 如果分数没有超过下界，说明该节点不会比之前的节点好，注意棋手每回合下两手，第二手才剪枝
        #         #     return best_score, -1
        #         a = best_score
        #
        # else:
        #     best_score = MAX_SCORE
        #     for action in board.neighbor:
        #         child = Node(copy.deepcopy(board), action, node.depth + 1)
        #         score, _ = self.evaluate(child, a, b)
        #         if score <= best_score:
        #             best_score = score
        #             best_action = action
        #         if is_prune and (best_score > b):
        #             return best_score, -1
        #         b = best_score

        best_score = -MAX_SCORE
        for action in board.neighbor:
            child = Node(copy.deepcopy(board), action, node.depth + 1)
            score, _ = self.evaluate(child, a, b)
            if score >= best_score:
                best_score = score
                best_action = action
            a = best_score
        del board
        return best_score, best_action

    def get_move(self, board):
        best_action = None
        best_next_action = None
        best_score = -MAX_SCORE
        scores = []
        for action in board.neighbor:
            node = Node(copy.deepcopy(board), action, 2)
            score, next_action = self.evaluate(node)
            scores.append((board.move_to_location(action), score))
            if score >= best_score:
                best_score = score
                best_action = action
                best_next_action = next_action
        print(scores)
        return best_action, best_next_action


class MinMaxPlayer:
    """AI player based on game tree"""

    def __init__(self, depth=3):
        self.player = None
        self.mmt = None
        self.depth = depth

    def set_player_ind(self, p):
        self.player = p
        self.mmt = MinMaxTree(evaluate_roku, self.player, self.depth)

    def get_action(self, board):
        if len(board.availables) > 0:
            move = self.mmt.get_move(board)  # 根据博弈树获取最佳行动
            return move
        else:
            print("WARNING: the board is full")

    def __str__(self):
        return "Game Tree {}".format(self.player)


class MMTEngine:
    """
    AI player based on MMT for SAU
    """

    def __init__(self, depth=3, name="MMTEngine"):
        self.player = None
        self.name = name
        self.mmt = None
        self.depth = depth
        self.first_turn = False  # 首回合落子在天元
        self.chess = 2
        self.next_action = None

    def set_player_ind(self, p):
        self.player = p
        self.mmt = MinMaxTree(evaluate_roku, self.player, self.depth)
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
            action, self.next_action = self.mmt.get_move(board)  # 根据博弈树获取最佳行动
            self.chess = 1
            return action
        else:
            print("WARNING: the board is full")

    def __str__(self):
        return "Engine RL MCTS {}".format(self.player)
