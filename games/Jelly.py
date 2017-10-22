"""
Created on Mar 02, 2017

@author: the_roth

Wrote this game earlier this year after Shadowkiller4826 asked for it. It's pretty
fun! The equipping and character scripts are written just using conditionals
but as an exercise I could probably get the game to optimise its own equipping
and battle scripts.
"""

import math
import random

from games.Jelly_Lists import weaponDict, weaponEquipDict, defaultAttackDict, \
	magicDict, spellUseList, capsuleMonstersDict, jellySayings
from games import Jelly_WallofShame
from games.game import Game
from Config import jellyGameTake5PlayersOnly, useWallOfShame

JELLY_ON_COOLDOWN_MESSAGE = "The next unfortunate party will reach the master jelly "
JELLY_COOLDOWN_DURATION = 1500

class Jelly(Game):
	"""
	This game is designed to mimic the Jelly fight at the end of
	the Ancient Cave playthrough in Lufia 2.

	We try to keep with the strongest party (Dekar, Guy, Maxim, Arty)
	but have a chance of those characters
	being swapped out for others, so that there is about a
	50% chance of keeping the strongest party.

	Summary of Jelly Bot steps:
	(Jelly_Lists.py)
	Define items that will be used in the game and whether they are
		fractional or damage based attacks
	Also Create magic, capsule monster and jelly saying dictionaries

	(Jelly.py)
	1 - Create a character with only a default weapon and Dragon spells equipped
		and empty rock (and armor) slots
	2 - Randomly generate a pool of items for the game that would be found
		in a typical Ancient Cave playthrough
	3 - Assign weapons, rocks and then spells to characters in the order
		(Dekar, Guy, Maxim, Arty, (Selan, Tia, Lexis - not sure here))
	4 - Generate attack scripts for each character based on the items
		they have equipped
	5 - Determine the damage values for all of the attacks used in the game
	6 - Simluate the battle and store results in a list
	7 - Write the results to file and to the Wall of Shame Google Spreadsheet
		if it's required

	If there are any bugs please let me know on Twitch @ the_roth. Thanks!
	"""

	def __init__(self, *args, **kwargs):
		super(Jelly, self).__init__(
			"jelly",
			JELLY_ON_COOLDOWN_MESSAGE,
			cooldown_duration=JELLY_COOLDOWN_DURATION,
			*args, **kwargs)

	def signup_player(self, user):
		super(Jelly, self).signup_player(user)
		if jellyGameTake5PlayersOnly and len(self._player_list) == 5:
			self._bot.send_message('Signups for the jelly game are now closed, '
				+ 'our 5 members will soon do battle with the jelly.')
			self.close_signups()


	# It's easier to make a function for the intro
	# as it gets played before the results get processed in run.py
	def introduction(self, person):
		intro = [
		'Jelly: I never imagined ' + person.capitalize()
			+ ' could make it this far... Fool! I am the oldest and smelliest '
			+ 'of jellies, I control everything in this cave.',
		'Jelly: I am also the last enemy you meet here. Since you\'ve '
			+ 'come this far, show me what you\'re made of!',
		'Five people will be chosen to join the battle - type "!jelly" '
			+ 'within the next 2 minutes to have that chance!'
		]
		return intro

	# 6 -  Now for the gaaaaaaaaaaaaaaaaaaame
	def results(self, testing = False, googleSheets = useWallOfShame):
		players = list(self._player_list)
		if len(players) < 5:
			# preserve player list but add blank players afterwards
			playersToWrite = players[:]
			players = players + ['blank player'] * (5 - len(players))
		else: # only 5 players will get to play the game and score results
			players = players[:5]
			# preserve player list for later, we now only want the actual players
			playersToWrite = players[:]
		random.shuffle(players)

		partyLevel = 'Level 30'
		capsuleLevel = 'Level 28'
		result = []	# Place to store results (duh)

		# Give a chance of replacing each main party character with a Reject% one
		mainChars = ['Guy', 'Dekar', 'Arty', 'Maxim']
		random.shuffle(mainChars)
		replacements = ['Tia', 'Lexis', 'Selan']
		noOfReplacements = 0
		for i in range(len(mainChars)):
			number = random.randint(1,4)	# 25% chance of replacing each character
			if number == 1 and len(replacements) > 0:
				noOfReplacements += 1
				mainChars[i] = random.choice(replacements)
				replacements.remove(mainChars[i])
		mainChars = sorted(mainChars, key = lambda x: party[x][1])

		# If Dekar/Guy not in party, capsule monster and some item chances change
		dekarInParty = 'Dekar' in mainChars
		guyInParty = 'Guy' in mainChars
		items = create_item_pool(dekarInParty, guyInParty)

		result.append('Signups are now closed! The item pool for this game is: '
						+ item_pool_grammar_fix(items))

		# Create item slots for party characters, then equip them from the item pool
		unequippedChars = create_characters(mainChars)
		equippedChars = equip_items(unequippedChars, items, mainChars)

		# Then add a random capsule monster to the party after equipping is done.
		if dekarInParty == False:
			if guyInParty == True:
				partyLevel = 'Level 37'	# You'd grind more on the way to the Jelly
				capsuleLevel = 'Level 34'
				# Blaze and Flash are useless, omit them if Dekar not in party
				capsuleMonster = random.choice(['Sully', 'Darbi', 'Gusto', 'Zeppy', 'Foomy'])
			else:	# Without both Dekar and Guy you'd grind heaps
				partyLevel = 'Level 44'
				capsuleLevel = 'Level 39'
				capsuleMonster = random.choice(['Sully', 'Darbi'])
		else:
			capsuleMonster = random.choice(list(capsuleMonstersDict))
		# Put capsule monster at the right spot in the queue
		position = random.choice(capsuleMonstersDict[capsuleMonster]['Position'])
		mainChars.insert(position, capsuleMonster)

		# Player <-> Character translation
		playerList = players
		playerDict = {}

		for char in mainChars:
			player = random.choice(playerList)
			playerList.remove(player)
			if player == 'blank player':
				playerDict[char] = char
			else:
				playerDict[char] = player[0].upper() + player[1:]

		string = 'The party for this game is: '
		for i in range(len(mainChars)):
			char = mainChars[i]
			player = playerDict[char]
			string = (string
				+ (char + ' (Self' if player == char else player + ' (' + char))
			if char in equippedChars.keys():
				gear = [equippedChars[char][j] for j in equippedChars[char].keys()
						if equippedChars[char][j] not in [None, 'Default']]
				string = (string
					+ (': ' + ', '.join(gear) if gear else ': No special equipment'))
			string = string + '), '
			if i == 3:
				string = string[:-2] + ' and '
		result.append(string[:-2] + '.')

		# Script to write the battle to the 'results' list
		jellyHP = 9980
		trickUsed = False
		i = 1
		while i <= 3:
			result.append('Jelly ({} HP): {}' \
						.format(
							str(jellyHP),
							jellySayings['Normal Saying'][i-1]
						))
			for char in mainChars:
				if jellyHP > 0:
					if char in party.keys():
						action = party[char][0](
							char, equippedChars[char],
							i, jellyHP, mainChars,
							partyLevel, trickUsed
							)
					# The party dict doesn't contain capsule monsters
					else:
						action = capsule(char, capsuleMonstersDict[char], capsuleLevel)

					try:
						char, attack, dmgType, [dmgMin, dmgMax, noOfAttacks] = action
					except ValueError:
						print('an error has occured.')

					if dmgType == 'Frac':
						damage = int(jellyHP * random.uniform(dmgMin, dmgMax))
					else:
						damage = sum([random.randint(dmgMin, dmgMax) for x in range(noOfAttacks)])
					if attack == 'Trick':
						trickUsed = True
					# Trick only affects physical damage and non capsule monsters
					if trickUsed == True and dmgType == 'Dmg' and char in party.keys():
						if attack in ['Sky Splitter', 'Deep Freeze', 'Sizzle']:
							# A cheap way of dealing with approx. half attack/spell damage
							damage = int(damage * 1.1)
						else:
							damage = int(damage * 1.2)
					if attack == 'Attack' and char in party.keys() \
					and equippedChars[char]['Weapon'] in [
														'Dekar Blade', 'Fry Sword',
														'Sky Sword', 'Snow Sword',
														'Mega Ax'
														]:
						if random.randint(1, 100) <= 10:
							attack = 'Critical'
							damage = int(damage * 2) # damage here is also boosted by Trick

					jellyHP -= damage

					# Player / casts Blah /, hitting the Jelly for 238 damage /!
					result.append(playerDict[char] +
						(' attacks' if attack == 'Attack'
							else ' attacks (critical hit)' if attack == 'Critical'
							else ' casts ' + attack if dmgType == 'Spell'
							else ' casts ' + attack + ', increasing physical damage by 20%' if attack == 'Trick'
							else ' ' + attack if attack in ['tries to run', 'defends', 'proudly defends', 'DEFENDS!']
							else ' ' + attack + ' your party' if attack in ['uselessly restores', 'uselessly heals']
							else ' uses ' + attack)
						+ (', ' + random.choice(jellySayings['Hit']) + ' ' + str(damage) + ' damage' if damage > 0 else '') + '!')
				if jellyHP <= 0:
					result.append('Jelly: ' + random.choice(jellySayings['Death']))
					result.append('The Jelly turns into ' + random.choice(jellySayings['Trophy']) \
						+ ' Thanks for playing!')
					i = 4
					# For testing, see jelly_test.py
					testResult = [True, noOfReplacements, dekarInParty, guyInParty]
					break

			i += 1
		if 	jellyHP > 0:
			saying = (
				'Taunt2500' if jellyHP >= 2500
				else 'Taunt400' if jellyHP <= 400
				else 'Taunt'
				)
			result.append(
				'Jelly ({} HP): {}' \
				.format(jellyHP, random.choice(jellySayings[saying]))
				)
			result.append(
				'The Jelly escapes, '
				+ random.choice(jellySayings['Escape'])
				+ ' The Jelly game can be played again in about '
				+ '25 minutes, thanks for playing!'
				)
			# For testing
			testResult = [False, noOfReplacements, dekarInParty, guyInParty]

		# The battle plays out with too many messages, let's make a new list that
		# combines some messages so that the story is less cluttered
		compactResult = []
		for line in result[:3]:
			compactResult.append(line)
		string = ''
		count = 0
		for line in result[3:]:
			if line[:5] == 'Jelly':
				if len(string) > 0:
					compactResult.append(string)
					count = 0
					string = ''
				compactResult.append(line)
			else:
				string = string + line + ' '
				count += 1
			if count == 3:
				compactResult.append(string)
				count = 0
				string = ''
		compactResult.append(string)

		# Two files refer to this - run.py will want the game result
		# test.py wants whether the game wins or loses (plus a couple other stats)
		if testing == True:
			return testResult
		else:
			if jellyHP <= 0:
				write_to_jelly_kill(
					playersToWrite,
					1 if dekarInParty == False else 0,
					1 if dekarInParty == False and guyInParty == False else 0
					)
			else:
				if len(playersToWrite) > 0:
					Jelly_WallofShame.jelly_wall_of_shame(
						result[1][28:],
						jellyHP,
						toGoogleSheets = googleSheets
						)
			return compactResult

	# Return (kills, kills w/o Dekar, kills w/o Dekar/Guy)
	# and rank of player in Jelly game
	def rank(self, lst):
		with open('games/Jelly_Kills.txt', 'r') as f:
			st = ''
			score = 1000000000000000 # Arbitary large number, overwritten immediately
			position = 1
			entries = 1
			usersReturned = 0

			for line in f:
				line = line.strip().split()
				person, kills, killsWithoutDekar, killsWithoutDekarAndGuy = line
				userScore = (
					(int(kills) * 1000000)
					+ (int(killsWithoutDekar) * 1000)
					+ int(killsWithoutDekarAndGuy)
					)
				killStats = '{}/{}/{}' \
				.format(
					kills,
					killsWithoutDekar,
					killsWithoutDekarAndGuy
				)
				if userScore < score:
					score = userScore
					# only change the position if the score is different
					# to the # of entries checked so far
					position = entries
				if person in lst: 		# if we find the user, return that user
					st = '{}{}: Rank {} - {}{}' \
					.format(
						st,
						person.capitalize(),
						position,
						killStats,
						(' (Jelly kills/Without Dekar/Without Dekar or Guy), ' if usersReturned == 0 else ', ')
					)
					lst.remove(person)
					usersReturned += 1
				#if usersReturned == 5:	# uncomment if people are spamming this command
					#return(st[:-2] + '.')
				entries += 1

			if lst:	# only sends if users don't have a ranking in Jelly_Kills.txt
				st = st[:-2] + '. No jelly rank exists for ' # replaces ',' with sentence
				for person in lst:
					st = st + person.capitalize() + ', '
		return(st[:-2] + '.')


# 1 - Empty character dict
# Default weapon / Dragon spell / empty rock (and armor) slots if desired
def create_characters(party):
	characterDict = {}
	trickTest = random.random()
	for char in party:
		characterDict[char] = {
						'Weapon': 'Default',
						'Spell': 'Dragon',	# Dekar or Guy never cast spells
						'Armor': None,
						'Rock': None
		}
		# Assign Trick to characters if they can learn it
		if char in ['Lexis', 'Maxim', 'Selan', 'Tia', 'Arty']:
			characterDict[char]['Trick'] = None
			if trickTest <= 0.25:
				characterDict[char]['Trick'] = 'Trick'
		# Remove spell slot from Dekar and Guy. Easier to do it like this for now
		if char in ['Dekar', 'Guy']:
			characterDict[char].pop('Spell', None)
	return characterDict

# 2 - Randomly generate item pool that you find during an AC playthrough
def create_item_pool(d, g):
	# Create item pool, starting with weapons, then rocks
	itemPool = []
	for weapon in weaponDict.keys():
		maxItems = weaponDict[weapon][2]
		chance = weaponDict[weapon][3]
		# increase odds of some items if Dekar isn't in the party
		if d == False:
			if weapon in ['Lizard Blow', 'Deadly Rod']:
				maxItems += 1
				chance = 0.50
			if weapon == 'Snow Sword':
				change = 0.50
			if weapon in ['Cancer Rock', 'Hidora Rock', 'Gorgon Rock']:
				maxItems = 2
				chance = 0.30

		noOfItems = 0
		for n in range(0, maxItems):
			if random.random() <= chance:
				noOfItems += 1
		if noOfItems > 0:
			itemPool= itemPool + [weapon] * noOfItems

	itemPool = sorted(itemPool[:])
	rocks = [i for i in itemPool if i.find('Rock') != -1]
	for rock in rocks:
		itemPool.remove(rock)
	itemPool = itemPool[:] + rocks
	# Add in spells to the end of itemPool
	itemPool.append('Dragon')
	for spell in magicDict.keys():
		if random.random() >= 0.5 and spell != 'Dragon':
			itemPool.append(spell)
	return itemPool

# Fix printout of items later to the game
def item_pool_grammar_fix(itemList):
	s = ''
	setList = [
		i for i in sorted(set(itemList), key = itemList.index)
		if i not in ['Ice Valk', 'Firebird', 'Zap', 'Thunder', 'Dragon', 'Fry']
	]
	if len(setList) == 0:
		return 'Nothing!! Hahahahaha!'
	if len(setList) == 1:
		return setList[0] + '.'
	for i in setList:
		s = (s + (str(itemList.count(i)) + ' ' if itemList.count(i) > 1 else '')
			+ i
			+ ('s, ' if itemList.count(i) > 1 else ', '))
	if len(s) == 0:
		return 'Nothing!! Hahahahaha!'
	s = s[:-2] + '.'
	s = s[:s.rfind(',')] + ' and' + s[s.rfind(',') + 1:]
	return s

# Swap two players' items around
# Currently only limited to weapons and rocks (No armor present)
def swap_items(d, party, p1, weapon1, rock1, p2, weapon2, rock2):
	if (p1 in party and p2 in party
			and d[p1]['Weapon'] == weapon1
			and d[p2]['Weapon'] == weapon2
			and d[p1]['Rock'] == rock1
			and d[p2]['Rock'] == rock2):
		d[p1]['Weapon'], d[p2]['Weapon'] = d[p2]['Weapon'], d[p1]['Weapon']
		d[p1]['Rock'], d[p2]['Rock'] = d[p2]['Rock'], d[p1]['Rock']

# 3 - Assign weapons, rocks and then spells to characters.
# This can get convoluted, as you want the optimal gear AS A PARTY
def equip_items(d, pool, party):	# d = the player equipment dictionary
	equippedItems = []
	# Equip weapons first, force equipping to be done in a particular order
	for char in ['Dekar', 'Guy', 'Maxim', 'Arty', 'Selan', 'Tia', 'Lexis']:
		if char in party:
			for equippableItem in weaponEquipDict[char]:
				# only want the strongest weapon, so loop breaks once equipped,
				# the loop cycles through these items from strongest to weakest
				if equippableItem in pool:
					d[char]['Weapon'] = equippableItem
					pool.remove(equippableItem)
					equippedItems.append(equippableItem)
					# Cancer Rocks go well with Old Swords
					if equippableItem == 'Old Sword' and 'Cancer Rock' in pool:
						d[char]['Rock'] = 'Cancer Rock'
						pool.remove('Cancer Rock')
						equippedItems.append('Cancer Rock')
					break

			# Might as well set the spells as well
			for useableSpell in spellUseList[char]:
				# only want the strongest spell for each character here too
				if (useableSpell in pool
						and char not in ['Guy', 'Dekar']
						and d[char]['Spell'] == 'Dragon'):
					d[char]['Spell'] = useableSpell
					break

	# Equip Armor (If any, might not be bothered doing this, it's a lot of work)
	# pass

	# Remove spells from the pool just for aesthetics
	for spell in ['Ice Valk', 'Firebird', 'Thunder', 'Zap', 'Dragon']:
		if spell in pool:
			pool.remove(spell)

	### Update weapons in special circumstances
	# Maxim normally prefers the Deadly/Old Swords, but should equip Sky sword
	# if there are too many fractional damage items equipped
	if ('Maxim' in party
		and d['Maxim']['Weapon'] in ['Deadly Sword', 'Old Sword']
		and 'Sky Sword' in pool
		and d['Maxim']['Rock'] != 'Cancer Rock'):
		maximsWeapon = d['Maxim']['Weapon']
		countSky = 0
		for item in ['Dekar Blade', 'Myth Blade']:	# Dekar/Guy have good stuff
			if item in equippedItems:
				countSky += 1
		# 3rd member (not Maxim) has fractional item, swap for damage item
		if 'Deadly Rod' in equippedItems or 'Gorgon Rock' in equippedItems:
			countSky += 1
		if countSky >= 3:
			d['Maxim']['Weapon'] = 'Sky Sword'
			pool.remove('Sky Sword')
			equippedItems.remove(maximsWeapon)
			pool.append(maximsWeapon)

	# Sometimes Maxim won't have an item but Guy/Dekar have equipment choices
	if 'Maxim' in party	and d['Maxim']['Weapon'] == 'Default' and d['Maxim']['Rock'] == None:
		itemCheck = []
		for item in ['Mega Ax', 'Fry Sword']: # Mega Ax is stronger
			if item in pool:
				itemCheck.append(item)

		guyDekarCheck = []
		# Prioritise Guy as he has the weaker fractional weapon out of Dekar/Guy
		for person in ['Guy', 'Dekar']:
			if person in party:
				guyDekarCheck.append(person)

		# There is a scenario where its better to have a Frac weapon on Maxim
		# and Dmg items on Dekar / Guy, if they are both in the party
		if (len(guyDekarCheck) == 2
				and 'Fry Sword' in pool
				and d['Guy']['Weapon'] == 'Mega Ax'
				and d['Dekar']['Weapon'] in ['Myth Blade', 'Old Sword']):
			for weapon in ['Myth Blade', 'Old Sword']:
				if d['Dekar']['Weapon'] == weapon:
					d['Dekar']['Weapon'] = 'Mega Ax' # Dekar gets the stronger weapon
					d['Guy']['Weapon'] = 'Fry Sword'
					d['Maxim']['Weapon'] = weapon
					pool.remove('Fry Sword')
					guyDekarCheck = []	# cheesy way to stop second scenario from happening
					if weapon == 'Old Sword' and d['Dekar']['Rock'] == 'Cancer Rock':
						d['Maxim']['Rock'] = 'Cancer Rock'
						d['Dekar']['Rock'] = None

		# If Guy OR Dekar has Myth blade or Old Sword (and/or Cancer Rock),
		# Maxim has both no weapon or rock and there is a Mega Ax or Fry Sword
		# left over, rotate equipment and give Guy's stuff to Maxim
		if len(itemCheck) > 0 and len(guyDekarCheck) > 0:
			item = itemCheck[0]
			dude = guyDekarCheck[0]
			for weapon in ['Myth Blade', 'Old Sword']:
				if d[dude]['Weapon'] == weapon:
					d[dude]['Weapon'] = item
					d['Maxim']['Weapon'] = weapon
					pool.remove(item)
					equippedItems.append(item)
				if weapon == 'Old Sword' and d[dude]['Rock'] == 'Cancer Rock':
					d[dude]['Rock'] = None
					d['Maxim']['Rock'] = 'Cancer Rock'
	# Swap gear in certain situations to optimise damage dealt
	# Very small optimisations only - 10 - 20 damage over course of battle
	# swap_items(d, party, player1, weapon1, rock1, player2, weapon2, rock2)
	swap_items(d, party, 'Maxim', 'Old Sword', 'Cancer Rock', 'Guy', 'Myth Blade', None)
	swap_items(d, party, 'Dekar', 'Lizard Blow', None, 'Guy', 'Sky Sword', 'Hidora Rock')
	swap_items(d, party, 'Arty', 'Deadly Rod', None, 'Selan', 'Default', None)
	swap_items(d, party, 'Arty', 'Deadly Rod', None, 'Tia', 'Default', None)
	swap_items(d, party, 'Arty', 'Deadly Rod', None, 'Tia', 'Lizard Blow', None)
	swap_items(d, party, 'Arty', 'Deadly Rod', None, 'Selan', 'Lizard Blow', None)
	swap_items(d, party, 'Selan', 'Deadly Rod', None, 'Tia', 'Lizard Blow', None)

	# Equip Rocks
	# Equip Arty / Selan / Tia  with a Gorgon Rock first as their choices are limited
	# The strongest relevant character will then get Cancer Rock or Hidora Rock.
	for char in ['Arty', 'Selan', 'Tia', 'Dekar', 'Guy', 'Maxim', 'Lexis']:
		if char in party and d[char]['Weapon'] == 'Default' and 'Gorgon Rock' in pool:
			d[char]['Rock'] = 'Gorgon Rock'
			pool.remove('Gorgon Rock')
			equippedItems.append('Gorgon Rock')
		# Equip the others. Preference - Hidora (boosts ATP)  -> Cancer
		# (all Old Sword + Cancer Rock combos are equipped by now)
		# I have NOT boosted the ATP of characters with Hidora rocks equipped yet.
		elif char in ['Dekar', 'Guy', 'Maxim', 'Lexis']:
			if char in party and d[char]['Weapon'] in [
														'Mega Ax', 'Sky Sword',
														'Fry Sword', 'Default'
														]:
				if 'Hidora Rock' in pool:
					d[char]['Rock'] = 'Hidora Rock'
					pool.remove('Hidora Rock')
					equippedItems.append('Hidora Rock')
				elif 'Cancer Rock' in pool:
					d[char]['Rock'] = 'Cancer Rock'
					pool.remove('Cancer Rock')
					equippedItems.append('Cancer Rock')

	# If everyone has fractional items and we have reject% members,
	# Equip a reject% member with a Lizard Blow if there is one.
	# Do this in the order Selan, Tia
	# No point checking for Gorgon Rock as this means no LBs available anyway
	if any(x in party for x in ['Arty', 'Selan', 'Tia']):
		fractionalChecker = 0
		for char in party:
			if d[char]['Weapon'] in [
									'Myth Blade', 'Dekar Blade',
									'Deadly Rod', 'Deadly Sword',
									'Old Sword'
									]:
				fractionalChecker += 1
		# check/equip Lizard Blows if everyone has fractionals
		if fractionalChecker == 4 and 'Lizard Blow' in pool:
			for char in ['Arty', 'Selan', 'Tia']:
				if char in party and fractionalChecker == 4:
					pool.append(d[char]['Weapon'])
					equippedItems.remove(d[char]['Weapon'])
					d[char]['Weapon'] = 'Lizard Blow'
					pool.remove('Lizard Blow')
					equippedItems.append('Lizard Blow')
					fractionalChecker = 3	# break loop
	return d



# 5 - Determine damage values used for all attacks in game (next 2 functions)
def damage_calc(c, item, level, attribute):
	if attribute == 'STR':
		basePOW = defaultAttackDict[item][0] + party[c][2][level]['STR']
		boost = 1/4.
	if attribute == 'INT':
		basePOW = magicDict[item] + party[c][2][level]['INT']
		boost = 1/8. # Spells have different damage variance than attacks
	minDmg = math.floor(basePOW * 0.5)
	maxDmg = math.floor(basePOW * (1. + boost) * 0.5)
	return [minDmg, maxDmg]

# weaponDict damage ranges require info from either a list (fractional damage),
# integer (multiple attacks) or string (spell)
# The damage fn returns correct location of [minDmg, maxDmg] list from weaponDict
def damage(c, item, level, attack = False, attackWeapon = None):
	if item in ['Firebird', 'Dragon', 'Ice Valk', 'Thunder', 'Zap']: # Spells
		return damage_calc(c, item, level, 'INT') + [1]
	if attack == True:	# One normal attack
		return damage_calc(c, item, level, 'STR') + [1]

	# Special Attacks, these can be one of 3 categories.
	# The weaponDict uses different built in types to distinguish these
	damageInfo = weaponDict[item][1]

	# Fractional Attack, damage already known
	if isinstance(damageInfo, list):
		return damageInfo + [1]
	# Multiple attack damage, return base attack * no of attacks
	elif isinstance(damageInfo, int):
		if item in ['Cancer Rock', 'Hidora Rock']:
			item = attackWeapon
		return damage_calc(c, item, level, 'STR') + [damageInfo]
	# Attack + Spell, e.g. Sky Sword attacks + Casts Thunder on enemies
	elif isinstance(damageInfo, str):
		attackDamage = damage_calc(c, item, level, 'STR')
		spellDamage = damage_calc(c, damageInfo, level, 'INT')
		totalDamage = [x + y for x, y in zip(attackDamage, spellDamage)]
		return totalDamage + [1]
	else:
		print('An error has happened with ' + c + ' using ' + item + '.')
		return [1,1]

def capsule(monster, monsterDict, level):
	n = random.randint(1, 100)
	if n > 70:		# 30% chance of an attack
		action = 'Attack'
		baseATP = monsterDict[level]['ATP']
		multiplier = 1/2.
		boost = 1/4.
	else:
		action = random.choice(list(monsterDict['Specials']))
		damageType, multiplier = monsterDict['Specials'][action]
		baseATP = monsterDict[level][damageType]
		# capsule spell damage calc is different to party spell damage lol
		if damageType == 'INT':
			multiplier = multiplier * 5/8.
			boost = 1/8.
		else:
			multiplier = multiplier * 0.5
			boost = 1/4.
	minDmg = math.floor(baseATP * multiplier)
	maxDmg = math.floor(baseATP * multiplier * (1 + boost))
	return [monster, action, 'Dmg', [minDmg, maxDmg, 1]]

# 7 - Update Jelly Kill register if party wins
# d = 1 if Dekar not the party, else 0, same for dg (dekar and guy not in party)
def write_to_jelly_kill(players, d, dg):
	with open('games/Jelly_Kills.txt', 'r') as f:
		jellydata = [line.strip().split() for line in f]
	# print(jelly data, update players already in the list)
	for i in range(len(jellydata)):
		line = jellydata[i]
		# line = [player, kills, killsWithoutDekar, killsWithoutDekarAndGuy]
		if line[0] in players:
			line[1] = str(int(line[1]) + 1)
			line[2] = str(int(line[2]) + d)
			line[3] = str(int(line[3]) + dg)

	for player in players: # add new players to jellydata
		if player not in [i[0] for i in jellydata]:
			jellydata.append([player, '1', str(d), str(dg)])

	with open('games/Jelly_Kills.txt', 'w') as f:
		# Sort based on level, see above comment for line description
		for line in sorted(
				jellydata,
				key = lambda x: (int(x[1]), int(x[2]), int(x[3])),
				reverse = True):
			f.write(line[0] + ' ' + line[1] + ' ' + line[2] + ' ' + line[3] + '\n')

# 4 - Attack scripts for party members and capsule monsters (done collectively)
# {chardict = {'Armor': etc, 'Weapon': etc, 'Spell': etc, 'Rock': etc}}
def Dekar(c, charDict, n, hp, team, level, trickUsed):
	char = charDict	# Not sure why I did this, for ease of typing?
	weapon, rock, armor = char['Weapon'], char['Rock'], char['Armor']

	if n == 1:
		if weapon in ['Dekar Blade', 'Myth Blade', 'Old Sword']:
			return [c, weaponDict[weapon][0], 'Frac', damage(c, weapon, level)]
		elif rock == 'Gorgon Rock':
			return [c, weaponDict[rock][0], 'Frac', damage(c, rock, level)]
		else:
			return [c, 'Attack', 'Dmg', damage(c, weapon, level, attack=True)]
	elif n == 2:
		if rock == 'Cancer Rock':
			return [c, weaponDict[rock][0], 'Dmg', damage(c, rock, level, attackWeapon=weapon)]
		else:
			return [c, 'Attack', 'Dmg', damage(c, weapon, level, attack=True)]
	elif n == 3:
		if weapon in ['Fry Sword', 'Sky Sword', 'Lizard Blow', 'Gades Blade'] \
		and rock not in ['Hidora Rock', 'Cancer Rock']:
			return [c, weaponDict[weapon][0], 'Dmg', damage(c, weapon, level)]
		elif (rock == 'Cancer Rock' and weapon != 'Old Sword') or rock == 'Hidora Rock':
			return [c, weaponDict[rock][0], 'Dmg', damage(c, rock, level, attackWeapon=weapon)]
		else:
			return [c, 'Attack', 'Dmg', damage(c, weapon, level, attack=True)]

# Same script. Guy can't equip the Dekar blade, so no problem there
def Guy(c, chardict, n, hp, team, level, trickUsed):
	return Dekar(c, chardict, n, hp, team, level, trickUsed)

def Lexis(c, chardict, n, hp, team, level, trickUsed):
	char = chardict
	weapon, rock, spell, armor = char['Weapon'], char['Rock'], char['Spell'], char['Armor']

	if n == 1:
		if rock == 'Gorgon Rock':
			return [c, weaponDict[rock][0], 'Frac', damage(c, rock, level)]
		elif char['Trick'] == 'Trick' and trickUsed == False \
		and sum(team.count(i) for i in ['Guy', 'Dekar', 'Maxim']) >= 2:
			return [c, 'Trick', 'Trick', [0, 0, 1]]
		else:
			return [c, spell, 'Spell', damage(c, spell, level)]
	elif n == 2:
		if rock == 'Cancer Rock':
			return [c, weaponDict[rock][0], 'Dmg', damage(c, rock, level, attackWeapon=weapon)]
		elif char['Trick'] == 'Trick' and trickUsed == False \
		and sum(team.count(i) for i in ['Guy', 'Dekar', 'Maxim']) >= 2:
			return [c, 'Trick', 'Trick', [0, 0, 1]]
		else:
			return [c, spell, 'Spell', damage(c, spell, level)]
	elif n == 3:
		if weapon == 'Lizard Blow' and rock not in ['Cancer Rock', 'Hidora Rock']:
			return [c, weaponDict[weapon][0], 'Dmg', damage(c, weapon, level)]
		elif rock in ['Cancer Rock', 'Hidora Rock']:
			return [c, weaponDict[rock][0], 'Dmg', damage(c, rock, level, attackWeapon=weapon)]
		else:
			return [c, spell, 'Spell', damage(c, spell, level)]

def Maxim(c, chardict, n, hp, team, level, trickUsed):
	char = chardict
	weapon, rock, spell, armor = char['Weapon'], char['Rock'], char['Spell'], char['Armor']
	if n == 1:
		if weapon in ['Myth Blade', 'Old Sword', 'Deadly Sword']:
			return [c, weaponDict[weapon][0], 'Frac', damage(c, weapon, level)]
		elif rock == 'Gorgon Rock':
			return [c, weaponDict[rock][0], 'Frac', damage(c, rock, level)]
		elif char['Trick'] == 'Trick' and trickUsed == False \
		and sum(team.count(i) for i in ['Guy', 'Dekar', 'Maxim']) >= 2:
			return [c, 'Trick', 'Trick', [0, 0, 1]]
		elif weapon in ['Myth Blade', 'Old Sword', 'Lizard Blow', 'Sky Sword'] \
		or (weapon == 'Default' and trickUsed == True):
			return [c, 'Attack', 'Dmg', damage(c, weapon, level, attack=True)]
		else:
			return [c, spell, 'Spell', damage(c, spell, level)]
	elif n == 2:
		if (weapon in ['Myth Blade', 'Old Sword', 'Lizard Blow', 'Sky Sword']
				and rock not in ['Cancer Rock', 'Hidora Rock']):
			return [c, 'Attack', 'Dmg', damage(c, weapon, level, attack=True)]
		elif rock == 'Cancer Rock':
			return [c, weaponDict[rock][0], 'Dmg', damage(c, rock, level, attackWeapon=weapon)]
		elif char['Trick'] == 'Trick' and trickUsed == False \
		and sum(team.count(i) for i in ['Guy', 'Dekar', 'Maxim']) >= 2:
			return [c, 'Trick', 'Trick', [0, 0, 1]]
		elif weapon == 'Default' and trickUsed == True:
			return [c, 'Attack', 'Dmg', damage(c, weapon, level, attack=True)]
		else:
			return [c, spell, 'Spell', damage(c, spell, level)]
	elif n == 3:
		if weapon in ['Lizard Blow', 'Sky Sword'] and rock not in ['Cancer Rock', 'Hidora Rock']:
			return [c, weaponDict[weapon][0], 'Dmg', damage(c, weapon, level)]
		elif (rock == 'Cancer Rock' and weapon != 'Old Sword') or rock == 'Hidora Rock':
			return [c, weaponDict[rock][0], 'Dmg', damage(c, rock, level, attackWeapon=weapon)]
		elif weapon in ['Myth Blade', 'Old Sword', 'Lizard Blow'] \
		or (weapon == 'Default' and trickUsed == True):
			return [c, 'Attack', 'Dmg', damage(c, weapon, level, attack=True)]
		else:
			return [c, spell, 'Spell', damage(c, spell, level)]

def Selan(c, chardict, n, hp, team, level, trickUsed):
	char = chardict
	weapon, rock, spell, armor = char['Weapon'], char['Rock'], char['Spell'], char['Armor']
	if n == 1:
		if weapon == 'Deadly Rod':
			return [c, weaponDict[weapon][0], 'Frac', damage(c, weapon, level)]
		elif rock == 'Gorgon Rock':
			return [c, weaponDict[rock][0], 'Frac', damage(c, rock, level)]
		elif (char['Trick'] == 'Trick'
				and trickUsed == False
				and sum(team.count(i) for i in ['Guy', 'Dekar', 'Maxim']) >= 2):
			return [c, 'Trick', 'Trick', [0, 0, 1]]
		else:
			return [c, spell, 'Spell', damage(c, spell, level)]
	elif n == 2:
		# Take into account Spell damage as an alternative to
		# using the Deadly Rod here, in case Jelly has low HP.
		if weapon == 'Deadly Rod' \
		and hp > ((damage(c, spell, level)[0] + damage(c, spell, level)[1])
				/ (weaponDict['Deadly Rod'][1][0] + weaponDict['Deadly Rod'][1][1])):
			return [c, weaponDict[weapon][0], 'Frac', damage(c, weapon, level)]
		elif char['Trick'] == 'Trick' and trickUsed == False \
		and sum(team.count(i) for i in ['Guy', 'Dekar', 'Maxim']) >= 2:
			return [c, 'Trick', 'Trick', [0, 0, 1]]
		else:
			return [c, spell, 'Spell', damage(c, spell, level)]
	elif n == 3:
		if weapon == 'Deadly Rod' \
		and hp > ((damage(c, spell, level)[0] + damage(c, spell, level)[1])
				/ (weaponDict['Deadly Rod'][1][0] + weaponDict['Deadly Rod'][1][1])):
			return [c, weaponDict[weapon][0], 'Frac', damage(c, weapon, level)]
		elif weapon in ['Lizard Blow', 'Snow Sword']:
			return [c, weaponDict[weapon][0], 'Dmg', damage(c, weapon, level)]
		else:
			return [c, spell, 'Spell', damage(c, spell, level)]

# Same script as Selan but won't equip Snow Sword
def Tia(c, chardict, n, hp, team, level, trickUsed):
	return Selan(c, chardict, n, hp, team, level, trickUsed)
# Same script as Selan but cannot equip Snow Sword
def Arty(c, chardict, n, hp, team, level, trickUsed):
	return Selan(c, chardict, n, hp, team, level, trickUsed)


# Party Agilities and function reference list
# Since Trick uses this list, this list must not contain capsule monsters
party = {
	'Arty': [Arty, 1, {
			'Level 30': {'STR': 55, 'INT': 150},
			'Level 37': {'STR': 97, 'INT': 159},
			'Level 44': {'STR': 162, 'INT': 162}
	}],
	'Dekar': [Dekar, 7, {
			'Level 30': {'STR': 270, 'INT': 20},
			'Level 37': {'STR': 300, 'INT': 21},
			'Level 44': {'STR': 323, 'INT': 22}
	}],
	'Guy': [Guy, 6, {
			'Level 30': {'STR': 175, 'INT': 48},
			'Level 37': {'STR': 201, 'INT': 63},
			'Level 44': {'STR': 228, 'INT': 76}
	}],
	'Lexis': [Lexis, 4, {
			'Level 30': {'STR': 101, 'INT': 197},
			'Level 37': {'STR': 134, 'INT': 229},
			'Level 44': {'STR': 168, 'INT': 260}
	}],
	'Maxim': [Maxim, 5, {
			'Level 30': {'STR': 132, 'INT': 57},
			'Level 37': {'STR': 160, 'INT': 72},
			'Level 44': {'STR': 189, 'INT': 88}
	}],
	'Selan': [Selan, 3, {
			'Level 30': {'STR': 96, 'INT': 150},
			'Level 37': {'STR': 106, 'INT': 173},
			'Level 44': {'STR': 115, 'INT': 200}
	}],
	'Tia': [Tia, 2, {
			'Level 30': {'STR': 60, 'INT': 130},
			'Level 37': {'STR': 70, 'INT': 139},
			'Level 44': {'STR': 79, 'INT': 156}
	}]
}


if __name__ == "__main__":
	# set second argument to True if you want to do testing
	# see Jelly_test.py for test results
	# attempt = results([], googleSheets = False)
	# for line in attempt:
	# 	print(line)
	pass
