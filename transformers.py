import debugger as de
import gameData as gD



## == Helpful code snippets to transform data and return it

def listify(d, terminator='and', case='l'):
    
    # d = data, must be an array
    # terminator = 'word(s)' placed before the last item in the list
    # case = whole list: lower, firstlettercapitalized, upper
    
    # sort out list punctuation: "," "single item" & terminator
    myListString = ''
    for i in range(len(d)):
        if len(d) == 1:
            myListString += d[i]
        elif i < len(d)-1:
            myListString += d[i]
            myListString += ", "
        else:
            myListString += terminator 
            myListString += " " 
            myListString += d[i]
    
    if case == "l":
        return myListString.lower()
    elif case == "c":
        return myListString.capitalize()
    elif case == "u":
        return myListString.upper()
    else:
        print("::Error:: Missing argument 'case' = l/c/u for transformers.listify()")
        #TODO: Handle transformers.listify() error with proper error function


def objPermissions(d): # access control to certain objects
    
    perm_ok = False
    
    # check permissions on the object
    if len(d['permissions']) > 0:
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


def getInventorySlot(d):
    
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

def namestr(obj, namespace):
    return [name for name in namespace if namespace[name] is obj]
    
    
    
    
    
    
    
    
    
    
    