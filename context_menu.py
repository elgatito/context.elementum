import sys
import xbmc

if __name__ == '__main__':
    message = "Clicked on '%s'" % sys.listitem.getlabel()
    xbmc.executebuiltin("Notification(\"Hello context items!\", \"%s\")" % message)
