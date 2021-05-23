import sys
import xbmc
import xbmcgui

if __name__ == '__main__':
    try:
        path = sys.listitem.getfilename()
    except AttributeError:
        path = sys.listitem.getPath()
    truelabel = sys.listitem.getLabel()
    infolabel = xbmc.getInfoLabel('ListItem.Label')

    xbmcgui.Dialog().notification("truelabel: %s" % truelabel, "infolabel: %s; path %s" % (infolabel, path))
