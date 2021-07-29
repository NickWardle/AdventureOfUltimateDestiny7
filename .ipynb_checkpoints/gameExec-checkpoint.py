# -*- coding: utf-8 -*-
#Created on Fri Jul 13 09:24:51 2018

# @author: nick.wardle

import debugger as de
import gameData as gD
import settings as ss
import controllers
import input_parsing as parseInp
import command_handling as doCmd
import errorHandler


# == INITIALISE GAME DATA == ####################################

# initialise GLOBALS
gD.init()

de.bug(1, "allInputRefs", gD.allInputRefs)



# == RENDER FIRST/DEFAULT LOCATION == #############################

# render first/default location
loc = gD.DEFAULTLOC
controllers.changeLoc(loc)

###################################################################
# GAME STATE PLAYING LOOP 
###################################################################


WIN = False

while WIN == False:
    
    # == SET UP THE DATA ARRAYS == ################################

    moveObj = []
    legalMoves = []
    moveDesc = []
    moveDest = []

    # get all MOVES into a list for the location    
    de.bug(1, "current gD.LOCDATA moveCmds is", gD.LOCDATA['moveCmds'])

    for i in gD.LOCDATA['moveCmds']:
        moveObj.append(i)
        
    for m in moveObj:
        for i,j in gD.gameDB['moveCommandsDB'][m].items():
            legalMoves.append(gD.gameDB['moveCommandsDB'][m][i]['cmds'])
        
        
    # get OBJECTS and object 'refs' array for location
    allObjects = []
    tmp = []
    if 'locObjects' in gD.LOCDATA:
        for i in gD.LOCDATA['locObjects']:
            allObjects.append(i)
        objRefs = []
        for i in allObjects:
            for j in gD.gameDB['objectsDB'][i]['refs']:
                objRefs.append(j)
        
    
    # == ALL LEGAL INPUTS == #####################################
    
    # group all LEGALINPUTS into one library to match against
    # as individual 'command' entries

    legalInputsA = {}
    legalInputsB = {}
    legalInputsC = {}
    legalInputs = {}
    
    allLegalMoves = []
    tmp = []
    for i in legalMoves:
        for j in i:
            allLegalMoves.append(j)
    legalInputsA['m'] = allLegalMoves
    legalInputsA['o'] = objRefs
    legalInputsB = gD.gameDB['uiCmds']
    legalInputsC = gD.gameDB['actionCmds']
    gD.LEGALINPUTS = {**legalInputsC, **legalInputsB, **legalInputsA}
    de.bug(1, "legalInputs", gD.LEGALINPUTS)
    
    
    ##############################################################
    ##############################################################
    
    
    # == SET UP DATA == ##########################################
    
    # set DATA package to send with each 'general' UI command
    uiData = {'search':allObjects, 'cheat':legalMoves, 'help':[gD.gameDB['uiCmds'], gD.gameDB['actionCmds']['exploreCmds']], 'exit':'', 'look':''}
    
    
    # == CHECK INPUT ==  BUILD PLAYER PROMPT  == #################
    
    if gD.PROMPT == False: # default input prompt
        prompt = controllers.buildPrompt('default')
        myInput = input(prompt)
    elif gD.PROMPT == 'duplicates': # require more detail for input
        prompt = controllers.buildPrompt('duplicates', gD.INPUT_VARS['THIS_OBJ'])
        myInput = input(prompt)
    elif gD.PROMPT == 'reqconf': # require Y/N reconfirmation
        prompt = controllers.buildPrompt('did you mean', [gD.UNKNOWN_INPUT, gD.USERCONF])
        myInput = input(prompt)
    elif gD.PROMPT == 'autoresend': # no prompt, auto-resubmit commands
        gD.PROMPT = False
        myInput = gD.USERCONF
        
    # == PARSE AND HANDLE PLAYER INPUT == ########################
    
    # tokenise the input
    gD.TOKENS = parseInp.tokenizeInput(myInput)
    de.bug(1, "inputs tokens", gD.TOKENS)
       
    # parse and return information from the tokenized input data
    myCmd, myObj, conJunct, myVia = parseInp.parseInput()
    de.bug(1, "returned to gameExec with these:", myCmd, myObj, conJunct, myVia)
    
    # deal with returned information: perform actions, display feedback
    cmd_result = doCmd.doCommand(myCmd, myObj, conJunct, myVia, uiData)
    
    # EXITING game?
    if gD.EXIT == True:
        break

    # INPUT NOT RECOGNISED - feedback and fall back to the top to input()
    # Unless this is part of an automatic User Prompt Loop
    if gD.PROMPT == False:
        if cmd_result == False:
            errorHandler.inputError()

            
    #################################################################
    # END OF (WHILE WIN == FALSE) LOOP 
    #################################################################



# WIN = True? Have you won the game??
if WIN == True:
    controllers.printText(ss.winningMessage, "win")
        
