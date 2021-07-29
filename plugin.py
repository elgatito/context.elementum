# -*- coding: utf-8 -*-

"""
Misc functions for context handlers
"""

import sys
import xbmc
import xbmcaddon
import xbmcgui

try:
    import simplejson
except:
    import json as simplejson

import requests
import re

from future.utils import PY3

if PY3:
    from urllib.parse import urlparse, parse_qs
else:
    from urlparse import urlparse, parse_qs

from elementum.logger import log

ADDON = xbmcaddon.Addon()
api_key = ""


def doAssign():
    mediatype = getMediaType()

    try:
        path = sys.listitem.getfilename()
    except AttributeError:
        path = sys.listitem.getPath()

    use_elementum_path = False

    try:
        tmdbID = sys.listitem.getUniqueID('tmdb')
    except AttributeError:
        tmdbID = ""

    if tmdbID == "":
        if path.startswith("plugin://plugin.video.elementum"):
            use_elementum_path = True
            tmdbID = getTMDBidFromElementumPath(path)
            if not tmdbID:
                return

            if mediatype == 'season':
                season_number = getSeasonNumberFromElementumPath(path)
                if not season_number:
                    return

            if mediatype == 'episode':
                season_number = getSeasonNumberFromElementumPath(path)
                episode_number = getEpisodeNumberFromElementumPath(path)
                if not season_number or not episode_number:
                    return
        else:
            dbid = getDbId()
            if not dbid.isdigit():
                log.error("Kodi library ID is wrong %s" % dbid)
                xbmcgui.Dialog().notification(ADDON.getLocalizedString(32007), ADDON.getLocalizedString(32016), xbmcgui.NOTIFICATION_WARNING, 3000)
                return

    # we also can use plugin://plugin.video.elementum/torrents/
    file = xbmcgui.Dialog().browseSingle(1, ADDON.getLocalizedString(32010), 'files', '', False, False, 'plugin://plugin.video.elementum/history/')

    if file == '':
        return

    try:
        parsed_url = urlparse(file)
        params = parse_qs(parsed_url.query)
        if 'infohash' in params:
            torrentid = params['infohash'][0]
        else:
            torrentid = params['resume'][0]
    except Exception as e:
        log.error("Could not get torrent info for %s: %s" % (file, e))
        xbmcgui.Dialog().notification(ADDON.getLocalizedString(32007), ADDON.getLocalizedString(32015), xbmcgui.NOTIFICATION_WARNING, 3000)
        return

    if use_elementum_path:
        if mediatype == 'movie':
            url = "plugin://plugin.video.elementum/context/torrents/assign/%s/tmdb/%s/%s" % (torrentid, mediatype, tmdbID)
        elif mediatype == 'season':
            url = "plugin://plugin.video.elementum/context/torrents/assign/%s/tmdb/show/%s/%s/%s" % (torrentid, tmdbID, mediatype, season_number)
        elif mediatype == 'episode':
            url = "plugin://plugin.video.elementum/context/torrents/assign/%s/tmdb/show/%s/season/%s/%s/%s" % (torrentid, tmdbID, season_number, mediatype, episode_number)
        log.info("Assigning torrent %s for: TMDBID=%s, MediaType=%s" % (torrentid, tmdbID, mediatype))
    else:
        if tmdbID != "":
            url = "plugin://plugin.video.elementum/torrents/assign/%s/%s" % (torrentid, tmdbID)
            log.info("Assigning torrent %s for: TMDBID=%s, MediaType=%s" % (torrentid, tmdbID, mediatype))
        else:
            url = "plugin://plugin.video.elementum/context/torrents/assign/%s/kodi/%s/%s" % (torrentid, mediatype, dbid)
            log.info("Assigning torrent %s for: DBID=%s, MediaType=%s" % (torrentid, dbid, mediatype))

    xbmcgui.Dialog().notification(ADDON.getLocalizedString(32010), sys.listitem.getLabel(), xbmcgui.NOTIFICATION_INFO, 3000)

    log.info("Starting Elementum with: %s" % url)

    xbmc.Player().play(url)


def doPlay():
    dbid = getDbId()
    mediatype = getMediaType()

    use_elementum_path = False
    if not dbid.isdigit():
        try:
            path = sys.listitem.getfilename()
        except AttributeError:
            path = sys.listitem.getPath()
        if path.startswith("plugin://plugin.video.elementum"):
            use_elementum_path = True

    xbmcgui.Dialog().notification(ADDON.getLocalizedString(32009), sys.listitem.getLabel(), xbmcgui.NOTIFICATION_INFO, 3000)

    if use_elementum_path:
        log.info("Playing elementum item: path=%s, MediaType=%s" % (path, mediatype))
        if mediatype == 'season':
            url = re.sub(r'/(episodes)(/?[^/]*)$', r'/links\g<2>', path, count=1)
        else:
            url = path
    else:
        log.info("Playing library item: DBID=%s, MediaType=%s" % (dbid, mediatype))
        url = "plugin://plugin.video.elementum/context/media/%s/%s/play" % (mediatype, dbid)

    log.info("Starting Elementum with: %s" % url)
    xbmc.Player().play(url)


def doDownload():
    dbid = getDbId()
    mediatype = getMediaType()

    use_elementum_path = False
    if not dbid.isdigit():
        try:
            path = sys.listitem.getfilename()
        except AttributeError:
            path = sys.listitem.getPath()
        if path.startswith("plugin://plugin.video.elementum"):
            use_elementum_path = True

    xbmcgui.Dialog().notification(ADDON.getLocalizedString(32013), sys.listitem.getLabel(), xbmcgui.NOTIFICATION_INFO, 3000)

    if use_elementum_path:
        log.info("Downloading elementum item: path=%s, MediaType=%s" % (path, mediatype))
        if mediatype == 'season':
            url = re.sub(r'/(episodes)(/?[^/]*)$', r'/download\g<2>', path, count=1)
        else:
            url = re.sub(r'/(play|links)(/?[^/]*)$', r'/download\g<2>', path, count=1)
    else:
        log.info("Downloading library item: DBID=%s, MediaType=%s" % (dbid, mediatype))
        url = "plugin://plugin.video.elementum/context/media/%s/%s/download" % (mediatype, dbid)

    log.info("Starting Elementum with: %s" % url)
    xbmc.Player().play(url)


def doLibraryAction(action):
    dbid = getDbId()
    try:
        tmdbID = sys.listitem.getUniqueID('tmdb')
    except AttributeError:
        tmdbID = ""
    mediatype = getMediaType()

    heading = ADDON.getLocalizedString(32017) if action == "add" else "Unsupported action"
    xbmcgui.Dialog().notification(heading, sys.listitem.getLabel(), xbmcgui.NOTIFICATION_INFO, 3000)

    log.info("%s library item: DBID=%s, MediaType=%s" % (action, dbid, mediatype))

    if tmdbID != "":
        url = "plugin://plugin.video.elementum/library/%s/%s/%s" % (mediatype, action, tmdbID)
    else:
        url = "plugin://plugin.video.elementum/context/library/%s/%s/%s" % (mediatype, dbid, action)
    log.info("Starting Elementum with: %s" % url)
    xbmc.Player().play(url)


def doTraktAction(action):
    dbid = getDbId()
    mediatype = getMediaType()

    if action == "watched":
        heading = ADDON.getLocalizedString(32018)
    elif action == "unwatched":
        heading = ADDON.getLocalizedString(32019)
    else:
        heading = "Unsupported action"

    if not dbid.isdigit():
        showtmdbid = xbmc.getInfoLabel('ListItem.Property(ShowTMDBId)')
        try:
            tmdbID = sys.listitem.getUniqueID('tmdb')
        except AttributeError:
            tmdbID = ""
        if tmdbID == "" or ((mediatype == 'season' or mediatype == 'episode') and showtmdbid == ""):
            log.error("Could not find TMDB id for %s" % dbid)
            xbmcgui.Dialog().notification(ADDON.getLocalizedString(32007), ADDON.getLocalizedString(32014), xbmcgui.NOTIFICATION_WARNING, 3000)
            return

    xbmcgui.Dialog().notification(heading, sys.listitem.getLabel(), xbmcgui.NOTIFICATION_INFO, 3000)
    if not dbid.isdigit():
        log.info("Make %s non-library item: tmdbID=%s, MediaType=%s" % (action, tmdbID, mediatype))
    else:
        log.info("Make %s library item: DBID=%s, MediaType=%s" % (action, dbid, mediatype))

    if not dbid.isdigit():
        if mediatype == 'movie':
            url = "plugin://plugin.video.elementum/movie/%s/%s" % (tmdbID, action)
        if mediatype == 'tvshow':
            url = "plugin://plugin.video.elementum/show/%s/%s" % (tmdbID, action)
        elif mediatype == 'season':
            season = xbmc.getInfoLabel('ListItem.Season')
            url = "plugin://plugin.video.elementum/show/%s/season/%s/%s" % (showtmdbid, season, action)
        elif mediatype == 'episode':
            season = xbmc.getInfoLabel('ListItem.Season')
            episode = xbmc.getInfoLabel('ListItem.Episode')
            url = "plugin://plugin.video.elementum/show/%s/season/%s/episode/%s/%s" % (showtmdbid, season, episode, action)
    else:
        url = "plugin://plugin.video.elementum/context/media/%s/%s/%s" % (mediatype, dbid, action)
    log.info("Starting Elementum with: %s" % url)
    xbmc.Player().play(url)


def getDbId():
    infolabel = xbmc.getInfoLabel('ListItem.Label')
    truelabel = sys.listitem.getLabel()

    if infolabel == truelabel and xbmc.getInfoLabel('ListItem.DBID'):
        dbid = xbmc.getInfoLabel('ListItem.DBID')
    else:
        if xbmc.getInfoLabel('ListItem.Episode') and xbmc.getInfoLabel('ListItem.TVSHowTitle') and xbmc.getInfoLabel('ListItem.Season'):
            season = int(xbmc.getInfoLabel('ListItem.Season'))
            episode = int(xbmc.getInfoLabel('ListItem.Episode'))

            dbid = '{} s{:02d}e{:02d}'.format(xbmc.getInfoLabel('ListItem.TVSHowTitle'), season, episode)
            dbid = requests.utils.quote(dbid)
        elif xbmc.getInfoLabel('ListItem.TVSHowTitle') and xbmc.getInfoLabel('ListItem.Season'):
            season = int(xbmc.getInfoLabel('ListItem.Season'))

            dbid = '{} s{:02d}'.format(xbmc.getInfoLabel('ListItem.TVSHowTitle'), season)
            dbid = requests.utils.quote(dbid)
        elif xbmc.getInfoLabel('ListItem.Title') and xbmc.getInfoLabel('ListItem.Year'):
            title = xbmc.getInfoLabel('ListItem.Title')
            year = xbmc.getInfoLabel('ListItem.Year')

            dbid = '{} ({})'.format(title, year)
            dbid = requests.utils.quote(dbid)
        else:
            dbid = requests.utils.quote(infolabel) if infolabel else requests.utils.quote(truelabel)
    return dbid


def getIMDBNumber():
    return getVideoTag().getIMDBNumber()


def getMediaType():
    version = xbmcVersion()

    if xbmc.getInfoLabel('ListItem.DBTYPE'):
        # Seasons and calls from library will work
        return xbmc.getInfoLabel('ListItem.DBTYPE')
    elif version >= 17:
        # Will work on Kodi 17 and further
        return getVideoTag().getMediaType()
    else:
        # No other way, we query Kodi for information
        dbid = getDbId()

        if dbid.isdigit():
            response = getJSONResponse('{"jsonrpc": "2.0", "method": "VideoLibrary.GetMovieDetails", "params": { "movieid": %s }, "id": "0"}' % dbid)
            if 'error' not in response:
                return 'movie'

            response = getJSONResponse('{"jsonrpc": "2.0", "method": "VideoLibrary.GetEpisodeDetails", "params": { "episodeid": %s }, "id": "0"}' % dbid)
            if 'error' not in response:
                return 'episode'

            response = getJSONResponse('{"jsonrpc": "2.0", "method": "VideoLibrary.GetSeasonDetails", "params": { "seasonid": %s }, "id": "0"}' % dbid)
            if 'error' not in response:
                return 'season'

        return None


def getEpisodeDetails():
    dbid = getDbId()
    response = getJSONResponse('{"jsonrpc": "2.0", "method": "VideoLibrary.GetEpisodeDetails", "params": { "episodeid": %s, "properties" : ["episode", "season","tvshowid"] }, "id": "0"}' % dbid)
    if 'result' in response:
        tvshowresponse = getJSONResponse('{"jsonrpc": "2.0", "method": "VideoLibrary.GetTVShowDetails", "params": { "tvshowid": %s, "properties" : ["imdbnumber"] }, "id": "0"}' % response["result"]["episodedetails"]["tvshowid"])
        if 'result' in tvshowresponse:
            return (tvshowresponse["result"]["tvshowdetails"]["imdbnumber"], response["result"]["episodedetails"]["season"], response["result"]["episodedetails"]["episode"])


def getVideoTag():
    return sys.listitem.getVideoInfoTag()


def xbmcVersion():
    build = xbmc.getInfoLabel('System.BuildVersion')

    methods = [
        lambda b: float(b.split()[0]),
        lambda b: float(b.split()[0].split('-')[1]),
        lambda b: float(b.split()[0].split('-')[0]),
        lambda b: 0.0
    ]

    for m in methods:
        try:
            version = m(build)
            break
        except ValueError:
            # parsing failed, try next method
            pass

    return version


def getJSONResponse(message):
    return simplejson.loads(xbmc.executeJSONRPC(message))


def getJSON(url):
    page = requests.get(url).content
    try:
        return simplejson.loads(page)
    except:
        return simplejson.loads(page.decode('utf-8'))


def configureTMDB():
    global api_key

    api_key = ADDON.getSetting('tmdb_api_key')
    if not api_key:
        # Temporarily use predefined key
        api_key = "29a551a65eef108dd01b46e27eb0554a"
        return True
        # xbmcgui.Dialog().notification(ADDON.getLocalizedString(32005),
        #    ADDON.getLocalizedString(32006), xbmcgui.NOTIFICATION_WARNING, 3000)
        # return False

    return True


def isTMDBId(mediatype, id):
    if mediatype == 'show':
        url = "https://api.themoviedb.org/3/tv/%s?api_key=%s&language=en-US" % (id, api_key)
    elif mediatype == 'movie':
        url = "https://api.themoviedb.org/3/movie/%s?api_key=%s&language=en-US" % (id, api_key)

    response = getJSON(url)

    if 'status_code' in response:
        return False
    else:
        return True


def getTMDBId(mediatype, id):
    if isTMDBId(mediatype, id):
        return id
    else:
        if mediatype == 'movie':
            url = "https://api.themoviedb.org/3/find/%s?api_key=%s&language=en-US&external_source=%s" % (id, api_key, 'imdb_id')
        elif mediatype == 'show':
            url = "https://api.themoviedb.org/3/find/%s?api_key=%s&language=en-US&external_source=%s" % (id, api_key, 'tvdb_id')

        response = getJSON(url)

        if 'status_code' in response:
            xbmcgui.Dialog().notification(ADDON.getLocalizedString(32007), ADDON.getLocalizedString(32008), xbmcgui.NOTIFICATION_WARNING, 3000)
            return None

        if response['movie_results']:
            return response['movie_results'][0]['id']
        elif response['tv_results']:
            return response['tv_results'][0]['id']
        elif response['tv_episode_results']:
            return response['tv_episode_results'][0]['id']
        else:
            return None


def getTMDBidFromElementumPath(path):
    """plugin://plugin.video.elementum/movie/628/links/Interview%20with%20the%20Vampire%20%281994%29"""
    result = re.search(r'plugin://plugin.video.elementum/[^/]+/(\d+)/.*', path)
    if result:
        tmdbID = result.group(1)
        return tmdbID
    else:
        log.error("Could not find TMDB id for %s" % path)
        xbmcgui.Dialog().notification(ADDON.getLocalizedString(32007), ADDON.getLocalizedString(32014), xbmcgui.NOTIFICATION_WARNING, 3000)
        return ""


def getSeasonNumberFromElementumPath(path):
    """plugin://plugin.video.elementum/show/1622/season/15/episodes"""
    season_number = xbmc.getInfoLabel('ListItem.Season')
    if season_number:
        return season_number
    else:
        result = re.search(r'plugin://plugin.video.elementum/[^/]+/\d+/season/(\d+)/.*', path)
        if result:
            season_number = result.group(1)
            return season_number
        else:
            log.error("Could not find season number for %s" % path)
            xbmcgui.Dialog().notification(ADDON.getLocalizedString(32007), ADDON.getLocalizedString(32014), xbmcgui.NOTIFICATION_WARNING, 3000)
            return ""


def getEpisodeNumberFromElementumPath(path):
    """plugin://plugin.video.elementum/show/1622/season/15/episode/1/links/Supernatural%20S15E01"""
    episode_number = xbmc.getInfoLabel('ListItem.Episode')
    if episode_number:
        return episode_number
    else:
        result = re.search(r'plugin://plugin.video.elementum/[^/]+/\d+/season/\d+/episode/(\d+)/.*', path)
        if result:
            episode_number = result.group(1)
            return episode_number
        else:
            log.error("Could not find episode number for %s" % path)
            xbmcgui.Dialog().notification(ADDON.getLocalizedString(32007), ADDON.getLocalizedString(32014), xbmcgui.NOTIFICATION_WARNING, 3000)
            return ""
