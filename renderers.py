# -*- coding: utf-8 -*-
"""
Created on Fri Jul 13 09:24:51 2018

@author: nick.wardle
"""
import random
import transformers as tfs
import settings as ss

# == TEXT LINES ============================================
# feedback messages and descriptions

def render_Text(d, t="default"): #generic text renderer
    
    if t == 'move': # movement description text
        print(ss.inputChangeLocPre, d)
        
    elif t == 'win': # winning message
        print(ss.inputFeedbackPre, d)

    elif t == 'exit': #exit command
        print(ss.inputFeedbackPre, ss.exitMessage)
        
    elif t == 'cheat': #cheat command
        
        temp = 'this is t {}'.format(t)
        print(temp)
        # show all available movement commands for this location
        print(ss.inputFeedbackPre, "Available moves are", end=": ")
        tmp = []
        for i in d:
            for j in i:
                tmp.append(j)
        
        # list the commands
        print(tfs.listify(tmp))
        
        #show custom cheater feedback message
        messages = ss.cheaterMessage
        print(ss.inputFeedbackPre, messages[random.randint(0, len(messages)-1)])


    elif t == 'help': #help command
        
        genCmds = d[0]
        objCmds = d[1]
        # show all GENERAL commands for the game
        print(ss.inputFeedbackPre, "General commands", end=": ") # end= prevents new line
        
        # retrieve dictionary values with x, y and .items()
        tmp = []
        for i, k in genCmds.items():
            for j in k:
                tmp.append(j)
        
        # list the GENERAL commands
        print(tfs.listify(tmp))
        
        # show all OBJECT commands for the game
        print(ss.inputFeedbackPre, "Interaction commands", end=": ") # end= prevents new line
        
        # retrieve commands in array data
        tmp = []
        for i in objCmds:
            tmp.append(i)
        
        # list the GENERAL commands
        print(tfs.listify(tmp))

    elif t == 'search': #search command
        
        # show all objects in the location
        print(ss.inputFeedbackPre, "You find the following", end=": ")
        
        oRefs= []
        for i in d:
            oRefs.append(i['name'])
        
        # list the object refs
        print(tfs.listify(oRefs))
        
        # show all monsters in the location!
        
        # trigger all monsters revealed
        #### INCOMPLETE

    elif t == 'missing object': # part of controllers.useObject()
        print(ss.inputFeedbackPre, "There is no", d.lower(), "here")
        
    elif t == 'look at': # part of controllers.useObject()
        print(ss.inputFeedbackPre, "You see", d.lower())
                
    elif t == 'not in inv': # player trying to drop an obj not in their inv
        print(ss.inputFeedbackPre, "You do not have the", d.lower(), "in your inventory")
        
    elif t == 'already in inv': # trying to add an obj already in the inv
        print(ss.inputFeedbackPre, "You already have the", d.lower(), "in your inventory")
        
    elif t == 'examine': # part of controllers.useObject()
        
        # grab object name
        oword = d[len(d)-1].lower()
        d.pop() # remove the last item - the object name
        
        print(ss.inputFeedbackPre, "You can", end=" ") # end= prevents new line
        # list out the available commands
        print(tfs.listify(d, "or"), "the", oword)
        
    elif t == 'default': # just render payload
        print(d)
        

def render_prompt(d, t):
    
    if t == 'default prompt':
        return ss.inputQuestionPre + d + '\n' + ss.shortLnNewLine + '\n'
    
    elif t == 'did you mean':
        return ss.inputQuestionPre + "Did you mean '" + d.lower() + "'? Y/N\n" + ss.shortLnNewLine + '\n'


def render_objectActions(d, cmd, t):
    
    if t == "get-take" or t == "put-leave" or t == "open-OK":
        print(ss.inputFeedbackPre, "You", cmd, "the", d['name'].lower())
        
    elif t == "use": # singleton "use" command: use on what?
        print(ss.inputFeedbackPre, "Use the", d['name'].lower(), "to do what?")
        
    elif t == "locked_by": # tell player what req obj is
        print(ss.inputFeedbackPre, "This", d['name'].lower(), "is locked by the",  d['permissions']['locked_by']['name'].lower())
        
    elif t == "has-req-obj": # tell player to use the req obj
        print(ss.inputFeedbackPre, "Use the", d['permissions']['locked_by']['name'].lower(), "to", cmd, "the", d['name'].lower())
        
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
    

# == VIEWS =================================================
# screen renderers get their data from other modules


def render_locScreen(d): #generic location renderer
    
    # show location description
    print(d['locDesc'])

    # show additional location descriptions (optional)
    if d['locAdditionalDesc'] != '':
        print('\n', d['locAdditionalDesc'])
    
    # show result of entryConditions on char or world
    if len(d['entryConditions']) > 0:
        print("\nWe have some entryConditions!")



# def render_charHome
        
# def render_charSheet
        
# def render_charInventory
