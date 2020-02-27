import debugger as de
import gameData as gD



## == Helpful code snippets to transform data and return it

def listify(d, pronoun=False, terminator='and', case='l', sentence=False):
    
    # d = data, must be an array
    # terminator = 'word(s)' placed before the last item in the list
    #TODO: pronoun = 'word' placed before each item: the, a/an, 'user'
    # case = whole list: lower, firstlettercapitalized, upper
    #sentence = if the list should be separated by "." instead of ","
    
    # sort out list punctuation: "," "single item" & terminator
    myListString = ''
    for i in range(len(d)):
        if pronoun == True:
            if d[i][0].lower() in ('a','e','i','o','u','h'):
                pr = "an "
            else:
                pr = "a "
        else:
            pr = ''
        
        if len(d) == 1:
            myListString += pr
            myListString += d[i]
        elif i < len(d)-1:
            myListString += pr
            myListString += d[i]
            if sentence == True:
                myListString += ". "
            else:
                myListString += ", "
        else:
            if terminator != False:
                myListString += terminator 
            myListString += " " 
            myListString += pr
            myListString += d[i]
    
    if case == "l":
        return myListString.lower()
    elif case == "c":
        return myListString.capitalize()
    elif case == "u":
        return myListString.upper()
    else:
        print("::Error:: Missing argument 'case' = l/c/u for transformers.listify()")
        #TODO: Handle listify() error with proper error function


def getObjectState(d, s=None):
    
    if s:
        
        if s in d['state']:
        
            return d['state'][s]
        
        else:
            
            print("::Error::", s, "state not present on this object:", d['refs'])
            #TODO: Handle this error with proper error function
            return False
    
    else:
        
        return d['state']


def objPermissions(d): # access control to certain objects
    
    perm_ok = False
    
    # check the state of the object (locked etc)
    ob_access = d['state']['access']
    
    # get object permissions
    req_obj = d['permissions']
    
    if ob_access: # if the object has an access parameter
        
        if ob_access == 'locked':
            perm_type = "locked_by"
        elif ob_access == 'unlocked':
            perm_type = "unlocked_by"
        
        if perm_type in req_obj:
                
            o_name = gD.gameDB['objectsDB'][req_obj[perm_type]]['name'] # just a reference to match on
            
            de.bug(5, "checking player inventory for", o_name)
            # check if player has required object in their inventory
            for cat, objs in gD.PLAYERINV.items():
                for ob in objs:
                    if o_name == ob['name']: # this currently works for 'utils' data format
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


def getInventorySlot(d): # check if an item is in the inventory (and get slot)
    
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
    

def updateInventory(d, t):
    
    # NOTE: d must be a COMPLETE object, not just an obj_id
    
    # check if player owns obj and get inv_slot (by return)
    s = getInventorySlot(d)
    
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

def updateGameObjects(contents, action):
    
    # make array of contained obj refs
    cont_objs_ids = []
    cont_objs = []
    
    for ob in contents:
        cont_objs_ids.append(ob)
        cont_objs.append(gD.gameDB['objectsDB'][ob]['name'])
    
    if action == 'add':
    
        # Make "added" objects available to 
        # the player. We can add them to the objects for this 
        # location this will only last for this session, but it 
        # will persist within the session at least
        for ob in cont_objs_ids:
            if ob not in gD.locDB[gD.CURRENT_LOC]['locObjects']:
                gD.locDB[gD.CURRENT_LOC]['locObjects'].append(ob)
            
    
    elif action == 'remove':
        
        # remove the object(s) from the locObjects list
        for ob in cont_objs_ids:
            if ob in gD.locDB[gD.CURRENT_LOC]['locObjects']:
                gD.locDB[gD.CURRENT_LOC]['locObjects'].remove(ob)
    
    
    return cont_objs
    



def namestr(obj, namespace):
    return [name for name in namespace if namespace[name] is obj]
    
    
    
    
    
    
    
    
    
    
    