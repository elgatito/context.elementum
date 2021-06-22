import os
import sys
import json
import xbmc
import xbmcgui
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'lib'))

from plugin import getJSONResponse

from elementum.logger import log

info_labels = [
    "ListItem.DBID",
    "ListItem.DBTYPE",
    "ListItem.Mediatype",
    "ListItem.TMDB",
    "ListItem.UniqueID(tmdb)",
    "ListItem.UniqueID(Elementum)",
    "ListItem.Property(ShowTMDBId)",
    "ListItem.Label",
    "ListItem.Label2",
    "ListItem.ThumbnailImage",
    "ListItem.Title",
    "ListItem.OriginalTitle",
    "ListItem.TVShowTitle",
    "ListItem.Season",
    "ListItem.Episode",
    "ListItem.Premiered",
    "ListItem.Plot",
    "ListItem.PlotOutline",
    "ListItem.Tagline",
    "ListItem.Year",
    "ListItem.Trailer",
    "ListItem.Studio",
    "ListItem.MPAA",
    "ListItem.Genre",
    "ListItem.Mediatype",
    "ListItem.Writer",
    "ListItem.Director",
    "ListItem.Rating",
    "ListItem.Votes",
    "ListItem.IMDBNumber",
    "ListItem.Code",
    "ListItem.ArtFanart",
    "ListItem.ArtBanner",
    "ListItem.ArtPoster",
    "ListItem.ArtLandscape",
    "ListItem.ArtTvshowPoster",
    "ListItem.ArtClearArt",
    "ListItem.ArtClearLogo",
    "ListItem.Property(TotalSeasons)",
    "ListItem.Property(TotalEpisodes)",
    "ListItem.Property(WatchedEpisodes)",
    "ListItem.Property(UnWatchedEpisodes)",
    "ListItem.Property(NumEpisodes)",
    "ListItem.PlayCount",
    "ListItem.Path",
    "ListItem.FileName",
    "ListItem.FileNameAndPath",
    "ListItem.UserRating",
    "ListItem.Progress",
    "ListItem.Status",
    "ListItem.Count",
    "ListItem.PercentPlayed",
]

if __name__ == '__main__':
    item = sys.listitem  # xbmcgui.ListItem()
    try:
        path = item.getfilename()
    except AttributeError:
        path = item.getPath()
    truelabel = item.getLabel()
    infolabel = xbmc.getInfoLabel('ListItem.Label')
    dbid = xbmc.getInfoLabel('ListItem.DBID')
    mediatype = xbmc.getInfoLabel('ListItem.DBTYPE')
    try:
        tmdbID = item.getUniqueID('tmdb')
    except AttributeError:
        tmdbID = "not supported"

    properties = {
        'resume_time': item.getProperty('ResumeTime'),
        'start_offset': item.getProperty('StartOffset'),
        'start_percent': item.getProperty('StartPercent'),
        'total_time': item.getProperty('TotalTime')
    }
    log.info("Properties: %s;" % properties)

    all_labels = getJSONResponse('{"jsonrpc": "2.0", "method": "XBMC.GetInfoLabels", "params": { "labels": %s }, "id": "0"}' % json.dumps(info_labels))
    log.info("Labels: %s" % json.dumps(all_labels["result"], indent=4))

    log.info("truelabel: %s; infolabel: %s; dbid: %s; tmdbID: %s; mediatype: %s; path: %s;" % (truelabel, infolabel, dbid, tmdbID, mediatype, path))
    xbmcgui.Dialog().notification("truelabel: %s" % truelabel, "infolabel: %s; dbid: %s; tmdbID: %s; mediatype: %s;" % (infolabel, dbid, tmdbID, mediatype))
