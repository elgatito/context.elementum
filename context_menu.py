import sys
import xbmc
import xbmcgui

from elementum.logger import log


if __name__ == '__main__':
    try:
        path = sys.listitem.getfilename()
    except AttributeError:
        path = sys.listitem.getPath()
    truelabel = sys.listitem.getLabel()
    infolabel = xbmc.getInfoLabel('ListItem.Label')
    dbid = xbmc.getInfoLabel('ListItem.DBID')
    mediatype = xbmc.getInfoLabel('ListItem.DBTYPE')

    log.info("truelabel: %s; infolabel: %s; dbid: %s; path: %s;" % (truelabel, infolabel, dbid, path))
    xbmcgui.Dialog().notification("truelabel: %s" % truelabel, "infolabel: %s; dbid: %s; mediatype: %s; path: %s;" % (infolabel, dbid, mediatype, path))
