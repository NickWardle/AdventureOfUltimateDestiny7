# -*- coding: utf-8 -*-
"""
Created on Fri Jul 13 09:24:51 2018

@author: nick.wardle
"""
import debugger as de
import gameData as gD
import renderers
import transformers as tfs
import re
from nltk.tokenize import word_tokenize

#import errorHandler

# == INITIALISE DATA =================================================

# get ALL LOCATION DATABASE
locDb = gD.locDb
legalInps = {}

# == CONTROLLERS =================================================
# modules that take inputs from player, or other modules, and update the models

def clearLocData():
    
    gD.LOCDATA = ''

def buildPrompt(t, d=None):
    
#    de.bug("t", t, "d", d)
    
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
        de.bug("Location not in locDb")
    
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
        
    # handle empty c_lst - which could mean that the input was NONE
    # i.e. player probably just pressed RETURN
    if len(c_lst) > 0:
        # get an integer for every cmd+n keys in parsed list
        c_pos = c_lst[0][3:]
        c_pos = int(c_pos) - 1
    
        # remove all (junk word) tokens from inputTokenized list that appear 
        # before the first valid parsed_cmd     
        new_tokens = tks[c_pos:]
        user_conf = ' '.join(new_tokens)
        
        # return sanitised input and setup confirmation request prompt
        de.bug("3. confirm me this", user_conf)
        gD.PROMPT = 'reqconf'
        gD.USERCONF = user_conf
        
    else: # just spawn default PROMPT again
        
        de.bug("no input, just respawn default PROMPT")
        gD.PROMPT = False
        gD.USERCONF = None
    

def cmdLengthChecker(cmd_mtch, parsed_cmds, tkns, legalinputs):

    # verify that the input contains the right number of 
    # cmd words to complete a valid command phrase
    
    if cmd_mtch == None or cmd_mtch == {}:
        
        # if cmd_mtch is not given, then there is only ONE
        # command word in the input, so the correct length
        # of the valid cmd in the database to match against
        # must be ONE word long
        #
        # So find the commands in the parsed_cmds list that 
        # only have ONE word and then check if the single word player
        # input and any of those commands match exactly
        
        de.bug("singleton command, checking for length=1 valid commands in", parsed_cmds)
        
        for ky, va in parsed_cmds.items():
            for rf in va:
                rf_elems = rf.split("-")
                
                # find the appropriate cmd_list
                for a, b in legalinputs.items():
                    if rf_elems[0] == a:
                        cmd_wrds = b[int(rf_elems[1])]
                            
                # count the number of words in the command
                cmd_wrds_len = len(tokenizeInput(cmd_wrds))
                
                # we are only interested in one word commands               
                if cmd_wrds_len == 1:
                    # does input match command word?
                    if tkns[0] == cmd_wrds:
                        de.bug("valid command phrase matched:", tkns[0], "as", cmd_wrds, "returning ref", rf)
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
        de.bug("cmd wrds '", cmd_wrds, "' cmd len", cmd_len)
        
        # require this many sequential parsed_cmds.keys() matches
        q = 1
        cmd_valid = True
        while q <= cmd_len:
            
            # increment through each "cmd+n"
            myKey = "cmd" + str(q)
            
            #check we haven't just run out of cmds
            if myKey in parsed_cmds.keys():
                
                if cmd_item not in parsed_cmds[myKey]:
                    de.bug("missing in", myKey)
                    cmd_valid = False
            
            else: # failed to match full length, invalid command
                
                cmd_valid = False
        
            q = q + 1
            
        # if yes, this is our first command
        if cmd_valid == True:
            
            de.bug("valid command phrase matched:", cmd_wrds, "as", cmd_item)
            return cmd_item
        
        else:
            
            return False
        
        
    

def wrdChecker(tkns, parsed_cmds, legalinputs, key_num=1):
    
    # If parsed_cmds does NOT have a 'xxx'+key_num then the
    # input probably contained junk words before the commands
    # check with the player what they really wanted to do first
    # and automatically resend commands if correct to do so
    junk_wrds = False
    for k in parsed_cmds.keys():
        de.bug("checking for junk words", str(key_num), k[-1])
        if str(key_num) in k[-1]:
            break
        else:
            junk_wrds = True
    
    # handle finding junk words (above) or second pass as a "reqconf"
    if junk_wrds == True or gD.PROMPT == 'reqconf':
        
        if gD.PROMPT == False:
            cmdDidYouMeanThis(tkns, parsed_cmds)
            # return both p_cmds and good_cmd as False to parseInput()
            return False, False
        
        elif gD.PROMPT == 'reqconf': # require Y/N confirmation
            
            if tkns[0].lower() == "y": # if y or Y entered
                gD.PROMPT = 'autoresend'
                
            else: # if anything else treat it as a NO (bcoz 'n' = 'north')
                gD.USERCONF = None
                gD.PROMPT = False
            
            # return both p_cmds and good_cmd as False to parseInput()
            return False, False
            
    else: # check parsed_cmds as normal
        
        # if there is more than one potential match found
        if len(parsed_cmds) > 1:
            
            #### PROBLEM ##################################
            # the first command could STILL be a singleton!!! ###
            # which means cmd_check_list will be empty (I think)
            # so need to fix this assumption that multiple commands
            # in input are not singletons plus more commands down-the-line
            #####
            
            # check for *sequential* matched cmds lists
            # and record first occurences of matches for each cmd type
            # starting with the dict key called xxx'key_num'
            # to allow for multiple parsing of trimmed parsed_cmds dicts
            ii = key_num
            cmd_check_list = []
            mov_check_list = []
            obj_check_list = []
            firsts = {'c':None, 'm':None, 'o':None}
            trim_list = []
            for p in parsed_cmds:
                m = "mov" + str(ii)
                c = "cmd" + str(ii)
                o = "obj" + str(ii)
                if p == c:
                    # record first occurence of a 'cmd'
                    if firsts['c'] == None:
                        firsts['c'] = ii
                    # sequential, add to 'check list' and continue..
                    elif ii > firsts['c']:
                        cmd_check_list.append(parsed_cmds[c])
                        trim_list.append(c)
                    ii = ii + 1
                    
                elif p == m:
                    # record first occurence of a 'mov'
                    if firsts['m'] == None:
                        firsts['m'] = ii
                    # sequential, add to 'check list' and continue..
                    elif ii > firsts['m']:
                        mov_check_list.append(parsed_cmds[m])
                        trim_list.append(m)
                    ii = ii + 1
                    
                elif p == o:
                    # record first occurence of a 'obj'
                    if firsts['o'] == None:
                        firsts['o'] = ii
                    # sequential, add to 'check list' and continue..
                    elif ii > firsts['o']:
                        obj_check_list.append(parsed_cmds[o])
                        trim_list.append(o)
                    ii = ii + 1
                    
                else:
                    # no sequential matches found, or sequence was broken
                    cc = "match" + str(ii-1)
                    if (ii-1) > 1:
                        de.bug("sequential matches up to", cc)
                    else:
                        de.bug("command is a singleton with multiple potential matching commands. Need to check word length")
                        
            de.bug("firsts", firsts)            
            # check if any cmds in any cmd lists in the 'check list'
            # match any other cmds in any of the other cmd lists 
            # *unpack 'cmd_check_list' as the arguments of the intersection check
            
            cmd_mtch_c = {}
            cmd_mtch_m = {}
            cmd_mtch_o = {}
            
            if len(cmd_check_list) > 0:
                c_key = 'cmd' + str(firsts['c'])
                cmd_mtch_c = set(parsed_cmds[c_key]).intersection(*cmd_check_list)
            
            if len(mov_check_list) > 0:
                m_key = 'mov' + str(firsts['m'])
                cmd_mtch_m = set(parsed_cmds[m_key]).intersection(*mov_check_list)
                
            if len(obj_check_list) > 0:
                o_key = 'obj' + str(firsts['o'])
                cmd_mtch_o = set(parsed_cmds[o_key]).intersection(*obj_check_list)
            
            
            de.bug("matched input against these cmds", cmd_mtch_c, cmd_mtch_m, cmd_mtch_o)
            
            # for ANY matching commands
            cmd_mtchs = [cmd_mtch_c, cmd_mtch_m, cmd_mtch_o]
            for ls in cmd_mtchs:
                # check if the matched command is the correct length
                # to match a valid command in the database
                valid_cmd = cmdLengthChecker(ls, parsed_cmds, tkns, legalinputs)
                de.bug("after cmdLengthChecker() matched cmd is", valid_cmd)
                
                
                ###### GOT TO HERE   ###################
                # Is this the right place to return??
                # how does trim_list get triggered?
                # should we trim back in parseInput? might be
                # better to be honest.. then we just return 
                # parsed_cmds to parseInput and go from there
                # OR ########################
                # trim here and then 
                # need to return the trimmed_list to parse_Input
                # so we can decide to go again on wrdChecker() or not
                ##########################################
                
                if valid_cmd != False:
                    # RETURN the cmd to be added 
                    # to the list of commands we will return to gameExec
                    return parsed_cmds, valid_cmd
                else:
                    de.bug("not enough matches to complete command phrase - invalid command")
                    return parsed_cmds, valid_cmd
                
            else: # malformed command
                de.bug("that wasn't a valid command")
            
        
        elif len(parsed_cmds) == 1: # only 1 command and it's a singleton
            
            # check if the matched command is the correct length
            # to match a valid command in the database
            valid_cmd = cmdLengthChecker(None, parsed_cmds, tkns, legalinputs)
            
            if valid_cmd != False:
                # RETURN the cmd to be added 
                # to the list of commands we will return to gameExec
                de.bug("only one command found", parsed_cmds, "returning this", valid_cmd)
                return parsed_cmds, valid_cmd
            else:
                de.bug("singleton command found, but is not valid")
                return parsed_cmds, valid_cmd
            
        else: # parsed_cmds is empty
            
            de.bug("no commands found")
#            return parsed_cmds



def parseInput(tkns, legalinputs): # extract objects from tokenized input
    
    parsed_cmds = {}
    returned_cmds = []
    p_cmds = {}
    good_cmd = None
    obj = None
    tgt = None
    type_track = []
    
    i = 0
    # for each word in the input
    for w in tkns:
        
        i = i + 1
        
        ### Need a separate path to handle commands that are not actions
        # bascially need to pass AllLegalInputs from gameExec to here
        # not just aCmds (as actns)
        # and replicate the command parsing from 177 in gameExec
        # not forgetting the multipart command bit at 137
        # so as to take into account pseudo-cmd2 cases
        # format: cmd-obj-'with/on/in'-tgt
        ### This bit needs major amplification
        ### Might be better to "handle" the commands in a separate function
        # called on ln149 in gameExec
        
        ################### PROBLEM #####################
        # "up there" doesn't work properly              
        #################################################
        
        # check against every type of input and parse 
        # out useful references for handling back in gameExec  
        
        for j, k in legalinputs.items():
            # for each cmd in each cmd group
            for l in k:
                # is the word in the cmd group
                if re.search(w, l):
                    
                    # complex bit: if the type of command changes
                    # between m, o, and c for the SAME word in tkns
                    # artificially bump i to avoid duplicate index numbers
                    type_track.append(j)
                    if len(type_track) > 1:
                        # match back for 'm'
                        if type_track[len(type_track)-1] == 'm':
                            if type_track[len(type_track)-2] != 'm':
                                i = i + 1
                        # match back for 'o'                           
                        if type_track[len(type_track)-1] == 'o':
                            if type_track[len(type_track)-2] != 'o':
                                i = i + 1
                        # match back for neither 'm' or 'o'
                        if type_track[len(type_track)-1] != 'o':
                            if type_track[len(type_track)-1] != 'm':
                                if type_track[len(type_track)-2] == 'o' or type_track[len(type_track)-2] == 'm':
                                    i = i + 1
                    
                    # handle each of the command types
                    # because move and object don't have
                    # explicit labels for j, unlike cmds
                    if j == "m":
                        c = "mov"
                    elif j == "o":
                        c = "obj"
                    else:
                        c = "cmd"
                    
                    ####### PROBLEM #########################
                    # calling things cmd1 and obj3 is 
                    # confusing because the number is the 
                    # position of the token, not the number of
                    # occurences of that type of command/object
                    # ############
                    # Need to change it to: 1-cmd and 3-obj
                    # for all cmds and then find the places that 
                    # strip an index off (like in wrdChecker for junk 
                    # words) and re-do the index stripping code

                    
                    # combine cmdgrp name - match index as label
                    c = c + str(i)

                    ###### PROBLEM ############################
                    # this works fine for commands, but not objects
                    # simply iterating through and labelling 
                    # every object word found as o-1, o-2, o-3
                    # is not helpful. Need to send the list to 
                    # an ObjectChecker at this point and then
                    # return a valid list of objects for the 
                    # location or the player inventory
                    #
                    
                    ##### GOT TO HERE NUMBER TWO ###########
                    # But I think I need to start here really !! 
                    ###### SUGGESTION #######################
                    # Rename myTarget in gameExec to myVia
                    # so that you have a CMD that affects an OBJ
                    # with an optional VIA
                    # e.g. open the box with the red key
                    # myCmd = open
                    # myObj = box
                    # myVia = red key
                    # e.g. put the red key in the box
                    # myCmd = put
                    # myObj = red key
                    # myVia = box
                    
                    # combine j and the index of k as valid
                    # matching cmds
                    
                    ind = j + "-" + str(k.index(l))
                    
                    # build list of MATCHES                        
                    if c in parsed_cmds.keys():
                        parsed_cmds[c].append(ind)
                    else:
                        parsed_cmds[c] = [ind]
                
        ########### REMOVE THIS ONCE SECOND PARSING IS WORKING #########
        # as this will find all objects and Targets instead
        
        # find the object(s)
#        if w in legalinputs['o']:
#            de.bug("object is", w)
#            obj = w

        # SET myTarget
#        de.bug("check for a target after myObject")
        
        ###############################################################
        
    # Now check that parsed cmds list!
    # If this is the first time we have parsed the input then just do this
    de.bug("1.", tkns, parsed_cmds)
    if len(parsed_cmds) > 0:
        p_cmds, good_cmd = wrdChecker(tkns, parsed_cmds, legalinputs)
    
    de.bug(">>>>> wrdChecker() returned this", p_cmds, "and", good_cmd)
    
    #######################################################
    #######################################################
    #######################################################
    ######################### WAIT A MINUTE ###############
    #######################################################
    #######################################################
    #######################################################

    # we should be trimming the tkns
    # not the parsed_cmds
    # and sending through any tkns that have not yet been
    # processed and categorised by wrdChecker()
    

    # so we need to put each TOKEN into a dict
    # parsed_tkns = {'get': True, 'key': False}
    # and change the flag each time a tkn gets categorised
    # when all values are True, 
    # return cmd(s), obj, trgt
    
    
    
    #######################################################
    #######################################################
    
    
    # but if it is a second parse then check parsed_Cmds length
    # then trim parsed_cmds
    ##### PROBLEM ######################################
    # How do we know which ones to trim?
    # How do we know which ones were checked against and an be trimmed?
    # Keep a list of the checked ones? and send here?
    # or trim in wrdChecker() with that list? and send the trimmed
    # parsed_cmds list back. Easier, no?
    ########################################################
     # remove these from list and go again
#                de.bug("cmd list pre trimming", parsed_cmds)
#                    
#                ### ASSUMPTION HERE it will be cmd1, could be mov1 or obj1
#                trim_list.insert(0, 'cmd1')
#                for i in trim_list:
#                    parsed_cmds.pop(i)
#                
#                de.bug("trim list", trim_list)
#                de.bug("trimmed remaining cmds", parsed_cmds)
     ###############################
    # then find the new lowest key number in parsed_cmds
    # find the NEW lowest numbered cmd/obj/mov in 
                # the trimmed parsed_cmds dict
#                n = 1
#                for k in parsed_cmds.keys():
#                    if str(n) in k[-1]:
#                        de.bug("found lowest numbered key", k)
#                    else:
#                        n += 1
    # and then send to wrdChecker() again with key_num as last param
    
    # wrdChecker(None, parsed_cmds, legalinputs, n)
    
    # if len(parsed_cmds) == 0:
    # then do the next bit returning all the values to gameExec
    
    
    if good_cmd == False:
        de.bug("USERCONF", gD.USERCONF)
        de.bug("PROMPT", gD.PROMPT)
    elif good_cmd != None:
        # add successfully found command to what we send back to gameExec
        de.bug("successfully matched this command", good_cmd)
        returned_cmds.append(good_cmd)
    
    else:
        de.bug("there were no valid commands matched in the input")
    
    ########################################
    # Note: I removed obj finding code above here. obj always == None
    # RETURN all of the things!!
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
                                    de.bug("2nd command", cmd2)
                                    de.bug("use key on -", theTgt)
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
                de.bug('missing object')
                renderers.render_Text(theObj, 'missing object')
    
        else:
            # no objects at all at this loc
            de.bug('no objects')
            renderers.render_Text(theObj, 'missing object')
    
    else:
        # if singleton, show correct actionCmd feedback help
        renderers.render_actionHelp(cmd)
    
    
    
def objectState(o): # what happens after the useObject action is successful?
    
#    de.bug(eval(o))
#    de.bug('' + o)
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
                        de.bug("new route available")
                    elif tt == 'object':
                        # add the new object to the objects in the location
                        # render a message to the player about this
                        de.bug("new object visible")
    



          

        
        
        
# def letsFight - fight arena/module - generic combat 



# def worldNav(locJustLeft, locGoingNext)
    # need to know where I have just come from - locJustLeft
    # and where Im travelling to - locGoingNext
    # what happens on exit of this location - look in locDb for leaveConditions
    # what happens on entry on next location - look in locDb for entryConditions
    # what updates to storyProgression and charProgression and charInventory and charHome
    



