# -*- coding: utf-8 -*-
"""
Created on Fri Jul 13 09:24:51 2018

@author: nick.wardle
"""
import debugger as de
import gameData as gD
import settings as ss
import controllers
import errorHandler


# == INITIALISE GAME DATA == ####################################

# initialise GLOBALS
gD.init()
gD.GENCMDS = gD.uiCmds
gD.ACTCMDS = gD.actionCmds
gD.PLAYERINV = gD.player_inventory

# set up INPUT commands lists
gCmds = gD.GENCMDS['generalCmds']
aCmds = gD.ACTCMDS


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

    
    # get all legal MOVES for location 
    moveObj = gD.moveCommandsDB[gD.LOCDATA['moveCmds']]
    legalMoves = []
    moveDesc = []
    moveDest = []
    
    for i in range(len(moveObj)):
        legalMoves.append(moveObj[i][0])
        moveDesc.append(moveObj[i][1])
        moveDest.append(moveObj[i][2])
        
    # get OBJECTS and object 'refs' array for location
    allObjects = []
    tmp = []
    if 'locObjects' in gD.LOCDATA:
        for i in gD.LOCDATA['locObjects']:
            allObjects.append(i)
        objRefs = []
        for i in allObjects:
            for j in gD.objectsDB[i]['refs']:
                objRefs.append(j)
        
    
    # == ALL LEGAL INPUTS == #####################################
    
    # group all LEGALINPUTS into one library to match against
    # as individual 'command' entries
    # [legalMoves, objRefs, UI, actions]

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
    legalInputsB = gD.uiCmds
    legalInputsC = gD.actionCmds
    legalInputs = {**legalInputsC, **legalInputsB, **legalInputsA}
    de.bug(1, "legalInputs", legalInputs)
    
    
    ##############################################################
    ##############################################################
    
    
    # == SET UP DATA == ##########################################
    
    # set DATA package to send with each 'general' UI command
    uiData = {'search':allObjects, 'cheat':legalMoves, 'help':[gD.uiCmds, aCmds['objCmds']], 'exit':'', 'look':''}
    
    
    # == CHECK INPUT ==  BUILD PLAYER PROMPT  == #################
    
    if gD.PROMPT == False: # default input prompt
        prompt = controllers.buildPrompt('default')
        myInput = input(prompt)
    elif gD.PROMPT == 'reqconf': # require Y/N reconfirmation
        prompt = controllers.buildPrompt('did you mean', gD.USERCONF)
        myInput = input(prompt)
    elif gD.PROMPT == 'autoresend': # no prompt, auto-resubmit commands
        gD.PROMPT = False
        myInput = gD.USERCONF
        
    # == PARSE AND HANDLE PLAYER INPUT == ########################
    
    # tokenise the input
    inputTokenized = controllers.tokenizeInput(myInput)
    de.bug(1, "inputs tokens", inputTokenized)
       
    # parse and return information from the tokenized input data
    myCmd, myObj, conJunct, myVia = controllers.parseInput(inputTokenized, legalInputs)
    de.bug("returned to gameExec with these:", myCmd, myObj, conJunct, myVia)
    
    # deal with returned information: perform actions, display feedback
    cmd_result = controllers.doCommand(myCmd, myObj, conJunct, myVia, legalInputs, uiData)
            
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
        
