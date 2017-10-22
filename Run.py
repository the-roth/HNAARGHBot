# -*- encode: utf-8 -*-

"""
Copyright (c) 2017 David Rothall <david.rothall@gmail.com>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

"""
Created on Jun 22, 2017

@author: the_roth and Rudy Laprade (penguin8r)
"""

from commands.hnaargh import HNAARGH
from commands.info import InfoCommand
from commands.text_response import TextResponse
from games.Jelly import Jelly
from games.Meateo import Meateo
from games.Outback import Outback
from twitch_bot import TwitchBot

"""
run.py starts the bot, grabbing necessary information from twitch_bot.py.
There are also various commands and games that chat will interact with which are
added as modules to the bot later on.

When initialized, the bot does the following steps:
1: Connects to Twitch Chat via open_socket and join_room methods
2: Adds any commands requested using the add_command method
3: The bot then runs using the runtime method, which is an infinite loop.
   It extracts the user/message from a response and then executes commands
   depending on what the message is, i.e. run games, Arnold quotes etc.
   It also responds to chat using send_message, whisper and timeout commands
"""

if __name__ == "__main__":
	hnaargh_bot = TwitchBot()

	# Add !info
	hnaargh_bot.add_command(InfoCommand(
		"Please visit www.twitch.tv/HNAARGHbot for further game details!"))

	# Add Kriegspyre's AC Guide
	lufiaGuide = TextResponse(
		"acguide",
		"Lufia 2: Ancient Cave speedrun guide by Kriegspyre - goo.gl/GPiMdm")
	hnaargh_bot.add_command(lufiaGuide)

	# Jelly Game Wall of Shame
	wallOfShame = TextResponse(
		"wallofshame",
		"Jelly game Wall of Shame - http://bit.ly/2xvKrZM")
	hnaargh_bot.add_command(wallOfShame)

	# Respond to variations of "HNAARGH", "HNAARRGHGHGHGHGHG!" (and "KittyT")
	hnaargh_bot.add_command(HNAARGH())
	# Add Meateo, Outback and Jelly Games
	hnaargh_bot.add_command(Meateo())
	hnaargh_bot.add_command(Jelly())
	hnaargh_bot.add_command(Outback())

	# Finally, Run the bot. Make sure all comands are added beforehand
	hnaargh_bot.runtime()
