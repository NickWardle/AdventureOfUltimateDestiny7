
import debugger as de

## == Helpful code snippets to transform data and return it

def listify(d, pronoun=False, terminator='and', case='l', separator=False, mark=False, markPattern=[]):
    
    # d = data, must be a list
    # terminator = 'word(s)' placed before the last item in the list
    # pronoun = 'word' placed before each item: the, a/an, 'user'
    # case = whole list: lower, firstlettercapitalized, upper
    # separator = specify a custom separator e.g. "/" instead of default ","
    # mark = a special mark that is only rendered according to...
    # markPattern = a list of indexes where the mark should be rendered
    

    # EXAMPLE: set mark as "." and specify ends of sentences with markPattern
    
    csr = 0 # set a cursor for stepping through markPattern list
    myListString = ''
    for i in range(len(d)):
        
        # determine correct pronoun based on first letter of each item
        # but no pronoun for descriptions starting with "a " or "an "
        if pronoun == True and d[i][0:2] != "a " and d[i][0:3] != "an ":
            if d[i][0].lower() in ('a','e','i','o','u','h'):
                pr = "an "
            else:
                pr = "a "
        else:
            pr = ''
        
        if len(d) == 1: # one item list
            myListString += pr
            myListString += d[i]
        elif i < len(d)-1: # middle items in the list
            myListString += pr
            myListString += d[i]
                
            # use markPatten to render mark in correct places
            if markPattern != []:
                if markPattern[csr] == i+1:
                    if mark != False:
                        myListString += mark
                    csr += 1
                else: # render a separator where there is no mark specified
                    if separator != False:
                        myListString += separator
                    else:
                        myListString += ", "
            else: # render separators if there is no markPattern
                if separator != False:
                    myListString += separator
                else:
                    myListString += ", "
                        
        else:
            
            # handle the final item in the list wtih an optional terminator
            if terminator != False:
                myListString += terminator 
                myListString += " " 
            myListString += pr
            myListString += d[i]
    
    # general case-options    
    if case == "l":
        return myListString.lower()
    elif case == "c":
        return myListString.capitalize()
    elif case == "u":
        return myListString.upper()
    elif case == False: # just return the string with no change to formatting
        return myListString
    else:
        print("::Error:: Missing argument 'case' = l/c/u for transformers.listify()")
        #TODO: Handle listify() error with proper error function



    
    
    
    
    
    
    
    