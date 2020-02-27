# -*- coding: utf-8 -*-

"""
Created on Fri Jul 13 09:24:51 2018

@author: nick.wardle
"""

# == GLOBAL: SHOW DEBUG MESSAGES? =====================================
debug = True
#debug = False

# Hide specific groups of debug messages, add group number to the list
#group_hide = []
group_hide = [1,2,3]



# == SETTINGS & TEXT STRINGS FOR THE GAME ===================================

# == Input text prefixes

inputQuestionPre = '>> '
inputFeedbackPre = '## '
inputChangeLocPre = '~>> '
errorPre = '!!!- '


# == Input window formatters

shortLnNewLine = '-' * 40 + '\n'


# == UI feedback text

locStarters = ['There\'s', 'You see', 'There is', 'You can see']

locListings = ['And', 'Also', 'Then', 'And there is']

locTerminus = ['And finally', 'And also']

exitMessage = "Exiting game..."

cheaterMessage = ["Cheaters never win!", "Really? That's how you roll?", "I can see you, you know?"]

winningMessage = "\n\nCONGRATULATIONS!!! YOU WIN!!!\n\n"

# == Invalid input feedback text

illegalMove = ["What the hell do you think you're doing?!", "No. Just, no.", "Try again, dumbass...", "That's clearly not right.", "Do you even know what we are trying to do here..?!", "Ok.. Ok.. Look, I'll use small words to explain..", "Oh yeah! Great. Why don't you just roll your face across the keyboard as well..?!"]


# == BOX & LAYOUT ELEMENTS ===============================================

slot_shim = '          '
vertDiv = ' || '
rowDiv = '======================================================'

inventoryTitle = '\n====================  INVENTORY  ====================='
characterTitle = '\n====================  CHARACTER  ====================='