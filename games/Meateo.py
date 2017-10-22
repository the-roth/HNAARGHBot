"""
Created in July 2016

@author: the_roth

First game I ever wrote, apologies for the bad code :)
"""
import random
import re

from games.lists import meateoDict
from games.game import Game
from commands.command import SubCommand

MEATEO_ON_COOLDOWN_MESSAGE = "The meateo game can be played again "
MEATEO_COOLDOWN_DURATION = 900


class Meateo(Game):
	"""
	A simple guessing game. Cid appears with a random character and casts MEATEO
	on a random boss. His damage is an even number between 1600 and 2110, so
	users are asked to guess between these values. If they type 1 or a number
	that is slightly higher than someone else's guess then the bot has a chance
	to purge that person from the game.

	After the game, points are calculated based on how many people entered.
	The closest and second closest players receive points (based on Price is
	Right strats, closest to without going over) as well as anyone who is within
	50 points of the correct value.

	Base Points (BP) = number of players
	First = 6*BP
	Second = 3*BP
	Within 4 / 15 / 50 points respectively = 15*BP / 4*BP / 1*BP
	Exact guess = 50*BP

	!meateorank or !meateolevel returns a users points and position in the game
	!meateostats returns the top 5 players and their total points.
	"""


	def __init__(self, *args, **kwargs):
		super(Meateo, self).__init__(
			"meateo",
			MEATEO_ON_COOLDOWN_MESSAGE,
			signup_time=0,
			running_duration=130,
			cooldown_duration=MEATEO_COOLDOWN_DURATION,
			*args, **kwargs)
		self._subcommands.append(Meateo.Stats(self))
		self.guessList = []
		self.who = ""
		self.meateoValue = "Computing before guessing is cheating"


	def introduction(self, user):
		partner = self.who
		intro = [
			"Your {} {} of {} were wandering around in {} when suddenly {} appears!" \
			.format(
				random.choice(meateoDict["warriors_description"]),
				random.choice(meateoDict["group"]),
				random.choice(meateoDict["warriors"]),
				random.choice(meateoDict["background"]),
				random.choice(meateoDict["enemy"])
			),
			"Cid appears from nowhere with " + partner
				+ " and yells \"Quick! let's do the MEATEO !\"",
			"Cid and " + partner + " prepare to do the "
				+ "MEATEO - an even number between 1600 and 2110. Price is "
				+ "right strats, so closest guess without going over wins."
		]
		return intro


	def initialize_game(self):
		"""
		Does any variable initialization and starting actions for the game.
		This is a separate function so that it can be easily overridden

		Cid's damage roll is always even because FF4.
		"""
		self.guessList = []
		self.who = random.choice(meateoDict['friend'])
		self.meateoValue = random.randrange(1600, 2110, 2)


	def running_phase_initialization(self):
		"""
		Called at the start of the running phase
		"""
		pass


	def action_when_running(self, user, message):
		"""
		Accepts guesses when Meateo game is in the running phase

		guesses are added to guessList as
		[user, guess, 0 (placeholder for guess difference later on in results)]
		Could add guess difference in here now, but this way the results aren't
		known until results() is called.

		:param user:
		:param message:
		"""
		if str(message).isnumeric() and user not in [i[0] for i in self.guessList]:
			guess = int(message)
			if guess == 1:
				self._bot.send_message("SHUT UHP")
				self._bot.timeout(user)
				self.guessList.append([user, 3000, 0])
			if guess >= 1600 and guess <= 2110:
				if guess in [i[1] for i in self.guessList]:
					self._bot.send_message(message + " is taken, " + user + ', please try again')
				elif guess in [i[1] + 1 for i in self.guessList] + [i[1] + 2 for i in self.guessList] \
							and random.randint(0,1) == 1: # avoid snipes
					self._bot.send_message("Snipes HNAARGH")
					self._bot.timeout(user)
					self.guessList.append([user, 3000, 0])
					print('user sniped ' + str(guess))
				else:
					print (user + " guessed " + message)
					self.guessList.append([user, guess, 0])


	# Display top 5 stats in Meateo games
	def meateo_stats(self):
		with open("games/Meateo.txt","r") as f:
			placing = [line.strip().split() for line in f]
			message = ("The top 5 in the Meateo game are currently - 1: "
						+ placing[0][0].capitalize())
			position = 1
			placesToAdd = 1
			i = 1
			while position <= 5:
				# If points between users is the same, they are equally placed
				if placing[i][1] == placing [i-1][1]:
					if position <= 5:
						placesToAdd += 1
					message += ", " + placing[i][0].capitalize()
				else:
					position += placesToAdd # if 2 people tied at 1st, next position is 3
					placesToAdd = 1
					message += " (" + placing[i-1][1] + ")"
					if position <= 5:
						message += " "+ str(position) + ": "+ placing[i][0].capitalize()
				i += 1
		return message + "."


	# Displays position / points of users requested
	def rank(self, lst):
		with open("games/Meateo.txt", "r") as f:
			st = ""

			score = 1000000000000000 # Arbitary large, overwritten immediately
			position = 1
			entries = 1

			for line in f:
				person = line[:line.find(" ")]
				# name and corresponding points is separated by a space
				# last char is a newline so we omit it
				userScore = int(line[line.find(" ") + 1:-1])
				# only change the position if score is different,
				# to the # of entries checked so far
				if userScore < score:
					score = userScore
					position = entries
				# if we find the user, return that user
				if person in lst:
					st = "{}: Position {}, {} point{}" \
					.format(
						st + person.capitalize(),
						position,
						userScore,
						("s, " if userScore > 1 else ", ")
					)
					lst.remove(person)
				entries += 1

			# Add a different message for those who don't have ranks
			if lst:
				st = st[:-2] + ". No rank exists for " 	#replaces last ',' with sentence
				for person in lst:
					st = st + person.capitalize() + ", "
		return st[:-2] + "."


	# Figures out the results from the current game and writes them to file
	# Could be done WAY better, use dictionary for the resultList to begin with
	def results(self, addResults=True):
		resultList = self.guessList
		damageRoll = self.meateoValue
		for row in resultList:
			guess = row[1]
			row[2] = abs(guess - damageRoll)  # row[2] is guess difference

		results = [i for i in resultList if i[1] <= damageRoll and i[1] <= 2110]
		basePoints = len(resultList)
		win = basePoints * 6
		secondPoints = basePoints * 3
		# generate all close guesses even if the guess was over
		closeGuess = [i for i in resultList if abs(i[2]) <= 50]
		# Make the second element = points scored for the close guess
		for row in closeGuess:
			row.append(
				basePoints * 50 if row[2] == 0
				else basePoints * 15 if row[2] <= 2
				else basePoints * 4 if row[2] <= 10
				else basePoints
			)
		points = {}
		if not results:		# no winners
			resultString = "Nobody wins."
		if results:			# at least 1 winner
			winnerRow = sorted(results, key = lambda x: x[2])[0]
			winner = winnerRow[0]
			winnerGuess = str(winnerRow[1])
			points[winner] = win
			resultString = "{} wins with a guess of {}, receiving {} points!" \
			.format(
				winner.capitalize(),
				winnerGuess,
				win
			)

		# If 2 people guessed lower than the correct guess then we have a runner up
		if len(results) >= 2:
			secondRow = sorted(results, key = lambda x: x[2])[1]
			second = secondRow[0]
			secondGuess = str(secondRow[1])
			points[second] = secondPoints
			resultString += " {} was second closest, guessing {} and gets {} point{}!" \
			.format(
				second.capitalize(),
				secondGuess,
				secondPoints,
				("s" if secondPoints > 1 else "")
			)

		# Do we have close guess points to award?
		if closeGuess:
			resultString += " Extra points for close guesses -  "
			for i in sorted(closeGuess, key = lambda x: x[3], reverse = True):
				person = i[0]
				guessPoints = i[3]
				resultString += "{}: {}, ".format(person.capitalize(), i[3])

				# If 1st, 2nd guessed close, update their points and remove them
				# from the closeGuess table, otherwise they get duplicate points.
				if person in points.keys():
					points[person] = points[person] + guessPoints
					i[3] = 0

			resultString = resultString[:-2] + "."	# replace last comma for a .

		# finalResult is returned by the game (Run.py requires list format)
		finalResult = [
			"The MEATEO does {} damage. {} Thanks for playing!" \
			.format(
				damageRoll,
				resultString
			)]


		# Write the results to a file, must read in existing data first.
		with open("games/Meateo.txt","r") as f:
			filedata = [line.strip().split() for line in f]

		# Add 1st, 2nd and Close Guesses to people already in the results file
		for line in filedata:
			if points and line[0] == winner:
				line[1] = str(int(line[1]) + points[winner])
			if len(points) == 2 and line[0] == second:
				line[1] = str(int(line[1]) + points[second])
			if closeGuess and line[0] in [i[0] for i in closeGuess]:
				# This line looks tricky, but we search the closeGuess list by username
				# and then pull out the points scored from the row
				line[1] = str(int(line[1]) + closeGuess[[i[0] for i in closeGuess].index(line[0])][3])

		# Add them if they are not. Need to search through all the first elements.
		if points and winner not in [i[0] for i in filedata]:
			filedata.append([winner, str(points[winner])])
		if len(points) == 2 and second not in [i[0] for i in filedata]:
			filedata.append([second, str(points[second])])
		# Add close guesses (1st/2nd have their points added to their total instead)
		if closeGuess:
			for row in closeGuess:
				if row[0] not in [i[0] for i in filedata]:
					filedata.append([row[0], str(row[3])])

		# Update the file and sort it based on points
		if addResults == True:
			with open("games/Meateo.txt","w") as f:
				for line in sorted(filedata, key = lambda x:int(x[1]), reverse=True):
					f.write(line[0] + " " +  line[1] + "\n")
		return finalResult


	class Stats(SubCommand):

		def __init__(self, main_command, *args, **kwargs):
			"""
			:param main_command:  Should be a Meteo instance
			"""
			super(Meateo.Stats, self).__init__(
				"meteostats",
				main_command,
				cooldown_duration=5,
				*args, **kwargs)

		def matches(self, user, message):
			return re.match("!meateo(results|stats)$", message.lower())

		def respond(self, user, message):
			self._bot.send_message(self._main_command.meateo_stats())
