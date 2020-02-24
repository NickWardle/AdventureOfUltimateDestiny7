# -*- coding: utf-8 -*-

"""
Created on Fri Jul 13 09:24:51 2018

@author: nick.wardle
"""

import pandas as pd
import numpy as np


# == GLOBALS ============================================================

def init():
    global allInputRefs
    global CURRENT_LOC
    global LOCDATA
    global PLAYERINV
    PLAYERINV = player_inventory
    global DEFAULTLOC
    DEFAULTLOC = 'z0001'
    global CHEATER
    CHEATER = False
    global EXIT
    EXIT = False
    global PROMPT
    PROMPT = False
    global USERCONF
    USERCONF = False
    global UNKNOWN_INPUT
    UNKNOWN_INPUT = None
    
    # create allInputRefs list (to match against tokens to find ANY possible match, not just matches legal within the current location)
    allUICmds = gameDB['uiCmds']
    allActCmds = gameDB['actionCmds']
    allMoves = {}
    allMoves_lst = []
    for i, j in gameDB['moveCommandsDB'].items():
        for k in j:
            for l in k[0]:
                allMoves_lst.append(l)
    allMoves['m'] = list(set(allMoves_lst))
    allObjects = {}
    allObjects_lst = []
    for i, j in gameDB['objectsDB'].items():
        for k in j['refs']:
            allObjects_lst.append(k)
    # remove duplicates in allObjects_lst using a set{}
    allObjects['o'] = list(set(allObjects_lst))
    # explode all dicts to create a super-dict-DB with all inside flattened
    allInputRefs = {**allActCmds, **allUICmds, **allMoves, **allObjects}
    

# def gameStory - adventure chapters, progression spine

# def worldState - state of world game progression

# def charProgression - character progression and stats

# def charInventory - inventory of char items

# def charHome - spaceship features and progression

# == EXCLUDED COMMAND WORDS  =========================================

ignoreWords = ['the', 'to', 'a', 'and', '?', '!']



##################### ALL THINGS DB #####################################
#########################################################################
gameDB = {
##########################################################################



# == UI COMMANDS  =====================================================

# the idea with 'search' is that it reveals all objects at the location
# for example to help you find keys that are not stated in the desc of 
# the loc (deliberately). However, the risk is that you will uncover a
# a MONSTER when you search..!

'uiCmds' : {

# all general UI commands    
'generalCmds' : ['help', 'cheat', 'exit'],

# all player charcter commands
'playerCmds' : ['inv', 'inventory'],

}
,



# == ACTION COMMANDS ===============================================

# NOTE these commands will impact controllers.useObject() if changed

# NOTE all command arrays must be added explicitly to OBJECTS below
# NOTE changing command words will affect OBJECTS that list them

'actionCmds' : {

# conjunctions affect the outcome of an actionCmd on an object
'conJuncts' : ['with', 'through', 'in', 'from', 'into', 'on', 'under', 'near', 'next', 'inside'],

# navigation commands for moving around the spaces
'navCmds' : ['go', 'walk', 'run', 'leave'],

# exploration commands that reveal information about a whole location (no obj)
'exploreCmds' : ['search', 'look'],

# commands that reveal detailed iformation about an object (req obj)
'examineCmds' : ['look at', 'examine', 'look for', 'where', 'search for', 'find'],

# get commands add an object to the player's hands
'getCmds' : ['get', 'take', 'pick up'],

# put commands move an object from the players hands to another location
'putCmds' : ['leave', 'drop', 'put down', 'put'],

# interaction commands change the state of an object
# some objects need to be in the players hands first
'intCmds' : ['open', 'close', 'move', 'pick', 'lock', 'unlock'],

# use commands consume one use of an object
# some objects have infinite uses
'useCmds' : ['use', 'drink', 'eat', 'attack', 'shoot', 'stab'],

}
,







# == ALL MOVES ============================================================
'moveCommandsDB' : {

'm010001' : [ 
    [
        ["n", "north"], 
        "You take the path to the North", 
        'z0002'
    ],
    [
        ["e", "east"], 
        "You walk east into the dark forest", 
        'z0004'
    ]
]
,
'm010002' : [ 
    [
        ["s", "south"], 
        "You take the path to the South", 
        'z0001'
    ]
]
,  
'm010003' : [ 
    [
        ["inside", "into"], 
        "You step into the dark doorway", 
        'z0003'
    ]
]
,
'm010004' : [ 
    [
        ["outside"], 
        "You step back out into the sunlight", 
        'z0001'
    ]
]  
 
    
}
,

    
# == OBJECTS ============================================================


# keys, codes, magic charm - unlockKeys that toggle location conditions

# potions, food, drinks - powerups that change % event outcomes OR location conditions (invisibility)

# teleporters, vehicles, wormholes - move you to other locations

## location is an optional additional description of the place the object can be found
## NOTE: objects could have an "orthogonal location", or be associated with a "point of interest", such as "north", or "the old tree". Then you could "search around the old tree". And you could build locations out of the component p.o.i that comprise it i.e. the exits and the poi's in it. But this is complex.
## state describes conditions like 'locked_by' or 'contains'. If there is a one-to-many relationship, put the state on the "one" for look-up ease
## inventory slots are the legal player inventory slots for the object. No inv slots means the player cannot store this item in their inventory
## Object Permissions
# 'permissions' can be: 'locked_by' etc req different actions to get access to the object. See controllers.objPermissions()
## Command List Inclusion / Limitations
# limit to specific commands in a command group by listing them in the getCmds-OK: ['list'] for example. Or allow all commands in a group to be used on an object by simply adding the empty list e.g. putCmds-OK: []
# IMPORTANT NOTE: all action command list keys MUST be in the format 'comand list name'+'-OK' so they are included in the collation of available commands in controllers.useObject()

'objectsDB' : {

'ob0001' : {
    'refs': ['key', 'red key'],
    'name': 'Red key',
    'desc': 'A particularly ornate, shiny, red, metal key', 
    'location': 'partially hidden under a bush', 
    'permissions': {}, 
    'state': {}, 
    'inventory-slot': 'utils', 
    'getCmds-OK': [],
    'putCmds-OK': [], 
#    'intCmds-OK': [], 
    'useCmds-OK': ['use']
}
,
'ob0002' : {
    'refs': ['box', 'big box', 'metal box', 'heavy box'],
    'name': 'Big box',
    'desc': 'A large, heavy, metal lock box', 
    'location': 'under a tree', 
    'permissions': {'locked_by': 'ob0001'}, 
    'state': {'access': 'locked', 'contains': ['ob0006','ob0003']}, 
#    'inventory-slot': '', 
#    'getCmds-OK': [],
#    'putCmds-OK': [],
    'intCmds-OK': []
#    'useCmds-OK': []
}
,
'ob0006' : {
    'refs': ['key', 'yellow key'],
    'name': 'Yellow key',
    'desc': 'A rusted old iron key covered in flaking yellow paint', 
    'location': 'just sitting there', 
    'permissions': {}, 
    'state': {'contained_by': ['ob0002']}, 
    'inventory-slot': 'utils', 
    'getCmds-OK': [],
    'putCmds-OK': [], 
#    'intCmds-OK': [], 
    'useCmds-OK': ['use']
}
,
'ob0005' : {
    'refs': ['door', 'yellow door'],
    'name': 'Yellow door',
    'desc': 'An old dirty yellow door', 
    'location': 'covered in vines and roots', 
    'permissions': {'locked_by': 'ob0006'}, 
    'state': {'access': 'locked', 'contains': ['m010003']}, 
#    'inventory-slot': '', 
#    'getCmds-OK': [],
#    'putCmds-OK': [],
    'intCmds-OK': ['open', 'close']
#    'useCmds-OK': []
}
,
'ob0004' : {
    'refs': ['door', 'red door'],
    'name': 'Red door',
    'desc': 'A freshly painted red door', 
    'location': 'in the middle of a wall', 
    'permissions': {'locked_by': 'ob0001'}, 
    'state': {'access': 'locked', 'contains': ['m010003']}, 
#    'inventory-slot': '', 
#    'getCmds-OK': [],
#    'putCmds-OK': [],
    'intCmds-OK': ['open', 'close']
#    'useCmds-OK': []
}
,
'ob0003' : {
    'refs': ['dagger', 'sharp dagger'],
    'name': 'Sharp dagger',
    'desc': 'A vicious, sharp, pointy dagger', 
    'location': 'glinting on the floor', 
    'permissions': {}, 
    'state': {'contained_by': ['ob0002']}, 
    'inventory-slot': 'weapons', 
    'getCmds-OK': [],
    'putCmds-OK': [],
#    'intCmds-OK': [],
    'useCmds-OK': ['stab', 'attack']
}

}
,







# == MOBS ============================================================

# npcs
# monsters/opponents

'mobsDB' : {

'mob0001' : {
    'refs' : ['monster']
}

}

        
        
####################### END OF ALL THINGS DB #############################        
}
##########################################################################



# == CHARACTER CONFIGURATION ===============================================

# Set up the basic attributes of teh Player Character

character_handedness = 'right' # 'right' or 'left'





# == CHARACTER INVENTORY ===============================================

# the player only has two hands and one is "default", set in Character Config
player_hands = {'right': [], 'left': [], 'default': [character_handedness]}

### When the structure of this dictionary changes, adjust parsing in controllers.objPermissions()
player_inventory = {'utils': [], 'weapons':[], 'food':[], 'clothes':[]}










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


# == All location objects
locDB = {

'z0001' : {
    'locInputDesc': 'What will you do next?', 
    'locDesc': 'You are standing in a clearing. There is an exit to the NORTH through the dark trees. Another to the EAST along a well worn path. And a BOX at the edge of the clearing.', 
    'locAdditionalDesc': '', 
    'entryConditions': ['e010001', 'e020001'], 
    'leaveConditions': ['l010001', 'l020001'], 
    'moveCmds': 'm010001', 
    'locObjects': ['ob0001', 'ob0002']
}    
,
'z0002' : {
    'locInputDesc': 'What will you do now?', 
    'locDesc': 'There\'s nothing of interest here. You should turn around.', 
    'locAdditionalDesc': '', 
    'entryConditions': ['e010001', 'e020001'], 
    'leaveConditions': ['l010001', 'l020001'], 
    'moveCmds': 'm010002'
}   
,
'z0003' : {
    'locInputDesc': 'Now what?', 
    'locDesc': 'It sure is dark in here...', 
    'locAdditionalDesc': '', 
    'entryConditions': ['e010001', 'e020001'], 
    'leaveConditions': ['l010001', 'l020001'], 
    'moveCmds': 'm010004'
}

}


# == Entry conditions
entryConditionsDB = {
    
'e010001' : {
    'worldState': 'something'
}
,
'e020001' : {
    'charState': 'something'
}

}

# == Leave conditions
leaveConditions : {

'l010001' : {
    'worldState': 'something'
}
,
'l020001' : {
    'charState': 'something'
}

}


    
# == STATE MACHINE ===================================================

# Add another ROW for each new object that requires stateful data

df_data = np.array([['','state_data'],
                    ['ob0002',{'entry':'locked', 'contains':['ob0003']}],
                    ['ob0004',{'entry':'locked'}],
                    ['ob0005',{'entry':'locked'}],
                    ])


# Build DataFrame for WORLD_frame initial state

World_frame = pd.DataFrame(data=df_data[1:,1:],
                  index=df_data[1:,0],
                  columns=df_data[0,1:])

# Build DataFrame for STATE_frame state updates

State_frame = pd.DataFrame(columns=df_data[0,1:])








