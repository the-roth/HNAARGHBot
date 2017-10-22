"""
Created on Jun 21, 2017

@author: Rudy Laprade (penguin8r) and David Rothall (the_roth)
"""
import threading
import re

class Command(object):
	"""
	General commands that games (Meateo, Outback etc.) and bot mechanisms
	(e.g. !info,'HNAARGH') have access to. They are initialised upon running the
	bot and will either be active or inactive depending on how they are used.

	Upon initiazation the Command object receives mechanisms as to how to
	respond	to user messages. Currently these commands are !info, !acguide,
	!wallofshame and variations of spellings of 'HNAARGH!'. The amount that
	these can be spammed in chat or during games are controlled by the
	include_in_info, cooldown_duration and disabled_on_game attributes.

	The get_name command simply returns the names of the commands available
	to the bot. Some of these are hidden, so the bot doesn't show all of them
	 (for example, the HNAARGH Command is hidden from !info).

	The set_bot method is used by the TwitchBot's add_command method which
	enables the bot to use the Command in Twitch Chat.

	The process, can_be_used and matches methods control whether the bot should
	respond to a message in chat (i.e. to prompt a game or a response). The bot
	then does the necessary action with the response method (which is
	overwritten	by each separate object, as they all have different behaviour).

	The cooldown methods halt commands from being used, either when spammed in
	chat too often or while games are being played.

	SubCommands are rarely used and probably don't need to be yet. currently
	only the Meateo game uses them to display the top 5 ranked players.
	"""


	def __init__(
		self,
		name,
		include_in_info=True,
		cooldown_duration=10,
		disabled_on_game=False,
		*args, **kwargs):
		"""
		Constructor
		Make sure to run set_bot() before trying to use the command.

		:param bot: Name of bot (this should get passed in immediately)
		:param name: Name of the command
		:param include_in_info:  Boolean indicating whether this command should
								 be written out with an info command
		:param on_cooldown: Whether the game can be used or not
		:param cooldown_duation:  How long this command should stay on cooldown
								  after being used, set to 0 for no cooldown
		:param disabled_on_game:  Boolean value, if True, this command can not
								  be used during a game
		"""
		super(Command, self).__init__(*args, **kwargs)
		self._bot = None
		self._name = name
		self.include_in_info = include_in_info
		self._on_cooldown = False  # Ends up being negated a lot. Maybe rename and invert
		self._cooldown_duration = cooldown_duration
		self._disabled_on_game = disabled_on_game
		self._subcommands = []

	def __str__(self, *args, **kwargs):
		return self._name

	def __repr__(self, *args, **kwargs):
		return self._name

	def get_name(self):
		return self._name

	def set_bot(self, bot):
		"""
		Associates this command with a TwitchBot.
		A bit inelegant to have this separate from the initialization.
		Also associates subcommands with the bot.

		:param bot:  Pointer to the TwitchBot
		"""
		self._bot = bot
		for sc in self._subcommands:
			bot.add_command(sc)

	def process(self, user, message):
		"""
		Handles whatever this command wants to do on the given user and a sent message.
		By default checks if the command matches and performs respond() if so.
		Also handles command cooldown
		Should probably not be overridden

		:param user: String containing a username
		:param message: User chat message
		"""
		if self._bot is None:
			raise RuntimeError("Trying to run command {} without an associated bot.".format(self))
		if self.can_be_used() and self.matches(user, message):
			self.respond(user, message)
			self.cooldown_switch()

	def can_be_used(self):
		"""
		Returns True if this command can be used
		"""
		return not self._on_cooldown and not (self._disabled_on_game and self._bot.has_active_game)

	def matches(self, user, message):
		"""
		Checks whether the message corresponds to this command.
		Can be overridden for more advanced matching, such as regex or
		additional argument processing

		:param user: String containing a username
		:param message: User chat message
		"""
		return re.match("!{name}$".format(name=self._name), message.lower())

	def respond(self, user, message):
		"""
		Performs the basic response of this command to user input.
		Should be overridden by subclass.
		"""
		pass

	def cooldown_switch(self):
		"""
		Puts this command on cooldown for the self._cooldown_duration seconds
		Questionable whether this should have a duration argument or just read
		the instance variable

		Default cooldown functionality doesn't need Timer, could compare
		timestamps instead
		"""
		if self._cooldown_duration == 0:
			# Save a thread if this command has no cooldown
			return
		self._on_cooldown = True
		# Changes _on_cooldown back to False after a certain time
		threading.Timer(self._cooldown_duration, self.cooldown).start()

	def cooldown(self):
		"""
		Pops when the cooldown of this command expires
		"""
		self._on_cooldown = False


class SubCommand(Command):

	def __init__(self, name, main_command, *args, **kwargs):
		"""
		:param main_command: A pointer to the main command this is attached to
		"""
		super(SubCommand, self).__init__(name, *args, **kwargs)
		self._main_command = main_command

if __name__ == "__main__":
	pass
