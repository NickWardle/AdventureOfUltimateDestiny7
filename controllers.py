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
        # get an integer for every n+-cmd keys in parsed list
        c_pos = c_lst[0][0]
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
    
    if type(cmd_mtch) == list:
        
        # If the object to be checked is a list (not a set{})
        # then it is a singleton and we only need to find the commands 
        # in the list that only have ONE word and then check if the 
        # tokenised single word player input and any of those commands 
        # match exactly
        
        de.bug("singleton command, checking for length=1 valid commands in", cmd_mtch)
                
        for rf in cmd_mtch:
            rf_elems = rf.split("-")
            
            # find the appropriate cmd_list in legalinputs
            for a, b in legalinputs.items():
                if rf_elems[0] == a:
                    cmd_wrds = b[int(rf_elems[1])]
                        
            # count the number of words in the command
            cmd_wrds_len = len(tokenizeInput(cmd_wrds))
            
            # we are only interested in one word commands               
            if cmd_wrds_len == 1:
                # does the player input match any single command word?
                for t in tkns:
                    if t == cmd_wrds:
                        de.bug("valid command phrase matched:", t, "as", cmd_wrds, "returning ref", rf)
                        return rf
                
        return False
            
    else:
        # if cmd_match is not a list then check each item in the set
        # to see if they share a multi-word command
        
        for cmd_item in cmd_mtch:
            
            # get the actual command-tokened words
            cmd_elems = cmd_item.split("-")
            
            # handle each of the types of command
            if (cmd_elems[0] == 'o') or (cmd_elems[0] == 'm'):
              cmd_lst = legalinputs[cmd_elems[0]]
            else:
             cmd_lst = gD.actionCmds[cmd_elems[0]]
            
            if cmd_elems[0] == 'o':
                suf = "-obj"
            elif cmd_elems[0] == 'm':
                suf = "-mov"
            elif cmd_elems[0] == 'conJuncts':
                suf = "-jun"
            else:
                suf = "-cmd"
            
            # count the number of words
            cmd_wrds = cmd_lst[int(cmd_elems[1])]
            cmd_len = len(tokenizeInput(cmd_wrds))
            de.bug("cmd wrds '", cmd_wrds, "' cmd len", cmd_len)
            
            # require this many sequential parsed_cmds.keys() matches
            q = 1
            cmd_valid = True
            while q <= cmd_len:
                
                # increment through each "n-suffix"
                myKey = str(q) + suf
                de.bug("check this key", myKey)
                
                #check we haven't just run out of cmds
                if myKey in parsed_cmds.keys():
                    
                    if cmd_item not in parsed_cmds[myKey]:
                        de.bug("missing in", myKey)
                        cmd_valid = False
                
                else: # failed to match full length, invalid command
                    
                    cmd_valid = False
            
                q = q + 1
                
            # if yes, this is a valid command
            if cmd_valid == True:
                
                de.bug("valid command phrase matched:", cmd_wrds, "as", cmd_item)
                return cmd_item
                
                # no need to check further cmd_items
                break

        
        
    

def wrdChecker(tkns, parsed_cmds, legalinputs, key_num=1):
    
    # If parsed_cmds does NOT have a 'xxx'+key_num then the
    # input probably contained junk words before the commands
    # check with the player what they really wanted to do first
    # and automatically resend commands if correct to do so
    
    junk_wrds = False
    for k in parsed_cmds.keys():
        de.bug("checking for junk words", str(key_num), k[0])
        if str(key_num) in k[0]:
            break
        else:
            junk_wrds = True
    
    # handle finding junk words (above) or second pass as a "reqconf"
    if junk_wrds == True or gD.PROMPT == 'reqconf':
        
        if gD.PROMPT == False:
            cmdDidYouMeanThis(tkns, parsed_cmds)
            # return matched_cmds as False to parseInput()
            return False
        
        elif gD.PROMPT == 'reqconf': # require Y/N confirmation
            
            if tkns[0].lower() == "y": # if y or Y entered
                gD.PROMPT = 'autoresend'
                
            else: # if anything else treat it as a NO (bcoz 'n' = 'north')
                gD.USERCONF = None
                gD.PROMPT = False
            
            # return matched_cmds as False to parseInput()
            return False
            
    else: # check parsed_cmds as normal
        
        # create an empty list for matched valid_cmds for THIS PASS
        valid_cmds = []
        
        # if there is more than one potential match found
        if len(parsed_cmds) > 1:
            
            # check for string matches in sequential cmd-lists, because these might be two-word entities (or two seperate entities)
            check_array = []
            known_cmds = [] 
            parsed_matches = []
            check_start_index = 0
            sequence = 0
            
            for p, q in parsed_cmds.items():
                de.bug("FOR LOOP: we are at", q)
                
                # put current cmd-list into a check array
                check_array.append(q)
                de.bug("1. current check array", check_array)
                
                # check to see if the check array slice has more than one item in it
                if len(check_array) > 1:
                    # Check if the item we just added has anything 
                    # similar in to the any of the other items in the 
                    # check list back as far as the check-start-index
                    check_array_slice = check_array[check_start_index:]
                    de.bug("2. compare check array from this start point", check_start_index, check_array_slice)
                    for itm in check_array_slice:
                        de.bug("3. items in sequence so far", sequence)
                        found_match = set(check_array_slice[len(check_array_slice)-1]).intersection(itm)
                        if len(found_match) > 0 and q != itm:
                            # if it does
                            de.bug("4. check for a match and found something", found_match)
                            sequence += 1
                            
                            # no need to check further
                            break
                        
                        else:
                            de.bug("4. nothing matching found")
                            
                            if sequence == 1:
                                # add the command/object one less than the current list 
                                # length to the list of known commands to return
                                de.bug("5.", check_array_slice[len(check_array_slice)-2], "must be a singleton")
#                                known_cmds.append(check_array_slice[len(check_array_slice)-2])
#                                de.bug("6. adding it to known_cmds", known_cmds)
                                parsed_matches.append(check_array_slice[len(check_array_slice)-2])
                            
                                # clean last element off check_array
                                check_array.pop(len(check_array)-2)
                                de.bug("7. removed it from check array", check_array)
    
                            else:
                                de.bug("4-i. But what was sequence at this point?", sequence)
                                st = ((len(check_array)-1)-sequence)
                                en = len(check_array)-1
                                parsed_matches.append(check_array[st:en])
                                sequence = 1
                                de.bug("reset sequence to", sequence)
                                
                            
                            # set a new check-start-index as the length-1 of the check list
                            check_start_index = check_array.index(check_array_slice[len(check_array_slice)-1])
                            de.bug("8. new check start index", check_start_index)
                            
                            #no need to continue checking
                            break
                
                else:
                    de.bug("2. nothing to compare", check_array)
                    sequence += 1
            
                # increment to next item
            
            ### PARSING COMPLETE - POST FOR-LOOP CLEAN UP TIME ###############
            # If sequence > 1, we need to manually add the last multi-group to the master list
            # because the FOR loop finished before that happened
            if sequence > 1:
                st = len(check_array)-sequence
                en = len(check_array)
                parsed_matches.append(check_array[st:en])
                
            # If sequence == 1, pop() the last item from check_array
            # and append it to singletons instead, because it doesn't need checking as a 'multiple'
            elif sequence == 1:
                should_be_singleton = check_array.pop()
#                known_cmds.append(should_be_singleton)
                parsed_matches.append(should_be_singleton)
                
            
            # multi-part commands and singletons now in two lists
            de.bug("PARSED_MATCHES ::", parsed_matches)
#            de.bug("Parsing Complete: check these items", check_array)
#            de.bug("we found these singletons we are certain of", known_cmds)

            
############################################################################
            
            ii = key_num
            cmd_check_list = []
            mov_check_list = []
            jun_check_list = []
            obj_check_list = []
            firsts = {'c':None, 'm':None, 'cj':None, 'o':None}
            trim_list = []
            p_recheck = None
            for p in parsed_cmds:
                
                # reset p to previous one if a recheck is required (see else)
                if p_recheck != None:
                    p = p_recheck
                    p_recheck = None
                
                m = str(ii) + "-mov"
                c = str(ii) + "-cmd"
                o = str(ii) + "-obj"
                cj = str(ii) + "-jun"
                de.bug("p", p, "?= c", c, " m", m, " cj", cj, " o", o)
                if p == c:
#                    de.bug("p", p, " c", c)
                    # record first occurence of a 'cmd'
                    if firsts['c'] == None:
                        firsts['c'] = ii
                    # sequential, add to 'check list' and continue..
                    elif ii > firsts['c']:
                        cmd_check_list.append(parsed_cmds[c])
                        trim_list.append(c)
                    
#                    de.bug("list so far", cmd_check_list)
                    
                    # increment to check next item in parsed_cmds
                    ii = ii + 1
#                    de.bug("we are checking", ii, "next")
                    
                elif p == m:
#                    de.bug("p", p, " m", m)
                    # record first occurence of a 'mov'
                    if firsts['m'] == None:
                        firsts['m'] = ii
                    # sequential, add to 'check list' and continue..
                    elif ii > firsts['m']:
                        mov_check_list.append(parsed_cmds[m])
                        trim_list.append(m)
                    
#                    de.bug("list so far", mov_check_list)
                    
                    # increment to check next item in parsed_cmds
                    ii = ii + 1
#                    de.bug("we are checking", ii, "next")
                
                elif p == cj:
#                    de.bug("p", p, " cj", cj)
                    # record first occurence of a 'mov'
                    if firsts['cj'] == None:
                        firsts['cj'] = ii
                    # sequential, add to 'check list' and continue..
                    elif ii > firsts['cj']:
                        jun_check_list.append(parsed_cmds[cj])
                        trim_list.append(cj)
                    
#                    de.bug("list so far", jun_check_list)
                    
                    # increment to check next item in parsed_cmds
                    ii = ii + 1
#                    de.bug("we are checking", ii, "next")
                    
                elif p == o:
#                    de.bug("p", p, " o", o)
                    # record first occurence of a 'obj'
                    if firsts['o'] == None:
                        firsts['o'] = ii
                    # sequential, add to 'check list' and continue..
                    elif ii > firsts['o']:
                        obj_check_list.append(parsed_cmds[o])
                        trim_list.append(o)
                    
#                    de.bug("list so far", obj_check_list)
                    
                    # increment to check next item in parsed_cmds
                    ii = ii + 1
#                    de.bug("we are checking", ii, "next")
                    
                else:
                    # no sequential matches found, or sequence was broken
#                    cc = ii-1
#                    if cc > 1:
#                        de.bug("sequential matches up to", cc)
#                    else:
#                        de.bug("command is a singleton with multiple potential matching commands. Need to check word length")
                    
                    # increment to check next item in parsed_cmds
                    # the next item in the list will NOT be ++1 it will be 
                    # more than that so we need to get the next key to check 
                    # for from parsed_cmds itself
                    ii = int(p.split("-")[0])
#                    de.bug("ii jumps to", ii, " for next check")
                    
                    # recheck the last item again in the for loop
                    p_recheck = p

                        
#            de.bug("firsts", firsts)     
            
############################################################################
                    
                    
            # find the common cmds in each part of the parsed_matches list 
            # and put them into sets{}
            tmp_list = []
            final_candidates = []
            parsed_final = []
            match_candidates = {}
            
            for grp in parsed_matches:
                for i in grp:
                    # check the item is not a single word
                    if type(i) is list:
                        # concat all lists together to de-dupe later
                        tmp_list.extend(i)
                    else:
                        # just add the grp for singleton wrdLengthChecking later
                        final_candidates.append(grp)
                        break
                        
                # de-dupe list using this set{} function
                if tmp_list != []:
                    match_candidates = set([x for x in tmp_list if tmp_list.count(x) > 1])
                    final_candidates.append(match_candidates)
                    tmp_list = []
                
                    
            de.bug("final de-duped matches", final_candidates)
            
            # ONLY need to send set()s in final_candidates that have len > 1
            # to the lengthchecker, because we know ALREADY KNOW the others :)
            
            for s in final_candidates:
                if len(s) > 1:
                    de.bug("NEW LOOP sending this to lengthChecker", s)
                    valid = cmdLengthChecker(s, parsed_cmds, tkns, legalinputs)
                    de.bug("NEW LOOP after cmdLengthChecker() matched cmd is", valid)
                    
                    if valid != False:
                        # Add cmd to the list of commands we will return to gameExec
                        known_cmds.append(valid)
#                        valid_cmds.append(valid)
                        de.bug("found this valid cmd", valid)
                    else:
                        de.bug("not enough matches to complete command phrase - invalid command:", valid)
                    
                else:
                    
                    # add the item to the list of known_cmds
                    known_cmds.append(*s)
            
            de.bug("ALL KNOWN COMMANDS, in order", known_cmds)        
            
            ###### GOT TO HERE ###############
            # then classify each matched cmd as a type
            # o = obj, m = mov, conJunct = con 
            # else = cmd
            a_cmd = None
            a_obj = None
            a_conJunct = None
            a_via = None
            
            for i in known_cmds:
                els = i.split("-")
                if els[0] == "conJuncts":
                    a_conJunct = i
                elif els[0] == "o":
                    if known_cmds.count(i) > 1:
                        # first one is obj, second one is via
                        de.bug("obj and via present")
                    else:
                        a_obj = i
                else:
                    a_cmd = i
            
            parsed_final.append(a_cmd)
            parsed_final.append(a_obj)
            parsed_final.append(a_conJunct)
            parsed_final.append(a_via)
            
            de.bug("PARSED_FINAL", parsed_final)
#            return parsed_final

                    
                    
                    
############################################################################
            
            
            # check if any cmds in any cmd lists in the 'check list'
            # match any other cmds in any of the other cmd lists 
            # *unpack 'cmd_check_list' as the arguments of the intersection check
            # and put them into sets{} - these are NOT dicts
            
            cmd_mtch_c = {}
            cmd_mtch_m = {}
            cmd_mtch_o = {}
            cmd_mtch_j = {}
            
            if len(cmd_check_list) > 0:
                c_key = str(firsts['c']) + '-cmd'
                cmd_mtch_c = set(parsed_cmds[c_key]).intersection(*cmd_check_list)
            
            if len(mov_check_list) > 0:
                m_key = str(firsts['m']) + '-mov'
                cmd_mtch_m = set(parsed_cmds[m_key]).intersection(*mov_check_list)
                
            if len(jun_check_list) > 0:
                j_key = str(firsts['j']) + '-jun'
                cmd_mtch_j = set(parsed_cmds[j_key]).intersection(*jun_check_list)
                
            if len(obj_check_list) > 0:
                o_key = str(firsts['o']) + '-obj'
                cmd_mtch_o = set(parsed_cmds[o_key]).intersection(*obj_check_list)
            
            
            de.bug("matched input against these cmds", cmd_mtch_c, cmd_mtch_m, cmd_mtch_j, cmd_mtch_o)
            
            # for ANY matching commands
            cmd_mtchs = [cmd_mtch_c, cmd_mtch_m, cmd_mtch_j, cmd_mtch_o]
            
            
            for ls in cmd_mtchs:
                # check if the matched command is the correct length
                # to match a valid command in the database
                                
                valid =cmdLengthChecker(ls, parsed_cmds, tkns, legalinputs)
                de.bug("after cmdLengthChecker() matched cmd is", valid)
                
                if valid != False:
                    # Add cmd to the list of commands we will return to gameExec
                    valid_cmds.append(valid)
                else:
                    de.bug("not enough matches to complete command phrase - invalid command:", valid)
                
                # Return all valid cmds found THIS PASS
                return valid_cmds
            
        elif len(parsed_cmds) == 1: # only 1 command and it's a singleton
            
            # check if the matched command is the correct length
            # to match a valid command in the database
            valid = cmdLengthChecker(None, parsed_cmds, tkns, legalinputs)
            
            if valid != False:
                # RETURN the list of commands we will return to gameExec
                valid_cmds.append(valid)
                de.bug("only one command found", parsed_cmds, "returning this", valid)
            else:
                de.bug("singleton command found, but is not valid")
            
            # Return all valid cmds found THIS PASS
            return valid_cmds
            
        else: # parsed_cmds is empty
            
            de.bug("no commands found")



def parseInput(tkns, legalinputs): # extract objects from tokenized input
    
    parsed_cmds = {}
    matched_cmds = None
    obj = None
    jun = None ### need to add this in as a returnable for conJuncts
    tgt = None ### out of date, this should be via
    type_track = []
    
    i = 0
    # for each word in the input
    for w in tkns:
        
        i = i + 1
        
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
                        # match back for 'c'                           
                        if type_track[len(type_track)-1] == 'c':
                            if type_track[len(type_track)-2] != 'c':
                                i = i + 1
                        # match back for neither 'm' or 'o' or 'c'
                        if type_track[len(type_track)-1] != 'o':
                            if type_track[len(type_track)-1] != 'm':
                                if type_track[len(type_track)-1] != 'c':
                                    if type_track[len(type_track)-2] == 'o' or type_track[len(type_track)-2] == 'm' or type_track[len(type_track)-2] == 'c':
                                        i = i + 1
                     
                    # handle each of the command types
                    # because move and object don't have
                    # explicit labels for j, unlike cmds
                    if j == "m":
                        c = "mov"
                    elif j == "o":
                        c = "obj"
                    elif j == "conJuncts":
                        c = "jun"
                    else:
                        c = "cmd"
                    
                    # combine cmdgrp name - match index as label
                    c = str(i) + '-' + c

                    # combine j and the index of k as valid
                    # matching cmds
                    
                    ind = j + "-" + str(k.index(l))
                    
                    # build list of potential cmd matches
                    # called PARSED_CMDS
                    
                    if c in parsed_cmds.keys():
                        parsed_cmds[c].append(ind)
                    else:
                        parsed_cmds[c] = [ind]
                
    de.bug("Parsed input: tokens", tkns, "and cmds", parsed_cmds)
    
    # Now check the words in that parsed cmds list for matches
    if len(parsed_cmds) > 0:
        matched_cmds = wrdChecker(tkns, parsed_cmds, legalinputs)
    
    de.bug(">>>>> wrdChecker() returned this", parsed_cmds, "and matched these", matched_cmds)
       
    
    if matched_cmds == False:
        de.bug("USERCONF", gD.USERCONF)
        de.bug("PROMPT", gD.PROMPT)
    elif matched_cmds != None:
        # add successfully found command to what we send back to gameExec
        de.bug("successfully matched this command", matched_cmds)
#        returned_cmds.append(matched_cmds)
    
    else:
        de.bug("there were no valid commands matched in the input")
    
    ########################################
    # Note: I removed obj finding code above here. obj always == None
    # RETURN all of the things!!
    return matched_cmds, obj, jun, tgt



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
    



