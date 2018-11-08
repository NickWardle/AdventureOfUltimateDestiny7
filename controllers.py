# -*- coding: utf-8 -*-
"""
Created on Fri Jul 13 09:24:51 2018

@author: nick.wardle
"""
import gameData as gD
import renderers
import transformers as tfs
import re
from nltk.tokenize import word_tokenize
#import errorHandler

# == INITIALISE DATA =================================================

# get ALL LOCATION DATABASE
locDb = gD.locDb

# == CONTROLLERS =================================================
# modules that take inputs from player, or other modules, and update the models

def clearLocData():
    
    gD.LOCDATA = ''

def printText(d, t="default"): # generic text printer
    
    if t == 'exit': #exit command
        gD.EXIT = True
        
    if t == 'look': #look around again
        renderers.render_locScreen(gD.LOCDATA)
    else:
        renderers.render_Text(d, t)


def changeLoc(loc): #generic location changer 
    
    if loc in locDb:
        
        # get current location data and make it GLOBAL
        gD.LOCDATA = locDb[loc]
        
    else:
        print("Location not in locDb")
    
    # show thinkingDots
    print('\n. . . . L O A D I N G . . . .\n')
      
    # render new location
    renderers.render_locScreen(gD.LOCDATA)
      

def tokenizeInput(inp):
    
    # tokenise the input
    outputTokens = word_tokenize(inp)
    
    # strip out all 'ignored words' to REDUCE inputTokenized
    rm_list = []
    for w in outputTokens:
        if w in gD.ignoreWords:
            rm_list.append(w)
    
    for r in rm_list:
        outputTokens.remove(r)
    
    return outputTokens


def parseInput(tkns, actns, objs): # extract objects from (multiple word) tokenized input
    
    # looking for: cmd, cmd2, obj, tgt
    # format: cmd-obj(-cmd2-tgt)
    #
    # take into account pseudo-cmd2 cases
    # format: cmd-obj-'with/on'-tgt
    
    parsed_cmds = {}
    returned_cmds = []
    obj = None
    tgt = None
    
    if len(tkns) > 1: # single word inputs handled later, below
        
        i = 0
        # for each word
        for w in tkns:
            
            i = i + 1
            c = "cmd" + str(i)
            
            # match against COMMANDS ======
            for j, k in actns.items():
                # for each cmd in each cmd group
                for l in k:
                    # is the word in the cmd group
                    if re.search(w, l):
                        # group up matches into 'cmds'
                        c = "cmd" + str(i)
                        # combine cmdgrp name - match index as label
                        ind = j + "-" + str(k.index(l))
                        
                        # build list of matches                        
                        if c in parsed_cmds.keys():
                            parsed_cmds[c].append(ind)
                        else:
                            parsed_cmds[c] = [ind]
                    
        
        # if there is more than one cmd matched
        if len(parsed_cmds) > 1:
            
            # check the first command isn't a singleton
            if "cmd2" in parsed_cmds.keys():
            
                # check if second cmd list has a match to the first
                cmd_mtch = set(parsed_cmds['cmd1']).intersection(parsed_cmds['cmd2'])
                
                print("matched", cmd_mtch)
                
                # if success matching first command
                if len(cmd_mtch) > 0:
                    
                    # get the actual command-tokened words
                    cmd_item = cmd_mtch.pop()
                    cmd_elems = cmd_item.split("-")
                    
                    # count the number of words
                    cmd_lst = gD.actionCmds[cmd_elems[0]]
                    cmd_wrds = cmd_lst[int(cmd_elems[1])]
                    cmd_len = len(tokenizeInput(cmd_wrds))
                    print("cmd wrds '", cmd_wrds, "' cmd len", cmd_len)
                    
                    # require this many sequential parsed_cmds.keys() matches
                    q = 1
                    cmd_valid = True
                    while q <= cmd_len:
                        
                        # increment through each "cmd+n"
                        myKey = "cmd" + str(q)
                        
                        #check we haven't just run out of cmds
                        if myKey in parsed_cmds.keys():
                            
                            if cmd_item not in parsed_cmds[myKey]:
                                print("missing in", myKey)
                                cmd_valid = False
                        
                        else: # failed to match full length, invalid command
                            
                            print("not enough command matches - invalid command")
                            cmd_valid = False
                    
                        q = q + 1
                        
                    # if yes, this is our first command
                    if cmd_valid == True:
                        # add it to the list of commands we will return
                        returned_cmds.append(cmd_item)
                    
                    # remove these from list and go again
                    
                    ## THIS IS NEW!
                    
                    
                else: # malformed command
                    
                    print("that wasn't a valid command")
                    
                    # set commands returned as None
                
            else: # first command is a singleton
                
                print("deal with first command being a singleton, same as elif below")
            


        elif len(parsed_cmds) == 1:
        
            # loop each item in parsed_cmds[0]
                    
                # do an == check against the matched command
                print("only one cmd to check against")
                
        else: # parsed_cmds is empty
            
            print("no commands found")
        
        
        # let that cmd1 be true, otherwise delete that cmd1 and 
        # shuffle all the others up a place
        # return a list of cmd1, cmd2, cmd3 with the 
        # command text and type? or just type?

            
        # match against OBJECTS ======
        if w in objs:
            obj = w
    
        # SET myTarget
    
        print("check for a target after myObject")
    
    else: # single word input
        
        print("handling single word input")
        # check if it is a valid command
        
        # if it is append it to returned_cmds
        
    
    # RETURN all of the things!!
#    return cmd, obj, tgt
    return returned_cmds, obj, tgt



def useObject(cmd, cmd2, obj, tgt, obs): # generic Object handler
    
    # Resetting values
    oInfo = []
      
    # check against a singleton action command entry
    if obj != None:
        
        # Check for a target
        if tgt != None:
            
            # consolidate from inputTokenized array
            theTgt = tgt[0]
            if len(tgt) > 1:
                j = 1
                for i in range(len(tgt)-1):
                    theTgt += ' '
                    theTgt += tgt[j]
                    j += 1
        
        # Check obj is an array (and not a dumb string)
        if type(obj) != str:
            
            # consolidate obj reference (from "obj" : inputTokenized array)
            theObj = obj[0]
            if len(obj) > 1:
                j = 1
                for i in range(len(obj)-1):
                    theObj += ' '
                    theObj += obj[j]
                    j += 1
        
        else:
            
            # object was referenced with no action command
            # handle feedback below
            theObj = obj

        # check if location has any objects (data)
        if len(obs) > 0:
            
            # check the object exists in this location
            missing_object = True
            for o in obs:
                if theObj in o['refs']:
                    
                    #collate available commands for obj
                    for k, v in o.items():
                        #match any of "getCmds-OK, putCmds-OK" etc
                        if 'OK' in k: 
                            # limit to only the allowed cmds
                            if len(v) >= 1:
                                for i in range(len(v)):
                                    oInfo.append(v[i])
                            else:
                                # extract name-string of command list
                                # and get all cmds in that command list
                                w = k[:-3] 
                                a = eval("gD."+w)
                                for i in range(len(a)):
                                    oInfo.append(a[i])

                    
                    ### == GENERAL OBJECT COMMANDS ==========================
                    
                    if cmd == "look at":
                        renderers.render_Text(o['desc'], 'look at')
        
                    elif cmd == "examine":
                        #add name to oInfo for renderer
                        oInfo.append(o['name'])
                        
                        renderers.render_Text(oInfo, 'examine')
                            
                    ### == ACTION OBJECT COMMANDS ==========================
                    
                    # check legal action for the object
                    elif cmd in oInfo:
                          
                        # get command add object to inventory
                        # check all get aliases
                        for i in gD.ACTCMDS['getCmds']:
                            if cmd == i:
                                
                                # remove obj from inv
                                if tfs.updateInventory(o, "add") != False:
                                
                                    # render feedback to player
                                    renderers.render_objectActions(o, cmd, "get-take")
                                    
                                    ### INCOMPLETE NEED TO call
                                    ## PLAYER INV renderer here
                                    print(gD.PLAYERINV)
                                
                                else:
                                    
                                    # trying to add obj ALREADY in inv
                                    renderers.render_Text(o['name'], 'already in inv')
                                
                        # put command remove object from inventory
                        # check all put aliases
                        for i in gD.ACTCMDS['putCmds']:
                            if cmd == i:
                                
                                # INCOMPLETE don't be specific on 
                                # the item you are dropping if
                                # its not in your inv
                                # as it could be any one of several
                                # items in that inv slot!
                                
                                # remove obj from inv
                                if tfs.updateInventory(o, "remove") != False:
                                
                                    # render feedback to player
                                    renderers.render_objectActions(o, cmd, "put-leave")
                                    
                                    ### INCOMPLETE NEED TO call
                                    ## PLAYER INV renderer here
                                    print(gD.PLAYERINV)
                                    
                                else:
                                    
                                    # trying to remove obj not in inv
                                    renderers.render_Text(o['name'], 'not in inv')
                    
                        # use commands do object custom action
                        if cmd == "use":
                            
                            # check used obj is in player inv
                            if tfs.playerOwns(o) != False:
                            
                                # no target, singleton "use"
                                if theTgt != None:
                                    
                                    ## INCOMPLETE . JUST ALL OF THIS!!
                                    
                                    # check object STATE
                                    objectState(o)
                                    print("2nd command", cmd2)
                                    print("use key on -", theTgt)
                                    #use key on box
                                    
    #                                renderers.render_objectActions(o, cmd, cmd)
                                    
                                    #check correct req obj for obj
                                    
                                    # do something now the obj is used
                                    # for example a box display stuff inside
                                                                
                                else:
                                    
                                    # use key - "use key on what?"
                                    # render feedback to player
                                    renderers.render_objectActions(o, cmd, cmd)
                                    
                            else:
                                # trying to use obj not in inv
                                renderers.render_Text(o['name'], 'not in inv')
                        
                        if cmd == "open":
                            
                            # check if object permissions prevent action
                            can_open = tfs.objPermissions(o)
                            if can_open == "ok":
                                # update object state according to o['state']
                                objectState(o['state'])
                                
                                                                
                                
                            elif can_open == "has-req-obj":
                                # tell player they need to use the req obj
                                renderers.render_objectActions(o, cmd, "has-req-obj")
                                
                            else:
                                # send open-FAIL type and object to renderer
                                t = can_open[0]
                                renderers.render_objectActions(o, cmd, t)
                    
                    elif cmd != None:
                        # must be an illegal command for this object
                        # feedback 'you can't do that to this object'
                        t = "illegal"
                        renderers.render_objectActions(o, cmd, t)
                    
                    ### == NO COMMAND GIVEN ==========================
                    
                    if cmd == None:
                        # User referenced an object WITHOUT putting
                        # an action command - So give them help
                        renderers.render_objectHelp(oInfo, o['name'])
                            
                    # exit this loop, as we have actioned our player input
                    missing_object = False
                    break
                    
            # handle input reference to an object that is not at this loc
            if missing_object == True:
                print('missing object')
                renderers.render_Text(theObj, 'missing object')
    
        else:
            # no objects at all at this loc
            print('no objects')
            renderers.render_Text(theObj, 'missing object')
    
    else:
        # if singleton, show correct actionCmd feedback help
        renderers.render_actionHelp(cmd)
    
    
    
def objectState(o): # what happens after the useObject action is successful?
    
#    print(eval(o))
#    print('' + o)
    test_o = tfs.namestr(o, globals())
    print(gD.World_frame.loc[test_o])
    
    # if o != None
    if len(o) > 0:
        for t in o:
            if t == 'access_to':
                for tt in t:
                    if tt == 'move':
                        # add the new move to the legal moves for the location
                        # render a message to the player about this
                        print("new route available")
                    elif tt == 'object':
                        # add the new object to the objects in the location
                        # render a message to the player about this
                        print("new object visible")
    



          

        
        
        
# def letsFight - fight arena/module - generic combat 



# def worldNav(locJustLeft, locGoingNext)
    # need to know where I have just come from - locJustLeft
    # and where Im travelling to - locGoingNext
    # what happens on exit of this location - look in locDb for leaveConditions
    # what happens on entry on next location - look in locDb for entryConditions
    # what updates to storyProgression and charProgression and charInventory and charHome
    



