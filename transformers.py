import debugger as de
import gameData as gD



## == Helpful code snippets to transform data and return it

def listify(d, pronoun=False, terminator='and', case='l'):
    
    # d = data, must be an array
    # terminator = 'word(s)' placed before the last item in the list
    #TODO: pronoun = 'word' placed before each item: the, a/an, 'user'
    # case = whole list: lower, firstlettercapitalized, upper
    
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
            myListString += ", "
        else:
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


def objPermissions(d): # access control to certain objects
    
    perm_ok = False
    
    # check permissions on the object
    if len(d['permissions']):
        for t, o in d['permissions'].items():
            
            o_name = gD.gameDB['objectsDB'][o]['name'] # just a reference to match on
            
            # match against each type
            if t == "locked_by":
                
                de.bug(3, "checking lock perms")
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
            return t
    else:
        # no restrictions so return "ok" (not True, or it overrides every other condition check!)
        return "ok"


def getInventorySlot(d): # check if an item is in the inventory (and get slot)
    
     # get object's inventory-slot
    inv_slot = d['inventory-slot']
    
    # check if object is IN inv
    if d in gD.PLAYERINV[inv_slot]:
        return inv_slot
    else:
        return False
    

def updateInventory(d, t):
    
    # check if player owns obj and get inv_slot (by return)
    s = getInventorySlot(d)
    
    #TODO: Need to add the whole object including id to the inv, so change other calls to this too
    
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

def update_gameObjects(contents, action):
    
    # make array of contained obj refs
    cont_objs_ids = []
    cont_objs = []
    
    for s, t in contents.items():
        if s == 'object':
            for ob in t:
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
    
    
    
    
    
    
    
    
    
    
    