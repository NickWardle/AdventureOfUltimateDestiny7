# -*- coding: utf-8 -*-
"""
Created on Fri Jul 13 09:24:51 2018

@author: nick.wardle
"""
import debugger as de
import gameData as gD
import renderers as rndr
#import transformers as tfs
import settings as ss


# == CONTROLLERS =================================================
# modules that take inputs from player, or other modules, and update the models


# == GENERAL HELPER CONTROLLERS =======================================


def namestr(obj, namespace):
    return [name for name in namespace if namespace[name] is obj]

def clearLocData():
    
    gD.LOCDATA = ''
    
    
# == USER FEEDBACK CONTROLLERS  ==================================


def buildPrompt(t, d=None):
    
#    de.bug("t", t, "d", d)
    
    if t == 'default':
        return rndr.render_prompt(gD.LOCDATA['locInputDesc'], 'default prompt')
    
    elif t == 'did you mean':
        return rndr.render_prompt(d, 'did you mean')
    

def printText(d, t="default"): # generic text printer
    
    if t == 'exit': #exit command
        gD.EXIT = True
        
    if t == 'look': #look around again
        rndr.render_locScreen(gD.LOCDATA)
    else:
        rndr.render_Text(d, t)
        
        
# == LOCATION CONTROLERS  ========================================


def changeLoc(loc): #generic location changer 
    
    if loc in gD.locDB:
        
        # get current location data and make it GLOBAL
        gD.CURRENT_LOC = loc
        gD.LOCDATA = gD.locDB[loc]
    
    # show location Loading text-pattern
    printText("\n" + ss.locLoading)
      
    # render new location
    rndr.render_locScreen(gD.LOCDATA)
    

def locConjGenerator(n, t):
    
    if t == "s":
        return ss.locStarters[n]
    elif t == "l":
        return ss.locListings[n]
    elif t == "t":
        return ss.locTerminus[n]



# == PLAYER INVENTORY CONTROLLERS  ===============================


def get_InventorySlot(d): # check if an item is in the inventory (and get slot)
    
    # NOTE: d must be a COMPLETE object, not just an obj_id
    
    # CHECK (and return) object's inventory-slot
    if 'inventory-slot' in d:
        inv_slot = d['inventory-slot']
        
        # check if object is IN inv
        if d in gD.PLAYERINV[inv_slot]:
            return inv_slot
        else:
            return False
    
    else:
        # check if item can take GET, PUT or USE commands
        if any (k in d for k in ('getCmds-OK', 'putCmds-OK', 'useCmds-OK')):
            de.bug(5, "ERROR, missing inventory slot on ", d, "in gameData file")
        else:
            de.bug(5, "this object ", d['name'], "cannot exist in the inventory")
            return False
    

def update_Inventory(d, t):
    
    # NOTE: d must be a COMPLETE object, not just an obj_id
    
    # check if player owns obj and get inv_slot (by return)
    s = get_InventorySlot(d)
    
    # add to inventory
    if t == "add":
    
        if s != False:
            return False
        else:
            # get object's inventory-slot
            inv_slot = d['inventory-slot']
            gD.PLAYERINV[inv_slot].append(d)
    
    # remove from inventory
    elif t == "remove":
        
        if s != False:
            gD.PLAYERINV[s].remove(d)
        else:
            return False



# == OBJECT CONTROLLERS ==============================================

      
def get_ObjectState(d, s=None):
    
    if s:
        
        if s in d['state']:
        
            return d['state'][s]
        
        else:
            
            print("::Error::", s, "state not present on this object:", d['refs'])
            #TODO: Handle this error with proper error function
            return False
    
    else:
        
        return d['state']




def get_ObjectPermissions(d): # access control to certain objects
    
    # Returns: 
    # "ok" if no access restrictions on object
    # "has-req-obj" if player has req_obj to access locked object
    # "locked_by" or "unlocked_by" if access is denied
    
    perm_ok = False
    
    # check the state of the object (locked etc)
    if 'access' in d['state']:
        
        if d['state']['access'] == 'locked':
            perm_type = "locked_by"
        elif d['state']['access'] == 'unlocked':
            perm_type = "unlocked_by"
            
        # get object permissions
        req_perm = d['permissions']
        
        if perm_type in req_perm:
                
            req_obj = gD.gameDB['objectsDB'][req_perm[perm_type]] 
            
            # check if player has required object in their inventory
            de.bug(5, "checking player inventory for", req_obj)
            
            if get_InventorySlot(req_obj):
                perm_ok = True
  
        
        if perm_ok == True:
            # player has the req obj
            return "has-req-obj"
        else:
            # player does NOT have req obj, just return state
            return perm_type
    
    else:
        # no restrictions so return "ok" (not True, or it overrides every other condition check!)
        return "ok"




def get_ObjectContents(obj_id):
    
    # get contents of an objects. Returns [ids, descs, type-of-containment]
    obj = gD.gameDB['objectsDB'][obj_id]
    
    # check this obj actually HAS children
    if 'contains' in obj['state']: 
        
        # required access check
        if get_ObjectPermissions(obj) != 'locked':
            
            # reset type
            t = False
            
            # make array of contained obj refs
            cont_objs_ids = []
            cont_objs = []
            
            # Determine if contained objects are "in" or "via" their container
            # makes a "mixed bag" of descriptions if there are multiple types
            # type inherits from the last item in the list
            # could be changed to make it smarter if we need that functionality    
            for o in obj['state']['contains']:
                    cont_objs_ids.append(o)
            
                    if o[0:2] == "ob":
                            cont_objs.append(gD.gameDB['objectsDB'][o]['name'])
                            t = "in"
        
                    elif o[0] == "m":
                            for i, j in gD.gameDB['moveCommandsDB'][o].items():
                                cont_objs.append(j['moveDesc'])
                            t = "via"
        
            # return a list [ids, obs, t] == ids, descriptions, type
            return [cont_objs_ids, cont_objs, t]
            
        else:
            
            de.bug(6, "Cannot access object:", obj_id)
            return obj_id, False, False
    
    else:
            
        de.bug(6, "Object:", obj_id, "has no contents")
        return obj_id, False, False

    
    
    
def update_ObjectState(obj_id, o, cmd_ref, p=None): 
    
    # p is the parent container, optional param
    
    # reset values
    o_s = o['state']
    
    # == Simple state changes ==================================
    if cmd_ref == 'un_contain': 
                
        de.bug(5, "Want to un-parent this:", obj_id, "from this:", gD.gameDB['objectsDB'][p[0]]['state']['contains'])
        
        gD.gameDB['objectsDB'][p[0]]['state']['contains'].remove(obj_id)
        
    elif cmd_ref == 'add':
        
        de.bug(5, "Adding", obj_id, "to", p)
        
        gD.gameDB['objectsDB'][p]['state']['contains'].append(obj_id)
        
    
    # == GET/PUT COMMANDS =============================================
    
    ## If object is contained, change its state to not-contained and
    # return the parent object for future processing
    
    elif cmd_ref in gD.gameDB['actionCmds']['getCmds']: 
        
        if len(o_s): 
            for s, t in o_s.items():
                
                if s == 'contained_by':
                        
                    # get parent container
                    p = gD.gameDB['objectsDB'][obj_id]['state']['contained_by']
                    
                    # remove contained by state as the object is now 
                    # out of its container and into the world
                    del gD.gameDB['objectsDB'][obj_id]['state']['contained_by']
                    
                    # return requirement to update parent container
                    return p
                

    # == OPEN/UNLOCK COMMANDS ==========================================
                
    elif cmd_ref in ('open','unlock'): # open, unlock etc.
        
        if len(o_s): 
            
            # change STATE and PERMISSIONS of object
                
            if 'access' in o_s:
                
                # RENAME the 'locked' state to 'unlocked' 
                gD.gameDB['objectsDB'][obj_id]['state']['access'] = 'unlocked'
                
                # RENAME the permissions field
                # so a record of the locking item is kept (for re-locking)
                if 'locked_by' in o['permissions']:
                    gD.gameDB['objectsDB'][obj_id]['permissions']['unlocked_by'] = gD.gameDB['objectsDB'][obj_id]['permissions']['locked_by']
                    del gD.gameDB['objectsDB'][obj_id]['permissions']['locked_by']
            
            de.bug(5, "changed state of", obj_id, "to", gD.gameDB['objectsDB'][obj_id]['state']['access'], "and", gD.gameDB['objectsDB'][obj_id]['permissions'])
            
            if 'contains' in o_s:

                
                # GET the contained objects
                ids, descs, t = get_ObjectContents(obj_id)
                
                # ADD the contained items to the game world
                update_WorldState(ids, t, 'add')
                                
                # feedback to player the objects they have discovered
                if t == "in":
                    printText([descs, o['name']], "contained by")
                   
                elif t == "via":
                    printText([descs, o['name']], "seen through")
 
    
    
    
    # == CLOSE/LOCK COMMANDS ==========================================
    
    elif cmd_ref in ('close','lock'): # close, lock etc.
        
        if len(o_s): 
            
            # have to do contents removal first, because otherwise
            # the box is locked and contents are inaccessible! :D
            
            if 'contains' in o_s:
                    
                # GET the contained objects
                ids, descs, t = get_ObjectContents(obj_id)
                
                # ADD the contained items to the game world
                update_WorldState(ids, t, 'remove')
            
            
            if 'access' in o_s:
                
                # RENAME the 'unlocked' state to 'locked' 
                gD.gameDB['objectsDB'][obj_id]['state']['access'] = 'locked'
                
                # RENAME the permissions field
                # so a record of the locking item is kept (for un-locking)
                if 'unlocked_by' in o['permissions']:
                    gD.gameDB['objectsDB'][obj_id]['permissions']['locked_by'] = gD.gameDB['objectsDB'][obj_id]['permissions']['unlocked_by']
                    del gD.gameDB['objectsDB'][obj_id]['permissions']['unlocked_by']
            
            de.bug(5, "changed state of", obj_id, "to", gD.gameDB['objectsDB'][obj_id]['state']['access'], "and", gD.gameDB['objectsDB'][obj_id]['permissions'])
            
            
            
# == WORLD STATE CONTROLLERS ============================================
            
                    
def update_WorldState(ids, t, c): 
    
    # change the World State e.g. objects in the world: add, remove etc.
    
    de.bug(1, "update World State with", ids, " ", t, "and", c)
    
    # == REMOVE OBJECTS ==============================
    
#    if cmd_ref in gD.gameDB['actionCmds']['getCmds']:
    if c == 'remove':
        
        if t == False: # sent obj has no contents
            
            if ids in gD.locDB[gD.CURRENT_LOC]['locObjects']:
                    gD.locDB[gD.CURRENT_LOC]['locObjects'].remove(ids)
            
        else:
            
            for ob in ids:
                if t == "in":
                    if ob in gD.locDB[gD.CURRENT_LOC]['locObjects']:
                        gD.locDB[gD.CURRENT_LOC]['locObjects'].remove(ob)
                elif t == "via":
                    if ob in gD.LOCDATA['moveCmds']:
                        gD.LOCDATA['moveCmds'].remove(ob)
        
    
    # == ADDING OBJECTS ==============================
        
#    elif cmd_ref in gD.gameDB['actionCmds']['putCmds']:
    elif c == 'add':
        
        if t == False: # sent obj has no contents
            
            if ids not in gD.locDB[gD.CURRENT_LOC]['locObjects']:
                    gD.locDB[gD.CURRENT_LOC]['locObjects'].append(ids)
            
        else:
        
            for ob in ids:
                if t == "in":
                    # add contained objects to locdata objects list
                    if ob not in gD.LOCDATA['locObjects']:
                        gD.LOCDATA['locObjects'].append(ob)
                    
                elif t == "via":
                    if ob not in gD.LOCDATA['moveCmds']:
                        gD.LOCDATA['moveCmds'].append(ob)






                
                
# stuff for dataframes
                    
#    test_o = namestr(o, globals())
#    print(gD.World_frame.loc[test_o])
            
        
        
# def letsFight - fight arena/module - generic combat 



# def worldNav(locJustLeft, locGoingNext)
    # need to know where I have just come from - locJustLeft
    # and where Im travelling to - locGoingNext
    # what happens on exit of this location - look in locDb for leaveConditions
    # what happens on entry on next location - look in locDb for entryConditions
    # what updates to storyProgression and charProgression and charInventory and charHome
    



