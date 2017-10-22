"""
Created in October, 2016

@author: the_roth

Second game written, had difficulties with optimising parameters as they
were all done by hand. In the future I'd automate the procedure a lot more.
"""
import random
import threading
import math

from games.game import Game
from games.lists import outbackDict, outbackLevels, outbackLevelDesc, description

OUTBACK_ON_COOLDOWN_MESSAGE = "The next tourist in the Australian outback can be attacked "
OUTBACK_COOLDOWN_DURATION = 1800

class Outback(Game):

	"""
	This class handles the whole outback game. The idea is that a random enemy
	difficulty is chosen, and then players and the enemy automatically
	deal damage to each other. This damage is dependent on max HP only, and so
	players have the same chance of dying regardless of their max HP etc.

	The game is currently designed to take around 4.5 rounds to complete. There
	generally aren't many survivors if the party wins. Not sure if it's possible
	to change this while keeping the party win rates & the av. # of rounds
	the same.

	The game needs a few helper functions to optimise party/individual survival
	rates as well as the game lengths. These are damage_scale and game_length.
	I'd suggest leaving these alone but if you have any ideas to make this easier
	please let me know. You can test survial rates by using outback_test.py.

	Level difficulty / Party win rate / Individual Survival Rate

	1 Very Easy: 	80 - 85%	/	40 - 55%
	2 Easy: 		75 - 80%	/	35 - 48%
	3 Medium: 		70 - 75%	/	30 - 40%
	4 Hard: 		60 - 65%	/	25 - 33%
	5 Very Hard: 	40 - 45%	/	15 - 20%

	This game currently only works for up to 12 players, I think it is a good
	amount. Any more ruins the damage formula (not tested).
	"""


	def __init__(self, *args, **kwargs):
		super(Outback, self).__init__(
			"outback",
			OUTBACK_ON_COOLDOWN_MESSAGE,
			cooldown_duration=OUTBACK_COOLDOWN_DURATION,
			print_speed=20,
			*args, **kwargs)
		self._enemy = ""
		self._desc = ""
		self._level = 0
		self._difficulty = ""
		self._testNumPlayers = random.randint(1, 12)


	def initialize_game(self):
		self._desc = random.choice(description) + ' '
		self._enemy = random.choice(outbackDict['animal'])
		level, difficulty = self.outback_random() # [level, ': description']
		self._level = level
		self._difficulty = difficulty


	def signup_player(self, user):
		super(Outback, self).signup_player(user)
		if len(self._player_list) == 12:
			if 'the_roth' in self._player_list:
				self._player_list.remove('the_roth')
				self._bot.send_message(
					'Roth gets kicked off the bus! '
					+ 'There is room for one more person.')
			else:
				self._bot.send_message(
					self.socket,
					'The bus going to help out against the '
						+ self._enemy
						+ ' is now full! The party of 12 will soon do battle...')
				self.close_signups()


	# Outback Game! Australian animals attack tourists
	def introduction(self, user):
		intro = [
			"{} was {} the outback when {} (level {}) attacks them!" \
			.format(
				user.capitalize(),
				random.choice(outbackDict["activity"]),
				self._desc + self._enemy,
				str(self._level) + self._difficulty
				),
			" They need help! Type \"!outback\" to get on the bus and help "
			+ "defend against the Australian wildlife!"
			]
		return intro


	# Displays position and points of a users in the Outback game
	def rank(self, lst):
		with open("games/Outback.txt", "r") as f:
			st = ""
			for line in f:
				spl = line.split()
				user, currentLevel = spl
				currentLevel = int(float(currentLevel))
				if user in lst:
					for i in range(len(outbackLevels)):
						if currentLevel >= outbackLevels[i]:
							st = "{}: Level {} ({}), {} HP, " \
							.format(
								st + user.capitalize(),
								currentLevel,
								outbackLevelDesc[i],
								str(30 + (currentLevel - 1) * 2)
							)
							lst.remove(user)
							break
			if lst:			# only sends if users don't have a ranking in Outback.txt
				st = st[:-2] + ". No rank exists for " 	# replaces comma with sentence
				for person in lst:
					st = st + person.capitalize() + ", "
		return st[:-2] + "."


	def results(self, testing = False):
		animal = self._enemy
		animalLevel = self._level
		diff = self._difficulty     # not used?
		# I think this could be done more nicely,
		# but I don't want to go mucking through the Outback game
		players = dict((p, [30, 30]) for p in self._player_list)

		# special scenario to add Liin1 and to kill him with laughter
		liinKill = 0
		if "liin1" not in players.keys():
			liinKill = 1

		# Outback Game! Australian animals attack tourists
		# Modify players' HP if they have played before and potentially leveled up
		# and add new players to the file to be written later
		with open("games/Outback.txt", "r") as f:
			outbackdata = [line.strip().split() for line in f]
		# print outbackdata
		for player, hp in outbackdata:
			HP = 30 + (int(float(hp)) - 1) * 2 # level 1 = 30HP, level 2 = 32HP etc.
			if player in players.keys():
				players[player] = [HP, HP]
		for key in players.keys(): # add new players not on file
			if key not in [i[0] for i in outbackdata]:
				outbackdata.append([key, "1"])

		if testing:
			players = self.test_player_list()

		# Place to store results. Start with the battle intro already here.
		result = [
			"The tourists will soon do battle with the "
			+ "dangerous Australian wildlife... Are the tourists tasty? "
			+ "Will they survive? Or will they become delicious meals?"
			]

		numPlayers = len(players)

		# Animal HP is based off of # of players
		animal = "The " + animal	# Make the game readable
		animalHP = len(players) * 50
		animalMaxHP = animalHP
		# (Game win rate - 1: 80-85%, 2: 75-80%, 3: 70-75%, 4: 60-65%, 5: 40-45%)
		levelDict = {1:1.45, 2:1.32, 3:1.245, 4:1.13, 5:0.942}

		# Generate 1st attack of the game - has different text to the rest of game
		initialAnimalDamage = int(round((
			self.damage_to_animal(animalMaxHP, players, levelDict[animalLevel])
			* self.damage_scale(numPlayers)
			* self.game_length(numPlayers)
			)))

		animalHP -= initialAnimalDamage
		animalHPLeft = " ({}/{})".format(animalHP, animalMaxHP) # e.g. (3/15)

		result.append("The{}{}{} receives {} damage{}." \
			.format(
				" " + str(len(players)) if len(players) > 1 else "",
				" tourists attack! " if len(players) > 1 else " tourist attacks! ",
				animal,
				initialAnimalDamage,
				animalHPLeft
			))

		# Game loop - enemy attacks, then remaining players attack, repeat
		while sum([i[0] for i in players.values()]) > 0 and animalHP > 0:
			# Determine # of people the animal attacks
			noOfTargets = self.number_of_targets(numPlayers, players)

			# Choose random targets
			targets = random.sample(list(players), noOfTargets)

			# Determine damage to targets. Based off of:
			# 1: Starting # of players - done so that games are finished
			# 	 in a similar amount of rounds regardless of how many enter.
			# 2: # of targets. The fewer targets, the more damage dealt
			# 3: Max HP - scaled so that the enemy does the
			#	 same relative damage to everyone regardless of their max HP.
			damageToPlayers = [random.randint(1, int(round(
				3.5 * players[targets[i]][1]
				* self.game_length(numPlayers, "yes")
				/ (noOfTargets * self.damage_scale(numPlayers))
				))) for i in range(0, noOfTargets)]

			# Damage to enemy scaled relative to maxAnimalHP and # of players alive
			animalDamage = int(round((
				self.damage_to_animal(animalMaxHP, players, levelDict[animalLevel])
				* self.damage_scale(numPlayers)
				* self.game_length(numPlayers)
				)))

			result.append("{} {}{}!" \
				.format(
					animal + animalHPLeft,
					random.choice(outbackDict["enemy_growl"]),
					random.choice(outbackDict["enemy_counter"])
				))

			# Have a place to store the text generated by the round
			rounds = ""

			for i in range(0, len(targets)):
				player = targets[i]
				currHP = players[player][0] # player[0] = current HP left
				# Make damage readable if the hit is overkill
				# e.g. if 237 damage to a 30 HP person, then this reads 30 instead
				hit = currHP if damageToPlayers[i] >= currHP else damageToPlayers[i]
				# Check if the hit would kill a player and adjust to make readable
				players[player][0] = 0 if hit > currHP else currHP - hit
				playerMaxHP = players[targets[i]][1]
				rounds += "{} - {} damage ({}/{}), " \
					.format(
						player,
						hit,
						players[player][0],	# Current Player HP after taking damage
						playerMaxHP
					)
				if players[player][0] == 0:	# ded
					del players[player]
			result.append(rounds[:-2]) # remove last comma

			# If tourists survived they respond, otherwise they are eaten, game ends
			if sum([i[0] for i in players.values()]) > 0:
				if liinKill > 0:
					liinKill = random.choice(range(10))
					if liinKill == 0:
						result.append("Liin1 joins the fray out of nowhere, and "
						+ "with a mighty roar attacks "
						+ animal[0].lower() + animal[1:]
						+ " but misses! He is killed instantly.")

				# "The X remaining tourist/s (descriptive) regroup (descriptive)
				#  attack! The Animal (3/30 HP) receives X damage.""
				result.append("The {}{}tourist{}{}{}! {} receives {} damage." \
					.format(
						str(len(players)) + " " if len(players) >= 2 else "",
						"remaining " if numPlayers > 1 else "",
						" " if len(players) == 1 else "s ",
						random.choice(outbackDict[
							"tourist"
							+ ("s" if len(players) > 1 else "")
							+ "_regroup"
							]),
						random.choice(outbackDict[
							"tourist"
							+ ("s" if len(players) > 1 else "")
							+ "_attack"
							]),
						animal + animalHPLeft,
						str(animalHP) if animalDamage >= animalHP else str(animalDamage)
					))
				animalHP -= animalDamage
				animalHPLeft = " ({}/{})".format(animalHP, animalMaxHP) #e.g. (3/15)

			else:
				# The tourist(s) are eaten by the cat (1/123). Thanks for playing!
				result.append("The tourist{}{}. Thanks for playing!" \
					.format(
					  "s are eaten by " if numPlayers > 1 else " is eaten by ",
					  animal[0].lower() + animal[1:] + animalHPLeft
					))

				if testing == True:
					#[we lost = False, number of rounds, no players left = empty]
					return [
						False,
						int(math.ceil((len(result) - (3 if liinKill == 0 else 2))/3)),
						players
						]
				else:
					return result

			# if animal is dead, say so, otherwise repeat the loop
			if animalHP <= 0:
				playersRemaining = ""
				for i in players.keys():
					playersRemaining += i + ", "
				playersRemaining = playersRemaining[:-2]
				lastComma = playersRemaining.rfind(",")
				if lastComma != -1:
					playersRemaining = (
						playersRemaining[:lastComma]
						+ " and"
						+ playersRemaining[lastComma + 1:])

				result.append("The tourists are victorious, with "
				+ playersRemaining
				+ " still standing! Thanks for playing!")

				if testing == True:
					# [We won = True, number of rounds taken, survivors]
					return [
						True,
						int(math.ceil((len(result) - (3 if liinKill == 0 else 2))/3.)),
						players
						]
				else:
					# Update player HP, if any of them survived the fight
					# For levels 1 -> 5 respectively,
					# suvivors gain 1, 1.5, 2, 3.5 and 5 levels.
					for line in outbackdata:
						if line[0] in players.keys():
							line[1] = float(line[1]) + (
											1 if animalLevel == 1
											else 1.5 if animalLevel == 2
											else 2 if animalLevel == 3
											else 3.5 if animalLevel == 4
											else 5
											)
					f = open("games/Outback.txt", "w")
					# Sort based on level, might as well
					for line in sorted(outbackdata, key = lambda x: float(x[1]), reverse = True):
						f.write(line[0] + " " + str(line[1]) + "\n")
					f.close()
					return result


	def deploy_printout(self, result):
		# Outback game printout is different to jelly/meateo games
		for i in range(0, len(result)):
			# Tourist attack line
			if i % 3 == 1:
				threading.Timer(self._print_speed * i + 5, self.line_print, (result[i],)).start()
			# Next two lines are printed 10 seconds apart as they are the enemy attack
			elif i % 3 == 2:
				threading.Timer(self._print_speed * i + 10, self.line_print, (result[i],)).start()
			else:
				threading.Timer(self._print_speed * i, self.line_print, (result[i],)).start()


	# Generate a random player list with stats
	# For testing purposes
	def test_player_list(self):
		testingPlayerList = [
			["a",[30,30,]], ["b",[40,40]], ["c",[50,50]],
			["d",[60,60]], ["e",[70,70]], ["f",[80,80]],
			["g",[90,90]], ["h",[100,100]], ["i",[110,110]],
			["j",[140,140]], ["k",[170,170]], ["l",[200,200]]
			]
		teamStats = {}
		team = random.sample(testingPlayerList, self._testNumPlayers)
		for (player, (minHP, maxHP)) in team:
			teamStats[player] = [maxHP, maxHP]
		return teamStats


	# Chooses level difficulty for !outback game
	def outback_random(self):
		num = random.random()
		return(
			[1, ": Very Easy"] if num >= 0.85
			else [2, ": Easy"]  if num >= 0.55
			else [3, ": Medium"] if num >= 0.25
			else [4, ": Hard"] if num >= 0.1
			else [5, ": Very Hard"])


	# Calculates damage to animal based on animal max HP
	# This scales as the number of players decreases during a game
	def damage_to_animal(self, hp, p, level):
		return int(random.randint(1, int(round(hp * .56)) if len(p) >= 6
			else int(round(hp * .435)) if len(p) >= 4
			else int(round(hp * .33)) if len(p) >= 2
			else int(round(hp * .24))) * level)


	# Scale player and enemy damage based on the no. of players present in a game
	# This scales with the starting number of players only, not during a game
	def damage_scale(self, p):
		damageScaleList = [
			[1,3.333], [2,1.9], [3,1.5], [4,1.145], [5,1], [6,0.825],
			[7,0.74], [8,0.685], [9, 0.633], [10,0.591], [11,0.567], [12,0.538]
			]
		return damageScaleList[p - 1][1]


	# Game length is inversely proportional to the no. of players p in the game
	# This function adjusts both party and enemy damage as to vary the game length
	# Additional scale needed to boost animal damage as a single scale alone
	# doesn't keep win rate at the right amount
	def game_length(self, p, animalBoost = "no"):
		lengthScaleList = [
			[1,0.47], [2,0.69], [3,0.90], [4,0.95], [5,1.08], [6,1.06],
			[7,1.16], [8,1.21], [9, 1.3], [10,1.37], [11,1.44], [12,1.49]
			]
		boostScaleList = [
			[1,0.86], [2,0.84], [3,0.95], [4,0.97], [5,1.04], [6,1.03],
			[7,1.15], [8,1.14], [9, 1.32], [10,1.56], [11,1.57], [12,1.93]
				]
		lengthScale = lengthScaleList[p-1][1]
		boostScale = boostScaleList[p-1][1] if animalBoost == "yes" else 1
		return lengthScale * boostScale


	# Number of targets is determined by starting no. of players
	# This scales with the starting number only
	def number_of_targets(self, p, currentNumberOfPlayers):
		number = 6 if p > 10 else 5 if p > 7 else 4 if p > 4 else 3
		return min(random.randint(1, number), len(currentNumberOfPlayers))

if __name__ == '__main__':
	pass

	# animal = "Big Fluffy Cat Purrhead"
	# animalLevel = 1
	# diff = 'Medium'
	#
	# players = test_player_list(testingPlayerList, 6)
	#
	# battle = results(players, animal, animalLevel, diff, testing = False)
	# for line in battle:
	# 	print(line)
