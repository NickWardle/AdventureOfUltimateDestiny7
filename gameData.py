# -*- coding: utf-8 -*-

"""
Created on Fri Jul 13 09:24:51 2018

@author: nick.wardle
"""

import pandas as pd
import numpy as np

# == GLOBALS ============================================================

def init():
    global LOCDATA
    global GENCMDS
    global ACTCMDS
    global PLAYERINV
    global DEFAULTLOC
    DEFAULTLOC = 'z0001'
    global CHEATER
    CHEATER = False
    global EXIT
    EXIT = False



# def gameStory - adventure chapters, progression spine

# def worldState - state of world game progression

# def charProgression - character progression and stats

# def charInventory - inventory of char items

# def charHome - spaceship features and progression

# == EXCLUDED COMMAND WORDS  =========================================

ignoreWords = ['the', 'to', 'a', 'and']


# == UI COMMANDS  =====================================================

# the idea with 'search' is that it reveals all objects at the location
# for example to help you find keys that are not stated in the desc of 
# the loc (deliberately). However, the risk is that you will uncover a
# a MONSTER when you search..!

# all general UI commands    
generalCmds = ['look', 'search', 'help', 'cheat', 'exit']

uiCmds = {'generalCmds':generalCmds}


# == ACTION COMMANDS ===============================================

# NOTE these commands will impact controllers.useObject() if changed

# NOTE all command arrays must be added explicitly to OBJECTS below
# NOTE changing command words will affect OBJECTS that list them

# object commands interact with objects without changing the world
objCmds = ['look at', 'examine']

# get commands add an object to player inventory
getCmds = ['get', 'take', 'pick up']

# put commands remove an object from player inventory
putCmds = ['leave', 'drop', 'put down', 'put up there', 'put in', 'put']

# interaction commands change the state of an object in inventory or location
intCmds = ['open', 'close', 'move', 'get in']

# use commands consume one use of an object
useCmds = ['use', 'drink', 'eat', 'attack', 'shoot', 'stab']

#### Commands Dictionary object: all all command arrays
actionCmds = {'objCmds':objCmds, 'getCmds':getCmds, 'putCmds':putCmds, 'intCmds':intCmds, 'useCmds':useCmds}



# == CHARACTER INVENTORY ===============================================

### When the structure of this dictionary changes, adjust parsing in controllers.objPermissions()
player_inventory = {'utils': [], 'weapons':[], 'food':[], 'clothes':[]}



# == MOBS ============================================================

# npcs
# monsters/opponents

mob0001 = {}


# == ALL MOVES ============================================================

# == Move commands: LEGAL (m) and ILLEGAL (x)
m010001 = [ # legal moves
    [
        ["n", "north"], 
        "You take the path to the North", 
        'z0002'
    ]
#    [
#        ["open", "box"], 
#        "You reach down and try to open the box at your feet", 
#        'z0003', 
#        ["Fortunately, you have the right key and the box springs open!", "This box is firmly locked. You'll need to find the key"]
#    ]
]

#x010001 = [ # illegal moves
#    [
#        ["e", "east"], 
#        "Did you think you could go East? You can't go East..."
#    ], 
#    [
#        ["w", "west"], 
#        "Can't see the wood for the trees, eh...?"
#    ]
#]



m010002 = [ # legal moves
    [
        ["s", "south"], 
        "You take the path to the South", 
        'z0001'
    ]
]
    

m010003 = [ # legal moves
    [
        ["in", "inside", "into"], 
        "You step into the dark doorway", 
        'z0003'
    ]
]


m010004 = [ # legal moves
    [
        ["out", "outside"], 
        "You step back out into the sunlight", 
        'z0001'
    ]
]  
    
    
# == OBJECTS ============================================================


# keys, codes, magic charm - unlockKeys that toggle location conditions

# potions, food, drinks - powerups that change % event outcomes OR location conditions (invisibility)

# teleporters, vehicles, wormholes - move you to other locations

# Do not include action command lists if the object cannot be "get" or "put" or "use"
# 'permissions' can be: 'locked_by' etc req different actions to get access to the object. See controllers.objPermissions()
# IMPORTANT NOTE: all action command list keys MUST be in the format 'comand list name'+'-OK' so they are included in the collation of available commands in controllers.useObject()

ob0006 = {
    'refs': ['key', 'yellow key'],
    'name': 'Yellow key',
    'desc': 'A rusted old iron key covered in flaking yellow paint', 
    'permissions': {}, 
    'state': {}, 
    'getCmds-OK': [],
    'putCmds-OK': [], 
    'inventory-slot': 'utils', 
#    'intCmds-OK': [], 
    'useCmds-OK': ['use']
}

ob0001 = {
    'refs': ['key', 'red key'],
    'name': 'Red key',
    'desc': 'A particularly ornate, vermillion, shiny metal key', 
    'permissions': {}, 
    'state': {}, 
    'getCmds-OK': [],
    'putCmds-OK': [], 
    'inventory-slot': 'utils', 
#    'intCmds-OK': [], 
    'useCmds-OK': ['use']
}

ob0005 = {
    'refs': ['door', 'yellow door'],
    'name': 'Yellow door',
    'desc': 'An old dirty yellow door', 
    'permissions': {'locked_by': ob0006}, 
    'state': {'access_to': {'move': m010003}}, 
#    'getCmds-OK': [],
#    'putCmds-OK': [],
#    'inventory-slot': 'weapons', 
    'intCmds-OK': ['open', 'close'],
#    'useCmds-OK': []
}

ob0004 = {
    'refs': ['door', 'red door'],
    'name': 'Red door',
    'desc': 'A freshly painted red door', 
    'permissions': {'locked_by': ob0001}, 
    'state': {'access_to': {'move': m010003}}, 
#    'getCmds-OK': [],
#    'putCmds-OK': [],
#    'inventory-slot': 'weapons', 
    'intCmds-OK': ['open', 'close'],
#    'useCmds-OK': []
}

ob0003 = {
    'refs': ['dagger', 'sharp dagger'],
    'name': 'Sharp dagger',
    'desc': 'A vicious, sharp, pointy dagger', 
    'permissions': {}, # could have a level requirement to use
    'state': {}, 
    'getCmds-OK': [],
    'putCmds-OK': [],
    'inventory-slot': 'weapons', 
#    'intCmds-OK': [],
    'useCmds-OK': ['stab', 'attack']
}

ob0002 = {
    'refs': ['box', 'big box', 'metal box', 'heavy box'],
    'name': 'Big box',
    'desc': 'A large, heavy, metal lock box', 
    'permissions': {'locked_by': ob0001}, # affects controllers.objPermissions and controllers.useObject "open" command
    'state': {'access_to': {'object': ob0003}}, 
#    'getCmds-OK': [],
#    'putCmds-OK': [],
#    'inventory-slot': '', 
    'intCmds-OK': [], 
#    'useCmds-OK': []
}


# == LOCATIONS ============================================================

# locDb - list of all location keys/IDs
# locID - unique ID for this location
# locInputDesc - text for player input at this location    
# locDesc - description of this location
# locDescAdditional - extra conditional description(s) required by game state ****MAKE THIS BETTER
# entryConditions - what happens on entry on this location
    # update worldState (optional)
    # effects on char (optional)
# leaveConditions - what happens on exit of this location
    # update worldState (optional)
    # effects on char (optional)
# moveCmds - list of valid moveCmds, moveDescs and associated locIDs and moveConditions (optional)
# moveCmds - [[["N", "North"] "moveDesc", ?locID, ?["pass description", "fail description"]], [["Open", "box"] "moveDesc", ?locID, ?["pass description", "fail description"]]
# illegalMoveCmds - whitelist of special messages for certain locIDs

# == Entry conditions
e010001 = {'worldState': 'something'}
e020001 = {'charState': 'something'}

# == Leave conditions
l010001 = {'worldState': 'something'}
l020001 = {'charState': 'something'}



# == All location objects
z0001 = {
    'locInputDesc': 'What will you do next?', 
    'locDesc': 'You are standing in a clearing. There is an exit to the NORTH through the dark trees. Another to the EAST along a well worn path. And a BOX at the edge of the clearing.', 
    'locAdditionalDesc': '', 
    'entryConditions': [e010001, e020001], 
    'leaveConditions': [l010001, l020001], 
    'moveCmds': m010001, 
#    'illegalMoveCmds': x010001,
    'locObjects': [ob0001, ob0002]
}    

z0002 = {
    'locInputDesc': 'What will you do now?', 
    'locDesc': 'There\'s nothing of interest here. You should turn around.', 
    'locAdditionalDesc': '', 
    'entryConditions': [e010001, e020001], 
    'leaveConditions': [l010001, l020001], 
    'moveCmds': m010002
}   

z0003 = {
    'locInputDesc': 'Now what?', 
    'locDesc': 'It sure is dark in here...', 
    'locAdditionalDesc': '', 
    'entryConditions': [e010001, e020001], 
    'leaveConditions': [l010001, l020001], 
    'moveCmds': m010004
#    'illegalMoveCmds': x010001
}   
# == Locations database
locDb = {'z0001':z0001, 'z0002':z0002, 'z0003':z0003}


    
# == STATE MACHINE ===================================================

# Add another ROW for each new object that requires stateful data

df_data = np.array([['','state_data'],
                    ['ob0002',{'entry':'locked', 'contains':[ob0003]}],
                    ['ob0004',{'entry':'locked'}],
                    ['ob0005',{'entry':'locked'}],
                    ])


# Build DataFrame for WORLD_frame initial state

World_frame = pd.DataFrame(data=df_data[1:,1:],
                  index=df_data[1:,0],
                  columns=df_data[0,1:])

# Build DataFrame for STATE_frame state updates

State_frame = pd.DataFrame(columns=df_data[0,1:])








