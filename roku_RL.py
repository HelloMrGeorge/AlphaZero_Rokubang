# -*- coding: utf-8 -*-

import numpy as np
import copy


def softmax(x):
    probs = np.exp(x - np.max(x))
    probs /= np.sum(probs)
    return probs


class TreeNode:
    """A node in the MCTS tree.

    Each node keeps track of its own value Q, prior probability P, and
    its visit-count-adjusted prior score u.
    """

    def __init__(self, parent, prior_p):

        self.children = {}  # a map from action to TreeNode
        self.n_visits = 0

        self._parent = parent
        self._Q = 0
        self._u = 0
        self._P = prior_p

    def expand(self, action_priors):
        """Expand tree by creating new children.
        action_priors: a list of tuples of actions and their prior
            probability according to the policy function.
        """
        for action, prob in action_priors:
            if action not in self.children:
                self.children[action] = TreeNode(self, prob)

    def select(self, c_puct):
        """
        Select action among children that gives maximum action value Q
        plus bonus u(P).

        Return: A tuple of (action, next_node)
        """
        return max(self.children.items(),
                   key=lambda act_node: act_node[1].get_value(c_puct))

    def update(self, leaf_value):
        """Update node values from leaf evaluation.

        leaf_value: the value of subtree evaluation from the current player's perspective.
        """
        # Count visit.
        self.n_visits += 1
        # Update Q, a running average of values for all visits.
        self._Q += (leaf_value - self._Q) / self.n_visits

    def update_recursive(self, leaf_value, flag):
        """
        Like a call to update(), but applied recursively for all ancestors.
        flag=1: 表示当前棋子是对应选手下的第2个棋子，其父节点是选手下的第一个棋子
        leaf_value: 是从父节点的视角看，选哪个子节点比较好
        """
        # If it is not root, this node's parent should be updated first.
        if self._parent:
            if flag:
                self._parent.update_recursive(-leaf_value, 1 - flag)
            else:
                self._parent.update_recursive(leaf_value, 1 - flag)
        self.update(leaf_value)

    def get_value(self, c_puct):
        """
        Calculate and return the value for this node.
        It is a combination of leaf evaluations Q, and this node's prior
        adjusted for its visit count, u.

        c_puct: a number in (0, inf) controlling the relative impact of
            value Q, and prior probability P, on this node's score.
        """
        self._u = (c_puct * self._P *
                   np.sqrt(self._parent.n_visits) / (1 + self.n_visits))
        return self._Q + self._u

    def is_leaf(self):
        """Check if leaf node (i.e. no nodes below this have been expanded)."""
        return self.children == {}

    def is_root(self):
        return self._parent is None


class MCTS:
    """An implementation of Monte Carlo Tree Search."""

    def __init__(self, policy_value_fn, c_puct=5, n_playout=10000):
        """
        policy_value_fn:
            a function that takes in a board state and outputs
            a list of (action, probability) tuples and also a score in [-1, 1]
            (i.e. the expected value of the end game score from the current
            player's perspective) for the current player.
        c_puct:
            a number in (0, inf) that controls how quickly exploration
            converges to the maximum-value policy. A higher value means
            relying on the prior more.
        """
        self._root = TreeNode(None, 1.0)
        self._policy = policy_value_fn
        self._c_puct = c_puct
        self._n_playout = n_playout

    def _playout(self, state):
        """
        Run a single playout from the root to the leaf, getting a value at
        the leaf and propagating it back through its parents.
        State is modified in-place, so a copy must be provided.
        """
        node = self._root
        # current_player = state.get_current_player() # 发出当前动作的选手
        while True:
            if node.is_leaf():
                break
            # Greedily select next move.
            action, node = node.select(self._c_puct)
            state.do_move(action)

        # Evaluate the leaf using a network which outputs a list of
        # (action, probability) tuples p and also a score v in [-1, 1]
        # for the current player.
        action_probs, leaf_value = self._policy(state)
        # Check for end of game.
        end, winner = state.game_end()
        if not end:
            node.expand(action_probs)
        else:
            # for end state，return the "true" leaf_value
            if winner == -1:  # tie
                leaf_value = 0.0
            else:
                # 当先手下完棋后，先改变了current_player，再判断赢家，如果先手赢了，那么得到的leaf_value是-1
                # 因为state.chesses == 2，所以更新的是-leaf_value，仍然是+1
                leaf_value = (
                    1.0 if winner == state.get_current_player() else -1.0
                )

        if state.chesses == 2:
            node.update_recursive(-leaf_value, 0)
        else:
            node.update_recursive(leaf_value, 1)

    def get_move_probs(self, state, temp=1e-3):
        """
        Run all playouts sequentially and return the available actions and
        their corresponding probabilities.

        state: the current game state
        temp: temperature parameter in (0, 1] controls the level of exploration
        """
        for n in range(self._n_playout):
            state_copy = copy.deepcopy(state)
            self._playout(state_copy)

        # calc the move probabilities based on visit counts at the root node
        act_visits = [(act, node.n_visits)
                      for act, node in self._root.children.items()]
        acts, visits = zip(*act_visits)
        act_probs = softmax(1.0 / temp * np.log(np.array(visits) + 1e-10))

        return acts, act_probs

    def update_with_move(self, last_move):
        """Step forward in the tree, keeping everything we already know
        about the subtree.
        """
        if last_move in self._root.children:
            self._root = self._root.children[last_move]
            self._root._parent = None
        else:
            self._root = TreeNode(None, 1.0)

    def __str__(self):
        return "MCTS"


class MCTSPlayer(object):
    """AI player based on MCTS"""

    def __init__(self, policy_value_function, c_puct=5, n_playout=2000, is_selfplay=0):
        self.player = None
        self.mcts = MCTS(policy_value_function, c_puct, n_playout)
        self._is_selfplay = is_selfplay

    def set_player_ind(self, p):
        self.player = p

    def reset_player(self):
        self.mcts.update_with_move(-1)

    def get_action(self, board, temp=1e-3, return_prob=0):
        sensible_moves = board.availables
        # the pi vector returned by MCTS as in the alphaGo Zero paper
        move_probs = np.zeros(board.width * board.height)
        if len(sensible_moves) > 0:
            acts, probs = self.mcts.get_move_probs(board, temp)
            move_probs[list(acts)] = probs
            if self._is_selfplay:
                # add Dirichlet Noise for exploration (needed for
                # self-play training)
                move = np.random.choice(
                    acts,
                    p=0.75 * probs + 0.25 * np.random.dirichlet(0.3 * np.ones(len(probs)))
                )
                # update the root node and reuse the search tree
                self.mcts.update_with_move(move)
            else:
                # with the default temp=1e-3, it is almost equivalent
                # to choosing the move with the highest prob
                move = np.random.choice(acts, p=probs)
                # reset the root node
                self.mcts.update_with_move(-1)

            if return_prob:
                return move, move_probs
            else:
                return move
        else:
            print("WARNING: the board is full")

    def __str__(self):
        return "Alpha Zero MCTS {}".format(self.player)


class RLEngine:
    """
    AI player based on MCTS for SAU
    """

    def __init__(self, policy_value_function, c_puct=5, n_playout=200, name="RLEngine"):
        self.player = None
        self.name = name
        self.mcts = MCTS(policy_value_function, c_puct, n_playout)
        self.first_turn = False  # 首回合落子在天元

    def set_player_ind(self, p):
        self.player = p
        if self.player == 1:
            self.first_turn = True

    def reset_player(self):
        self.mcts.update_with_move(-1)

    def get_action(self, board, temp=1e-3):
        if self.first_turn:
            self.first_turn = False
            return 180  # 9 + 19 * 9

        if len(board.availables) > 0:
            acts, probs = self.mcts.get_move_probs(board, temp)
            move = acts[np.argmax(probs)]  # 取概率最大的
            self.mcts.update_with_move(-1)
            return move
        else:
            print("WARNING: the board is full")

    def __str__(self):
        return "Engine RL MCTS {}".format(self.player)
