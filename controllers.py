# -*- coding: utf-8 -*-
"""
Created on Fri Jul 13 09:24:51 2018

@author: nick.wardle
"""
import debugger as de
import gameData as gD
import renderers as rndr
import transformers as tfs
import settings as ss


# == CONTROLLERS =================================================
# modules that take inputs from player, or other modules, and update the models

def clearLocData():
    
    gD.LOCDATA = ''

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


def changeLoc(loc): #generic location changer 
    
    if loc in gD.locDB:
        
        # get current location data and make it GLOBAL
        gD.CURRENT_LOC = loc
        gD.LOCDATA = gD.locDB[loc]
        
    else:
        de.bug("Location not in gD.locDB")
    
    # show location Loading text-pattern
    printText(ss.locLoading)
      
    # render new location
    rndr.render_locScreen(gD.LOCDATA)
    

def locConjGenerator(n, t):
    
    if t == "s":
        return ss.locStarters[n]
    elif t == "l":
        return ss.locListings[n]
    elif t == "t":
        return ss.locTerminus[n]
      

                
def update_worldState(o_id, o, cmd_ref): # get, drop etc. updates world state
    
    
    if cmd_ref in gD.gameDB['actionCmds']['getCmds']:
        
        tfs.updateGameObjects(o_id, 'remove')
        
    elif cmd_ref in gD.gameDB['actionCmds']['putCmds']:
        
        tfs.updateGameObjects(o_id, 'add')
    
    
    
    
def update_objectState(obj_id, o, cmd_ref, p=None): # what happens after the useObject action is successful?
    
    # p is the parent container, optional param
    
#    test_o = tfs.namestr(o, globals())
#    print(gD.World_frame.loc[test_o])
    
    # reset values
    o_s = o['state']
    
    # Simple state changes
    if cmd_ref == 'un_contain': 
                
        de.bug(5, "Want to un-parent this:", obj_id, "from this:", gD.gameDB['objectsDB'][p[0]]['state']['contains'])
        gD.gameDB['objectsDB'][p[0]]['state']['contains'].remove(obj_id)
        
    elif cmd_ref == 'add':
        
        de.bug(5, "Adding", obj_id, "to", p)
        gD.gameDB['objectsDB'][p]['state']['contains'].append(obj_id)
        
    elif cmd_ref in ('open','unlock'): # open, unlock etc.
        
        if len(o_s): 
                
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
                    
                # add the contained items to the game world
                #send t  --  {'object' : [..,..]} dict
                cont_objs, t = tfs.updateGameObjects(o_s['contains'], 'add') 
                
                # returns a list [cont_objs, t]
                # cont_objs are the object descriptions
                # t is the type of container (i.e. box, door)
                
                # feedback to player the objects they have discovered
                if t == "in":
                    printText([cont_objs, o['name']], "contained by")
                   
                elif t == "via":
                    printText([cont_objs, o['name']], "seen through")
 
    elif cmd_ref in ('close','lock'): # close, lock etc.
        
        if len(o_s): 
                
            if 'access' in o_s:
                
                # RENAME the 'unlocked' state to 'locked' 
                gD.gameDB['objectsDB'][obj_id]['state']['access'] = 'locked'
                
                # RENAME the permissions field
                # so a record of the locking item is kept (for un-locking)
                if 'unlocked_by' in o['permissions']:
                    gD.gameDB['objectsDB'][obj_id]['permissions']['locked_by'] = gD.gameDB['objectsDB'][obj_id]['permissions']['unlocked_by']
                    del gD.gameDB['objectsDB'][obj_id]['permissions']['unlocked_by']
            
            de.bug(5, "changed state of", obj_id, "to", gD.gameDB['objectsDB'][obj_id]['state']['access'], "and", gD.gameDB['objectsDB'][obj_id]['permissions'])
            
            if 'contains' in o_s:
                    
                # remove the contained items to the game world
                #send t  --  {'object' : [..,..]} dict
                cont_objs = tfs.updateGameObjects(o_s['contains'], 'remove') 
                    
                
    elif cmd_ref in gD.gameDB['actionCmds']['getCmds']: # get, put etc.
        
        if len(o_s): 
            for s, t in o_s.items():
                
                if s == 'contained_by':
                        
                    # get parent container
                    p = gD.gameDB['objectsDB'][obj_id]['state']['contained_by']
                    
                    # remove contained by state as the object is now 
                    # out of its container and into the world
                    del gD.gameDB['objectsDB'][obj_id]['state']['contained_by']
                    
                    # remove object from local world as now in inventory
                    update_worldState([obj_id], o, cmd_ref)
                    
                    # return requirement to update parent container
                    return p


                
                
                
            
        
        
# def letsFight - fight arena/module - generic combat 



# def worldNav(locJustLeft, locGoingNext)
    # need to know where I have just come from - locJustLeft
    # and where Im travelling to - locGoingNext
    # what happens on exit of this location - look in locDb for leaveConditions
    # what happens on entry on next location - look in locDb for entryConditions
    # what updates to storyProgression and charProgression and charInventory and charHome
    



