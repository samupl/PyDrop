# -*- encoding: utf-8 -*

import time
import datetime

_colors = {
            'BOLDRED1': "\033[1;31m",
            'BOLDYELLOW1': "\033[1;33m",
            'END1': "\033[0;0m",
}

def pdate():
    return str(datetime.datetime.now())
    
def perror(text):
    print "%s[EE]%s <%s> %s" % (_colors['BOLDRED1'], _colors['END1'], pdate(), str(text))

def pdebug(text):
    print "[  ] <%s> %s" % (pdate(), text)

def pwarning(text):
    print "%s[WW]%s <%s> %s" % (_colors['BOLDYELLOW1'], _colors['END1'], pdate(), str(text))
