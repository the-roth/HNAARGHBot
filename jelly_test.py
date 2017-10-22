"""
Created on Mar 12, 2017

@author: the_roth

Test the win rates with combinations of Dekar and Guy either in or out of
the party.
"""


from games.Jelly import Jelly

testGame = Jelly()
testGame.initialize_game()
testGame._player_list = []

#_______________________________________________________________________________
"""
The loop_printout function prints:
	A list of the # of games played with 0, 1, 2 or 3 replacements
	A list of the wins in these Games
	Printouts of the % win rates with Y not in party and X replacements
"""
def loop_printout(lst, lstWins, start, s1, s2):
	print(lst)
	print(lstWins)
	for i in range(start, len(lst)):
		if lst[i] > 0:
			print(printout(s1, i, s2, lstWins[i], lst[i]))
	print(' ')

def printout(s1, s2, s3, s4, s5):
	return('{}{}{}{}'.format(s1, s2, s3, round(s4 * 1.0 / s5, 4)))

k = 1
wins = 0

# no of chars replaced
replaced = [0, 0, 0, 0]
replacedWins = [0, 0, 0, 0]

# if Dekar is in the party
dekar = [0,0,0,0]
dekarWins = [0,0,0,0]

# if Dekar is not in party
replacedDekar = [0,0,0,0]
replacedDekarWins = [0,0,0,0]

# If Dekar AND Guy not in party
replacedDekarAndGuy = [0,0,0,0]
replacedDekarAndGuyWins = [0,0,0,0]

while k <= 100000:
	test = testGame.results(testing = True, googleSheets = False)
	testResult, noCharsReplaced, isDekarIn, isGuyIn = test

	isWin = int(testResult == True)

	wins += isWin
	replacedWins[noCharsReplaced] += isWin
	replaced[noCharsReplaced] += 1

	if isDekarIn == True:
		dekarWins[noCharsReplaced] += isWin
		dekar[noCharsReplaced] += 1
	else:
		if isGuyIn == True:
			replacedDekarWins[noCharsReplaced] += isWin
			replacedDekar[noCharsReplaced] += 1
		else:
			replacedDekarAndGuyWins[noCharsReplaced] += isWin
			replacedDekarAndGuy[noCharsReplaced] += 1
	k += 1

print('Number of Games won = ' + str(wins) + ' / ' + str(k - 1) + '\n')

loop_printout(
	replaced, replacedWins, 0,
	'Number of replacements = ', ': '
	)
loop_printout(
	dekar, dekarWins, 1,
	'Dekar in party and ', ' replacements win rate: '
	)
loop_printout(
	replacedDekar, replacedDekarWins,
	 1, 'Dekar not in party, Guy in party and ', ' replacements win rate: '
	 )
loop_printout(
	replacedDekarAndGuy, replacedDekarAndGuyWins, 2,
	'Dekar and Guy not in party and ', ' replacements win rate: '
	)
