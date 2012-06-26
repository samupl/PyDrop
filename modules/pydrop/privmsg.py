# -*- encoding: utf-8 -*

import pydrop.variables

def init(original_list, text):
    print pydrop.variables.owner
    print "PRIVMSG!"
    print "Original list: "+str(original_list)
    print "TEXT: "+str(text)
    return True
