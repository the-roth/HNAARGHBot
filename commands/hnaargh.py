'''
Created on Jun 21, 2017

@author: the_roth and Rudy Laprade (penguin8r)
'''
import re
import random
from commands.command import Command
from games.lists import HNAARGHList

class HNAARGH(Command):
	'''
	Responds to various user inputs, mainly centering around alterations of the
	word 'HNAARGH', or 'hnaarghhghghg!!' etc.
	Includes KittyT because he's a cool cat

	Isn't displayed in !info

	Some work can be done here to make the Class methods simpler. The process
	method just calls the previous functions hnaargh_Start and hnaargh instead
	of dealing with them directly.
	'''


	def __init__(self):
		'''
		Constructor
		'''
		super(HNAARGH, self).__init__(
			"HNAARGH",
			cooldown_duration=5,
			include_in_info=False,
			disabled_on_game=True)


	def matches(self, user, message):
		"""
		Matching is complicated so not actually handled here - see hnaargh_start
		"""
		return True


	def process(self, user, message):
		"""
		Didn't see a nice way to fit the current functionality into the
		command's process method
		Ideally would probably be re-written to use match and respond
		like everyone else

		:param message: User chat message
		"""
		if self._bot is None:
			raise RuntimeError("Trying to run command {} without an associated bot.".format(self))
		if self.can_be_used():
			self.hnaargh_start(user, message)


	def hnaargh_start(self, user, message):
		# Select a random arnie quote, with a 25% ish chance of a random HNARGH
		self.hnaargh(
			r'^hu*h*n+a+r+[gh][gh]+!*$',
			message,
			random.choice(
						HNAARGHList
						+ ["HNAARGH"] * 3
						+ ["HNARGH HNAAAARGH!"] * 3
						+ [message] * 3
						),
			1)
		self.hnaargh(
			r'^HU*H*N+A+R+[GH][GH]+!*$',
			message,
			random.choice(
						HNAARGHList
						+ ["HNAARGH"] * 3
						+ ["HNARGH HNAAAARGH!"] * 3
						+ [message] * 3),
			1)

		# Dumb responses if people don't use caps of have silly spelling
		self.hnaargh(r'^[Hh][Nn]+[A]a+[Rr]+[GgHh][GgHh]+!*$', message, "her naarg")
		# This one times out user for 1 second, dammit Brossentia for the meme
		# HUH NAAARG
		self.hnaargh(r'^h[eu][hr] *na+r+g+!*', message.lower(),
						"SHUT UHP", user, 1, 0.5)

		# Gotta have KittyT here too
		self.hnaargh(r'KittyT', message, "Grr.. Zrrrr... Purr KittyT")


	def hnaargh(self, searchString, string, output, person=None, prob=1, t_out=0):
		"""
		Returns a message back to chat based on which command in HNAARGH_Start
		is activated. Runs a timer so that arnie quotes aren't spammed too often
		:param searchString:
		:param string:
		:param output:
		:param person:
		:param prob:
		:param t_out:
		"""
		if re.match(searchString, string):
			self.cooldown_switch()
			self.random_message(prob, output)
			if random.random() > 1 - t_out:
				self._bot.timeout(person)


	def random_message(self, prob, message):
		"""
		Changes frequency of HNAARGHbot message spamming if needed
		"""
		if random.random() >= 1 - prob:
			return self._bot.send_message(message)
