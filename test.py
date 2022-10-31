import numpy as np
import agent_minmax_v2
import agent_minmax_v3
import agent_greedy
import agent_minmax_v3_numba
import agent_minmax_v4
import agent_minmax_v4_simplified
import agent_minmax_v5
from play import Playground, COLOR_BLACK, COLOR_WHITE, TIMEOUT



def twoRounds(agent0, agent1, verbose=0):
	Playground(agent0.AI(8, COLOR_BLACK, TIMEOUT), agent1.AI(8, COLOR_WHITE, TIMEOUT), verbose=verbose).play()
	Playground(agent1.AI(8, COLOR_BLACK, TIMEOUT), agent0.AI(8, COLOR_WHITE, TIMEOUT), verbose=verbose).play()

# twoRounds(agent_minmax_v3, agent_greedy, verbose=1)
# twoRounds(agent_minmax_v3, agent_minmax_v2, verbose=1)
# twoRounds(agent_minmax_v3_numba, agent_minmax_v4, verbose=1)
twoRounds(agent_minmax_v5, agent_minmax_v4_simplified, verbose=1)


