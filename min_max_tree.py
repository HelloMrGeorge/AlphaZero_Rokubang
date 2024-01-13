import copy
import numpy as np
from game import Board

# 我方评分，注意是假设在空位下完棋子后的棋形
SCORES_1 = {'h6': 80, 'h5': 80, 'm5': 40, 'h4': 40, 'm4': 20, 'h3': 20, 'm3': 5, 'h2': 1, 'm2': 0}
# 对方评分
SCORES_2 = {'h6': 10000, 'h5': 10000, 'm5': 10000, 'h4': 100, 'm4': 50, 'h3': 25, 'm3': 5, 'h2': 1, 'm2': 1}

DIRECTIONS = [(0, 1), (1, 0), (1, 1), (-1, 1)]


def index_flag(h, w, player, square):
    try:
        flag = (square[h, w] == player)
    except IndexError:
        flag = False
    return flag


def cal_form(h, w, direction, board: Board, player):
    square = board.square
    oppo_player = 3 - player
    connect_num = 1  # 假设在(h, w)的空位下了一枚我方的棋子
    left = right = 0  # 记录连珠边缘(h, w)相对的偏移量, right代表方向的正向

    for i in range(1, 6):
        if index_flag(h + (i * direction[0]), w + (i * direction[1]), player, square):
            connect_num += 1
        else:
            right = i
            break
    for i in range(1, 6):
        if index_flag(h - (i * direction[0]), w - (i * direction[1]), player, square):
            connect_num += 1
        else:
            left = i
            break

    extend_num = 6 - connect_num
    potential_num = connect_num
    block_flag = False

    for i in range(extend_num):
        if index_flag(h + (right + i) * direction[0], w + (right + i) * direction[1], oppo_player, square):
            block_flag = True
            break
        else:  # 不必担心延伸出去的格点是否是空位还是我方棋子，因为如果有我方棋子，则中途的空位的记分会增加
            potential_num += 1
    for i in range(extend_num):
        if index_flag(h - (left + i) * direction[0], w - (left + i) * direction[1], oppo_player, square):
            block_flag = True
            break
        else:
            potential_num += 1

    if potential_num < 6:
        return "default"  # 不可能6连珠的是死棋
    elif block_flag:
        return f"m{connect_num}"  # 在空位下棋后，会形成眠x
    else:
        return f"h{connect_num}"  # 在空位下棋后，会形成活x



def score_fn(board: Board, player):
    # 自己的赢面 = 自己对对手的威胁 - 对手对自己的威胁
    my_score = 0
    oppo_score = 0
    oppo_player = 3 - player
    for point in board.neighbor:
        max_add = 0
        for direction in DIRECTIONS:
            # 一个空位只取最好的棋形，因为无论多少棋形，对手只要一步就能破坏他们
            h, w = board.move_to_location(point)
            form = cal_form(h, w, direction, board, player)
            add_score = SCORES_1.get(form, 0)
            if add_score > max_add:
                max_add = add_score
        my_score += max_add

    for point in board.neighbor:
        max_add = 0
        for direction in DIRECTIONS:
            h, w = board.move_to_location(point)
            form = cal_form(h, w, direction, board, oppo_player)
            add_score = SCORES_2.get(form, 0)
            if add_score > max_add:
                max_add = add_score
        oppo_score += max_add

    return my_score - oppo_score


class MinNode:
    def __init__(self, board, action, layer, player):
        self.board: Board = board  # 设置棋盘属性
        self.action: list = action  # 节点的动作，包含两手棋，它是节点与父节点连线上的动作
        self.layer = layer  # 节点的层数，叶子节点的层数是0
        self.player = player  # 根节点的玩家

    def evaluate(self, cal_score, alpha=-np.inf):
        board = self.board
        if self.layer == 0:
            return *self.action, cal_score(board, self.player)
        else:
            min_score = np.inf
            min_action = None
            for first_action in board.neighbor:
                first_board = copy.deepcopy(board)
                first_board.do_move(first_action)

                # 对结束比赛的走法进行剪枝
                end, winner = first_board.game_end()
                if end:
                    if winner == -1:
                        return 0
                    else:
                        return -np.inf  # 对手行棋后，要么平局，要么对手赢

                for second_action in first_board.neighbor:
                    second_board = copy.deepcopy(first_board)
                    second_board.do_move(second_action)

                    end, winner = second_board.game_end()
                    if end:
                        if winner == -1:
                            return 0
                        else:
                            return -np.inf

                    action = [first_action, second_action]
                    node = MaxNode(second_board, action, self.layer - 1, self.player)
                    *_, score = node.evaluate(cal_score, beta=min_score)
                    if score <= alpha:
                        return alpha  # alpha剪枝，上层的极大值节点不需要比alpha小的下层极小值点
                    if min_score > score:
                        min_score = score
                        min_action = action

            return *min_action, min_score


class MaxNode:
    def __init__(self, board, action, layer, player):
        self.board: Board = board  # 设置棋盘属性
        self.action: list = action  # 节点的动作，包含两手棋，它是节点与父节点连线上的动作
        self.layer = layer  # 节点的层数，叶子节点的层数是0
        self.player = player

    def evaluate(self, cal_score, beta=np.inf):
        board = self.board
        if self.layer == 0:
            return *self.action, cal_score(board, self.player)
        else:
            max_score = -np.inf
            max_action = None
            for first_action in board.neighbor:
                first_board = copy.deepcopy(board)
                first_board.do_move(first_action)

                # 对结束比赛的走法进行剪枝
                end, winner = first_board.game_end()
                if end:
                    if winner == -1:
                        return 0
                    else:
                        return np.inf  # 自己行棋后，要么平局，要么自己赢

                for second_action in first_board.neighbor:
                    second_board = copy.deepcopy(first_board)
                    second_board.do_move(second_action)

                    end, winner = second_board.game_end()
                    if end:
                        if winner == -1:
                            return 0
                        else:
                            return np.inf

                    action = [first_action, second_action]
                    node = MinNode(second_board, action, self.layer - 1, self.player)
                    *_, score = node.evaluate(cal_score, alpha=max_score)
                    if score >= beta:
                        return beta  # beta剪枝，极小值节点不需要比beta大的下层极大值点
                    if max_score < score:
                        max_score = score
                        max_action = action

            return *max_action, max_score
