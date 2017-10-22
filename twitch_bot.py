"""
Created on Jun 22, 2017

@author: the_roth and Rudy Laprade (penguin8r)
"""
import string
import socket

import Config


class TwitchBot:
	"""
	A basic TwitchBot.  It can be customized by feeding commands and actions
	into the constructor.
	Could also be extended for more advanced functionality.

	When initialized, the bot does the following steps:
	1: Connects to Twitch Chat via open_socket and join_room methods
	2: Adds any commands requested using the add_command method
	3: The bot then runs using the runtime method, which is an infinite loop.
	   It extracts the user/message from a response and then executes commands
	   depending on what the message is, i.e. run games, Arnold quotes etc.
	   It also responds to chat using send_message, whisper and timeout commands
	"""


	def __init__(self):
		"""
		Constructor
		Initializes the bot

		:param s: Connects to Chat via settings in Config.py
		:param commands: These are actions that the bot is able to do (e.g. games,
				HNAARGH responses), and are added as modules before running the bot
		:param has_active_game: Whether a game is currently running or not
		:param readbuffer: A spot to read in lines typed into Chat
		"""

		self.s = self.open_socket()
		self.join_room(self.s)

		self.commands = []
		self.has_active_game = False
		self.readbuffer = ""


	def open_socket(self):
		"""
		Socket Details to connect to Twitch IRC

		:param s: Socket
		"""
		self.s = socket.socket()
		self.s.connect((Config.HOST, Config.PORT))
		self.s.send(("PASS " + Config.PASS + "\r\n").encode(encoding='utf_8'))
		self.s.send(("NICK " + Config.IDENT + "\r\n").encode(encoding='utf_8'))
		self.s.send(("JOIN #" + Config.CHANNEL + "\r\n").encode(encoding='utf_8'))
		return self.s


	def join_room(self, s):
		"""
		Parse initial loading lines
		and use the LoadingComplete fn to tell when loading's complete
		"""
		readbuffer = ""
		loading = False
		while not loading:
			readbuffer = readbuffer + self.s.recv(1024).decode()
			temp = readbuffer.split("\n")
			readbuffer = temp.pop()

			for line in temp:
				print(line)
				loading = self.loading_complete(line)
		# send_message(s, "I am HNAARGH bot")


	def loading_complete(self, line):
		return "End of /NAMES list" in line


	def add_command(self, command):
		"""
		Adds an unprompted respond to this bot.
		All commands must be added before running the bot in run.py.

		:param command: Command to add
		"""
		self.commands.append(command)
		command.set_bot(self)


	def get_user(self, line):
		"""
		Extract the user from a response
		"""
		separate = line.split(":", 2)
		user = separate[1].split("!", 1)[0]
		return user.rstrip()

	def get_message(self, line):
		"""
		Extract the message from a response
		"""
		separate = line.split(":", 2)
		message = separate[2]
		return message.rstrip()


	def send_message(self, message):
		"""
		Send a message to chat
		"""
		messageTemp = "PRIVMSG #" + Config.CHANNEL + " :" + message
		self.s.send((messageTemp + "\r\n").encode(encoding='utf_8'))
		print("Sent: " + messageTemp)


	def whisper(self, user, message):
		"""
		Whisper to a user, i.e. Private message
		"""
		self.send_message('/w ' + user + ' ' + message)
		print("Whispered to " + user + ': ' + message)


	def timeout(self, user, secs=1):
		"""
		BANHAMMER (Kappa)

		:param user: the user to be timed out
		:param secs: the length of the timeout in seconds (default 1)
		"""
		print("Purged " + user)
		return self.send_message('/timeout ' + user + ' ' + str(secs))


	def runtime(self):
		"""
		Infinite loops time
		"""
		while True:
			readbuffer = self.readbuffer + self.s.recv(1024).decode()
			temp = readbuffer.split("\n")
			readbuffer = temp.pop()

			for line in temp:
				# print(line)

				if (line.startswith("PING ")):    # If PING, respond with PONG
					self.s.send(b"PONG tmi.twitch.tv\r\n")
					break

				# Parse the lines and return a better format
				# but keep the original line for now too.
				user = self.get_user(line)
				message = self.get_message(line)
				# Should probably do logging rather than just printing to console
				print(user + " typed: " + message)

				for command in self.commands:
					command.process(user, message)
