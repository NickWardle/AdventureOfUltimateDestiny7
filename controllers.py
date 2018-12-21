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

def buildPrompt(t, d=None):
    
    print("t", t, "d", d)
    
    if t == 'default':
        return renderers.render_prompt(gD.LOCDATA['locInputDesc'], 'default prompt')
    
    elif t == 'did you mean':
        return renderers.render_prompt(d, 'did you mean')
    

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
      

def tokenizeInput(inp): # tokenise the input
    
    outputTokens = word_tokenize(inp)
    
    # strip out all 'ignored words' to REDUCE inputTokenized
    rm_list = []
    for w in outputTokens:
        if w in gD.ignoreWords:
            rm_list.append(w)
    
    for r in rm_list:
        outputTokens.remove(r)
    
    return outputTokens


def cmdDidYouMeanThis(tks, pdl): # check with player what input actually was
    
    # get first 'cmd' in parsed_list of cmds
    c_lst = []
    for a, b in pdl.items():
        c_lst.append(a)
        
    c_pos = c_lst[0][3:]
    c_pos = int(c_pos) - 1
    
    # remove all tokens from inputTokenized list before first
    # parsed_cmd index    
    new_tokens = tks[c_pos:]
    user_conf = ' '.join(new_tokens)
    
    # return sanitised input and setup confirmation request prompt
    print("3. confirm me this", user_conf)
    gD.PROMPT = 'reqconf'
    gD.USERCONF = user_conf

    

def cmdLengthChecker(cmd_mtch, parsed_cmds):

    # verify that the input contains the right number of 
    # cmd words to complete a valid command phrase
    
    if cmd_mtch == None:
        
        # if cmd_mtch is not given, then there is only ONE
        # command word in the input, so the correct length
        # of the valid cmd in the database to match against
        # must be ONE word long
        #
        # So find the command in the parsed_cmds list that 
        # only has ONE word and that is the valid_cmd with 
        # the correct length to return
        
        print("singleton command, checking for length=1 valid commands in", parsed_cmds)
        
        for rf in parsed_cmds['cmd1']:
            rf_elems = rf.split("-")
            
            # count the number of words
            cmd_lst = gD.actionCmds[rf_elems[0]]
            cmd_wrds = cmd_lst[int(rf_elems[1])]
            cmd_len = len(tokenizeInput(cmd_wrds))
            
            if cmd_len == 1:
                
                print("valid command phrase matched:", cmd_wrds, "as", rf)
                return rf
            
        return False
            
    else:
        # if cmd_match is given then check length as normal
        
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
                
                cmd_valid = False
        
            q = q + 1
            
        # if yes, this is our first command
        if cmd_valid == True:
            
            print("valid command phrase matched:", cmd_wrds, "as", cmd_item)
            return cmd_item
        
        else:
            
            return False
        
    

def cmdChecker(tkns, parsed_cmds):
    
    
    if 'cmd1' not in parsed_cmds.keys():
        
        # If parsed_cmds does NOT start with 'cmd1' then the
        # input contained junk words before the command words
        # check with the player what they really wanted to do first
        if gD.PROMPT == False:
            print("2. did you mean this")
            cmdDidYouMeanThis(tkns, parsed_cmds)
            return False
        
        elif gD.PROMPT == 'reqconf': # require Y/N confirmation
            print("only Y/N are valid inputs")
            print("We got", tkns, parsed_cmds)
            gD.PROMPT == False
            return False
            
            
    else: 
        
        # if there is more than one cmd word detected
        if len(parsed_cmds) > 1:
            
            #### NOTE the first command could STILL be a singleton!!! ###
            # which means check_list will be empty (I think)
            # so need to fix this assumption that multiple commands
            # in input are not singletons plus more commands down-the-line
            #####
            
            # check for *sequential* matched cmds lists 
            ii = 1
            check_list = []
            trim_list = []
            for p in parsed_cmds:
                c = "cmd" + str(ii)
                if p == c:
                    # sequential, add to 'check list' and continue..
                    if ii > 1:
                        check_list.append(parsed_cmds[c])
                        trim_list.append(c)
                    ii = ii + 1
                else:
                    # sequence broken
                    cc = "cmd" + str(ii-1)
                    print("sequential matches up to", cc)
            
            
            print("cmds check_list", check_list)
            
            # check if any cmds in any cmd lists in the 'check list'
            # match any other cmds in any of the other cmd lists 
            # *unpack 'check_list' as the arguments of the intersection check
            cmd_mtch = set(parsed_cmds['cmd1']).intersection(*check_list)
            print("matched input against these cmds", cmd_mtch)
            
            # if any matching commands
            if len(cmd_mtch) > 0:
                
                # check if the matched command is the correct length
                # to match a valid command in the database
                valid_cmd = cmdLengthChecker(cmd_mtch, parsed_cmds)
                print("matched cmd is", valid_cmd)
    
                if valid_cmd != False:
                    # RETURN the cmd to be added 
                    # to the list of commands we will return to gameExec
                    return valid_cmd
                else:
                    print("not enough matches to complete command phrase - invalid command")
    
    
    
                #############################################
                ### sometimes this doesn't happen
                ### and it is not running cmdChecker() more than
                ### once. If I want to return more than one matched
                ### command in any single input I need to fix this
                #############################################
                
                # remove these from list and go again
                print("cmd list pre trimming", parsed_cmds)
                    
                trim_list.insert(0, 'cmd1')
                for i in trim_list:
                    parsed_cmds.pop(i)
                
                print("trim list", trim_list)
                print("trimmed remaining cmds", parsed_cmds)
                
                ####AND THEN RUN THROUGH THE MATCHING AGAIN
                ### WITH THE NEW TRUNCATED LIST OF CANDIDATES TO FIND 
                ### SECOND COMMAND GROUPS TO RETURN
                cmdChecker(None, parsed_cmds)
                
            else: # malformed command
                print("that wasn't a valid command")
            
        
        elif len(parsed_cmds) == 1: # only 1 command and it's a singleton
            
            # check if the matched command is the correct length
            # to match a valid command in the database
            valid_cmd = cmdLengthChecker(None, parsed_cmds)
            
            if valid_cmd != False:
                # RETURN the cmd to be added 
                # to the list of commands we will return to gameExec
                print("only one command found", parsed_cmds, "returning this", valid_cmd)
                return valid_cmd
            else:
                print("singleton command found, but is not valid")
            
        else: # parsed_cmds is empty
            
            print("no commands found")



def parseInput(tkns, actns, objs, legalinputs): # extract objects from tokenized input
    
    #### we don't need to pass actns in here once this is
    #### refactored for all command checking (using legalinputs)
    
    parsed_cmds = {}
    returned_cmds = []
    obj = None
    tgt = None
    
    i = 0
    # for each word in the input
    for w in tkns:
        
        i = i + 1
        c = "cmd" + str(i)
        
        ### Need a separate path to handle commands that are not actions
        # bascially need to pass AllLegalInputs from gameExec to here
        # not just aCmds (as actns)
        # and replicate the command parsing from 177 in gameExec
        # not forgetting the multipart command bit at 137
        # so as to take into account pseudo-cmd2 cases
        # format: cmd-obj-'with/on/in'-tgt
        ### This bit needs major amplification
        
        
        ##### GOT TO THIS BIT !!!!!              ##########
        # Now we are passing ALL legal inputs for parsing #
        # we need to not assume that 'cmd1' is an action  #
        # command, as the check_list now includes obj refs #
        # and everything! so, build this out to check     #
        # to check against every type of input and parse #
        # out useful references for handling back in gameExec #
        #############   SIMPLES :)    #######################
        
        
#        for j, k in actns.items():
        for j, k in legalinputs.items():
            # for each cmd in each cmd group
            for l in k:
                # is the word in the cmd group
                if re.search(w, l):
                    # group up matches into 'cmds'
                    c = "cmd" + str(i)
                    # combine cmdgrp name - match index as label
                    ind = j + "-" + str(k.index(l))
                    
                    # build list of MATCHES                        
                    if c in parsed_cmds.keys():
                        parsed_cmds[c].append(ind)
                    else:
                        parsed_cmds[c] = [ind]
                
    
    # Now check that parsed cmds list!
    print("1.", tkns, parsed_cmds)
    good_cmd = cmdChecker(tkns, parsed_cmds)
    
    if good_cmd != None:
        # add successfully found command to what we send back to gameExec
        print("successfully matched this command", good_cmd)
        returned_cmds.append(good_cmd)
    elif good_cmd == False:
        print("USERCONF", gD.USERCONF)
    else:
        print("there were no valid commands matched in the input")
    
        
    # match against OBJECTS ======
    if w in objs:
        obj = w

    # SET myTarget

    print("check for a target after myObject")

    
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
    



