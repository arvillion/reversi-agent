from time import time
import numpy as np
from timeout import timeout, TimeoutError

COLOR_BLACK = -1
COLOR_WHITE = 1
COLOR_NONE = 0
TIMEOUT = 5
CHESSBOARD_SIZE = 8

class Playground:
	def __init__(self, agent_black, agent_white, verbose=0):
		self.agent_black = agent_black
		self.agent_white = agent_white
		self.agent_black.name = getattr(agent_black, 'name', 'BLACK')
		self.agent_white.name = getattr(agent_white, 'name', 'WHITE')


		self.verbose = verbose

		self.directions = [
			[-1, -1], [0, -1], [1, -1],
			[-1, 0],           [1, 0],
			[-1, 1],  [0, 1],  [1, 1]
		]

		self.chessboard = np.zeros((8, 8), dtype=int)
		self.chessboard[[3, 4], [3, 4]] = COLOR_WHITE
		self.chessboard[[3, 4], [4, 3]] = COLOR_BLACK

	def isTerminal():
		return True

	def play(self):
		player_now = COLOR_BLACK
		round_doubled = 0

		pass_count = 0
		time_total = {}
		time_max = {}

		while(True):
			agent = self.agent_black if player_now == COLOR_BLACK else self.agent_white
			player_name = agent.name

			if player_name not in time_total:
				time_total[player_name] = 0
			
			if player_name not in time_max:
				time_max[player_name] = 0

			if (self.verbose >= 1 and round_doubled % 2 == 0):
				print(f'------------Round {round_doubled // 2}------------')
			round_doubled += 1

			try:
				time_start = time()
				self.goAgent(agent)
			except TimeoutError as e:
				print(f'[{player_name}] Time exceeded!')
			finally:
				time_spent = round(time() - time_start, 3)

				time_total[player_name] += time_spent
				time_max[player_name] = max(time_max[player_name], time_spent)

				if self.verbose >= 1:
					print(f'[{player_name}] Time usage: {time_spent} seconds')

			candidate_list = agent.candidate_list
			if not self.checkCandidateList(candidate_list, player_now):
				raise Exception(f"Failed to pass the candidate list check\n list={candidate_list}")
			
			if len(candidate_list) == 0:
				if self.verbose >= 2:
					print(f'[{player_name}] Pass the round')
				pass_count += 1

				if pass_count == 2:
					break

				player_now = -player_now
				continue

			pass_count = 0
			if (self.verbose >= 2):
				print(f'[{player_name}] Place the chess at {candidate_list[-1]}')
			self.go(candidate_list[-1], player_now)

			if self.verbose >= 2:
				self.printChessBoard()

			player_now = -player_now
		
		winner, count_black, count_white = self.getWinner()
		winner_name = 'Nobody' if winner is None else self.agent_black.name if winner == COLOR_BLACK else self.agent_white.name
		print('-------------------------------')
		print(f'[End] {winner_name} wins!')
		print(f'[End] total/{self.agent_black.name}(Black)/{self.agent_white.name}(White): {CHESSBOARD_SIZE*CHESSBOARD_SIZE}/{count_black}/{count_white}')
		
		ps = list(time_total.keys())
		for p in ps:
			print(f'[{p}] Avg: {round(time_total[p]/(round_doubled//2), 3)} Max: {time_max[p]}')

		return winner, count_black, count_white

	def isOutOfBoard(self, x, y):
		return x < 0 or x >= CHESSBOARD_SIZE or y < 0 or y >= CHESSBOARD_SIZE

	def getWinner(self):
		count_black = np.sum(self.chessboard == COLOR_BLACK)
		count_white = np.sum(self.chessboard == COLOR_WHITE)
		
		winner = None
		if count_black > count_white:
			winner = COLOR_WHITE
		elif count_black < count_white:
			winner = COLOR_BLACK

		return winner, count_black, count_white


	def checkCandidateList(self, candidate_list, player_now):
		movable_chess = set(self.getMovableChess(player_now))
		return movable_chess == set(candidate_list)

	def printChessBoard(self):
		print('  ' + ' '.join([str(_) for _ in range(CHESSBOARD_SIZE)]))
		for line, _ in enumerate(self.chessboard):
			print(line, end=' ')
			for __ in _:
				print(chr(0x25c9) if __ == COLOR_BLACK else (chr(0x25cb) if __ == COLOR_WHITE else '.') , end=' ')
			print()

	def go(self, pos, player_now):
		chess_to_reverse = []
		for d in self.directions:
			nx, ny = pos[0] + d[0], pos[1] + d[1]
			if self.isOutOfBoard(nx, ny):
				continue
			if self.chessboard[nx][ny] != -player_now:
				continue			
			chess_to_reverse += self.getReversions((nx, ny), d)
		
		self.chessboard[tuple(zip(*chess_to_reverse))] = player_now
		self.chessboard[pos] = player_now


	def getMovableChess(self, player_now):

		rival_chess_positions = np.where(self.chessboard == -player_now)
		rival_chess_positions = list(zip(rival_chess_positions[0], rival_chess_positions[1]))

		visited = {}
		movable_chess = []

		for pos in rival_chess_positions:
			for d in self.directions:
				nx = pos[0] + d[0]
				ny = pos[1] + d[1]
				if self.isOutOfBoard(nx, ny):
					continue

				if visited.get((nx, ny)) is not None: 
					continue

				if self.chessboard[nx][ny] != COLOR_NONE:
					continue

				if self.countReversions(pos, (-d[0], -d[1]), self.chessboard):
					movable_chess.append((nx, ny))
					visited[(nx, ny)] = True
		
		return movable_chess

	def countReversions(self, pos, direction, chessboard):
		x, y = pos
		cnt = 0

		rival_color = chessboard[x][y]
		color = -rival_color
		ok = False

		while not self.isOutOfBoard(x, y):
			if chessboard[x][y] == rival_color:
				cnt += 1
				x += direction[0]
				y += direction[1]
			elif chessboard[x][y] == color:
				ok = True
				break
			else:
				ok = False
				break
		return cnt if ok else 0

	def getReversions(self, pos, direction):
		x, y = pos
		revs = []

		rival_color = self.chessboard[x][y]
		color = -rival_color
		ok = False

		while not self.isOutOfBoard(x, y):
			if self.chessboard[x][y] == rival_color:
				revs.append((x, y))
				x += direction[0]
				y += direction[1]
			elif self.chessboard[x][y] == color:
				ok = True
				break
			else:
				ok = False
				break
		return revs if ok else []
		
	@timeout(seconds=TIMEOUT)
	def goAgent(self, agent):
		agent.go(self.chessboard)

