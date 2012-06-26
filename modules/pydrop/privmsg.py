# -*- encoding: utf-8 -*

import pydrop.variables
import pydrop.core
import hashlib

def init(sock, original_list, text):
    ltext = text.split()
    nick, user, host = pydrop.core.unpackUserHost(original_list[0])
    
    if ltext[0].lower() == "identify" and len(ltext) == 2 and original_list[2] == pydrop.variables.nick:
        if nick == pydrop.variables.owner and hashlib.sha256(ltext[1]).hexdigest() == pydrop.variables.password and nick == pydrop.variables.owner:
            if not pydrop.variables.owner_identified:
                pydrop.core.ircSend(sock, "PRIVMSG %s :Access granted" % (nick))
                pydrop.variables.owner_identified = True
            else:
                pydrop.core.ircSend(sock, "PRIVMSG %s :You are already identified" % (nick))
        else:
            pydrop.core.ircSend(sock, "PRIVMSG %s :Permission Denied" % (nick))
            pydrop.core.ircSend(sock, "PRIVMSG %s :%s (%s@%s) Failed to identify to the bot." % (pydrop.variables.owner, nick, user, host))
"""
    if ltext[0].lower() == "reload" and original_list[2] == pydrop.variables.nick:
        if True:
            print "Reload start"
            #print main.binds
            print "Reload end"
        else:
            pydrop.core.ircSend(sock, "PRIVMSG %s :Permission Denied" % (nick))
"""
"""
    print ltext[0].lower()
    if ltext[0].lower() == "reload" and original_list[2] == pydrop.variables.nick:
        print "?"
        #if nick == pydrop.variables.owner and pydrop.variables.owner_identified:
        if True:
            print "Here it goes"
            import pydrop.binds
            reload(pydrop.binds)
            print pydrop.binds
            
        else:
            pydrop.core.ircSend(sock, "PRIVMSG %s :Permission Denied" % (nick))
"""
