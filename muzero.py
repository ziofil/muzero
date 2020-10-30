import numpy as np
np.set_printoptions(suppress=False, linewidth=280)
import tensorflow.keras as k
import tensorflow as tf
from games import TicTacToe
from mcts import Tree

class MuzeroCell(k.layers.Layer):
    def __init__(self, state_size, policy_size, **kwargs):
        super().__init__(**kwargs)
        self.state_size = state_size
        self.policy_size = policy_size
        self.output_size = [(policy_size, 1, 1), state_size] # policy, action, value, state (no reward for zero-sum games)
        
    def build(self, input_shapes):
        # not using input_shapes because we only pass the state

        self.policy = k.Sequential([tf.keras.Input(shape=(self.state_size,)),
        k.layers.Dense(32, activation="relu", kernel_regularizer=k.regularizers.l1(l2=1e-4), bias_regularizer=k.regularizers.l1(1e-4), activity_regularizer=k.regularizers.l1(1e-5)),
        k.layers.Dense(16, activation="relu", kernel_regularizer=k.regularizers.l1(l2=1e-4), bias_regularizer=k.regularizers.l1(1e-4), activity_regularizer=k.regularizers.l1(1e-5)),
        k.layers.Dense(input_shapes[0][1], activation="softmax", kernel_regularizer=k.regularizers.l1(l2=1e-4), bias_regularizer=k.regularizers.l1(1e-4))])

        self.value = k.Sequential([tf.keras.Input(shape=(self.state_size,)),
        k.layers.Dense(32, activation="relu", kernel_regularizer=k.regularizers.l1(l2=1e-4), bias_regularizer=k.regularizers.l1(1e-4), activity_regularizer=k.regularizers.l1(1e-5)),
        k.layers.Dense(16, activation="relu", kernel_regularizer=k.regularizers.l1(l2=1e-4), bias_regularizer=k.regularizers.l1(1e-4), activity_regularizer=k.regularizers.l1(1e-5)),
        k.layers.Dense(1, kernel_regularizer=k.regularizers.l1(l2=1e-4), bias_regularizer=k.regularizers.l1(1e-4))])

        self.next_state = k.Sequential([k.layers.Concatenate(axis=1),
        k.layers.Dense(128, activation="relu", kernel_regularizer=k.regularizers.l1(l2=1e-4), bias_regularizer=k.regularizers.l1(1e-4), activity_regularizer=k.regularizers.l1(1e-5)),
        k.layers.Dense(64, activation="relu", kernel_regularizer=k.regularizers.l1(l2=1e-4), bias_regularizer=k.regularizers.l1(1e-4), activity_regularizer=k.regularizers.l1(1e-5)),
        k.layers.Dense(self.state_size, kernel_regularizer=k.regularizers.l1(l2=1e-4), bias_regularizer=k.regularizers.l1(1e-4))])

    def call(self, inputs, states):
        state = states[0]
        policy = self.policy(state)
        value = self.value(state)
        action = self._sample(inputs, policy) # using inputs to mask illegal moves
        next_state = self.next_state([state, action])
        output = (policy, value, action)
        return output, next_state

    @staticmethod
    def _sample(mask, policy):
        policy = policy * mask
            if np.allclose(policy, 0): # if no legal moves are available
                policy = mask
        return np.random.choice(len(policy), p = policy/np.sum(policy))


class MuzeroRNN(k.layers.RNN):
    def __init__(self, state_size, policy_size, K, **kwargs):
        self.K = K
        super().__init__(self.cell, return_sequences=True)

    def call(self, inputs, initial_state):
        output, state = self.cell(inputs, initial_state)
        for k in range(self.K-1):
            output = self.cell(inputs, initial_state)
            


class Muzero:

    representation = k.Sequential([
        k.layers.Dense(128, activation="relu", kernel_regularizer=k.regularizers.l1(l2=1e-4), bias_regularizer=k.regularizers.l1(1e-4), activity_regularizer=k.regularizers.l1(1e-5)),
        k.layers.Dense(64, activation="relu", kernel_regularizer=k.regularizers.l1(l2=1e-4), bias_regularizer=k.regularizers.l1(1e-4), activity_regularizer=k.regularizers.l1(1e-5)),
        k.layers.Dense(32, kernel_regularizer=k.regularizers.l1(l2=1e-4), bias_regularizer=k.regularizers.l1(1e-4))]) 
        
    # reward = k.Sequential([
    #     k.layers.Dense(32, activation="relu", kernel_regularizer=k.regularizers.l1(l2=1e-4), bias_regularizer=k.regularizers.l1(1e-4), activity_regularizer=k.regularizers.l1(1e-5)), 
    #     k.layers.Dense(16, activation="relu", kernel_regularizer=k.regularizers.l1(l2=1e-4), bias_regularizer=k.regularizers.l1(1e-4), activity_regularizer=k.regularizers.l1(1e-5)),
    #     k.layers.Dense(1, kernel_regularizer=k.regularizers.l1(l2=1e-4), bias_regularizer=k.regularizers.l1(1e-4))])

    

    def __init__(self, Game):
        self.REPLAY_BUFFER = []
        self.game = Game
        self.MCTS_tree = Tree()

    def h(self, observations: list):
        return tf.reduce_sum(self.representation(tf.convert_to_tensor(observations, dtype=tf.float32)), axis=0, keepdims=True)

    def f(self, state):
        return self.policy(state), self.value(state)

    def g(self, state, action: int):
        z = np.zeros((1,9), dtype=np.float32)
        z[0, action] = 1
        return (self.reward(k.layers.Concatenate(axis=1)([state, z])), 
               self.new_state(k.layers.Concatenate(axis=1)([state, z])))

    # A
    def MCTS_policy(self, observations:list, num_simulations: int):
        self.MCTS_tree.reset()
        self.MCTS_tree.set_obs_model(observations, (self.f, self.g, self.h))
        pi, nu = self.MCTS_tree.policy_value(num_simulations)
        return pi, nu

    # B
    def self_play(self):
        game = self.game()
        observations = game.observations
        policies_pi = []
        actions = []
        illegal = 0
        while not game.end:
            pi, nu = self.MCTS_policy(game.observations, num_simulations=50)
            pi_legal = pi*game.legal_moves_mask
            if np.allclose(pi_legal, 0):
                illegal += 1
                continue
            a = np.random.choice(len(pi), p = pi_legal/sum(pi_legal))
            z = game.play(a) # at the end of the game, z contains the final value (+1 win, -1 loss, 0 graw)
            actions.append(a)
            policies_pi.append(pi)
            observations.extend(game.observations)
        if illegal > 0:
            print(f'skipped {illegal} illegal moves')
        return observations, actions, policies_pi, z

    # Model rollout (C)
    def model_pv(self, observations:list, actions:list):
        s = self.h(observations[0][None,:]) #NOTE: should it be observations[0] ?
        policies_p = []
        values_v = []
        for k in range(min(5, len(actions))): # TODO: for a in actions
            p, v = self.f(s)
            policies_p.append(p[0])
            values_v.append(v[0,0])
            r, s = self.g(s, actions[k])
        return policies_p, values_v


    def loss(self):
        observations, actions, policies_pi, z = self.self_play()
        self.REPLAY_BUFFER.append((observations, actions, policies_pi, z))
        policies_p, values_v = self.model_pv(observations, actions)

        loss_v = 0
        loss_p = 0
        for k in range(min(5, len(policies_p))): # TODO: for k in len(policies_p)
            loss_p += tf.reduce_sum(policies_pi*tf.math.log(1e-7+policies_p[k])) # learning P
            loss_v += (z - values_v[k])**2 # learning V

        return loss_p + loss_v 

    @property
    def trainable_variables(self):
        return  (self.policy.trainable_variables + 
                self.value.trainable_variables + 
                self.representation.trainable_variables + 
                self.new_state.trainable_variables) # not reward for games


