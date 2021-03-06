# -*- coding: utf-8 -*-

"""
Created on Fri Jul 13 09:24:51 2018

@author: nick.wardle
"""
import debugger as de
import gameData as gD
import settings as ss
import renderers

# == SOMEWHERE TO HANDLE ALL OF THE POSSIBLE ERROR MESSAGING ==================

# == Movement command inputs

def inputError(loc=0): #optional location param
    
    # show generic "try again" message
    renderers.render_inputError()
    


#def codingError(f, d):
#    
#    # use to show specific responses to known/likely code/function mistakes
#    if f == 'update_worldState':
#        if type(d) != dict:
#            print(ss.errorPre, f, "expects a dict as first arg")
#            
#            return False


def throwError(s, dd):
    de.bug("we are in throwError() with this data: ", dd)
    # error types and data truths
    theTruth = {'uiSpawn':gD.gameDB['uiCmds']}
    
    # throw an error of source s
    if s in theTruth:
        # expect data d
        for i, j in theTruth.items():
            d = j
        # but got data dd
        if d != dd:
        # show error message plus data mismatch
            print(ss.errorPre + "Data mismatch")
            print(ss.errorPre + "Expect data: '", d, "' but received data: '", dd, "'")
        else:
            print(ss.errorPre + "No error found...")
    # error source not recognised
    else:
        print(ss.errorPre + "Error source '", s, "' not recognised")