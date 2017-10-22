"""
Created on Apr 10, 2017

@author: the_roth
"""

from Config import CHANNEL, WALLOFSHAMEFILE

import gspread
import time
import itertools
from oauth2client.service_account import ServiceAccountCredentials

def jelly_wall_of_shame(game, damage, toGoogleSheets = False):

	with open('games/Jelly_WallofShame.txt', 'r') as f:
		shame_list = []
		for line in f:
			shame_list.append(line[:-1].split('.'))	# without the '\n' character
	f.close()

	# We will keep only the below line for when uploading to Google Sheets if we desire.
	result = game.replace(' and ', ', ').replace('), ', ').') + str(damage)

	shame_list.append(result.split('.'))
	shame_list = sorted(shame_list, key = lambda x: int(x[-1]), reverse = True)[:50]
	with open('games/Jelly_WallofShame.txt', 'w') as f:
		for line in shame_list:
			f.write('.'.join(line) + '\n')

	# Writing to Spreadsheet time! Please see http://bit.ly/2xvKrZM for the Jelly Wall of Shame
	if toGoogleSheets == True:
		# Connect to Google Spreadsheet containing the Wall of Shame information
		json_key = WALLOFSHAMEFILE
		scope = ['https://spreadsheets.google.com/feeds']
		credentials = ServiceAccountCredentials.from_json_keyfile_name(json_key, scope)

		gc = gspread.authorize(credentials)
		wks = gc.open("Ancient Cave Jelly Bot Game").worksheet("Wall of Shame")

		# Convert the game list (info about Users / characters they were, and the damage remaining on the jelly)
		result = game.replace(' and ', ', ').replace('), ', ').') + str(damage)
		char_list = result.split('.')
		char1, char2, char3, char4, char5, gameHP = char_list

		# Find where the results start in the spreadsheet (in case I modify the sheet a little)
		results_start_row = wks.find("Jelly HP Remaining").row
		results_start_col = wks.find("Jelly HP Remaining").col
		position = 1
		isRowAdded = False
		date = time.strftime("%d %b %Y")

		gameCells = wks.range('A4:I23')

		# Check if it's even needed to update the rows
		twentiethHP = gameCells[-6].value
		if len(twentiethHP) == 0: 	# Check if we actually have 20 results first, as an empty cell is the empty string
			twentiethHP = '0'
		if int(gameHP) <= int(twentiethHP):
			print("Current game doesn't make it to the Wall of Shame.")
			return

		updatedCells = []

		HP = 9999 # Gets overwritten immediately
		currentHP = 9999 # Gets overwritten immediately
		position = 1
		entries = 1
		for i in range(0, 20):
			row = [gameCells[j].value for j in range(9*i, 9*(i + 1))]
			rankHP = row[3] if len(row[3]) > 0 else '0'	# it's a string here, or force it to be 0 HP if cell is empty
			if isRowAdded == False and int(gameHP) > int(rankHP):
				currentHP = int(gameHP)
				if HP > currentHP:
					HP = currentHP
					position = entries
				updatedCells.append([str(position), date, CHANNEL, str(gameHP), char1, char2, char3, char4, char5])
				isRowAdded = True
				entries += 1

			currentHP = int(rankHP)
			if HP > currentHP:
				HP = currentHP
				position = entries
			row[0] = str(position)
			updatedCells.append(row)
			entries += 1
		# update the cells now (could probably do this in the for loop above, but not for now)
		flattenedUpdatedCellList = list(itertools.chain.from_iterable(updatedCells))

		for i in range(0, len(gameCells)):
			# This will ignore the last row as gameCells is only 20 rows, not 21
			gameCells[i].value = flattenedUpdatedCellList[i]

		wks.update_cells(gameCells) # Update in batch

"""
result = "B (Arty: Ice Valk, Gorgon Rock), D (Maxim: Old Sword, Ice Valk), C (Guy: Fry Sword), A (Dekar: Myth Blade) and E (Blaze)."
jelly_wall_of_shame(result, 1966, toGoogleSheets = True)
"""
