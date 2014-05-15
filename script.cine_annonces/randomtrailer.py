# -*- coding: latin-1 -*-
import xbmc
import xbmcgui
import sys
import os
import random
import simplejson as json
import time
import datetime
import xbmcaddon
from datetime import date
addon = xbmcaddon.Addon()
number_trailers =  addon.getSetting('number_trailers')
do_curtains = addon.getSetting('do_animation')
do_year = addon.getSetting('do_year')
do_genre = addon.getSetting('do_genre')
do_last = addon.getSetting('do_last')
do_mute = addon.getSetting('do_mute')
hide_info = addon.getSetting('hide_info')
addon_path = addon.getAddonInfo('path')
hide_watched = addon.getSetting('hide_watched')
watched_days = addon.getSetting('watched_days')
resources_path = xbmc.translatePath( os.path.join( addon_path, 'resources' ) ).decode('utf-8')
media_path = xbmc.translatePath( os.path.join( resources_path, 'media' ) ).decode('utf-8')
open_curtain_path = xbmc.translatePath( os.path.join( media_path, 'OpenSequence.mp4' ) ).decode('utf-8')
close_curtain_path = xbmc.translatePath( os.path.join( media_path, 'ClosingSequence.mp4' ) ).decode('utf-8')
selectedGenre =''
exit_requested = False
movie_file = ''
viewed=[]
actualyear = date.today().year
if len(sys.argv) == 2:
	do_genre ='false'
else:
	do_password='false'

trailer=''
do_timeout = False
def askGenres():
	addon = xbmcaddon.Addon()
	# default is to select from all movies
	selectGenre = False
	# ask user whether they want to select a genre
	a = xbmcgui.Dialog().yesno("Genre", "Voulez-vous choisir un genre ?")
	# deal with the output
	if a == 1: 
	# set filter
		selectGenre = True
	return selectGenre  

def selectGenre():
	success = False
	selectedGenre = ""
	myGenres = []
	trailerstring = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "VideoLibrary.GetMovies", "params": { "properties": ["genre", "playcount", "file", "trailer"]}, "id": 1}')
	trailerstring = unicode(trailerstring, 'utf-8', errors='ignore')
	trailers = json.loads(trailerstring)
	for movie in trailers["result"]["movies"]:
		# Let's get the movie genres
		genres = movie["genre"]
		for genre in genres:
			# check if the genre is a duplicate
			if not genre in myGenres and not genre =='':
				# if not, add it to our list
				myGenres.append(genre)
	myGenres.append("3D")
	# sort the list alphabetically       
	mySortedGenres = sorted(myGenres)
	# prompt user to select genre
	selectGenre = xbmcgui.Dialog().select('Choisissez un genre', mySortedGenres)
	# check whether user cancelled selection
	if not selectGenre == -1:
		# get the user's chosen genre
		selectedGenre = mySortedGenres[selectGenre].encode('utf-8')
		success = True
	else:
		success = False
	# return the genre and whether the choice was successfult
	return success, selectedGenre
def askyear():
	# default is to select from all movies
	selectyear = False
	# ask user whether they want to select a year
	a = xbmcgui.Dialog().yesno(u"Filtrer sur l'année", u"Voulez-vous filtrer sur l'année ?")
	# deal with the output
	if a == 1: 
		# set filter
		selectyear = True
	return selectyear

def selectYear():
	success = False
	selectedYear = ""
	# sort the list alphabetically        
	myYear = [u'Cette année', u'2 dernères années', u'5 dernères années', u'10 dernères années', u'15 dernères années', u'20 dernères années', u'30 dernères années', u'50 dernères années']
	# prompt user to select genre
	selectYear = xbmcgui.Dialog().select(u"A partir de quelle année ", myYear)
	# check whether user cancelled selection
	if not selectYear == -1:
		# get the user's chosen genre
		selectedYear = myYear[selectYear]
	if selectedYear == u'Cette année':
		selectedYear = int(actualyear) - 0
		success = True
	elif selectedYear == u'2 dernères années':
		selectedYear = int(actualyear) - 2
		success = True
	elif selectedYear == u'5 dernères années':
		selectedYear = int(actualyear) - 5
		success = True
	elif selectedYear == u'10 dernères années':
		selectedYear = int(actualyear) - 10
		success = True
	elif selectedYear == u'15 dernères années':
		selectedYear = int(actualyear) - 15
		success = True
	elif selectedYear == u'20 dernères années':
		selectedYear = int(actualyear) - 20
		success = True
	elif selectedYear == u'30 dernères années':
		selectedYear = int(actualyear) - 30
		success = True
	elif selectedYear == u'50 dernères années':
		selectedYear = int(actualyear) - 50
		success = True
	else:
		success = False
	# return the year and whether the choice was successfult
	return success, selectedYear 

def asklast():
	# default is to select from all movies
	selectlast = False
	# ask user whether they want to select a year
	a = xbmcgui.Dialog().yesno(u"Date de téléchargement", u"Voulez-vous filtrer sur la date de téléchargement ?")
	# deal with the output
	if a == 1: 
		# set filter
		selectlast = True
	return selectlast

def selectlast():
	success = False
	selectedlast = ""
	# sort the list alphabetically        
	mylast = ['Aujourdhui', 'Cette semaine', 'Ces 15 derniers jours', 'Ce mois', 'Ces 2 derniers mois', 'Ces 3 derniers mois', 'Ces 6 derniers mois', u'Cette année']
	# prompt user to select genre
	selectlast = xbmcgui.Dialog().select(u"Téléchargé depuis quand ?", mylast)
	# check whether user cancelled selection
	if not selectlast == -1:
		# get the user's chosen genre
		selectedlast = mylast[selectlast]
	if selectedlast == 'Aujourdhui':
		selectedlast = 1
		success = True
	elif selectedlast == 'Cette semaine':
		selectedlast = 7
		success = True
	elif selectedlast == 'Ces 15 derniers jours':
		selectedlast = 15
		success = True
	elif selectedlast == 'Ce mois':
		selectedlast = 31
		success = True
	elif selectedlast == 'Ces deux derniers mois':
		selectedlast = 62
		success = True
	elif selectedlast == 'Ces 3 derniers mois':
		selectedlast = 93
		success = True
	elif selectedlast == 'Ces 6 derniers mois':
		selectedlast = 186
		success = True
	elif selectedlast == u'Cette année':
		selectedlast = 365
		success = True
	else:
		success = False
	# return the year and whether the choice was successfult
	return success, selectedlast

def getTrailers(genre,year,last):
	# get the raw JSON output
	list3D=[]
	if last == '':
		if genre == '3D':
			trailerstring = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "VideoLibrary.GetMovies", "params": {"properties": ["title", "lastplayed", "studio", "writer", "plot", "votes", "top250", "originaltitle", "director", "tagline", "fanart", "runtime", "mpaa", "rating", "thumbnail", "file", "year", "genre", "trailer","cast"], "filter": { "and":[{"field": "year", "operator": "greaterthan", "value": "%s"}]}}, "id": 1}' % (str(year)))
		else:	
			trailerstring = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "VideoLibrary.GetMovies", "params": {"properties": ["title", "lastplayed", "studio", "writer", "plot", "votes", "top250", "originaltitle", "director", "tagline", "fanart", "runtime", "mpaa", "rating", "thumbnail", "file", "year", "genre", "trailer","cast"], "filter": { "and":[{"field": "genre", "operator": "contains", "value": "%s"},{"field": "year", "operator": "greaterthan", "value": "%s"}]}}, "id": 1}' % (genre,str(year)))
	else:
		if genre == '3D':
			trailerstring = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "VideoLibrary.GetMovies", "params": {"properties": ["title", "lastplayed", "studio", "writer", "plot", "votes", "top250", "originaltitle", "director", "tagline", "fanart", "runtime", "mpaa", "rating", "thumbnail", "file", "year", "genre", "trailer","cast"], "filter": { "and":[{"field": "year", "operator": "greaterthan", "value": "%s"},{"field":"dateadded","operator":"inthelast","value":"%s"}]}}, "id": 1}' % (str(year),str(last)))
		else:
			trailerstring = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "VideoLibrary.GetMovies", "params": {"properties": ["title", "lastplayed", "studio", "writer", "plot", "votes", "top250", "originaltitle", "director", "tagline", "fanart", "runtime", "mpaa", "rating", "thumbnail", "file", "year", "genre", "trailer","cast"], "filter": { "and":[{"field": "genre", "operator": "contains", "value": "%s"},{"field": "year", "operator": "greaterthan", "value": "%s"},{"field":"dateadded","operator":"inthelast","value":"%s"}]}}, "id": 1}' % (genre,str(year),str(last)))
	trailerstring = unicode(trailerstring, 'utf-8', errors='ignore')
	trailers = json.loads(trailerstring)
	if genre =='3D':
		for x in trailers['result']['movies']:
			if '3DBD' in x['file']:
				list3D.append(x)
		trailers['result']['movies']=list3D
	return trailers

class movieWindow(xbmcgui.WindowXMLDialog):

	def onInit(self):
		global SelectedGenre
		global SelectedYear
		global SelectedLast
		global trailer
		global do_timeout
		global viewed
		trailer=random.choice(trailers["result"]["movies"])
		lastPlay = True
		if not trailer["lastplayed"] =='' and hide_watched == 'true':
			pd=time.strptime(trailer["lastplayed"],'%Y-%m-%d %H:%M:%S')
			pd = time.mktime(pd)
			pd = datetime.datetime.fromtimestamp(pd)
			lastPlay = datetime.datetime.now() - pd
			lastPlay = lastPlay.days
			if lastPlay > int(watched_days) or watched_days == '0':
				lastPlay = True
			else:
				lastPlay = False
		if  trailer["trailer"] != '' and lastPlay and trailer["movieid"] not in viewed:
			if hide_info == 'false':
				viewed.append(trailer["movieid"])
				w=infoWindow('script-DialogVideoInfo.xml',addon_path,'default')
				do_timeout=True
				w.doModal()
				do_timeout=False
				del w
				if exit_requested:
					xbmc.Player().stop()
			else:
				viewed.append(trailer["movieid"])
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
		ACTION_STOP = 13
		
		xbmc.log('action  =' + str(action.getId()))
		
		global exit_requested
		global movie_file
		if action == ACTION_PREVIOUS_MENU or action == ACTION_LEFT or action == ACTION_BACK or action == ACTION_STOP:
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
		ACTION_STOP = 13
		
		xbmc.log('action  =' + str(action.getId()))
		global do_timeout
		global exit_requested
		global movie_file
		if action == ACTION_PREVIOUS_MENU or action == ACTION_LEFT or action == ACTION_BACK or ACTION_STOP:
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
		
def playTrailers():
	bs=blankWindow('script-BlankWindow.xml', addon_path,'default',)
	bs.show()
	global exit_requested
	global movie_file
	movie_file = ''
	exit_requested = False
	player = XBMCPlayer()
	#xbmc.log('Getting Trailers')
	DO_CURTIANS = addon.getSetting('do_animation')
	DO_EXIT = addon.getSetting('do_exit')
	NUMBER_TRAILERS =  int(addon.getSetting('number_trailers'))
	if do_mute == 'true':
		muted = xbmc.getCondVisibility("Player.Muted")
		if not muted:
			xbmc.executebuiltin('xbmc.Mute()')
	if DO_CURTIANS == 'true':
		player.play(open_curtain_path)
		while player.isPlaying():
			xbmc.sleep(250)
	trailercount = 0
	while not exit_requested:
		if NUMBER_TRAILERS == 0:
			while not exit_requested and not xbmc.abortRequested:
				myMovieWindow = movieWindow('script-trailerwindow.xml', addon_path,'default',)
				myMovieWindow.doModal()
				del myMovieWindow
		else:
			for x in xrange(0, NUMBER_TRAILERS):
				myMovieWindow = movieWindow('script-trailerwindow.xml', addon_path,'default',)
				myMovieWindow.doModal()
				del myMovieWindow
				if exit_requested:
					break
		if not exit_requested:
			if DO_CURTIANS == 'true':
				player.play(close_curtain_path)
				while player.isPlaying():
					xbmc.sleep(250)
		exit_requested=True
	if do_mute == 'true':
		muted = xbmc.getCondVisibility("Player.Muted")
		if muted:
			xbmc.executebuiltin('xbmc.Mute()')
	if not movie_file == '':
		xbmc.Player(0).play(movie_file)
	del bs

filtergenre = False
filteryear = False
filterlast = False
if do_genre == 'true':
	filtergenre = askGenres()
successgenre = False
if filtergenre:
	successgenre, selectedGenre = selectGenre()
if do_year == 'true':
	filteryear = askyear()
successyear = False
if filteryear:
	successyear, selectedYear = selectYear()
if do_last == 'true':
	filterlast = asklast()
successlast = False
if filterlast:
	successlast, selectedlast = selectlast()
if successgenre:
	genrechoice=selectedGenre
else:
	genrechoice=''
if successyear:
	yearchoice=selectedYear-1
else:
	yearchoice=''
if successlast:
	lastchoice=selectedlast
else:
	lastchoice=''
trailers = getTrailers(genrechoice,yearchoice,lastchoice)
if len(trailers['result']['movies'])==0:
	xbmcgui.Dialog().ok('Dommage', 'Aucun de vos films ne repond aux critères')
else:
	playTrailers()
