# -*- coding: utf-8 -*-
"""
Created on Fri Jul 13 09:24:51 2018

@author: nick.wardle
"""
import debugger as de
import random
import transformers as tfs
import settings as ss
import gameData as gD



# == TEXT LINES ============================================
# feedback messages and descriptions

def render_Text(d, t="default"): #generic text renderer
    
    if t == 'move': # movement description text
        print(ss.inputChangeLocPre, d)
        
    elif t == 'win': # winning message
        print(ss.inputFeedbackPre, d)

    elif t == 'exit': #exit command
        print(ss.inputFeedbackPre, ss.exitMessage)
        
#    elif t == 'unlocked': # now open
#        print(ss.inputFeedbackPre, "The", d.lower(), "is now", t)
        
    elif t == 'already locked': # now open
        print(ss.inputFeedbackPre, "The", d.lower(), "is", t)
        
    elif t == 'cheat': #cheat command
        
        temp = 'this is t {}'.format(t)
        de.bug(temp)
        # show all available movement commands for this location
        print(ss.inputFeedbackPre, "Available moves are", end=": ")
        
        # unpack commands from nested dicts{}
        tmp = [j for i in d for j in i]
        
        # list the commands
        print(tfs.listify(tmp))
        
        #show custom cheater feedback message
        messages = ss.cheaterMessage
        print(ss.inputFeedbackPre, messages[random.randint(0, len(messages)-1)])


    elif t == 'help': #help command
        
        # split d - data payload in params
        genCmds = d[0] 
        objCmds = d[1]
        
        # show all GENERAL commands for the game
        print(ss.inputFeedbackPre, "General commands", end=": ") # end= prevents new line
        
        # unpack commands from nested dicts{}                
        tmp = [j for i, k in genCmds.items() for j in k]
        
        # list the GENERAL commands
        print(tfs.listify(tmp))
        
        # show all OBJECT commands for the game
        print(ss.inputFeedbackPre, "Interaction commands", end=": ") # end= prevents new line
        
        # retrieve commands in array data
        tmp = [i for i in objCmds]
        
        # list the OBJECT commands
        print(tfs.listify(tmp))

    elif t in ('look', 'search'): #search command
        
        # show all objects in the location
        print(ss.inputFeedbackPre, "You find the following", end=": ")
        
        oRefs= [gD.gameDB['objectsDB'][i]['name'] for i in gD.LOCDATA['locObjects']]
#        for i in d:
#            oRefs.append(gD.gameDB['objectsDB'][i]['name'])
        
        # list the object refs
        print(tfs.listify(oRefs, True))
        
        # show all monsters in the location!
        
        #TODO: Make search trigger all monsters revealed
        #### INCOMPLETE
        
    elif t in ('look for', 'where'): # requires an obj [desc,location] array
        print(ss.inputFeedbackPre, "You see", d[0].lower(), d[1].lower())

    elif t == 'missing object': # part of controllers.useObject()
        print(ss.inputFeedbackPre, "You can't see the", d.lower(), "here")
        
    elif t == 'look at': # d is a list but [1] can be False is d has no access restrictions i.e. "locked"
        if (len(d) > 1) and (d[1] != False):
            print(ss.inputFeedbackPre, "You see", d[0].lower(), ". It is", d[1].lower())
        else:
            print(ss.inputFeedbackPre, "You see", d[0].lower())
                
    elif t == 'not in inv': # player trying to drop an obj not in their inv
        print(ss.inputFeedbackPre, "You do not have the", d.lower(), "in your inventory")
        
    elif t == 'already in inv': # trying to add an obj already in the inv
        print(ss.inputFeedbackPre, "You already have the", d.lower(), "in your inventory")
        
    elif t == 'contained by':
        print(ss.inputFeedbackPre, "You see", tfs.listify(d[0], True), "in the", d[1].lower()) 
        
    elif t == 'container empty':
        print(ss.inputFeedbackPre, "The", d.lower(), "is empty!") 

    elif t == 'examine': # part of controllers.useObject()
        
        # grab object name & remove from list
        oword = d.pop()
        
        print(ss.inputFeedbackPre, "You can", end=" ") # end= prevents new line
        # list out the available commands
        print(tfs.listify(d, False, "or"), "the", oword.lower())
        
    elif t == 'default': # just render payload
        print(d)
        

def render_prompt(d, t):
    
    if t == 'default prompt':
        return ss.inputQuestionPre + d + '\n' + ss.shortLnNewLine + '\n'
    
    elif t == 'did you mean':
        return ss.inputQuestionPre + "I didnt understand '" + d[0].lower() + "' Did you mean '" + d[1].lower() + "'? Y/N\n" + ss.shortLnNewLine + '\n'


def render_objectActions(d, cmd, t, ob=None):
    
    de.bug(3, "data for interaction is", d)
    
    if t in ("get-take", "put-leave", "ok", "unlocked"):
        print(ss.inputFeedbackPre, "You", cmd, "the", d['name'].lower())

    elif t == "has-req-obj":
        print(ss.inputFeedbackPre, "You", cmd, "the", d['name'].lower(), "with the",  gD.gameDB['objectsDB'][ob]['name'].lower())
        
    elif t == "use": # singleton "use" command: use on what?
        print(ss.inputFeedbackPre, "Use the", d['name'].lower(), "to do what?")
        
    elif t == "locked_by": # tell player what req obj is
        print(ss.inputFeedbackPre, "The", d['name'].lower(), "is locked by the",  gD.gameDB['objectsDB'][d['permissions']['locked_by']]['name'].lower())
        
    elif t == "unlocked_by": # tell player what req obj is
        print(ss.inputFeedbackPre, "The", d['name'].lower(), "can be locked using the",  gD.gameDB['objectsDB'][d['permissions']['unlocked_by']]['name'].lower())

    elif t == "illegal": # user tried to do an illegal action on an object
        print(ss.inputFeedbackPre, "You can\'t", cmd, "the", d['name'].lower())


def render_inputError():
    
    #show random "wrong try again" message
    messages = ss.illegalMove
    print(ss.inputFeedbackPre + messages[random.randint(0, len(messages)-1)])  


def render_actionHelp(c):
    
    # show appropriate hint feedback for misused action command
    print(ss.inputFeedbackPre, c.capitalize(), "what? Type", c, "and then the name of the thing you want to", c)


def render_objectHelp(d, n):
    
    # grab object name
    oword = n.lower()
    
    #show feedback and available commands for that object
    print(ss.inputFeedbackPre, "What do you want to do with the", oword + "?")
    print(ss.inputFeedbackPre, "Available commands are:", end=" ") # end= prevents new line
            
    # list out the available commands
    print(tfs.listify(d))
    
def render_objectDedupe(d, inp):
    
    print(ss.inputFeedbackPre, "Which", inp, "do you mean:", tfs.listify(d, False, 'or'), "?")


# == VIEWS =================================================
# screen renderers get their data from other modules


def render_locScreen(d): #generic location renderer
    
    #TODO: Want to build a location out of the available points of interest
    # such as exits: orthogonal and object-based
    
    # show location description
    print(d['locDesc'])

    # show additional location descriptions (optional)
    if d['locAdditionalDesc'] != '':
        print('\n', d['locAdditionalDesc'])
    
    # show result of entryConditions on char or world
    if len(d['entryConditions']) > 0:
        print("\nWe have some entryConditions!")



def render_charInventory(): # render player inventory
    
    # reset vars
    invEmpty = True
    
    print(ss.inventoryTitle, '\n')
    
    for item_slot, slot_items in gD.player_inventory.items():
        
        # pad item_slot to 10 chars
        pad = len(item_slot) + (10 - len(item_slot))
        item_slot = item_slot.ljust(pad)
        
        if len(slot_items):
            
            invEmpty = False
            
            for item in slot_items:
                
                # a or an?
                if item['name'][0].lower() in ('a', 'e', 'i', 'o', 'u', 'h'):
                    ind_pron = 'An'
                else:
                    ind_pron = 'A'
                
                if slot_items.index(item) == 0:
                    print(item_slot, ss.vertDiv, ind_pron, item['name'].lower(), '\n')
                else:
                    print(ss.slot_shim, ss.vertDiv, ind_pron, item['name'].lower(), '\n')
                    
            print(ss.rowDiv, '\n')
            
        else:
            
            if invEmpty == False:
            
                print(item_slot, ss.vertDiv, '(No items) \n')
                print(ss.rowDiv, '\n')
    
    
    if invEmpty == True:
        print("\n          You have nothing in your Inventory \n\n")
        print(ss.rowDiv, '\n')
    
    

# def render_charHome
        
# def render_charSheet
        

