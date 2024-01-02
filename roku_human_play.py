# -*- coding: utf-8 -*-

from roku_game import Board, Game
# from roku_mcts import MCTSPlayer
# from roku_RL import RLEngine as MCTSPlayer
# from roku_MMT import MinMaxPlayer, MMTEngine
from roku_MT import MTEngine

# import pickle
# from mcts_alphaZero import MCTSPlayer
# from policy_value_net_numpy import PolicyValueNetNumpy
# from policy_value_net_pytorch import PolicyValueNet  # Pytorch

# from policy_value_net import PolicyValueNet  # Theano and Lasagne
# from policy_value_net_tensorflow import PolicyValueNet # Tensorflow
# from policy_value_net_keras import PolicyValueNet  # Keras


class Human:
    """
    human player
    """

    def __init__(self):
        self.player = None

    def set_player_ind(self, p):
        self.player = p

    def get_action(self, board):
        try:
            location = input("Your move: ")
            if isinstance(location, str):  # for python3
                location = [int(n, 10) for n in location.split(",")]
            move = board.location_to_move(location)
        except Exception as e:
            move = -1
        if move == -1 or move not in board.availables:
            print("invalid move")
            move = self.get_action(board)
        return move

    def __str__(self):
        return "Human {}".format(self.player)


def run():
    n = 6
    width, height = 19, 19
    model_file = './engine.model'  # './engine.npy'
    try:
        board = Board(width=width, height=height, n_in_row=n)
        game = Game(board)

        # ############### human VS AI ###################
        # load the trained policy_value_net in either Theano/Lasagne, PyTorch or TensorFlow
        # best_policy = PolicyValueNet(width, height, model_file=model_file)
        # mcts_player = MCTSPlayer(best_policy.policy_value_fn, c_puct=5, n_playout=100)

        # load the provided model (trained in Theano/Lasagne) into a MCTS player written in pure numpy
        # best_policy = PolicyValueNetNumpy(width, height, model_file)
        # mcts_player = MCTSPlayer(best_policy.policy_value_fn, c_puct=5, n_playout=30)

        # uncomment the following line to play with pure MCTS (it's much weaker even with a larger n_playout)
        # mcts_player = MCTSPlayer(c_puct=5, n_playout=30)

        # min-max tree player
        ai_player = MTEngine()

        # human player, input your move in the format: 2,3
        human = Human()

        # set start_player=0 for human first
        game.start_play(human, ai_player, start_player=0, is_shown=1)
    except KeyboardInterrupt:
        print('\n\rquit')


if __name__ == '__main__':
    run()
