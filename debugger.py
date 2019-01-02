
import settings as ss

############ CUSTOM DEBUG PRINT FUNCTION ###################
######## ENBALES ALL PRINT DEBUG MESSAGES TO BE ############
######## SWITCHED ON / OFF WITH ONE GLOBAL VAR #############

def bug(*a): # * here is to allow for an unspecified number of args
    if ss.debug == True:
        print(*a) # * here is to 'explode' the tuple of args to remove the ()s