from gate_synthesis import *
from operators import *
import numpy as np
from visu import *

np.random.seed(1954)


import numpy as np
I = np.array([[1,0],[0,1]])
II = np.tensordot(I, I, axes=0)
P0 = np.array([[1,0],[0,0]]) #what???
P1 = np.array([[0,0],[0,1]])
toffoli = np.tensordot(P0, II, axes=0) + np.tensordot(P1, CNOT, axes=0)

q1_gates = [X, Y, Z, S, H, T, Tdag]
q2_gates = [CNOT]
init = np.tensordot(I, II, axes=0)

game = GateSynthesis(TOFFOLI, init, 500, q1_gates, q2_gates)

print("##### DETERMINISTIC DRIVER DEMO FOR TOFFOLI GATE #####")
print(f"Initial distance to target = {game.dist_to_target(game.curr_unitary)}")
print("- - - - - - - - - ")


print("Do step #0 : apply CNOT to q0,q1")
a = (CNOT, (0, 1))
r = game.step(a)
print(f"Distance to target = {game.dist_to_target(game.curr_unitary)}, \t rwd {r}")
print("- - - - - - - - - ")


print("Do step #1a : apply T to q0")
a = (T, 0)
r = game.step(a)
print(f"Distance to target = {game.dist_to_target(game.curr_unitary)}, \t rwd {r}")
print("- - - - - - - - - ")

print("Do step #1b : apply Tdag to q1")
a = (Tdag, 1)
r = game.step(a)
print(f"Distance to target = {game.dist_to_target(game.curr_unitary)}, \t rwd {r}")
print("- - - - - - - - - ")

print("Do step #2a : apply CNOT to q0, q1")
a = (CNOT, (0, 1))
r = game.step(a)
print(f"Distance to target = {game.dist_to_target(game.curr_unitary)}, \t rwd {r}")
print("- - - - - - - - - ")

print("Do step #2b : apply H to q2")
a = (H, 2)
r = game.step(a)
print(f"Distance to target = {game.dist_to_target(game.curr_unitary)}, \t rwd {r}")
print("- - - - - - - - - ")

print("Do step #3a : apply T to q1")
a = (T, 1)
r = game.step(a)
print(f"Distance to target = {game.dist_to_target(game.curr_unitary)}, \t rwd {r}")
print("- - - - - - - - - ")

print("Do step #3b : apply T to q2")
a = (T, 2)
r = game.step(a)
print(f"Distance to target = {game.dist_to_target(game.curr_unitary)}, \t rwd {r}")
print("- - - - - - - - - ")

print("Do step #4 : apply CNOT to q0, q2")
a = (CNOT, (0,2))
r = game.step(a)
print(f"Distance to target = {game.dist_to_target(game.curr_unitary)}, \t rwd {r}")
print("- - - - - - - - - ")

print("Do step #5 : apply Tdag to q2")
a = (Tdag, 2)
r = game.step(a)
print(f"Distance to target = {game.dist_to_target(game.curr_unitary)}, \t rwd {r}")
print("- - - - - - - - - ")

print("Do step #6 : apply CNOT to q1, q2")
a = (CNOT, (1,2))
r = game.step(a)
print(f"Distance to target = {game.dist_to_target(game.curr_unitary)}, \t rwd {r}")
print("- - - - - - - - - ")

print("Do step #7 : apply T to q2")
a = (T, 2)
r = game.step(a)
print(f"Distance to target = {game.dist_to_target(game.curr_unitary)}, \t rwd {r}")
print("- - - - - - - - - ")

print("Do step #8 : apply CNOT to q0, q2")
a = (CNOT, (0,2))
r = game.step(a)
print(f"Distance to target = {game.dist_to_target(game.curr_unitary)}, \t rwd {r}")
print("- - - - - - - - - ")

print("Do step #9 : apply Tdag to q2")
a = (Tdag, 2)
r = game.step(a)
print(f"Distance to target = {game.dist_to_target(game.curr_unitary)}, \t rwd {r}")
print("- - - - - - - - - ")

print("Do step #10 : apply CNOT to q1, q2")
a = (CNOT, (1,2))
r = game.step(a)
print(f"Distance to target = {game.dist_to_target(game.curr_unitary)}, \t rwd {r}")
print("- - - - - - - - - ")

print("Do step #2b : apply H to q2")
a = (H, 2)
r = game.step(a)
print(f"Distance to target = {game.dist_to_target(game.curr_unitary)}, \t rwd {r}")
print("- - - - - - - - - ")


print(f"End result current == target? {np.allclose(game.curr_unitary, game.target_unitary)}")
