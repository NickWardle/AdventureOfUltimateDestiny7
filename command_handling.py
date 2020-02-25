# -*- coding: utf-8 -*-
"""
Created on Fri Jul 13 09:24:51 2018

@author: nick.wardle
"""
import debugger as de
import gameData as gD
import renderers
import transformers as tfs
import controllers as ctrls


# == HANDLING ALL PLAYER COMMANDS =========================================
# modules that take inputs from player, or other modules, and update the models


def doCommand(cmd, obj, jun, via, legalInputs, uiData):
    
    if cmd != None:
    
        # we only need to identify the TYPE of cmd
        # so we can action the correct function next
        cmd_spl = cmd.split("-")
        cmd_ky = cmd_spl[0]
        my_cmd = legalInputs[cmd_spl[0]][int(cmd_spl[1])]
        
        if cmd_ky == "m": # MOVEMENT command
            
            for i in gD.gameDB['moveCommandsDB'][gD.LOCDATA['moveCmds']]:
                for j in i[0]:
                    if my_cmd == j:
                        moveDesc = i[1]
                        if len(i) > 2:
                            moveDest = i[2]
                        else:
                            de.bug("this cmd doesn't change our location")
            
            # show moveDesc feedback for moveCmd
            ctrls.printText(moveDesc, "move")            
            
            # if associated locID for moveCmd - ctrls.changeLoc
            ctrls.changeLoc(moveDest)
            
            
        elif cmd_ky in gD.gameDB['uiCmds'].keys(): # UI command
            
            # send to uiActions to handle the UI command
            uiActions(cmd, obj, jun, via, legalInputs, uiData)
            
            
        elif cmd_ky in gD.gameDB['actionCmds'].keys(): # ACTION command
            
            de.bug(2, "locDATA", gD.LOCDATA)
            
            # send the cmd and the obj to useObject for more detailed handling
            useObject(cmd, obj, jun, via, legalInputs)
            
        else: # Command not known
            
            de.bug("Error (doCommand): The command", cmd, "is not handled yet")
        
    elif obj != None: # empty cmd but we have a singleton obj
        
        # send to useObject anyway to give Player object help feedback
        useObject(cmd, obj, jun, via, legalInputs)
            
    else: # Too many params are None to do anything useful
        
        return False
    


def uiActions(cmd, obj, jun, via, inps, uiData): # generic UI cmd handler
    
    # Resetting values
    my_cmd = None
    
    # check for singleton object with no command (show help if it is)
    if cmd != None:
        
        # consolidate cmd reference word
        c_elems = cmd.split("-")
        my_cmd = inps[c_elems[0]][int(c_elems[1])]

    # render the appropriate user feedback message for the cmd
    if my_cmd in gD.gameDB['uiCmds']['playerCmds']:
        
        if my_cmd == "inv" or my_cmd == "inventory":
            
            renderers.render_charInventory()

    elif my_cmd in gD.gameDB['uiCmds']['generalCmds']: 
        
            # Just print out the message for the UI command
            ctrls.printText(uiData[my_cmd], my_cmd)
        
    else: 
        de.bug("Error (doCommand): command '", my_cmd, "' not found in uiCmds")



def useObject(cmd, obj, jun, via, inps): # generic Object handler
    
    # E.G. cmd: generalCmds-0 | obj: o-7 | jun: conJuncts-2 | via: o-11
    
    # Resetting values
    obs_list = gD.LOCDATA['locObjects']
    obj_cmds = [] # list of all local object valid COMMAND WORDS e.g. "get"
    obs = [] # list of all local OBJECT complete dicts {}
    found_objects = [] # list of any objects matched to user input
    cmd_ref = None
    obj_ref = None
    via_ref = None
    jun_ref = None
    obj_id = None
    this_obj = None
    this_via = None
    missing_object = True
    
    
    
    # CONSOLIDATE REFERENCE WORDS IN USER INPUT
    
    if cmd != None:
        c_elems = cmd.split("-")
        cmd_ref = inps[c_elems[0]][int(c_elems[1])] # inps is legalInputs

    if via != None:
        v_elems = via.split("-")
        via_ref = gD.allInputRefs[v_elems[0]][int(v_elems[1])] # ALL possible
        for u, v in gD.gameDB['objectsDB'].items():
            if via_ref in v['refs']:
                via_id = u # set script global via_id for refs to gD.gameDB
                this_via = v # set script global this_via for other functions
        
    if jun != None:
        j_elems = jun.split("-")
        jun_ref = inps[j_elems[0]][int(j_elems[1])]

    if obj != None:
        o_elems = obj.split("-")
        obj_ref = gD.allInputRefs[o_elems[0]][int(o_elems[1])] # ALL possible
        
        # LOCATE OBJ AND SET OBJECT ID, DESC, LOC ETC.
        
        for dc in obs_list:
            
            # IF OBJ IN USER INPUT PRESENT AT LOCATION
            
            if obj_ref in gD.gameDB['objectsDB'][dc]['refs']:
                obj_id = dc # set script global obj_id for refs to gD.gameDB
                obj_desc = gD.gameDB['objectsDB'][dc]['desc']
                obj_loc = gD.gameDB['objectsDB'][dc]['location']
                
                # set script global this_obj for other functions
                this_obj = gD.gameDB['objectsDB'][obj_id] 
                
                # we found an object!
                missing_object = False
                found_objects.append(obj_id)
                de.bug(5, "Found the", obj_ref, "(", obj_id, ") at the location!")
        
        if obj_id == None:
            
            # IF OBJ IN USER INPUT IN INVENTORY
            
            de.bug(5, "In Player INVENTORY:", gD.PLAYERINV)
            
            for sl, its in gD.PLAYERINV.items():
                for it in its:
                    if obj_ref in it['refs']:
                        obj_desc = it['desc']
                        obj_loc = it['location']
                        
                        # upwards search in gameDB for obj_id, match on desc as that is more unique than refs
                        for ob in gD.gameDB['objectsDB']:
                            if obj_desc in gD.gameDB['objectsDB'][ob]['desc']:
                                obj_id = ob # set script global obj_id for refs to gD.gameDB
                        
                        # set script global this_obj for other functions
                        this_obj = gD.gameDB['objectsDB'][obj_id] 
                        
                        # we found an object!
                        missing_object = False
                        found_objects.append(obj_id)
                        de.bug(5, "Found the", obj_ref, "(", obj_id, ") in Player Inventory!")
                        
        
        # HANDLE MULTIPLE OBJECTS FOUND FROM VAGUE USER INPUT
        
        if len(found_objects) > 1:
            
            de.bug(5, "Found multiple objects for that input:", found_objects)
            
            # get object descriptions
            found_object_descs = []
            for o in found_objects:
                found_object_descs.append(gD.gameDB['objectsDB'][o]['desc'])
            
            # print back human readable object list 
            renderers.render_objectDedupe(found_object_descs, obj_ref)
            
            return
        
                
        # IF OBJ IN USER INPUT NOT FOUND AT LOCATION OR INVENTORY
        
        # handle input reference to an object that is not at this loc
        if missing_object == True:
            de.bug('missing object', obj_ref)
            ctrls.printText(obj_ref, 'missing object') 
            
            # EXIT this function
            
            return False 

        de.bug(3, "this_obj is", this_obj)                    
        de.bug(3, "obj values ref", obj_ref, "id", obj_id, "desc & loc", obj_desc, " ", obj_loc)
    
        # GET ALL COMMANDS FOR THE OBJECT IN THE USER INPUT
        
        for k, v in this_obj.items():
            #match any of "getCmds-OK, putCmds-OK" etc
            if 'OK' in k: 
                # limit to only the allowed cmds
                if len(v) >= 1:
                    for i in range(len(v)):
                        obj_cmds.append(v[i])
                else:
                    # extract name-string of command list
                    # and get all cmds in that command list
                    w = k[:-3] 
                    a = gD.gameDB['actionCmds'][w]
                    for i in range(len(a)):
                        obj_cmds.append(a[i])
                                    
                                    
            # User referenced a VALID object WITHOUT putting
            # an action command - So give them help
            if cmd_ref == None:
                renderers.render_objectHelp(obj_cmds, this_obj['name'])
                return False # exit this function
    

     
    
    ############## COMMANDS THAT REQUIRE NO OBJECT ################
    
    if cmd_ref in gD.gameDB['actionCmds']['exploreCmds'] and via == None:
        
        # give user feedback on their command
        ctrls.printText(None, cmd_ref)
        return True # exit this function, we're done here
    
    
    if via != None:
    
        ### == specific explore COMMANDS: look in / under etc ====   
    
        if cmd_ref in ('look'):
        
            de.bug(4, "We have a VIA UI command!", cmd_ref, jun, via)
            
            # check object access state
            ob_access = tfs.getObjectState(this_via, 'access')
                
            de.bug(4, "ob_access is:", ob_access)
            
            ## check if object permissions prevent action
            if ob_access == "unlocked":
                
                # add the contained items to the game world
                cont_objs = tfs.updateGameObjects(gD.gameDB['objectsDB'][via_id]['state']['contains'], 'add') 
                
                # full or empty container?
                if len(cont_objs) > 0:
                    # feedback to player what they have discovered
                    ctrls.printText([cont_objs, this_via['name']], "contained by")
                else:
                    ctrls.printText(this_via['name'], 'container empty')
                
            elif ob_access == "locked":
                
                # feedback to player about the req object
                renderers.render_objectActions(this_via, cmd_ref, "locked_by")
                
                # does player have the req object?
                this_via_obj = gD.gameDB['objectsDB'][this_via['permissions']['locked_by']]
                if tfs.getInventorySlot(this_via_obj) == False:
                    ctrls.printText(this_via_obj['name'], 'not in inv')
            
            else:
                
                can_look_in = tfs.objPermissions(this_via)
                de.bug(4, "obj perms are", can_look_in)
                
                if can_look_in in ("ok", "unlocked"):
                    
                    # add the contained items to the game world
                    cont_objs = tfs.updateGameObjects(gD.gameDB['objectsDB'][via_id]['state']['contains'], 'add') 
                    
                    # full or empty container?
                    if len(cont_objs) > 0:
                        # feedback to player what they have discovered
                        ctrls.printText([cont_objs, this_via['name']], "contained by")
                    else:
                        ctrls.printText(this_via['name'], 'container empty')
                
                else:
                    
                    # feedback to player about the req object
                    renderers.render_objectActions(this_via, cmd_ref, can_look_in)
                    
                    # does player have the req object?
                    this_via_obj = gD.gameDB['objectsDB'][this_via['permissions']['locked_by']]
                    if tfs.getInventorySlot(this_via_obj) == False:
                        ctrls.printText(this_via_obj['name'], 'not in inv')
                
                
        ### == navigation COMMANDS w/o VIA e.g. 'go in; =========
                                
        elif cmd_ref in ('get', 'go', 'walk'):
                        
            de.bug(3, "We have a VIA movement type of command!", cmd_ref, jun, via)
        
            #TODO: Handle changing location with a cmd, jun, via input
            
            ######### NOT COMPLETE NEED RENDER TEXT TO HANDLE THIS ##
            # Needs to handle changing location using the via  
            ########################################################                   
    
    
    
    ############## COMMANDS THAT NEED AN OBJECT ################
    
    if obj != None:
                    
        ### == examine COMMANDS: look at, examine etc. =============
        
        if cmd_ref == "look at":
            
            d = [this_obj['desc'],tfs.getObjectState(this_obj, s='access')]
#            d.append(this_obj['desc'])
#            d.append(tfs.getObjectState(this_obj, s='access'))
            
            # show object description
            ctrls.printText(d, 'look at')
    
        elif cmd_ref in ("examine", "inspect"):
            # bit of a hack this... add obj name to end of obj_cmds
            # for renderer to .pop() off afterwards
            obj_cmds.append(this_obj['name'])
            
            ctrls.printText(obj_cmds, 'examine')
            

        ### == explore COMMANDS: look for, where etc ===========
        
        elif cmd_ref in ('look for', 'where'):
            
            # show both obj desc and loc together                        
            ctrls.printText([obj_desc, obj_loc], cmd_ref)
            

        ### == get, put, use, int COMMANDS =====================
    
        # check legal action for the object
        elif cmd_ref in obj_cmds:
              
            ### == get command add object to inventory ============
            
            # check all get aliases
            for i in gD.gameDB['actionCmds']['getCmds']:
                if cmd_ref == i:
                    
                    de.bug(4, "this_obj", this_obj)
                    
                    # add obj to inv & ctrls.update_worldState
                    if tfs.updateInventory(this_obj, "add") != False:
                    
                        # render feedback to player
                        renderers.render_objectActions(this_obj, cmd_ref, "get-take")
                        
                        # render the player inventory
                        renderers.render_charInventory()
                        
                        # update child object state & get parent container
                        p = ctrls.update_objectState(obj_id, this_obj, cmd_ref)
                        
                        if p != None:
                            
                            # update parent container (p) state
                            ctrls.update_objectState(obj_id, this_obj, 'un_contain', p)
                            
                        else:
                        
                            # no parent container, update world state instead
                            ctrls.update_worldState([obj_id], this_obj, cmd_ref)
                        
                    
                    else:
                        
                        # trying to add obj ALREADY in inv
                        ctrls.printText(this_obj['name'], 'already in inv')
                    
            
            ### == put command remove object from inventory =========
            
            #TODO: Need a more complex "put ... in... " version where this_obj
            # gets added to a new parent_container, not to local Objects
            # see 'get' above for handling parents vs local world objects
            
            # check all put aliases
            for i in gD.gameDB['actionCmds']['putCmds']:
                if cmd_ref == i:
                    
                    # remove obj from inv
                    if tfs.updateInventory(this_obj, "remove") != False:
                        
                        # is there a VIA object for the action?
                        if via != None: # put something IN somewhere (VIA)
                        
                            # update parent container (via) state
                            ctrls.update_objectState(obj_id, this_obj, 'add', via_id)
                            
                        else: # simple put/drop command
                        
                            # render feedback to player
                            renderers.render_objectActions(this_obj, cmd_ref, "put-leave")
                        
                        # remove the object from the world local objects
                        ctrls.update_worldState([obj_id], this_obj, cmd_ref)
                        
                        # render the player inventory
                        renderers.render_charInventory()
                        
                        
                    else:
                        
                        # trying to remove obj not in inv
                        ctrls.printText(this_obj['name'], 'not in inv')
        
            
            ### == use command do object custom action =============
            
            if cmd_ref == "use":
                
                # check used obj is in player inv
                if tfs.getInventorySlot(this_obj) != False:
                
                    # no target, singleton "use"
                    if via != None:
                        
                        #TODO: The USE command and results of it
                        
                        ## INCOMPLETE . JUST ALL OF THIS!!
                        
                        # check object STATE
                        ctrls.update_objectState(obj_id, this_obj, cmd_ref)
                        de.bug("use key on -", via)
                        #use key on box
                        
                        # renderers.render_objectActions(o, cmd, cmd)
                        
                        # check correct req obj for obj
                        
                        # do something now the obj is used
                        # for example a box display stuff inside
                                                    
                    else:
                        
                        # use key - "use key on what?"
                        # render feedback to player
                        renderers.render_objectActions(this_obj, cmd_ref, cmd_ref)
                        
                else:
                    # trying to use obj not in inv
                    ctrls.printText(this_obj['name'], 'not in inv')
            
            ### == open/unlock command do object custom action =============
            
            elif cmd_ref in ("open", "unlock"):
                
                # check object access state
                ob_access = tfs.getObjectState(this_obj, s='access')
                
                de.bug(4, "ob_access is:", ob_access)
                
                if ob_access == 'locked':
                
                    # check if object permissions prevent action
                    can_open = tfs.objPermissions(this_obj)
                    de.bug(4, "lock perms are", can_open)
                    
                    if can_open in ("ok", "unlocked", "has-req-obj"): # obj not locked
                        
                        # render feedback to player
                        renderers.render_objectActions(this_obj, cmd_ref, can_open, this_obj['permissions']['locked_by'])
                        
                        # update object state
                        ctrls.update_objectState(obj_id, this_obj, cmd_ref)
                        
                    else:
                        
                        # feedback access state of object to player
                        renderers.render_objectActions(this_obj, cmd_ref, can_open)
                        
                        # player does not have the req object
                        this_via = gD.gameDB['objectsDB'][this_obj['permissions']['locked_by']]
                        if tfs.getInventorySlot(this_via) == False:
                            ctrls.printText(this_via['name'], 'not in inv')
                        
                else:
                    
                    # not locked => can open: update object state
                    ctrls.update_objectState(obj_id, this_obj, cmd_ref)
    

            ### == close/lock command do object custom action =============
            
            elif cmd_ref in ("lock", "close"):
                
                # check object access state
                ob_access = tfs.getObjectState(this_obj, s='access')
                de.bug(4, "ob_access is:", ob_access)
                
                
                
                if ob_access == 'unlocked':
                    
                    # check if object permissions prevent action
                    can_close = tfs.objPermissions(this_obj)
                    de.bug(4, "lock perms are", can_close)
                    
                    if can_close == "has-req-obj": 
                    
                        # render feedback to player
                        renderers.render_objectActions(this_obj, cmd_ref, can_close, this_obj['permissions']['unlocked_by'])
                        
                        # update object state
                        ctrls.update_objectState(obj_id, this_obj, cmd_ref)
                        
                    else:
                        
                        # render object state feedback to player
                        renderers.render_objectActions(this_obj, cmd_ref, can_close)
                        
                        # player does not have the req object
                        this_via = gD.gameDB['objectsDB'][this_obj['permissions']['unlocked_by']]
                        if tfs.getInventorySlot(this_via) == False:
                            ctrls.printText(this_via['name'], 'not in inv')
                    
                else:
                    
                    # feedback to player object already locked
                    ctrls.printText(this_obj['name'], 'already locked')
                    
        
        else:
            
            # must be an illegal command for this object
            # feedback 'you can't do that to this object'
            t = "illegal"
            renderers.render_objectActions(this_obj, cmd_ref, t)    
                        


    # IF ALL ELSE FAILS cmd is a singleton, show correct actionHelp feedback 
    if cmd != None and obj == None and via == None:
        renderers.render_actionHelp(cmd_ref) 



    



