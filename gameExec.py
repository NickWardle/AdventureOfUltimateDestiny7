# -*- coding: utf-8 -*-
"""
Created on Fri Jul 13 09:24:51 2018

@author: nick.wardle
"""

import gameData as gD
import settings as ss
import controllers
import errorHandler


# =====INITIALISE GAME DATA ===============

# initialise GLOBALS
gD.init()
gD.GENCMDS = gD.uiCmds
gD.ACTCMDS = gD.actionCmds
gD.PLAYERINV = gD.player_inventory

# set up INPUT commands lists
gCmds = gD.GENCMDS['generalCmds']
aCmds = gD.ACTCMDS


# ===== RENDER FIRST/DEFAULT LOCATION =================

# render first/default location
#print("defaut loc render")
loc = gD.DEFAULTLOC
controllers.changeLoc(loc)

# == GAME STATE PLAYING LOOP ===================================

WIN = False

while WIN == False:
    
      
    # == MOVES AND OBJECTS =====================================
    
    # get all legal and illegal MOVES for location 
    moveObj = gD.LOCDATA['moveCmds']
    moveDesc = []
    moveDest = []
    moveConds = []
    
    legalMoves = []
    for i in range(len(moveObj)):
        legalMoves.append(moveObj[i][0])
        moveDesc.append(moveObj[i][1])
        moveDest.append(moveObj[i][2])
        if len(moveObj) > 2:
            moveConds.append(moveObj[i][3])
    
#    illegalMoves = []
#    if 'illegalMoveCmds' in gD.LOCDATA:
#        illObj = gD.LOCDATA['illegalMoveCmds']
#        illmoveDesc = []
#        for i in range(len(illObj)):
#            illegalMoves.append(illObj[i][0])
#            illmoveDesc.append(illObj[i][1])
        
    # get OBJECTS and object 'refs' array for location
    allObjects = []
    tmp = []
    if 'locObjects' in gD.LOCDATA:
        allObjects = gD.LOCDATA['locObjects']
        objRefs = []
        for i in range(len(allObjects)):
            for j in range(len(allObjects[i]['refs'])):
                objRefs.append(allObjects[i]['refs'][j])
        
    # group all LEGALINPUTS into one library to match against
    # as individual 'command' entries
    # [legalMoves, objRefs, UI, actions]
    allLegalInputs = []
    tmp = []
    for i in range(len(legalMoves)):
        for j in range(len(legalMoves[i])):
            tmp.append(legalMoves[i][j])
    allLegalInputs.append(tmp) #1  
#    tmp = []
#    for i in range(len(illegalMoves)):
#        for j in range(len(illegalMoves[i])):
#            tmp.append(illegalMoves[i][j])
#    allLegalInputs.append(tmp)  #2    
    allLegalInputs.append(objRefs) #2
    allLegalInputs.append(gCmds) #3
    tmp = []
    for nm, arr in aCmds.items():
        for i in range(len(arr)):
            tmp.append(arr[i])
    allLegalInputs.append(tmp)  #4
    
    
    # == SET UP DATA =============================================
    
    # set DATA package to send with each 'general' UI command
    uiData = {'search':allObjects, 'cheat':legalMoves, 'help':[gD.uiCmds, aCmds['objCmds']], 'exit':'', 'look':''}
    
    
    # == CHECK INPUT ==  BUILD PLAYER PROMPT  ===============
    
    # build input prompt and wait for player input
    if gD.REQCONF == False:
        prompt = controllers.buildPrompt('default')
        myInput = input(prompt)
    elif gD.REQCONF == True:
        prompt = controllers.buildPrompt('did you mean', gD.USERCONF)
        myInput = input(prompt)
        gD.REQCONF = False
    
    
    # tokenise the input
    inputTokenized = controllers.tokenizeInput(myInput)
       
    # parse and return information from the tokenized input data
    myCmd, myObj, myTarget = controllers.parseInput(inputTokenized, aCmds, objRefs)
    
    print("returned to gameExec with these:", myCmd, myObj, myTarget)
    
    ####  CHANGE DATA STRUCTURE FROM HERE TO USE PARSEINPUT() RETURN ####
    
    # handle input commands
    if inputTokenized[0] == "use": 
        
        c2 = False
        ix = None
        for i in inputTokenized:
        
            # check for 2nd action word and get its index
            if c2 == False: # only register first cmd2 input
                for j, k in aCmds.items():
                    if i in k and i != "use":
                        ix = inputTokenized.index(i)
                        myCmd2 = i
                        c2 = True
        
        # handle 'use .. on' case
        if i == "on":
            ix = inputTokenized.index("on")
    
            # set myInput to first input word
            myInput = inputTokenized[0] 
        
            if ix != None:
                myObj = inputTokenized[1:ix] # before Cmd2
                myTarget = inputTokenized[(ix+1):] # after Cmd2
            else:
                myObj = inputTokenized[1:] # second plus the rest
        
        else:
            myInput = inputTokenized[0] # cmd is first word
            myObj = inputTokenized[1:] # second plus the rest
        
    else:
        
        # reset subsequent commands
        myObj = None
    
    # input OK flag for catching illegal input errors
    inpOK = False
    
    # loop through every word in the player input check against commands
    for w in inputTokenized:
        
        t = 0
        # loop through each command group
        for inputGroup in allLegalInputs:
            t += 1
            
            # check every command '' in the group list
            for ky in inputGroup:
                
                # reset Target
                myTarget = None
                
                
                
                # for each command type send through data to the appropriate controller
                
                if myInput == (ky):
    
                    inpOK = True
                    
                    print(t)
    
                    # action the move
                    if t == 1: #legal moves
    
                        y = 0
                        for arr in legalMoves:
                            y += 1
                            for i in range(len(arr)):
                                if ky == arr[i]:
                                    ind = y-1
    
                        # show moveDesc feedback for moveCmd
                        controllers.printText(moveDesc[ind], "move")
                        
                        # if associated locID for moveCmd - changeLoc
                        if moveDest != '':
                            controllers.changeLoc(moveDest[ind])
                        else:
                            print("this cmd doesn't change our location")
                                                    
#                    elif t == 2: #illegal moves
#    
#                        y = 0
#                        for arr in illegalMoves:
#                            y += 1
#                            for i in range(len(arr)):
#                                if ky == arr[i]:
#                                    ind = y-1
#    
#                        # show moveDesc feedback for moveCmd
#                        controllers.printText(illmoveDesc[ind], "move")
                                        
                    elif t == 2: #object reference with no command
                                           
                        # Send myInput as OBJECT param to check against
                        controllers.useObject(None, None, myInput, None, allObjects)
                        
                    elif t == 3: #UI command
                        controllers.printText(uiData[myInput], myInput)
    
                    elif t == 4: #action command
                        print("move:", myInput, "cmd2:", myCmd2, "myObj:", myObj, "myTgt:", myTarget)
                        controllers.useObject(myInput, myCmd2, myObj, myTarget, allObjects)
              
            
    # EXITING game?
    if gD.EXIT == True:
        break

    # INPUT NOT RECOGNISED - feedback and fall back to the top to input()
    if inpOK != True:
        errorHandler.inputError()


# WIN = True? Have you won the game??
if WIN == True:
    controllers.printText(ss.winningMessage, "win")
        
