
import settings as ss

############ CUSTOM DEBUG PRINT FUNCTION ###################
######## ENBALES ALL PRINT DEBUG MESSAGES TO BE ############
######## SWITCHED ON / OFF WITH ONE GLOBAL VAR #############

def bug(grp=None, *b): # * here is to allow for an unspecified number of args
    if ss.debug == True:
        
        if type(grp) == int:
            if grp in ss.group_hide:
                # group debug messages are hidden
                a = "a"
            else:
                # * here is to 'explode' the tuple of args to remove the ()s
                print(*b) 
        
        else:
            print(*b) # print all debug messages that do not have groups