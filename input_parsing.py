# -*- coding: utf-8 -*-
"""
Created on Fri Jul 13 09:24:51 2018

@author: nick.wardle
"""
import debugger as de
import gameData as gD
import re
from nltk.tokenize import word_tokenize



# == PARSE INPUT =================================================

def tokenizeInput(inp): # tokenise the input
    
    outputTokens = word_tokenize(inp)
    
    # strip out all 'ignored words' to REDUCE inputTokenized
    rm_list = [w for w in outputTokens if w in gD.ignoreWords]
    
    for r in rm_list:
        outputTokens.remove(r)
    
    return outputTokens


def cmdDidYouMeanThis(tks, pdl): # check with player what input actually was
    
    # get first 'cmd' in parsed_list of cmds
    c_lst = [a for a, b in pdl.items()]
    
    # handle empty c_lst - which could mean that the input was NONE
    # i.e. player probably just pressed RETURN
    if len(c_lst) > 0:
        # get an integer for every n+-cmd keys in parsed list
        c_pos = c_lst[0][0]
        c_pos = int(c_pos) - 1
        
        # grab all junk words to let user know they are unrecognised
        unknown_junk = ''
        for i in tks[:c_pos]:
            unknown_junk += str(i)
            if tks.index(i) < len(tks[:c_pos]) - 1:
                unknown_junk += ' '
            
        # remove all (junk word) tokens from inputTokenized list that appear 
        # before the first valid parsed_cmd     
        new_tokens = tks[c_pos:]
        user_conf = ' '.join(new_tokens)
        
        # return sanitised input and setup confirmation request prompt
        de.bug(1, "3. confirm me this", user_conf)
        gD.PROMPT = 'reqconf'
        gD.USERCONF = user_conf
        gD.UNKNOWN_INPUT = unknown_junk
        
    else: # just spawn default PROMPT again
        
        de.bug(1, "no input, just respawn default PROMPT")
        gD.PROMPT = False
        gD.USERCONF = None
        gD.UNKNOWN_INPUT = None
    

def cmdLengthChecker(cmd_mtch, parsed_cmds, tkns):

    # verify that the input contains the right number of 
    # cmd words to complete a valid command phrase
    
    if type(cmd_mtch) == list:
        
        # If the object to be checked is a list (not a set{})
        # then it is a singleton and we only need to find the commands 
        # in the list that only have ONE word and then check if the 
        # tokenised single word player input and any of those commands 
        # match exactly
        
        de.bug(1, "singleton command, checking for length=1 valid commands in", cmd_mtch)
                
        for rf in cmd_mtch:
            rf_elems = rf.split("-")
            
            # find the appropriate cmd_list in allInputRefs
            for a, b in gD.allInputRefs.items():
                if rf_elems[0] == a:
                    cmd_wrds = b[int(rf_elems[1])]
                        
            # count the number of words in the command
            cmd_wrds_len = len(tokenizeInput(cmd_wrds))
            
            # we are only interested in one word commands               
            if cmd_wrds_len == 1:
                # does the player input match any single command word?
                for t in tkns:
                    if t == cmd_wrds:
                        de.bug(1, "valid command phrase matched:", t, "as", cmd_wrds, "returning ref", rf)
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
              cmd_lst = gD.allInputRefs[cmd_elems[0]]
            else:
             cmd_lst = gD.gameDB['actionCmds'][cmd_elems[0]]
            
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
            de.bug(1, "cmd wrds '", cmd_wrds, "' cmd len", cmd_len)
            
            # require this many sequential parsed_cmds.keys() matches
            q = 1
            cmd_valid = True
            while q <= cmd_len:
                
                # increment through each "n-suffix"
                myKey = str(q) + suf
                de.bug(1, "check this key", myKey)
                
                #check we haven't just run out of cmds
                if myKey in parsed_cmds.keys():
                    
                    if cmd_item not in parsed_cmds[myKey]:
                        de.bug(1, "missing in", myKey)
                        cmd_valid = False
                
                else: # failed to match full length, invalid command
                    
                    cmd_valid = False
            
                q = q + 1
                
            # if yes, this is a valid command
            if cmd_valid == True:
                
                de.bug(1, "valid command phrase matched:", cmd_wrds, "as", cmd_item)
                return cmd_item
                
                # no need to check further cmd_items
                break

        

def wrdChecker(tkns, parsed_cmds, key_num=1):
    
    # If parsed_cmds does NOT have a 'xxx'+key_num then the
    # input probably contained junk words before the commands
    # check with the player what they really wanted to do first
    # and automatically resend commands if correct to do so
    
    junk_wrds = False
    for k in parsed_cmds.keys():
        de.bug(1, "checking for junk words", str(key_num), k[0])
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
                gD.UNKNOWN_INPUT = None
            
            # return matched_cmds as False to parseInput()
            return False
            
    else: # check parsed_cmds as normal
        
        # 'global' lists for if / else
        known_cmds = []
        parsed_final = []
        
        # if there is more than one potential match found
        if len(parsed_cmds) > 1:
            
            # check for string matches in sequential cmd-lists, because these might be two-word entities (or two seperate entities)
            check_array = []
            parsed_matches = []
            check_start_index = 0
            sequence = 0
            
            for p, q in parsed_cmds.items():
                de.bug(1, "FOR LOOP: we are at", q)
                
                # put current cmd-list into a check array
                check_array.append(q)
                de.bug(1, "1. current check array", check_array)
                
                # check to see if the check array slice has more than one item in it
                if len(check_array) > 1:
                    # Check if the item we just added has anything 
                    # similar in to the any of the other items in the 
                    # check list back as far as the check-start-index
                    check_array_slice = check_array[check_start_index:]
                    de.bug(1, "2. compare check array from this start point", check_start_index, check_array_slice)
                    for itm in check_array_slice:
                        de.bug(1, "3. items in sequence so far", sequence)
                        found_match = set(check_array_slice[len(check_array_slice)-1]).intersection(itm)
                        if len(found_match) > 0 and q != itm:
                            # if it does
                            de.bug(1, "4. check for a match and found something", found_match)
                            sequence += 1
                            
                            # no need to check further
                            break
                        
                        else:
                            de.bug(1, "4. nothing matching found")
                            
                            if sequence == 1:
                                # add the command/object one less than the current list 
                                # length to the list of known commands to return
                                de.bug(1, "5.", check_array_slice[len(check_array_slice)-2], "must be a singleton")
                                parsed_matches.append(check_array_slice[len(check_array_slice)-2])
                            
                                # clean last element off check_array
                                check_array.pop(len(check_array)-2)
                                de.bug(1, "7. removed it from check array", check_array)
    
                            else:
                                de.bug(1, "4-i. But what was sequence at this point?", sequence)
                                st = ((len(check_array)-1)-sequence)
                                en = len(check_array)-1
                                parsed_matches.append(check_array[st:en])
                                sequence = 1
                                de.bug(1, "reset sequence to", sequence)
                                
                            
                            # set a new check-start-index as the length-1 of the check list
                            check_start_index = check_array.index(check_array_slice[len(check_array_slice)-1])
                            de.bug(1, "8. new check start index", check_start_index)
                            
                            #no need to continue checking
                            break
                
                else:
                    de.bug(1, "2. nothing to compare", check_array)
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
                parsed_matches.append(should_be_singleton)
                
            # all commands now in one list parsed_matches
            de.bug(1, "PARSED_MATCHES ::", parsed_matches)

            # find the common cmds in each part of the parsed_matches list 
            # and put them into sets{}
            tmp_list = []
            final_candidates = []
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
                
                    
            de.bug(1, "final de-duped matches", final_candidates)
            
            # ONLY need to send set()s in final_candidates that have len > 1
            # to the lengthchecker, because we know ALREADY KNOW the others :)
            
            for s in final_candidates:
                if len(s) > 1:
                    de.bug(1, "sending this to lengthChecker", s)
                    valid = cmdLengthChecker(s, parsed_cmds, tkns)
                    de.bug(1, "after cmdLengthChecker() matched cmd is", valid)
                    
                    if valid != False:
                        # Add cmd to the list of commands we will return to gameExec
                        known_cmds.append(valid)
                        de.bug(1, "found this valid cmd", valid)
                    else:
                        de.bug(1, "not enough matches to complete command phrase - invalid command:", valid)
                    
                else:
                    
                    # add the item to the list of known_cmds
                    known_cmds.append(*s)
            
        # single word only inputted
        else:
            
            de.bug(1, "single word command detected")
            for x, y in parsed_cmds.items():
                valid = cmdLengthChecker(y, parsed_cmds, tkns)
                if valid != False:
                    known_cmds.append(valid)
                else: 
                    de.bug("that wasn't a fully formed command, ignoring it")
            
        de.bug(1, "ALL KNOWN COMMANDS, in order", known_cmds)        
        
        # then classify each matched cmd as a type
        # o = obj, m = mov, conJunct = con 
        # else = cmd
        a_cmd = None
        a_obj = None
        a_conJunct = None
        a_via = None
        obj_ls = []
        type_list = [None, None, None, None] # see grammar bit below
        
        for i in known_cmds:
            els = i.split("-")
            if els[0] == "conJuncts":
                a_conJunct = i
                type_list[known_cmds.index(i)] = 'jun'
            elif els[0] == "o":
                # obj and via present
                obj_ls.append(i)
                type_list[known_cmds.index(i)] = 'obj'
            else:
                a_cmd = i
                type_list[known_cmds.index(i)] = 'cmd'
                
        
        de.bug(1, "type_list", type_list)
        
        # assign obj and via
        # COMPLEX GRAMMAR BIT #######
        # if type_list is [cmd, jun, obj] then the obj is actually via
        # e.g. look in the box = look (me) in the box
        # or get in the box = get (me) in the box
        
        if type_list[0] == 'cmd' and type_list[1] == 'jun':
            if len(obj_ls) > 1:
                a_via = obj_ls[1] # ignore second obj in the list
            elif len(obj_ls) == 1:
                a_via = obj_ls[0]
        else:
            if len(obj_ls) > 1:
                a_obj, a_via = obj_ls
            elif len(obj_ls) == 1:
                a_obj = obj_ls[0]
        
        # build and return the correctly ordered variables to gameExec
        parsed_final.extend([a_cmd, a_obj, a_conJunct, a_via])
        de.bug(1, "PARSED_FINAL", parsed_final)
        return parsed_final
        


def parseInput(tkns, legalinputs): # extract objects from tokenized input
    
    parsed_cmds = {}
    matched_cmds = None
    type_track = []
    
    i = 0
    # for each word in the input
    for w in tkns:
        
        i = i + 1
        
        # check against every type of input and parse 
        # out useful references for handling back in gameExec  
        
        for j, k in gD.allInputRefs.items(): # used to be legalinputs.items()
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
                

    de.bug(1, "Parsed input: tokens", tkns, "and cmds", parsed_cmds)
    
    # Now check the words in that parsed cmds list for matches
    if len(parsed_cmds) > 0:
        matched_cmds = wrdChecker(tkns, parsed_cmds)
    
    if matched_cmds == False:
        de.bug(1, "USERCONF", gD.USERCONF)
        de.bug(1, "PROMPT", gD.PROMPT)
        de.bug(1, "UNKNOWN JUNK", gD.UNKNOWN_INPUT)
        matched_cmds = [None, None, None, None]
    elif matched_cmds != None:
        de.bug(1, "successfully matched these commands", matched_cmds)
    else:
        matched_cmds = [None, None, None, None]
        de.bug(1, "there were no valid commands matched in the input")
    
    # RETURN all of the things!!
    return matched_cmds



