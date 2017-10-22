'''
Created on Jun 22, 2017

@author: Rudy Laprade (penguin8r)
'''
from commands.command import Command

class InfoCommand(Command):
	'''
	This is a class for the !info command.  It displays all available commands,
	as well as optionally any additional info, and then goes on cooldown
	for 10 seconds.

	Uses the default Command settings

	Format: InfoCommand("Bot's response to someone typing !info in chat")
	'''


	def __init__(self, additonal_info = "", *kwargs):
		'''
		Constructor
		'''
		super(InfoCommand, self).__init__(
										"info",
										include_in_info=True,
										cooldown_duration=10,
										*kwargs)
		self._additional_info = additonal_info

	def respond(self, user, message):
		"""
		Retrieves all available commands and sends to chat. Some are hidden,
		such as the HNAARGH command as it's a response to certain random
		messages and not a specific command as such.
		"""
		command_list = [command.get_name() for command in self._bot.commands if command.include_in_info]
		if len(command_list) == 0:
			info_string = ""
		elif len(command_list) == 1:
			info_string = "Commands are !{}.".format(command_list[0])
		else:
			info_string = "Commands are !" + ", !".join(command_list[:-1]) \
					+ ", and !{last_command}.".format(last_command = command_list[-1])
		if self._additional_info:
			info_string += " " + self._additional_info
		self._bot.send_message(info_string)
