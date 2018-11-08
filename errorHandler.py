# -*- coding: utf-8 -*-

"""
Created on Fri Jul 13 09:24:51 2018

@author: nick.wardle
"""
import gameData as gD
import settings as ss
import renderers

# == SOMEWHERE TO HANDLE ALL OF THE POSSIBLE ERROR MESSAGING ==================

# == Movement command inputs

def inputError(loc=0): #optional location param
    
    # show generic "try again" message
    renderers.render_inputError()
    
    

def throwError(s, dd):
    print("we are in throwError() with this data: ", dd)
    # error types and data truths
    theTruth = {'uiSpawn':gD.uiCmds}
    
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