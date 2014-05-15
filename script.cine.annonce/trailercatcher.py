# -*- coding: latin-1 -*-
import subprocess
import time
import datetime
import sys
import os.path
import unicodedata
import Tkinter
import shutil
import tkFileDialog
import glob
import pprint
from allocine import allocine
import urllib
import urllib2
import logging
import mechanize
import re
from bs4 import BeautifulSoup
import xbmc
import xbmcgui
import simplejson
import random
api = allocine()
api.configure('100043982026','29d185d98c984a359e6e6f26a0474269')
rootDir = os.path.dirname(os.path.abspath(__file__))
try:
    _DEV_NULL = subprocess.DEVNULL
except AttributeError:
    _DEV_NULL = open(os.devnull, 'wb')

class trailercatcher(object):
    
    def logg(self,str,debug=None):
        ts=datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
        print (ts+' : '+str.encode('utf-8'))
        return True
    
    def cleantitle(self,title):
        specialchars=['/','(',')',',','.',';','!','?','-',':','_','[',']','|','  ','  ','  ']
        title=unicodedata.normalize('NFKD',title).encode('ascii','ignore')
        for chars in specialchars:
            title=title.replace(chars,' ')        
        return title.lower()
    
    def controltitle(self,title,moviename):
        realtitle=self.cleantitle(moviename[:-5].decode('unicode-escape'))
        year=moviename[len(moviename)-4:]
        listcommonwords=['youtube','dailymotion','vf','francais','francaise','vo','vost','version','annonce','bande','bande-annonce','trailer',
                         'vostfr','fr','bandeannonce','video','ba','hd','hq','720p','1080p','film','official','#1','#2',
                         '#4','#6','#7','du','and','premiere','n°1','n°2','n°3','n°4','n°5','officielle','theatrical']
        wordsleft=[]
        cleantitles=self.cleantitle(title)
        for word in cleantitles.split():
            if word not in listcommonwords and word not in realtitle.split() and word<>year:
                wordsleft.append(word)
        self.logg(title+' \\\\nettoye en//// '+str(wordsleft),True)
        if len(wordsleft)==0:
            return True
        else:
            return False

    def controltitle2(self,title,moviename):
        realtitle=self.cleantitle(moviename[:-5].decode('unicode-escape'))
        year=moviename[len(moviename)-4:]
        wordsleft=[]
        cleantitles=self.cleantitle(title)
        for word in realtitle.split():
            if word not in cleantitles.split():
                wordsleft.append(word)
        self.logg(title+' \\\\mots non trouves//// '+str(wordsleft),True)
        if len(wordsleft)==0:
            return True
        else:
            return False
        
    def cleandic(self,dict,moviename):
        series=['2','3','4','5','6','7','8']
        titlenames=dict.keys()
        listkeysvf=[]
        listkeysvostfr=[]
        listkeysvo=[]
        year=moviename[len(moviename)-4:]
        for titledict in titlenames:
            testcontinue=self.controltitle(titledict,moviename)
            if testcontinue==False:
                continue
            testcontinue2=self.controltitle2(titledict,moviename)
            if testcontinue2==False:
                continue
            cleandict=self.cleantitle(titledict)
            if ('vf' in cleandict or 'francais' in cleandict or ' fr ' in cleandict) and not ' vo ' in cleandict :
                if year in cleandict:
                    listkeysvf.append(titledict)
                else:
                    compteur=0
                    for x in series:
                        if x in cleandict and not x in moviename[:-5]:
                            compteur+=1
                    if compteur==0:
                        listkeysvf.append(titledict)
            elif ('vost' in cleandict):
                if year in cleandict:
                    listkeysvostfr.append(titledict)
                else:
                    compteur=0
                    for x in series:
                        if x in cleandict and not x in moviename[:-5]:
                            compteur+=1
                    if compteur==0:
                        listkeysvostfr.append(titledict)
            else:
                self.logg('Aucun moyen didentifier la langue pour '+cleandict+' je suppose que cest de la VO')
                if year in cleandict:
                    listkeysvo.append(titledict)
                else:
                    compteur=0
                    for x in series:
                        if x in cleandict and not x in moviename[:-5]:
                            compteur+=1
                    if compteur==0:
                        listkeysvo.append(titledict)
        urllistvf=[]
        urllistvostfr=[]
        urllistvo=[]
        for listkey in listkeysvf:
            urllistvf.append(dict[listkey])
        for listkey in listkeysvostfr:
            urllistvostfr.append(dict[listkey])
        for listkey in listkeysvo:
            urllistvo.append(dict[listkey])
        self.logg(str(len(urllistvf)) + ' liens de bandes annonces VF trouves sur google')
        self.logg(str(len(urllistvostfr)) + ' liens de bandes annonces VOSTFR trouves sur google')
        self.logg(str(len(urllistvo)) + ' liens de bandes annonces VO trouves sur google')
        return urllistvf,urllistvostfr,urllistvo
            
    def libraryscan(self,path):
        self.logg('Veuillez patienter pendant la recherche des films sans bandes-annonces dans ' + path)
        fichier=[] 
        self.logg('Calcul en cours....')
        numberfiles=0
        pathori=path
        trailerfound=''
        for path, dires, fics in os.walk(path):
            for f in fics:
                numberfiles+=1
        currentnumber=0
        for root, dirs, files in os.walk(pathori):
            for i in files:
                currentnumber+=1
                trailercount=0
                if ('.mkv' in i.lower() or '.avi' in i.lower() or '.mp4' in i.lower() or '.m2ts' in i.lower() or '.mk3d' in i.lower()) and '-trailer' not in i:
                    for x in os.listdir(root):
                        if '-trailer' in x:
                            trailercount+=1
                            trailerfound=x
                    if trailercount==0:
                        fileroot=root
                        filename=i
                        filename=filename[:filename.rfind(")")].replace(' 3DBD','').replace('(','').replace(')','')
                        fichier.append([fileroot,filename,i[:-4]])
                    self.logg(str(currentnumber)+' fichiers scannes sur un total de '+str(numberfiles))   
        self.logg(str(numberfiles)+' fichiers scannes sur un total de '+str(numberfiles))
        return fichier,trailerfound
    
    def googlesearch(self,searchstringori):
        uploadtoignore=['UniversalMoviesFR','ParamountmoviesFR']
        time.sleep(15)
        searchstring=searchstringori[:-5].replace(' ','+')
        
        regexurl ="url(?!.*url).*?&amp"
        patternurl = re.compile(regexurl)
    
        regextitle='">(?!.*">).*?<\/a'
        patterntitle= re.compile(regextitle)
    
        br=mechanize.Browser()
        br.set_handle_robots(False)
        br.addheaders=[('User-agent','chrome')]
    
        query="https://www.google.fr/search?num=100&q=bande-annonce+OR+bande+OR+annonce"+'"'+searchstring+'"'+"+VF+HD+site:http://www.youtube.com+OR+site:http://www.dailymotion.com&ie=latin-1&oe=latin-1&aq=t&rls=org.mozilla:fr:official&client=firefox-a&channel=np&source=hp&gfe_rd=cr&ei=MW9lU_vDIK2A0AXbroCADw"
        self.logg('En train de rechercher sur google : ' +searchstring)
        self.logg('Query : ' +query,True)
        htmltext=br.open(query).read()
        soup=BeautifulSoup(htmltext)
        search=soup.findAll('div',attrs={'id':'search'})
        searchtext = str(search[0])
    
        soup1=BeautifulSoup(searchtext)
        list_items=soup1.findAll('li')
        urldic={}
        for li in list_items:
            try:
                doweignore=0
                soup2 = BeautifulSoup(str(li))
                for toignore in uploadtoignore:
                    if toignore in str(soup2):
                        doweignore+=1
                if doweignore<>0:
                    continue
                links= soup2.findAll('a')
                if not 'webcache' in str(links): 
                    source_link=links[0]
                    source_url = str(re.findall(patternurl,str(source_link))[0]).replace('url?q=','').replace('&amp','').replace('%3F','?').replace('%3D','=')
                    source_title= str(re.findall(patterntitle,str(source_link))[0]).replace('">','').replace('</a','').replace('<b>','').replace('</b>','').decode("utf-8")
                    urldic.update({source_title:source_url})
                
            except:
                continue
        self.logg(str(len(urldic))+ ' resultats trouves sur google')
        return urldic
      
    def allocinesearch(self,moviename):
        series=['2','3','4','5','6','7','8']
        listallovostfr=[]
        listallovo=[]
        listallovf=[]
        self.logg('Tentative de recherche sur Allocine de ' +moviename[:-5])
        try:
            search = api.search(moviename[:-5], "movie")
            for result in search['feed']['movie']:
                countseries=0
                ficheresult=api.movie(result['code'])
                ficheresulttitle=self.cleantitle(ficheresult['movie']['title'])
                ficheresulttitleori=self.cleantitle(ficheresult['movie']['originalTitle'])
                yearresult=ficheresult['movie']['productionYear']
                test=self.cleantitle(moviename[:-5].decode('unicode-escape'))
                if not yearresult:
                    yearresult=0
                for x in series:
                    if (x in ficheresulttitle or x in ficheresulttitleori) and (not '3d' in ficheresulttitle and not '3d' in ficheresulttitleori):
                        if x not in moviename[:-5]:
                            countseries+=1                        
                if self.cleantitle(moviename[:-5].decode('unicode-escape')) in ficheresulttitle and countseries==0 and int(moviename[len(moviename)-4:])+2>yearresult and int(moviename[len(moviename)-4:])-2<yearresult:
                    goodresult=result
                    break
            
            self.logg('Recherche de la fiche du film avec le code : ' + str(goodresult['code']))
            movieallo = ficheresult
            for x in movieallo['movie']['link']:
                if x.has_key('name') and 'Bandes annonces' in x['name']:
                    pagetrailer=x['href']
                else:
                    continue
            soup = BeautifulSoup( urllib2.urlopen(pagetrailer), "html.parser" )
            rows = soup.findAll("a")
            
            for lien in rows:
                try:
                    if 'annonce' in str(lien).lower() and 'vf' in str(lien).lower():
                        lienid=lien['href'][:lien['href'].find('&')].replace('/video/player_gen_cmedia=','')
                        self.logg("Potentiel code de bande annonce [{0}] en VF".format(lienid))
                        trailerallo = api.trailer(lienid)
                        long=len(trailerallo['media']['rendition'])
                        bestba=trailerallo['media']['rendition'][long-1]
                        linkallo=trailerallo['media']['rendition'][long-1]['href']
                        heightbaallo=bestba['height']
                        longadr=len(linkallo)
                        extallo=linkallo[longadr-3:]
                        
                        listallovf.append({'link':linkallo,'ext':extallo,'height':heightbaallo})
                        if heightbaallo>=481:
                            self.logg('Bande annonce vf et HD trouve sur Allocine jarrete de chercher')
                            break
                        else:
                            self.logg('Bande annonce vf non HD trouve sur Allocine je continue de chercher')
                    elif 'annonce' in str(lien).lower() and 'vost' in str(lien).lower():
                        lienid=lien['href'][:lien['href'].find('&')].replace('/video/player_gen_cmedia=','')
                        self.logg("Potentiel code de bande annonce [{0}] en VOSTFR".format(lienid))
                        trailerallo = api.trailer(lienid)
                        long=len(trailerallo['media']['rendition'])
                        bestba=trailerallo['media']['rendition'][long-1]
                        linkallo=trailerallo['media']['rendition'][long-1]['href']
                        heightbaallo=bestba['height']
                        longadr=len(linkallo)
                        extallo=linkallo[longadr-3:]
                        
                        listallovostfr.append({'link':linkallo,'ext':extallo,'height':heightbaallo})
                        self.logg('Bande annonce vostfr trouve sur Allocine je continue de chercher')
                    elif 'annonce' in str(lien).lower() and ' VO' in str(lien):
                        lienid=lien['href'][:lien['href'].find('&')].replace('/video/player_gen_cmedia=','') 
                        trailerallo = api.trailer(lienid)
                        long=len(trailerallo['media']['rendition'])
                        bestba=trailerallo['media']['rendition'][long-1]
                        linkallo=trailerallo['media']['rendition'][long-1]['href']
                        heightbaallo=bestba['height']
                        longadr=len(linkallo)
                        extallo=linkallo[longadr-3:]
                        if hasattr(trailerallo['media'],'subtitles') and trailerallo['media']['subtitles']['$'].lower().replace('ç','c') ==u'francais':
                            self.logg("Potentiel code de bande annonce [{0}] en VOSTFR".format(lienid))
                            listallovostfr.append({'link':linkallo,'ext':extallo,'height':heightbaallo})
                            self.logg('Bande annonce vostfr trouve sur Allocine je continue de chercher')
                        else:
                            self.logg("Potentiel code de bande annonce [{0}] en VO".format(lienid))
                            listallovo.append({'link':linkallo,'ext':extallo,'height':heightbaallo})
                            self.logg('Bande annonce vo trouve sur Allocine je continue de chercher')
                    
                    else:
                        continue
                except Exception,e:
                    print e
                    continue
            self.logg(str(len(listallovf)) +" bandes annonces en VF trouvees sur allocine")
            self.logg(str(len(listallovostfr)) +" bandes annonces en VOSTFR trouvees sur allocine")
            self.logg(str(len(listallovo)) +" bandes annonces en VO trouvees sur allocine")       
            return listallovf,listallovostfr,listallovo
        except :
            self.logg(str(len(listallovf)) +" bandes annonces en VF trouvees sur allocine")
            self.logg(str(len(listallovostfr)) +" bandes annonces en VOSTFR trouvees sur allocine")
            self.logg(str(len(listallovo)) +" bandes annonces en VO trouvees sur allocine")  
            return listallovf,listallovostfr,listallovo
           
    def quacontrol(self,url):
        quallist=[]
        p=subprocess.Popen([os.path.join(rootDir,'youtube-dl.exe'), '-F',url], shell=True, stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        while p.poll() is None:
            l = p.stdout.readline()
            quallist.append(l)
        (out, err) = p.communicate()
        for qual in quallist:
            if 'best' in qual and ('720' in qual or '1080' in qual):
                return True
            else:
                continue
        return False
    
    
    def quacontrolallo(self,listallo,type):
        bestqualallo=0
        for linkvf in listallo:
            if bestqualallo<linkvf['height']:
                bestqualallo=linkvf['height']
        self.logg('Meilleure resolution trouvee sur Allocine en '+type+' : '+str(bestqualallo)+'p')
        return bestqualallo
    
    def videodl(self,cleanlist,trailername,moviename,trailerpath,allo=False,maxheight=0):
        if allo:
            for url in cleanlist:
                if maxheight==url['height']:
                    linkallo=url['link']
                    heightbaallo=url['height']
                    extallo=url['ext']
                    self.logg('Telechargement de la bande annonce suivante : ' + linkallo +' en '+str(heightbaallo)+'p en cours...')
                    try:
                        urllib.urlretrieve(linkallo, os.path.join(trailerpath,trailername)+'.'+extallo)
                        self.logg('Une bande annonce telechargee pour ' + moviename +' sur Allocine')
                        
                        return trailerpath+'/'+trailername+'.'+extallo
                        break
                    except:
                        continue
            return False
        else:
            bocount=0
            for bo in cleanlist:
                if bocount==0:
                    try:
                        self.logg('En train de telecharger : ' + bo + ' pour ' +moviename)
                        tempdest=unicodedata.normalize('NFKD', os.path.join(rootDir,trailername.replace("'",''))).encode('ascii','ignore')+u'.%(ext)s'
                        dest=os.path.join(trailerpath,trailername)
                        p=subprocess.Popen([os.path.join(rootDir,'youtube-dl.exe'), '-o',tempdest,'--newline', '--max-filesize', '105m', '--format','best',bo],shell=True, stdout=subprocess.PIPE,stderr=subprocess.PIPE)
                        while p.poll() is None:
                            l = p.stdout.readline()
                            if 'download' in l:
                                print l.replace('\n','')
                        (out, err) = p.communicate()
                        print out.replace('\n','')
                        print err.replace('\n','')
                        if err:
                            continue
                        else:
                            listetemp=glob.glob(os.path.join(rootDir,'*'))
                            for listfile in listetemp:
                                if unicodedata.normalize('NFKD', trailername.replace("'",'')).encode('ascii','ignore') in listfile:
                                    ext=listfile[-4:]
                                    destination=dest+ext
                                    shutil.move(listfile, destination)
                                    bocount=1
                                    self.logg('Une bande annonce telechargee pour ' + moviename)
                                    
                                    return trailerpath+'/'+trailername+ext
                        
                    except Exception,e:
                        print str(e)
                        continue
                else:
                    continue
            return False
        
    def totqualcontrol(self,listcontrol,type):
        compteurhd=0
        cleanlist=[]
        listlowq=[]
        for tocontrolqual in listcontrol:
            if compteurhd==3:
                self.logg('Suffisamment de bandes annonces '+type+ ' HD trouvees plus la peine de continuer')
                break
            self.logg('Controle de la qualite reelle de ' +tocontrolqual+ ' en cours...')
            
            if self.quacontrol(tocontrolqual):
                self.logg('La qualite de ' +tocontrolqual+' semble HD je rajoute a la liste  HD '+type)
                cleanlist.append(tocontrolqual)
                compteurhd+=1
            else:
                self.logg('Pfffff encore un mytho la qualite de ' +tocontrolqual+' nest pas HD je rajoute a la liste non HD '+type)
                listlowq.append(tocontrolqual)
        return cleanlist, listlowq
            
    def trailersearch(self,moviefolder):
        dp=xbmcgui.DialogProgress()
        dp.create('Recherche','','','En cours')
        self.logg('Ceci est une beta. Certaines bandes annonces pourront etre en anglais voir ne pas correspondre au film')
        if len(moviefolder) > 0:
            self.logg("Vous avez choisi : %s" % moviefolder)
        
        path = moviefolder
        
        fichier,trailerfound = self.libraryscan(path)
        if len(fichier)>0:
            self.logg(str(len(fichier)) + ' films sans bandes annonces ont ete trouves')
            for moviewithouttrailer in fichier:
                self.logg(unicodedata.normalize('NFKD', moviewithouttrailer[1]).encode('ascii','ignore'))
        else:
            self.logg('Aucun film sans bande annonce trouve')
            xbmcgui.Dialog().notification(u'Le film possède une bande annonce', u'Je rafraichis la base de données avec', xbmcgui.NOTIFICATION_INFO, 5000)
            os.path.join(moviefolder,trailerfound)
            return moviefolder+'/'+trailerfound
              
        for movie in fichier:
            trailerpath=movie[0]
            moviename = unicodedata.normalize('NFKD', movie[1]).encode('ascii','ignore')
            trailername=movie[2]+'-trailer'
            searchstring=moviename
            listvfallo,listvostfrallo,listvoallo=self.allocinesearch(moviename)
            if listvfallo:
                maxqual=self.quacontrolallo(listvfallo,'vf')
                for url in listvfallo:
                    if maxqual==url['height']:
                        xbmc.Player().play(url['link'])
                        xbmc.sleep(1000)
                        dp.close()
                        xbmc.sleep(1000)
                        dp.create(u'Lecture d\'une bande annonce provisoire','','',u'en attendant la recherche et le téléchargement')
                        
            elif listvostfrallo:
                maxqual=self.quacontrolallo(listvostfrallo,'vostfr')
                for url in listvostfrallo:
                    if maxqual==url['height']:
                        xbmc.Player().play(url['link'])
                        xbmc.sleep(1000)
                        dp.close()                        
                        xbmc.sleep(1000)
                        dp.create(u'Lecture d\'une bande annonce provisoire','','',u'en attendant la recherche et le téléchargement')
                                        
            elif listvoallo:
                maxqual=self.quacontrolallo(listvoallo,'vo')
                for url in listvoallo:
                    if maxqual==url['height']:
                        xbmc.Player().play(url['link'])
                        xbmc.sleep(1000)
                        dp.close()                        
                        xbmc.sleep(1000)
                        dp.create(u'Lecture d\'une bande annonce provisoire','','',u'en attendant la recherche et le téléchargement')
            else:
                moviestring = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "VideoLibrary.GetMovies", "params": { "properties": ["trailer"]}, "id": 1}')
                moviestring = unicode(moviestring, 'utf-8', errors='ignore')                                                            
                movies = simplejson.loads(moviestring)
                havetrailer=[]
                for movie in movies["result"]["movies"]:
                    if '-trailer' in movie["trailer"]:
                        havetrailer.append(movie["trailer"])
                if havetrailer:
                    random.shuffle(havetrailer)
                    xbmc.Player().play(havetrailer[0])
                    xbmc.sleep(1000)
                    dp.close()                        
                    xbmc.sleep(1000)
                    dp.create(u'Lecture d\'une bande annonce aléatoire','','',u'en attendant la recherche et le téléchargement')
                else:
                    dp.close()                        
                    xbmc.sleep(1000)
                    dp.create(u'Rien à montrer','','',u'en attendant la recherche et le téléchargement')
                
            if listvfallo:
                maxqual=self.quacontrolallo(listvfallo,'vf')
                       
                if maxqual>=481:
                    xbmc.sleep(5000)
                    dp.close()
                    xbmc.sleep(1000)
                    dp.create(u'Téléchargement','','','Bande annonce en VF en cours')
                    path=self.videodl(listvfallo,trailername,moviename,trailerpath,True,maxqual)
                    xbmcgui.Dialog().notification(u'Bande annonce téléchargée', u'Bande annonce téléchargée en VF. BDD mise à jour', xbmcgui.NOTIFICATION_INFO, 5000)
                    dp.close()
                    return path
                else:
                    self.logg('Bande annonce en VF non HD trouvee sur Allocine tentative de recherche dune meilleure qualite sur google')
            else:
                self.logg('Rien trouve sur Allocine en VF tentative de recherche sur google')
            urldic=self.googlesearch(searchstring)
            listgooglevf, listgooglevostfr,listgooglevo=self.cleandic(urldic,moviename)
            if listvfallo:
                maxqual=self.quacontrolallo(listvfallo,'vf')
                if listgooglevf:
                    self.logg('Jai trouve des bandes annonces VF sur google, controlons leur qualite')
                    cleanlistvf,listlowqvf=self.totqualcontrol(listgooglevf,'vf')
                    if cleanlistvf:
                        dp.close()
                        xbmc.sleep(1000)
                        dp.create(u'Téléchargement','','','Bande annonce en VF en cours')
                        self.logg('Si jen crois google jai trouve mieux que la bande annonce allocine . Lets go')
                        path=self.videodl(cleanlistvf,trailername,moviename,trailerpath)
                        xbmcgui.Dialog().notification(u'Bande annonce téléchargée', u'Bande annonce téléchargée en VF. BDD mise à jour', xbmcgui.NOTIFICATION_INFO, 5000)
                        dp.close()
                        return path
                    else:
                        dp.close()
                        xbmc.sleep(1000)
                        dp.create(u'Téléchargement','','','Bande annonce en VF en cours')
                        self.logg('Rien trouve de mieux sur google pour : '+moviename+' je telecharge donc la bande annonce non HD vf Allocine')
                        maxqual=self.quacontrolallo(listvfallo,'vf')
                        path=self.videodl(listvfallo,trailername,moviename,trailerpath,True,maxqual)
                        xbmcgui.Dialog().notification(u'Bande annonce téléchargée', u'Bande annonce téléchargée en VF. BDD mise à jour', xbmcgui.NOTIFICATION_INFO, 5000)
                        dp.close()
                        return path
                else:
                    dp.close()
                    xbmc.sleep(1000)
                    dp.create(u'Téléchargement','','','Bande annonce en VF en cours')
                    self.logg('Rien trouve de mieux sur google pour : '+moviename+' je telecharge donc la bande annonce non HD vf Allocine')
                    maxqual=self.quacontrolallo(listvfallo,'vf')
                    path=self.videodl(listvfallo,trailername,moviename,trailerpath,True,maxqual)
                    xbmcgui.Dialog().notification(u'Bande annonce téléchargée', u'Bande annonce téléchargée en VF. BDD mise à jour', xbmcgui.NOTIFICATION_INFO, 5000)
                    dp.close()
                    return path
                
            elif listgooglevf:
                cleanlistvf,listlowqvf=self.totqualcontrol(listgooglevf,'vf')
                if cleanlistvf:
                    dp.close()
                    xbmc.sleep(1000)
                    dp.create(u'Téléchargement','','','Bande annonce en VF en cours')
                    self.logg('Si jen crois google jai trouve mieux que la bande annonce allocine . Lets go')
                    path=self.videodl(cleanlistvf,trailername,moviename,trailerpath)
                    xbmcgui.Dialog().notification(u'Bande annonce téléchargée', u'Bande annonce téléchargée en VF. BDD mise à jour', xbmcgui.NOTIFICATION_INFO, 5000)
                    dp.close()
                    return path
                elif listlowqvf:
                    dp.close()
                    xbmc.sleep(1000)
                    dp.create(u'Téléchargement','','','Bande annonce en VF en cours')
                    self.logg('Rien trouve sur Allocine pour : ' +moviename+' je recupere donc une bande annonce non HD vf trouve sur google')
                    path=self.videodl(listlowqvf,trailername,moviename,trailerpath)
                    xbmcgui.Dialog().notification(u'Bande annonce téléchargée', u'Bande annonce téléchargée en VF. BDD mise à jour', xbmcgui.NOTIFICATION_INFO, 5000)
                    dp.close()
                    return path
            elif listvostfrallo:
                maxqual=self.quacontrolallo(listvostfrallo,'vostfr')
                                       
                if maxqual>=481:
                    dp.close()
                    xbmc.sleep(1000)
                    dp.create(u'Téléchargement','','','Bande annonce en VOST en cours')
                    path=self.videodl(cleanlistvf,trailername,moviename,trailerpath,True,maxqual)
                    xbmcgui.Dialog().notification(u'Bande annonce téléchargée', u'Bande annonce téléchargée en VOST. BDD mise à jour', xbmcgui.NOTIFICATION_INFO, 5000)
                    dp.close()
                    return path
                else:
                    if listgooglevostfr:
                        cleanlistvostfr,listlowqvostfr=self.totqualcontrol(listgooglevostfr,'vostfr')
                        if cleanlistvostfr:
                            dp.close()
                            xbmc.sleep(1000)
                            dp.create(u'Téléchargement','','','Bande annonce en VOST en cours')
                            self.logg('Si jen crois google jai trouve mieux que la bande annonce allocine . Lets go')
                            path=self.videodl(cleanlistvostfr,trailername,moviename,trailerpath)
                            xbmcgui.Dialog().notification(u'Bande annonce téléchargée', u'Bande annonce téléchargée en VOST. BDD mise à jour', xbmcgui.NOTIFICATION_INFO, 5000)
                            dp.close()
                            return path   
                        else:
                            dp.close()
                            xbmc.sleep(1000)
                            dp.create(u'Téléchargement','','','Bande annonce en VOST en cours') 
                            self.logg('Rien trouve de mieux sur google pour : '+moviename+' je telecharge donc la bande annonce non HD vostfr Allocine')
                            path=self.videodl(listvostfrallo,trailername,moviename,trailerpath,True,maxqual)
                            xbmcgui.Dialog().notification(u'Bande annonce téléchargée', u'Bande annonce téléchargée en VOST. BDD mise à jour', xbmcgui.NOTIFICATION_INFO, 5000)
                            dp.close()
                            return path
                    else:
                        dp.close()
                        xbmc.sleep(1000)
                        dp.create(u'Téléchargement','','','Bande annonce en VOST en cours')
                        self.logg('Rien trouve de mieux sur google pour : '+moviename+' je telecharge donc la bande annonce non HD vostfr Allocine')
                        path=self.videodl(listvostfrallo,trailername,moviename,trailerpath,True,maxqual)
                        xbmcgui.Dialog().notification(u'Bande annonce téléchargée', u'Bande annonce téléchargée en VOST. BDD mise à jour', xbmcgui.NOTIFICATION_INFO, 5000)
                        dp.close()
                        return path
            
            elif listgooglevostfr:
                cleanlistvostfr,listlowqvostfr=self.totqualcontrol(listgooglevostfr,'vostfr')
                if cleanlistvostfr:
                    dp.close()
                    xbmc.sleep(1000)
                    dp.create(u'Téléchargement','','','Bande annonce en VOST en cours')
                    self.logg('Si jen crois google jai trouve mieux que la bande annonce allocine . Lets go')
                    path=self.videodl(cleanlistvostfr,trailername,moviename,trailerpath)
                    xbmcgui.Dialog().notification(u'Bande annonce téléchargée', u'Bande annonce téléchargée en VOST. BDD mise à jour', xbmcgui.NOTIFICATION_INFO, 5000)
                    dp.close()
                    return path
                elif listlowqvostfr:
                    dp.close()
                    xbmc.sleep(1000)
                    dp.create(u'Téléchargement','','','Bande annonce en VOST en cours')
                    self.logg('Rien trouve sur Allocine pour : ' +moviename+' je recupere donc une bande annonce non HD vostfr trouve sur google')
                    path=self.videodl(listlowqvostfr,trailername,moviename,trailerpath)
                    xbmcgui.Dialog().notification(u'Bande annonce téléchargée', u'Bande annonce téléchargée en VOST. BDD mise à jour', xbmcgui.NOTIFICATION_INFO, 5000)
                    dp.close()
                    return path
            elif listvoallo:
                maxqual=self.quacontrolallo(listvoallo,'vo')
               
                if maxqual>=481:
                    dp.close()
                    xbmc.sleep(1000)
                    dp.create(u'Téléchargement','','','Bande annonce en VO en cours')
                    path=self.videodl(listvoallo,trailername,moviename,trailerpath,True,maxqual)
                    xbmcgui.Dialog().notification(u'Bande annonce téléchargée', u'Bande annonce téléchargée en VO. BDD mise à jour', xbmcgui.NOTIFICATION_INFO, 5000)
                    dp.close()
                    return path
                else:
                    if listgooglevo:
                        cleanlistvo,listlowqvo=self.totqualcontrol(listgooglevo,'vo')
                        if cleanlistvo:
                            dp.close()
                            xbmc.sleep(1000)
                            dp.create(u'Téléchargement','','','Bande annonce en VO en cours')
                            self.logg('Si jen crois google jai trouve mieux que la bande annonce allocine . Lets go')
                            path=self.videodl(cleanlistvo,trailername,moviename,trailerpath)
                            xbmcgui.Dialog().notification(u'Bande annonce téléchargée', u'Bande annonce téléchargée en VO. BDD mise à jour', xbmcgui.NOTIFICATION_INFO, 5000)
                            dp.close()
                            return path   
                        else: 
                            dp.close()
                            xbmc.sleep(1000)
                            dp.create(u'Téléchargement','','','Bande annonce en VO en cours')
                            self.logg('Rien trouve de mieux sur google pour : '+moviename+' je telecharge donc la bande annonce non HD vo Allocine')
                            path=self.videodl(listvoallo,trailername,moviename,trailerpath,True,maxqual)
                            xbmcgui.Dialog().notification(u'Bande annonce téléchargée', u'Bande annonce téléchargée en VO. BDD mise à jour', xbmcgui.NOTIFICATION_INFO, 5000)
                            dp.close()
                            return path
                    else:
                        dp.close()
                        xbmc.sleep(1000)
                        dp.create(u'Téléchargement','','','Bande annonce en VO en cours') 
                        self.logg('Rien trouve de mieux sur google pour : '+moviename+' je telecharge donc la bande annonce non HD vo Allocine')
                        path=self.videodl(listvoallo,trailername,moviename,trailerpath,True,maxqual)
                        xbmcgui.Dialog().notification(u'Bande annonce téléchargée', u'Bande annonce téléchargée en VO. BDD mise à jour', xbmcgui.NOTIFICATION_INFO, 5000)
                        dp.close()
                        return path
                    
            elif listgooglevo:
                cleanlistvo,listlowqvo=self.totqualcontrol(listgooglevo,'vos')
                if cleanlistvo:
                    dp.close()
                    xbmc.sleep(1000)
                    dp.create(u'Téléchargement','','','Bande annonce en VO en cours')
                    self.logg('Si jen crois google jai trouve mieux que la bande annonce allocine . Lets go')
                    path=self.videodl(cleanlistvo,trailername,moviename,trailerpath)
                    xbmcgui.Dialog().notification(u'Bande annonce téléchargée', u'Bande annonce téléchargée en VO. BDD mise à jour', xbmcgui.NOTIFICATION_INFO, 5000)
                    dp.close()
                    return path
                elif listlowqvo:
                    dp.close()
                    xbmc.sleep(1000)
                    dp.create(u'Téléchargement','','','Bande annonce en VO en cours')
                    self.logg('Rien trouve sur Allocine pour : ' +moviename+' je recupere donc une bande annonce non HD vo trouve sur google')
                    path=self.videodl(listlowqvo,trailername,moviename,trailerpath)
                    xbmcgui.Dialog().notification(u'Bande annonce téléchargée', u'Bande annonce téléchargée en VO. BDD mise à jour', xbmcgui.NOTIFICATION_INFO, 5000)
                    dp.close()
                    return path
            else:
                self.logg('Snifff encore un film pourri pas de bande annonce trouve pour ' + moviename)
                dp.close()
                xbmcgui.Dialog().notification(u'Bande annonce non trouvée', u'Allez la chercher à la main', xbmcgui.NOTIFICATION_INFO, 5000)
                xbmc.sleep(3250)
                return False
            