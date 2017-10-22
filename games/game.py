"""
Created on Jun 20, 2017

@author: Rudy Laprade (penguin8r) and the_roth
"""
import threading
import time
import re
from enum import Enum     # install via pip install enum34

from commands.command import Command, SubCommand

DEFAULT_SIGNUP_TIME = 130
DEFAULT_PRINT_SPEED = 30
TIMER_COOLDOWN_DURATION = 60

Status = Enum('Status', 'inactive signup results running on_cooldown signups_full')

class Game(Command):
	"""
	This class is the building block for implementing games.  It follows a
	multi-phase design with statuses defined by the Enum above.
	1. Inactive:  The game is not running nor on cooldown.  Ready to be played
				  if no other games are going on.
	2. Signup:    The game was started by !<game_name>.  In this phase other
				  users can signup with the command
	3. Running:   The game is now running.  Players may interact with
				  the game in some format.
	4. Results:   Results of the game are printed out. This is distinguished from
				  the Running phase in that no user interaction should be occurring.
	5. On_cooldown:  Only once the game is completed (end of Results phase) does
					 the game go on cooldown. Querying the game instead will
					print a message saying how long until the game is available.

	Currently, only one game is allowed to be running at a time.

	!game is hidden from !info but the actual games such as !meateo are not.

	See the __init__ method for initialization notes. Other points to note are:
	TIMER_COOLDOWN_DURATION = This variable stops the bot from responding to
	game commands when they've just been played.
	"""


	def __init__(
		self,
		name,
		on_cooldown_message,
		signup_time=DEFAULT_SIGNUP_TIME,
		running_duration=0,
		print_speed=DEFAULT_PRINT_SPEED,
		has_rank=True,
		*args, **kwargs):
		"""
		Constructor
		Only one game is allowed to be running at a time

		:param name:  Name of the game, the word/phrase used to start the game
		:param duration:  Duration of the game in seconds
		:param on_cooldown_message:  Message to display when someone tries to
									 play the game but it is on cooldown
		:param signup_time:  How long users are given to signup for the game
							 (in seconds)
		:param print_speed: Print speed of game (Outback game is variable speed)
		:param has_rank:  Boolean indicating whether this game should have a
						  Rank command
		"""
		super(Game, self).__init__(name, disabled_on_game=True, *args, **kwargs)
		self._on_cooldown_message = on_cooldown_message
		# Following 2 timer variables could at least be named better
		self._timer_last_used = time.time()
		self._timer = 0
		self._signup_time = signup_time
		self._running_duration = running_duration
		self._print_speed = print_speed
		self.status = Status.inactive
		self._player_list = set()
		if has_rank:
			self._subcommands.append(Game.Rank(self))

	##### Methods you should implement in Games #####

	def introduction(self, user):
		"""
		Returns a string introducing this game
		Call when someone starts the game
		This method should be overridden by any Game

		:param user: User who started the game
		"""
		raise NotImplementedError()

	def results(self):
		"""
		Returns a list of strings that the bot should print out for the results
		of the game.
		Called during the Results phase
		This method should be overridden by any Game
		"""
		raise NotImplementedError()

	##### Methods you might want to override #####

	def initialize_game(self):
		"""
		Does any variable initialization and starting actions for the game.
		This is a separate function so that it can be easily overridden
		"""
		pass

	def rank(self, users):
		"""
		Not sure if all Games should have rank commands, but as of now they do.
		Should be overridden if you want to allow a rank command (!<game>rank)

		:param users:  Users whom have requested their rank
		"""
		pass

	def running_phase_initialization(self):
		"""
		Called at the start of the running phase
		"""
		pass

	def action_when_running(self, user, message):
		"""
		Behavior to respond to a message when the game is in the running phase

		:param user:
		:param message:
		"""
		pass

	def signup_player(self, user):
		"""
		Signs up the user to play the game
		By default adds the user to the player list
		Can be overriden for more complex behavior
		Note that player list is a set so will not have duplicates
		"""
		self._player_list.add(user)

	def deploy_printout(self, result):
		"""
		Prints out the results of the game, line by line.
		Separated from start_results_phase so that each game can customize how
		it prints out results

		:param result: List of lines to print in the results.
		"""
		for i in range(len(result)):
			threading.Timer(self._print_speed * i, self.line_print, (result[i],)).start()

	def matches(self, user, message):
		"""
		Determines whether the message sent by the user should be used by this game
		Overrides default matching to depend on state
		By default, accepts any message when running so that the game can
			process anything users say
		Can be overridden for more customized behavior
		"""
		if self.status is Status.running:
			return True     # Could just write the whole thing as an OR but I think this is more readable
		return super(Game, self).matches(user, message)

	##### End of methods that you should likely need to override #####

	def respond(self, user, message):
		# If game is on cooldown, tells users how long until it can be played.
		if (self.status is Status.on_cooldown
				and self._timer > 0
				and time.time() - self._timer_last_used > TIMER_COOLDOWN_DURATION):
				# self._timer redundant here?  Last part compares current time
				# to last used time to see if allowed
			time_to_go = int(round((self._cooldown_duration - time.time() + self._timer)/60))
			time_printout = ('shortly!' if time_to_go <= 2
					else 'in about ' + str(time_to_go) + ' min!')
			self._bot.send_message(self._on_cooldown_message + time_printout)
			self._timer_last_used = time.time()
		elif self.status is Status.inactive:
			self._timer = 0
			# Start the game
			self.start_game(user)
		elif self.status is Status.signup:
			self.signup_player(user)
		elif self.status is Status.running:
			self.action_when_running(user, message)

	def can_be_used(self):
		"""
		Returns True iff this game can be used
		"""
		return (self.is_active()
			or (not (self._disabled_on_game and self._bot.has_active_game)))

	def cooldown_switch(self):
		"""
		Overridden to disable, because cooldown works differently for games.
		We now use class attributes instead of dictionary switches
		(see previous bot version)
		"""
		pass

	def put_game_on_cooldown(self):
		self.status = Status.on_cooldown
		threading.Timer(self._cooldown_duration, self.cooldown).start()

	def cooldown(self):
		super(Game, self).cooldown();
		self.status = Status.inactive
		self._bot.send_message('The ' + self._name.capitalize() + ' game (!' + self._name
			+ ') can be played once any current games are complete!')

	def is_active(self):
		"""
		Tells you whether the game is currently running
		"""
		return self.status in set((Status.signup, Status.running, Status.results, Status.signups_full))

	def line_print(self, line):
		"""
		This doesn't really need to be here.
		We could just have things call send_message directly.
		"""
		self._bot.send_message(line)

	def start_game(self, user):
		"""
		Initiates the game. Sets status variables and such appropriately.
		Starts signups for the game. Do not override this method.

		Going into this, player_list should be an empty set unless you
		have been messing with things you shouldn't have.

		:param user:  The user who initiated the game
		"""
		self._bot.has_active_game = True
		self.signup_player(user)
		self.initialize_game()
		self.game_intro(user)
		self.start_signup_phase()

	def game_intro(self, user):
		opening_speech = self.introduction(user)
		for i in range(len(opening_speech)):
			threading.Timer(10*i + 2, self._bot.send_message, [opening_speech[i]]).start()

	def start_signup_phase(self):
		"""
		Starts the signup phase of the game
		Debatable whether this should be combined with start_game()
		"""
		self.status = Status.signup
		threading.Timer(self._signup_time, self.start_running_phase).start()

	def close_signups(self):
		"""
		Closes signups.  Intermediate status where we are essentially just
		waiting for the game to start.
		"""
		self.status = Status.signups_full

	def start_running_phase(self):
		"""
		Starts the running phase of the game.
		"""
		self.status = Status.running
		self.running_phase_initialization()
		threading.Timer(self._running_duration, self.start_results_phase).start()

	def start_results_phase(self):
		"""
		Starts the results phase of the game
		Prints out the results of the game
		Also sets a timer to end the game once all results are printed.
		Perhaps there is a cleaner way to do this.
		Make sure the total printing time is accurate for your game, or fix it somehow
		"""
		self.status = Status.results
		result = self.results()
		self._timer = time.time()
		total_printing_time = self._print_speed * (len(result) - 1)
		threading.Timer(total_printing_time, self.end_game).start()
		self.deploy_printout(result)

	def end_game(self):
		"""
		Does the cleanup when the game is over.  Should be called somewhere in
		the chain of events of the game.
		Do not override this method.
		"""
		self._player_list = set()
		self._bot.has_active_game = False
		self.put_game_on_cooldown()


	class Rank(SubCommand):
		def __init__(self, main_command, *args, **kwargs):
			"""
			:param main_command:  Should be an instance of a Game
			"""
			super(Game.Rank, self).__init__(main_command._name + "rank", main_command,
											cooldown_duration=0, *args, **kwargs)
			self._queued = False
			self._users_requested = set()
			self.RANK_QUERY_TIME = 10

		def game(self):
			"""
			Convenience getter method
			"""
			return self._main_command

		def matches(self, user, message):
			return re.match("^!{}(rank|level)$".format(self._main_command), message.lower())

		def respond(self, user, message):
			if not self._queued:
				self._queued = True
				# Rank query executes after brief period (10 seconds by default)
				threading.Timer(self.RANK_QUERY_TIME, self.rank_query).start()
			self._users_requested.add(user)

		def can_be_used(self):
			"""
			Returns True iff this command can be used
			Overrides method from Command
			Rank is inactive when the game is running
			"""
			return super(Game.Rank, self).can_be_used() and not self.game().is_active()

		def rank_query(self):
			"""
			Executes any outstanding queries for ranks, sends the results, and resets state
			"""
			result = self.game().rank(self._users_requested)
			self._bot.send_message(result)
			self._queued = False
			self._users_requested = set()
