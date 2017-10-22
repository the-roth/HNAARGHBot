## HNAARGHBot!

This is the code for my Twitch bot, HNAARGHBot. I wrote this as a way of learning the Python language and was originally written in Python 2. I later updated the code to Python 3 and Rudy Laprade ([penguin8r](http://www.twitch.tv/penguin8r)) helped a lot with implementing classes and objects which made my code look and run a lot more smoothly.  

## Bot Functionality

HNAARGHBot essentially works like this:

- Run.py is the main file which starts the bot, which is a TwitchBot class (see twitch_bot.py). It simply connects to IRC and is able to send commands to chat or privately to users, timeout users etc.

- The bot then processes Commands which can be either an InfoCommand (displays the possible commands available to the user), TextResponse (responds to user input), HNAARGH response, or a Game (!meateo, !outback, !jelly).

HNAARGHBot was originally designed to just respond to variations of the word 'HNAARGH' with various Arnold Schwarzenegger quotes. I spelled out an Arnold Schwarzenegger grunt one day for some reason and it kinda stuck in chat one day and hasn't left since.  The chat bot games were later designed in the following order:

- Meateo - A guessing game designed around the end game of Final Fantasy IV when completing it using the 64 door glitch, where Cid casts Meteo on Zeromus instead of FuSoYa. Users are required to guess a number between 1600 and 2110, the typical Meteo damage of a game.

- Outback - An autobattle game where people in chat sign up to battle a creature from the Australian Outback. The game can currently hold up to 12 players.

- Jelly - Another autobattle game that mimics the end game fight against the Master Jelly in the Ancient Cave in Lufia 2: Rise of the Sinistrals. It generates an item pool found during a 'typical' Ancient Cave playthrough and then equips and uses these items against the Jelly in a somewhat optimal fashion.

I still need to make a few improvements which will (hopefully) happen over time, I have a few other projects to work on which will also be posted on Github in the future. You can find further information about my chat bot games [here](https://www.twitch.tv/hnaarghbot). If you have any feedback or questions about my bot, feel free to message me on [Twitch](http://www.twitch.tv/the_roth) or email me at david.rothall@gmail.com!
