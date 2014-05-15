# -*- coding: latin-1 -*-
# Surprise Me!
import xbmc
import xbmcgui
import xbmcaddon
import random
import simplejson
import time
import SelectionFilters as sf
from datetime import date
ACTION_PREVIOUS_MENU = 10
ACTION_SELECT_ITEM = 7
ACTION_MOUSE_LEFT_CLICK = 100
filterGenres=None
filterYear=None
filterlast=None
filterUnwatched=None
filterdisney=None
_A_ = xbmcaddon.Addon()
_S_ = _A_.getSetting


actualyear = date.today().year
addon = xbmcaddon.Addon()
addon_path = addon.getAddonInfo('path')
hide_info = addon.getSetting('hide_info_sur')
exit_requested = False
class movieWindow(xbmcgui.WindowXMLDialog):

    def onInit(self):
        
        global trailer
        global do_timeout
        if hide_info == 'false':
            w=infoWindow('script-DialogVideoInfo.xml',addon_path,'default')
            do_timeout=True
            w.doModal()
            do_timeout=False
            del w
            if exit_requested:
                xbmc.Player().stop()
        else:
            xbmc.Player().play(trailer["trailer"])
        self.getControl(30011).setLabel(trailer["title"] + ' - ' + str(trailer["year"]))
        self.getControl(30011).setVisible(True)
        while xbmc.Player().isPlaying():                
            xbmc.sleep(250)
        self.close()
        
    def onAction(self, action):
        ACTION_PREVIOUS_MENU = 10
        ACTION_BACK = 92
        ACTION_ENTER = 7
        ACTION_I = 11
        ACTION_LEFT = 1
        ACTION_RIGHT = 2
        ACTION_UP = 3
        ACTION_DOWN = 4
        ACTION_TAB = 18
        
        xbmc.log('action  =' + str(action.getId()))
        
        global exit_requested
        global movie_file
        if action == ACTION_PREVIOUS_MENU or action == ACTION_LEFT or action == ACTION_BACK:
            xbmc.Player().stop()
            exit_requested = True
            self.close()

        if action == ACTION_RIGHT or action == ACTION_TAB:
            xbmc.Player().stop()
            
        if action == ACTION_ENTER:
            exit_requested = True
            xbmc.Player().stop()
            movie_file = trailer["file"]
            self.getControl(30011).setVisible(False)
            self.close()
        
        if action == ACTION_I or action == ACTION_UP:
            self.getControl(30011).setVisible(False)
            w=infoWindow('script-DialogVideoInfo.xml',addon_path,'default')
            w.doModal()
            self.getControl(30011).setVisible(True)
            
class infoWindow(xbmcgui.WindowXMLDialog):

    def onInit(self):
        self.getControl(30001).setImage(trailer["thumbnail"])
        self.getControl(30003).setImage(trailer["fanart"])
        self.getControl(30002).setLabel(trailer["title"])
        directors = trailer["director"]
        movieDirector=''
        for director in directors:
            movieDirector = movieDirector + director + ', '
            if not movieDirector =='':
                movieDirector = movieDirector[:-2]
        self.getControl(30005).setLabel(movieDirector)
        writers = trailer["writer"]
        movieWriter=''
        for writer in writers:
            movieWriter = movieWriter + writer + ', '
            if not movieWriter =='':
                movieWriter = movieWriter[:-2]
        actors = trailer["cast"]
        movieActor=''
        actorcount=0
        for actor in actors:
            actorcount = actorcount + 1
            movieActor = movieActor + actor['name'] + ", "
            if actorcount == 6: break
            if not movieActor == '':
                movieActor = movieActor[:-2]
        self.getControl(30007).setLabel(movieWriter)
        self.getControl(30006).setLabel(movieActor)
        
        self.getControl(30009).setText(trailer["plot"])
        movieStudio=''
        studios=trailer["studio"]
        for studio in studios:
            movieStudio = movieStudio + studio + ', '
            if not movieStudio =='':
                movieStudio = movieStudio[:-2]
        self.getControl(30010).setLabel(movieStudio + ' - ' + str(trailer["year"]))
        movieGenre=''
        genres = trailer["genre"]
        for genre in genres:
            movieGenre = movieGenre + genre + ' / '
        if not movieGenre =='':
            movieGenre = movieGenre[:-3]
        self.getControl(30011).setLabel(str(trailer["runtime"] / 60) + ' Minutes - ' + movieGenre)
        imgRating='ratings/notrated.png'
        if trailer["mpaa"].startswith('G'): imgRating='ratings/g.png'
        if trailer["mpaa"] == ('G'): imgRating='ratings/g.png'
        if trailer["mpaa"].startswith('Rated G'): imgRating='ratings/g.png'
        if trailer["mpaa"].startswith('PG '): imgRating='ratings/pg.png'
        if trailer["mpaa"] == ('PG'): imgRating='ratings/pg.png'
        if trailer["mpaa"].startswith('Rated PG'): imgRating='ratings/pg.png'
        if trailer["mpaa"].startswith('PG-13 '): imgRating='ratings/pg13.png'
        if trailer["mpaa"] == ('PG-13'): imgRating='ratings/pg13.png'
        if trailer["mpaa"].startswith('Rated PG-13'): imgRating='ratings/pg13.png'
        if trailer["mpaa"].startswith('R '): imgRating='ratings/r.png'
        if trailer["mpaa"] == ('R'): imgRating='ratings/r.png'
        if trailer["mpaa"].startswith('Rated R'): imgRating='ratings/r.png'
        if trailer["mpaa"].startswith('NC17'): imgRating='ratings/nc17.png'
        if trailer["mpaa"].startswith('Rated NC17'): imgRating='ratings/nc1.png'
        self.getControl(30013).setImage(imgRating)
        if do_timeout:
            xbmc.sleep(5000)
            xbmc.Player().play(trailer["trailer"])
            self.close()
        
    def onAction(self, action):
        ACTION_PREVIOUS_MENU = 10
        ACTION_BACK = 92
        ACTION_ENTER = 7
        ACTION_I = 11
        ACTION_LEFT = 1
        ACTION_RIGHT = 2
        ACTION_UP = 3
        ACTION_DOWN = 4
        ACTION_TAB = 18
        
        xbmc.log('action  =' + str(action.getId()))
        global do_timeout
        global exit_requested
        global movie_file
        if action == ACTION_PREVIOUS_MENU or action == ACTION_LEFT or action == ACTION_BACK:
            do_timeout=False
            xbmc.Player().stop()
            exit_requested=True
            self.close()
            
        if action == ACTION_I or action == ACTION_DOWN:
            self.close()
            
        if action == ACTION_RIGHT or action == ACTION_TAB:
            xbmc.Player().stop()
            self.close()

        if action == ACTION_ENTER:
            movie_file = trailer["file"]
            xbmc.Player().stop()
            exit_requested=True
            self.close()
        
class blankWindow(xbmcgui.WindowXML):
    def onInit(self):
        pass

class XBMCPlayer(xbmc.Player):
    def __init__( self, *args, **kwargs ):
        pass
    def onPlayBackStarted(self):
        pass
    
    def onPlayBackStopped(self):
        global exit_requested
        pass

def log(txt):
    message = 'script.watchlist: %s' % txt
    xbmc.log(msg=message, level=xbmc.LOGDEBUG)

#####################
# set our preferences
#####################

# Defaults
numRuntime = int(float(_S_( "longruntime" ) ) )
numTrailers = 3
promptGenres = promptYear = promptUnwatched = promptdisney = fanartMode = playlistMode = promptlast = False

if (_S_("runmode")) == "1":
    # User has set defined mode in settings
    promptUser = False
    if (_S_("filtergenres")) == "0":
        promptGenres = True
    elif (_S_("filtergenres")) == "1":
        promptGenres = False
        filterGenres = True
    else:
        promptGenres = False
        filterGenres = False
    if (_S_("filteryear")) == "0":
        promptYear = True
    elif (_S_("filteryear")) == "1":
        promptYear = False
        filterYear = True
    else:
        promptYear = False
        filterYear = False
    if (_S_("filterdisney")) == "0":
        promptdisney = True
    elif (_S_("filterdisney")) == "1":
        promptdisney = False
        filterdisney = True
    else:
        promptdisney = False
        filterdisney = False
    if (_S_("filterlast")) == "0":
        promptlast = True
    elif (_S_("filterlast")) == "1":
        promptlast = False
        filterlast = True
    else:
        promptlast = False
        filterlast = False
    if (_S_("filterunwatched")) == "0":
        promptUnwatched = True
    elif (_S_("filterunwatched")) == "1":
        promptUnwatched = False
        filterUnwatched = True
    else:
        promptUnwatched = False
        filterUnwatched = False
  
    trailerMode = _S_( "trailermode" ) == "true"
  
    if trailerMode:
        numTrailers = int(float(_S_( "numtrailers" ) ) )
    
    playlistMode = _S_("playlistmode") == "true"
  
else: 
    # if not, we're in prompt mode
    promptUser = True
    filterUnwatched = filterYear = filterGenres = filterdisney = trailerMode = filterlast = False
    playlistMode = _S_("playlistmode") == "true"

def getMovieLibrary():
    # get the raw JSON output
    try:
        moviestring = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "VideoLibrary.GetMovies", "params": { "fields": ["genre", "playcount", "file"]}, "id": 1}')
        moviestring = unicode(moviestring, 'utf-8', errors='ignore')
        movies = simplejson.loads(moviestring)
        testError = movies["result"]
    except:
        moviestring = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "VideoLibrary.GetMovies", "params": { "properties": ["title","playcount", "lastplayed", "studio", "writer", "plot", "votes", "top250", "originaltitle", "director", "tagline", "fanart", "runtime", "mpaa", "rating", "thumbnail", "file", "year", "genre", "trailer","set","dateadded","cast"]}, "id": 1}')
        moviestring = unicode(moviestring, 'utf-8', errors='ignore')                                                            
        movies = simplejson.loads(moviestring)
    return movies
  
def BuildFilter(movies):
    filter = sf.SelectionFilters()
  
    askGenres = askYear = askdisney = askUnwatched = askTrailer = asklast = runtime = 0
    
    if promptUser or promptUnwatched:  
        askUnwatched = xbmcgui.Dialog().yesno("Films vus","Seulement les films non vus ?")

    if askUnwatched or filterUnwatched:
        filter.SetFilter("unwatched", True)
        unwatched = True
    else:
        unwatched = False
  
    if promptUser:  
        askTrailer = xbmcgui.Dialog().yesno("Voir des bandes-annonces", "Voulez vous voir des bandes annonces ?")

    if askTrailer:
        global trailerMode
        trailerMode = True
      
    if promptUser or promptGenres:
        askGenres = xbmcgui.Dialog().yesno("Filtrer sur un genre", "Voulez-vous choisir un genre ?")

    if askGenres or filterGenres:
        success, genre = selectGenre(unwatched, trailerMode)
        if success:
            filter.SetFilter("genre", True, genre=genre)
  
    if promptUser or promptYear:    
        askYear = xbmcgui.Dialog().yesno(u"Filtrer sur l'année", u"Voulez-vous filtrer sur l'année ?")
    
    if askYear or filterYear:
        success, year = selectYear(unwatched, trailerMode)
        if success:
            filter.SetFilter("year", True, year=year)
  
    if promptUser or promptlast:    
        asklast = xbmcgui.Dialog().yesno(u"Date de téléchargement", u"Voulez-vous filtrer sur la date de téléchargement?")
    
    if asklast or filterlast:
        success, last = selectlast(unwatched, trailerMode)
        if success:
            filter.SetFilter("last", True, last=last)
  
    askRuntime = xbmcgui.Dialog().yesno(u"Filtrer durée", "Voulez-vous ignorer les films longs ?")
    
    if askRuntime:# or filterYear:
        runtime = numRuntime*60
        filter.SetFilter("runtime", True, runtime=runtime)
  
    if promptUser or promptdisney:
        askdisney = xbmcgui.Dialog().yesno("Filtrer les Disney", "Voulez-vous ignorer les Walt Disney ?")

    if askdisney or filterdisney:
        disney = u"Walt Disney"    
        filter.SetFilter("disney", True, disney=disney)
        
    return filter


def selectGenre(filterWatched, trailer):
    success = False
    selectedGenre = ""
    myGenres = []
  
    for movie in moviesJSON["result"]["movies"]:
        # Let's get the movie genres
        # If we're only looking at unwatched movies then restrict list to those movies
        if (( filterWatched and movie["playcount"] == 0 ) or not filterWatched) and ((trailer and not movie["trailer"] == "") or not trailer):
            #print movie["trailer"]
            test = simplejson.dumps(movie["genre"],ensure_ascii=False, encoding='utf8')
            #test = unicode(test, 'utf8', errors='ignore')
            test = test.replace('"','')
            test = test.replace(']','')
            test = test.replace('[','') 	  
            genres = test.split(", ")
            for genre in genres:
                # check if the genre is a duplicate
                if not genre in myGenres:
                    # if not, add it to our list
                    myGenres.append(genre)
    myGenres.append("3D")
    # sort the list alphabetically        
    mySortedGenres = sorted(myGenres)
    # prompt user to select genre
    selectGenre = xbmcgui.Dialog().select("Choisissez le genre :", mySortedGenres)
    # check whether user cancelled selection
    if not selectGenre == -1:
        # get the user's chosen genre
        selectedGenre = mySortedGenres[selectGenre]
        success = True
    else:
        success = False
    # return the genre and whether the choice was successfull
    return success, selectedGenre


def selectYear(filterWatched, trailer):
    success = False
    selectedYear = ""
    # sort the list alphabetically        
    myYear = [u'Cette année',u'2 dernières années', u'5 dernières années', u'10 dernières années', u'15 dernières années', u'20 dernières années', u'30 dernières années',u'50 dernières années']
    # prompt user to select genre
    selectYear = xbmcgui.Dialog().select(u"A partir de quelle année ", myYear)
    # check whether user cancelled selection
    if not selectYear == -1:
        # get the user's chosen genre
        selectedYear = myYear[selectYear].encode('utf-8')
        if selectedYear == u'Cette année'.encode('utf-8'):
            selectedYear = int(actualyear) - 0
            success = True
        elif selectedYear == u'2 dernières années'.encode('utf-8'):
            selectedYear = int(actualyear) - 2
            success = True
        elif selectedYear == u'5 dernières années'.encode('utf-8'):
            selectedYear = int(actualyear) - 5
            success = True
        elif selectedYear == u'10 dernières années'.encode('utf-8'):
            selectedYear = int(actualyear) - 10
            success = True
        elif selectedYear == u'15 dernières années'.encode('utf-8'):
            selectedYear = int(actualyear) - 15
            success = True
        elif selectedYear == u'20 dernières années'.encode('utf-8'):
            selectedYear = int(actualyear) - 20
            success = True
        elif selectedYear == u'30 dernières années'.encode('utf-8'):
            selectedYear = int(actualyear) - 30
            success = True
        elif selectedYear == u'50 dernières années'.encode('utf-8'):
            selectedYear = int(actualyear) - 50
            success = True
    else:
        success = False
    # return the year and whether the choice was successfult
    return success, selectedYear 

def selectlast(filterWatched, trailer):
    success = False
    selectedlast = ""
    # sort the list alphabetically        
    mylast = [u'Aujourdhui',u'Cette semaine', u'Ces 15 derniers jours', u'Ce mois', u'Ces 2 derniers mois', u'Ces 3 derniers mois', u'Ces 6 derniers mois',u'Cette année']
    # prompt user to select genre
    selectlast = xbmcgui.Dialog().select(u"Téléchargé depuis quand ?", mylast)
    # check whether user cancelled selection
    if not selectlast == -1:
        # get the user's chosen genre
        selectedlast = mylast[selectlast]
        if selectedlast == u'Aujourdhui':
            selectedlast = 1
            success = True
        elif selectedlast == u'Cette semaine':
            selectedlast = 7
            success = True
        elif selectedlast == u'Ces 15 derniers jours':
            selectedlast = 15
            success = True
        elif selectedlast == u'Ce mois':
            selectedlast = 31
            success = True
        elif selectedlast == u'Ces 2 derniers mois':
            selectedlast = 62
            success = True
        elif selectedlast == u'Ces 3 derniers mois':
            selectedlast = 93
            success = True
        elif selectedlast == u'Ces 6 derniers mois':
            selectedlast = 186
            success = True
        elif selectedlast == u'Cette année'.encode('utf-8'):
            selectedlast = 365
            success = True
    else:
        success = False
    # return the year and whether the choice was successfult
    return success, selectedlast
  
def getVideoPlaylists():
    videostring = unicode(xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "Files.GetDirectory", "params": {"directory": "special://videoplaylists"}, "id": 1}'), errors='ignore')
    myVideoPlaylists = simplejson.loads(videostring)  
    return myVideoPlaylists

def chooseVideoPlaylist(videoPlaylists):
    myPlaylists = {}
    selectPlaylist = []
    for playlist in videoPlaylists["result"]["files"]:
        myPlaylists[playlist["label"]] = playlist["file"]
        selectPlaylist.append(playlist["label"])
        #selectPlaylist.append("Cancel")

    a = xbmcgui.Dialog().select("Select playlist",selectPlaylist)  
    if not a == -1:
        playliststring = unicode(xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "Files.GetDirectory", "params": {"directory": "' + myPlaylists[selectPlaylist[a]] + '", "media": "video"}, "id": 1}'), errors='ignore')
        myVideoPlaylists = simplejson.loads(playliststring)
        showfiles = []
        for movie in myVideoPlaylists["result"]["files"]:
            showfiles.append(movie["file"])
    
        return True, showfiles
    else:
        return False, ""

def getTrailers(movieList, numTrailers):
    trailerList = []
    global trailer
    global do_timeout
    global exit_requested    
    exit_requested = False
    player = XBMCPlayer()
    # We need to check that we have enough trailers to meet our user's requirements  
    if len(movieList) <= numTrailers:
        # if we don't then we need to limit the number of trailers to show
        listLimit = len(movieList)
    else:
        listLimit = numTrailers
  
    # Build list of trailers
    myRandomMovies = []        
    while len(trailerList) < listLimit:
        movieN = random.choice(movieList)
        if not movieN in trailerList:
            trailerList.append(movieN)           
            myRandomMovies.append(movieN)
    while not exit_requested:
        for item in trailerList:
            trailer=item
            myMovieWindow=movieWindow('script-trailerwindow.xml', addon_path,'default',)
            myMovieWindow.doModal()
            del myMovieWindow
            if exit_requested:
                break
        if not exit_requested:
            while player.isPlaying():
                xbmc.sleep(250)
        exit_requested=True
    
    randomList = []
    i = 1
    for movie in myRandomMovies:
        movietitle = simplejson.dumps(movie["label"],ensure_ascii=False, encoding='utf8')
        movietitle = movietitle.replace('"','')
        movieyear = simplejson.dumps(movie["year"],ensure_ascii=False, encoding='utf8')
        movieyear = movieyear.replace('"','')
        moviegenre = simplejson.dumps(movie["genre"],ensure_ascii=False, encoding='utf8')
        moviegenre = moviegenre.replace('"','')
        movielenghth = simplejson.dumps(movie["runtime"]/3600,ensure_ascii=False, encoding='utf8')
        movielenghth = movielenghth.replace('"','')
        movielenghtm = simplejson.dumps((movie["runtime"] -(int(movielenghth)*3600))/60,ensure_ascii=False, encoding='utf8')
        movielenghth = movielenghth.replace('"','')
        movielenghtm = movielenghtm.replace('"','')
        randomList.append(str(i) + ' : '+ movietitle + ' (' +movieyear+') - ' + moviegenre +' - ' +movielenghth + 'h' + movielenghtm +'min')
        i+=1
    if randomList == []:
        a = xbmcgui.Dialog().ok('Dommage', u'Aucun de vos films ne repond aux critères')
    else:
        a = xbmcgui.Dialog().select("Quel film voulez-vous lancer :", randomList)
    if not a == -1 and not randomList == []:
        success = True
        myMovie = simplejson.dumps(myRandomMovies[a]["file"],ensure_ascii=False, encoding='utf8')
    else:
        success = False
        myMovie = ""
    
    return success, myMovie

def FilterMovies(movies, filter, trailer):
    filteredlist = []
    for movie in movies["result"]["movies"]:
        if ((trailer and not movie["trailer"] == '') or not trailer):
            if filter.MeetsCriteria(movie):
                filteredlist.append(movie)

    return filteredlist

moviesJSON = getMovieLibrary()
# Create filter
bs = blankWindow('script-BlankWindow.xml', addon_path,'default',)
bs.show()
filter = BuildFilter(moviesJSON)
# apply filter to our library
filteredMovies = FilterMovies(moviesJSON, filter, trailerMode)
if trailerMode:
    success, myMovie = getTrailers(filteredMovies, numTrailers)
    if success:
        xbmc.executebuiltin('Playmedia(' + myMovie.encode('utf-8') + ')')
    elif _S_( "randommode" )=='true':
        randomMovie = random.choice(filteredMovies)
        xbmc.executebuiltin('Playmedia(' + randomMovie["file"].encode('utf-8') + ')')
del bs
