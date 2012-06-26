# -*- encoding: utf-8 -*

import pydrop.variables
import pydrop.messages
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

    if ltext[0].lower() == "reload" and original_list[2] == pydrop.variables.nick:
        if True:
            pydrop.messages.pdebug("Setting new modules for reloading...")
            reload(pydrop.binds)
            pydrop.variables.binds = pydrop.binds.binds
            for _bind in pydrop.binds.binds:
                for _mod in pydrop.binds.binds[_bind]:
                    pydrop.variables.need_reload.append(_mod)
            pydrop.messages.pdebug("Done...")
        else:
            pydrop.core.ircSend(sock, "PRIVMSG %s :Permission Denied" % (nick))
