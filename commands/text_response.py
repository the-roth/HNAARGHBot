'''
Created on Jun 22, 2017

@author: Rudy Laprade (penguin8r)
'''
from commands.command import Command

class TextResponse(Command):
	'''
	This is a basic text response command.  When a user posts a command
	(!{command name}), this will respond with a specified message and then
	go on cooldown for 10 seconds by defult.

	The format is TextResponse('command name', 'response')
	'''


	def __init__(self, name, response, *kwargs):
		'''
		Constructor

		:param name: Name of the command
		:param response: A string containing the desired response to the command
		'''
		super(TextResponse, self).__init__(name, *kwargs)
		self._response = response


	def respond(self, user, message):
		"""
		Bot sends a message corresponding to this command's response.
		Also goes on cooldown for _cooldown_length (default 10) seconds.

		:param user: Unused here, user who sent the message
		:param message:  Unused here, message the user sent
		"""
		self._bot.send_message(self._response)
