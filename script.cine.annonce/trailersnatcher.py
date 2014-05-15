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
api = allocine()
api.configure('100043982026','29d185d98c984a359e6e6f26a0474269')
global lastgsearch
global waittime
global countyoutube
global countdaily
countyoutube=0
countdaily=0
waittime=0
lastgsearch=0

def logg(str,debug=None):
    ts=datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
    if debug==None:
        print(ts +' : '+str)
    logging.info(ts+' : '+str)
    return True

def cleantitle(title):
    specialchars=['/','(',')',',','.',';','!','?','-',':','_','[',']','|','  ','  ','  ']
    title=unicodedata.normalize('NFKD',title).encode('ascii','ignore')
    for chars in specialchars:
        title=title.replace(chars,' ')        
    return title.lower()

def controltitle(title,moviename):
    realtitle=cleantitle(moviename[:-5].decode('unicode-escape'))
    year=moviename[len(moviename)-4:]
    listcommonwords=['youtube','dailymotion','vf','francais','francaise','vo','vost','version','annonce','bande','bande-annonce','trailer',
                     'vostfr','fr','bandeannonce','video','ba','hd','hq','720p','1080p','film','official','#1','#2',
                     '#4','#6','#7','du','and','premiere','n°1','n°2','n°3','n°4','n°5','officielle','theatrical']
    wordsleft=[]
    cleantitles=cleantitle(title)
    for word in cleantitles.split():
        if word not in listcommonwords and word not in realtitle.split() and word<>year:
            wordsleft.append(word)
    logg(title+' \\\\nettoye en//// '+str(wordsleft),True)
    if len(wordsleft)==0:
        return True
    else:
        return False

def controltitle2(title,moviename):
    realtitle=cleantitle(moviename[:-5].decode('unicode-escape'))
    year=moviename[len(moviename)-4:]
    wordsleft=[]
    cleantitles=cleantitle(title)
    for word in realtitle.split():
        if word not in cleantitles.split():
            wordsleft.append(word)
    logg(title+' \\\\mots non trouves//// '+str(wordsleft),True)
    if len(wordsleft)==0:
        return True
    else:
        return False

def cleandic(dict,moviename):
    series=['2','3','4','5','6','7','8']
    titlenames=dict.keys()
    listkeysvf=[]
    listkeysvostfr=[]
    listkeysvo=[]
    year=moviename[len(moviename)-4:]
    for titledict in titlenames:
        testcontinue=controltitle(titledict,moviename)
        if testcontinue==False:
            continue
        testcontinue2=controltitle2(titledict,moviename)
        if testcontinue2==False:
            continue
        cleandict=cleantitle(titledict)
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
            logg('Aucun moyen didentifier la langue pour '+cleandict+' je suppose que cest de la VO')
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
    logg(str(len(urllistvf)) + ' liens de bandes annonces VF trouves sur google')
    logg(str(len(urllistvostfr)) + ' liens de bandes annonces VOSTFR trouves sur google')
    logg(str(len(urllistvo)) + ' liens de bandes annonces VO trouves sur google')
    return urllistvf,urllistvostfr,urllistvo

def libraryscan(path):
    logg('Veuillez patienter pendant la recherche des films sans bandes-annonces dans ' + path)
    fichier=[] 
    logg('Calcul en cours....')
    numberfiles=0
    pathori=path
    for path, dires, fics in os.walk(path):
        for f in fics:
            numberfiles+=1
    currentnumber=0
    for root, dirs, files in os.walk(pathori):
        for i in files:
            currentnumber+=1
            trailercount=0
            if ('.mkv' in i or '.avi' in i or '.mp4' in i) and '-trailer' not in i:
                for x in os.listdir(root):
                    if '-trailer' in x:
                        trailercount+=1
                if trailercount==0:
                    fileroot=root
                    filename=i
                    filename=filename[:filename.rfind(")")].replace(' 3DBD','').replace('(','').replace(')','')
                    fichier.append([fileroot,filename,i[:-4]])
                logg(str(currentnumber)+' fichiers scannes sur un total de '+str(numberfiles))   
    logg(str(numberfiles)+' fichiers scannes sur un total de '+str(numberfiles))
    return fichier

def googlesearch(searchstringori):
    global lastgsearch
    global waittime
    uploadtoignore=['UniversalMoviesFR','ParamountmoviesFR']
    actualtime=int(time.time())
    if actualtime-lastgsearch<60:
        timetosleep= 60-(actualtime-lastgsearch)
        logg('Attente ' +str(timetosleep)+ ' secondes ....')
        time.sleep(timetosleep)
        waittime+=timetosleep
    lastgsearch = int(time.time())
    searchstring=searchstringori[:-5].replace(' ','+')
    
    regexurl ="url(?!.*url).*?&amp"
    patternurl = re.compile(regexurl)

    regextitle='">(?!.*">).*?<\/a'
    patterntitle= re.compile(regextitle)

    br=mechanize.Browser()
    br.set_handle_robots(False)
    br.addheaders=[('User-agent','chrome')]

    query="https://www.google.fr/search?num=100&q=bande-annonce+OR+bande+OR+annonce"+'"'+searchstring+'"'+"+VF+HD+site:http://www.youtube.com+OR+site:http://www.dailymotion.com&ie=latin-1&oe=latin-1&aq=t&rls=org.mozilla:fr:official&client=firefox-a&channel=np&source=hp&gfe_rd=cr&ei=MW9lU_vDIK2A0AXbroCADw"
    logg('En train de rechercher sur google : ' +searchstring)
    logg('Query : ' +query,True)
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
    logg(str(len(urldic))+ ' resultats trouves sur google')
    return urldic

def allocinesearch(moviename):
    series=['2','3','4','5','6','7','8']
    listallovostfr=[]
    listallovo=[]
    listallovf=[]
    logg('Tentative de recherche sur Allocine de ' +moviename[:-5])
    try:
        search = api.search(moviename[:-5], "movie")
        for result in search['feed']['movie']:
            countseries=0
            ficheresult=api.movie(result['code'])
            ficheresulttitle=cleantitle(ficheresult['movie']['title'])
            ficheresulttitleori=cleantitle(ficheresult['movie']['originalTitle'])
            yearresult=ficheresult['movie']['productionYear']
            test=cleantitle(moviename[:-5].decode('unicode-escape'))
            if not yearresult:
                yearresult=0
            for x in series:
                if (x in ficheresulttitle or x in ficheresulttitleori) and (not '3d' in ficheresulttitle and not '3d' in ficheresulttitleori):
                    if x not in moviename[:-5]:
                        countseries+=1                        
            if cleantitle(moviename[:-5].decode('unicode-escape')) in ficheresulttitle and countseries==0 and int(moviename[len(moviename)-4:])+2>yearresult and int(moviename[len(moviename)-4:])-2<yearresult:
                goodresult=result
                break
        logg("Resultat : Nombre [{0}] Code [{1}] Titre original [{2}]".format(search['feed']['totalResults'],
                                                                    goodresult['code'],
                                                                    goodresult['originalTitle'].encode("latin-1")))
        logg('Recherche de la fiche du film avec le code : ' + str(goodresult['code']))
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
                    logg("Potentiel code de bande annonce [{0}] en VF".format(lienid))
                    trailerallo = api.trailer(lienid)
                    long=len(trailerallo['media']['rendition'])
                    bestba=trailerallo['media']['rendition'][long-1]
                    linkallo=trailerallo['media']['rendition'][long-1]['href']
                    heightbaallo=bestba['height']
                    longadr=len(linkallo)
                    extallo=linkallo[longadr-3:]
                    
                    listallovf.append({'link':linkallo,'ext':extallo,'height':heightbaallo})
                    if heightbaallo>=481:
                        logg('Bande annonce vf et HD trouve sur Allocine jarrete de chercher')
                        break
                    else:
                        logg('Bande annonce vf non HD trouve sur Allocine je continue de chercher')
                elif 'annonce' in str(lien).lower() and 'vost' in str(lien).lower():
                    lienid=lien['href'][:lien['href'].find('&')].replace('/video/player_gen_cmedia=','')
                    logg("Potentiel code de bande annonce [{0}] en VOSTFR".format(lienid))
                    trailerallo = api.trailer(lienid)
                    long=len(trailerallo['media']['rendition'])
                    bestba=trailerallo['media']['rendition'][long-1]
                    linkallo=trailerallo['media']['rendition'][long-1]['href']
                    heightbaallo=bestba['height']
                    longadr=len(linkallo)
                    extallo=linkallo[longadr-3:]
                    
                    listallovostfr.append({'link':linkallo,'ext':extallo,'height':heightbaallo})
                    logg('Bande annonce vostfr trouve sur Allocine je continue de chercher')
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
                        logg("Potentiel code de bande annonce [{0}] en VOSTFR".format(lienid))
                        listallovostfr.append({'link':linkallo,'ext':extallo,'height':heightbaallo})
                        logg('Bande annonce vostfr trouve sur Allocine je continue de chercher')
                    else:
                        logg("Potentiel code de bande annonce [{0}] en VO".format(lienid))
                        listallovo.append({'link':linkallo,'ext':extallo,'height':heightbaallo})
                        logg('Bande annonce vo trouve sur Allocine je continue de chercher')
                
                else:
                    continue
            except Exception,e:
                print e
                continue
        logg(str(len(listallovf)) +" bandes annonces en VF trouvees sur allocine")
        logg(str(len(listallovostfr)) +" bandes annonces en VOSTFR trouvees sur allocine")
        logg(str(len(listallovo)) +" bandes annonces en VO trouvees sur allocine")       
        return listallovf,listallovostfr,listallovo
    except :
        logg(str(len(listallovf)) +" bandes annonces en VF trouvees sur allocine")
        logg(str(len(listallovostfr)) +" bandes annonces en VOSTFR trouvees sur allocine")
        logg(str(len(listallovo)) +" bandes annonces en VO trouvees sur allocine")  
        return listallovf,listallovostfr,listallovo

def quacontrol(url):
    quallist=[]
    p=subprocess.Popen([sys.executable, 'youtube_dl/__main__.py', '-F',url],cwd=rootDir, shell=True, stdout=subprocess.PIPE,stderr=subprocess.PIPE)
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

def quacontrolallo(listallo,type):
    bestqualallo=0
    for linkvf in listallo:
        if bestqualallo<linkvf['height']:
            bestqualallo=linkvf['height']
    logg('Meilleure resolution trouvee sur Allocine en '+type+' : '+str(bestqualallo)+'p')
    return bestqualallo

def videodl(cleanlist,trailername,moviename,trailerpath,allo=False,maxheight=0):
    global countyoutube
    global countdaily
    if allo:
        for url in cleanlist:
            if maxheight==url['height']:
                linkallo=url['link']
                heightbaallo=url['height']
                extallo=url['ext']
                logg('Telechargement de la bande annonce suivante : ' + linkallo +' en '+str(heightbaallo)+'p en cours...')
                try:
                    urllib.urlretrieve(linkallo, os.path.join(trailerpath,trailername)+'.'+extallo)
                    logg('Une bande annonce telechargee pour ' + moviename +' sur Allocine')
                    return True
                    break
                except:
                    continue
        return False
    else:
        bocount=0
        for bo in cleanlist:
            if bocount==0:
                try:
                    logg('En train de telecharger : ' + bo + ' pour ' +moviename)
                    tempdest=unicodedata.normalize('NFKD', os.path.join(rootDir,trailername.replace("'",''))).encode('ascii','ignore')+u'.%(ext)s'
                    dest=os.path.join(trailerpath,trailername)
                    p=subprocess.Popen([sys.executable, 'youtube_dl/__main__.py', '-o',tempdest,'--newline', '--max-filesize', '105m', '--format','best',bo],cwd=rootDir, shell=True, stdout=subprocess.PIPE,stderr=subprocess.PIPE)
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
                                logg('Une bande annonce telechargee pour ' + moviename)
                                if 'youtube' in bo:
                                    countyoutube+=1
                                else:
                                    countdaily+=1
                                return True
                except:
                    continue
            else:
                continue
        return False

def totqualcontrol(listcontrol,type):
    compteurhd=0
    cleanlist=[]
    listlowq=[]
    for tocontrolqual in listcontrol:
        if compteurhd==3:
            logg('Suffisamment de bandes annonces '+type+ ' HD trouvees plus la peine de continuer')
            break
        logg('Controle de la qualite reelle de ' +tocontrolqual+ ' en cours...')
        
        if quacontrol(tocontrolqual):
            logg('La qualite de ' +tocontrolqual+' semble HD je rajoute a la liste  HD '+type)
            cleanlist.append(tocontrolqual)
            compteurhd+=1
        else:
            logg('Pfffff encore un mytho la qualite de ' +tocontrolqual+' nest pas HD je rajoute a la liste non HD '+type)
            listlowq.append(tocontrolqual)
    return cleanlist, listlowq

logging.basicConfig(filename='trace.log', filemode='w', level=logging.DEBUG)
logg('Ceci est une beta. Certaines bandes annonces pourront etre en anglais voir ne pas correspondre au film')
root = Tkinter.Tk()
directory = tkFileDialog.askdirectory(parent=root,initialdir="/",title='Choisir le repertoire a scanner')
if len(directory) > 0:
    logg("Vous avez choisi : %s" % directory)
root.destroy()
rootDir = os.path.dirname(os.path.abspath(__file__))
try:
    _DEV_NULL = subprocess.DEVNULL
except AttributeError:
    _DEV_NULL = open(os.devnull, 'wb')
path = directory

fichier = libraryscan(path)
if len(fichier)>0:
    logg(str(len(fichier)) + ' films sans bandes annonces ont ete trouves')
    for moviewithouttrailer in fichier:
        logg(unicodedata.normalize('NFKD', moviewithouttrailer[1]).encode('ascii','ignore'))
else:
    logg('Aucun film sans bande annonce trouve. Appuyer sur ENTREE pour fermer la fenetre')
    raw_input()
    sys.exit()
    
countgoogle=0
countallo=0
counthdvfallo=0
countsdvfallo=0
counthdvostallo=0
countsdvostallo=0
counthdvoallo=0
countsdvoallo=0
counthdvfgoogle=0
countsdvfgoogle=0
counthdvostgoogle=0
countsdvostgoogle=0
counthdvogoogle=0
countsdvogoogle=0
compteur=0
notfound=[]
start=int(time.time())
for movie in fichier:
    logg('####################Il reste ' + str(len(fichier)-compteur)+' films######################')
    compteur+=1
    trailerpath=movie[0]
    moviename = unicodedata.normalize('NFKD', movie[1]).encode('ascii','ignore')
    trailername=movie[2]+'-trailer'
    searchstring=moviename
    listvfallo,listvostfrallo,listvoallo=allocinesearch(moviename)
    if listvfallo:
        maxqual=quacontrolallo(listvfallo,'vf')
        
        if maxqual>=481:
            videodl(listvfallo,trailername,moviename,trailerpath,True,maxqual)
            countallo+=1
            counthdvfallo+=1
            continue
        else:
            logg('Bande annonce en VF non HD trouvee sur Allocine tentative de recherche dune meilleure qualite sur google')
    else:
        logg('Rien trouve sur Allocine en VF tentative de recherche sur google')
    urldic=googlesearch(searchstring)
    listgooglevf, listgooglevostfr,listgooglevo=cleandic(urldic,moviename)
    if listvfallo:
        maxqual=quacontrolallo(listvfallo,'vf')
        if listgooglevf:
            logg('Jai trouve des bandes annonces VF sur google, controlons leur qualite')
            cleanlistvf,listlowqvf=totqualcontrol(listgooglevf,'vf')
            if cleanlistvf:
                logg('Si jen crois google jai trouve mieux que la bande annonce allocine . Lets go')
                videodl(cleanlistvf,trailername,moviename,trailerpath)
                countgoogle+=1
                counthdvfgoogle+=1
                continue
            else:
                logg('Rien trouve de mieux sur google pour : '+moviename+' je telecharge donc la bande annonce non HD vf Allocine')
                maxqual=quacontrolallo(listvfallo,'vf')
                videodl(listvfallo,trailername,moviename,trailerpath,True,maxqual)
                countallo+=1
                countsdvfallo+=1
                continue
        else:
            logg('Rien trouve de mieux sur google pour : '+moviename+' je telecharge donc la bande annonce non HD vf Allocine')
            maxqual=quacontrolallo(listvfallo,'vf')
            videodl(listvfallo,trailername,moviename,trailerpath,True,maxqual)
            countallo+=1
            countsdvfallo+=1
            continue
        
    elif listgooglevf:
        cleanlistvf,listlowqvf=totqualcontrol(listgooglevf,'vf')
        if cleanlistvf:
            logg('Si jen crois google jai trouve mieux que la bande annonce allocine . Lets go')
            videodl(cleanlistvf,trailername,moviename,trailerpath)
            countgoogle+=1
            counthdvfgoogle+=1
            continue
        elif listlowqvf:
            logg('Rien trouve sur Allocine pour : ' +moviename+' je recupere donc une bande annonce non HD vf trouve sur google')
            videodl(listlowqvf,trailername,moviename,trailerpath)
            countgoogle+=1
            countsdvfgoogle+=1
            continue
    elif listvostfrallo:
        maxqual=quacontrolallo(listvostfrallo,'vostfr')
        if maxqual>=481:
            videodl(cleanlistvf,trailername,moviename,trailerpath,True,maxqual)
            countallo+=1
            counthdvostallo+=1
            continue
        else:
            if listgooglevostfr:
                cleanlistvostfr,listlowqvostfr=totqualcontrol(listgooglevostfr,'vostfr')
                if cleanlistvostfr:
                    logg('Si jen crois google jai trouve mieux que la bande annonce allocine . Lets go')
                    videodl(cleanlistvostfr,trailername,moviename,trailerpath)
                    countgoogle+=1
                    counthdvostgoogle+=1
                    continue    
                else: 
                    logg('Rien trouve de mieux sur google pour : '+moviename+' je telecharge donc la bande annonce non HD vostfr Allocine')
                    videodl(listvostfrallo,trailername,moviename,trailerpath,True,maxqual)
                    countallo+=1
                    countsdvostallo+=1
                    continue
            else: 
                logg('Rien trouve de mieux sur google pour : '+moviename+' je telecharge donc la bande annonce non HD vostfr Allocine')
                videodl(listvostfrallo,trailername,moviename,trailerpath,True,maxqual)
                countallo+=1
                countsdvostallo+=1                    
                continue
    
    elif listgooglevostfr:
        cleanlistvostfr,listlowqvostfr=totqualcontrol(listgooglevostfr,'vostfr')
        if cleanlistvostfr:
            logg('Si jen crois google jai trouve mieux que la bande annonce allocine . Lets go')
            videodl(cleanlistvostfr,trailername,moviename,trailerpath)
            countgoogle+=1
            counthdvostgoogle+=1
            continue
        elif listlowqvostfr:
            logg('Rien trouve sur Allocine pour : ' +moviename+' je recupere donc une bande annonce non HD vostfr trouve sur google')
            videodl(listlowqvostfr,trailername,moviename,trailerpath)
            countgoogle+=1
            countsdvostgoogle+=1
            continue
    elif listvoallo:
        maxqual=quacontrolallo(listvoallo,'vo')
        if maxqual>=481:
            videodl(listvoallo,trailername,moviename,trailerpath,True,maxqual)
            countallo+=1
            counthdvoallo+=1
            continue
        else:
            if listgooglevo:
                cleanlistvo,listlowqvo=totqualcontrol(listgooglevo,'vo')
                if cleanlistvo:
                    logg('Si jen crois google jai trouve mieux que la bande annonce allocine . Lets go')
                    videodl(cleanlistvo,trailername,moviename,trailerpath)
                    countgoogle+=1
                    counthdvogoogle+=1
                    continue    
                else: 
                    logg('Rien trouve de mieux sur google pour : '+moviename+' je telecharge donc la bande annonce non HD vo Allocine')
                    videodl(listvoallo,trailername,moviename,trailerpath,True,maxqual)
                    countallo+=1
                    countsdvoallo+=1
                    continue
            else: 
                logg('Rien trouve de mieux sur google pour : '+moviename+' je telecharge donc la bande annonce non HD vo Allocine')
                videodl(listvoallo,trailername,moviename,trailerpath,True,maxqual)
                countallo+=1
                countsdvoallo+=1
                continue
            
    elif listgooglevo:
        cleanlistvo,listlowqvo=totqualcontrol(listgooglevo,'vos')
        if cleanlistvo:
            logg('Si jen crois google jai trouve mieux que la bande annonce allocine . Lets go')
            videodl(cleanlistvo,trailername,moviename,trailerpath)
            countgoogle+=1
            counthdvogoogle+=1
            continue
        elif listlowqvo:
            logg('Rien trouve sur Allocine pour : ' +moviename+' je recupere donc une bande annonce non HD vo trouve sur google')
            videodl(listlowqvo,trailername,moviename,trailerpath)
            countgoogle+=1
            countsdvogoogle+=1
            continue
    else:
        logg('Snifff encore un film pourri pas de bande annonce trouve pour ' + moviename)
        notfound.append(moviename)
        continue
end=int(time.time())
duree=round((end-start)/60,2)
dureehorswait=round((end-start-waittime)/60,2)
textdureehorswait=str(dureehorswait)
textduree=str(duree)
if notfound:
    file = open("BANONDL.txt", "w")
for nf in notfound:
    logg('Aucune bande annnonce trouvee pour ' + nf)
    file.write(nf+"\n")
if notfound:
    file.close()

logg('------------------------------------------RAPPORT-----------------------------------------------')

logg(str(countallo) + ' bandes annonces telechargees sur Allocine')
logg('      '+str(counthdvfallo)+' en HD/VF')
logg('      '+str(countsdvfallo)+' en SD/VF')
logg('      '+str(counthdvostallo)+' en HD/VOST')
logg('      '+str(countsdvostallo)+' en SD/VOST')
logg('      '+str(counthdvoallo)+' en HD/VO')
logg('      '+str(countsdvostallo)+' en SD/VOST')
logg('      ' +str(counthdvfallo+counthdvostallo+counthdvoallo)+' en HD, '+str(countsdvfallo+countsdvostallo+countsdvoallo)+' en SD ( '+str(counthdvfallo+countsdvfallo)+' en VF, '+str(counthdvostallo+countsdvostallo)+' en VOST, '+str(counthdvoallo+countsdvoallo)+ ' en VO)')
logg(' ')
logg(str(countgoogle) + ' bandes annonces telechargees sur Google ( '+str(countyoutube)+ ' sur youtube, '+str(countdaily)+' sur dailymotion)')
logg('      '+str(counthdvfgoogle)+' en HD/VF')
logg('      '+str(countsdvfgoogle)+' en SD/VF')
logg('      '+str(counthdvostgoogle)+' en HD/VOST')
logg('      '+str(countsdvostgoogle)+' en SD/VOST')
logg('      '+str(counthdvogoogle)+' en HD/VO')
logg('      '+str(countsdvostgoogle)+' en SD/VOST')
logg('Soit ' +str(counthdvfgoogle+counthdvostgoogle+counthdvogoogle)+' en HD, '+str(countsdvfgoogle+countsdvostgoogle+countsdvogoogle)+' en SD ( '+str(counthdvfgoogle+countsdvfgoogle)+' en VF, '+str(counthdvostgoogle+countsdvostgoogle)+' en VOST, '+str(counthdvogoogle+countsdvogoogle)+ ' en VO)')
logg(' ')
logg(str(countallo+countgoogle)+ ' bandes annonces telechargees sur un total de '+str(len(fichier)))
logg('      '+str(counthdvfgoogle+counthdvfallo)+' en HD/VF')
logg('      '+str(countsdvfgoogle+countsdvfallo)+' en SD/VF')
logg('      '+str(counthdvostgoogle+counthdvostallo)+' en HD/VOST')
logg('      '+str(countsdvostgoogle+countsdvostallo)+' en SD/VOST')
logg('      '+str(counthdvogoogle+counthdvoallo)+' en HD/VO')
logg('      '+str(countsdvostgoogle+countsdvostallo)+' en SD/VOST')
logg('Soit ' +str(counthdvfgoogle+counthdvostgoogle+counthdvogoogle+counthdvfallo+counthdvostallo+counthdvoallo)+' en HD, '+str(countsdvfgoogle+countsdvostgoogle+countsdvogoogle+countsdvfallo+countsdvostallo+countsdvoallo)+' en SD ( '+str(counthdvfgoogle+countsdvfgoogle+counthdvfallo+countsdvfallo)+' en VF, '+str(counthdvostgoogle+countsdvostgoogle+counthdvostallo+countsdvostallo)+' en VOST, '+str(counthdvogoogle+countsdvogoogle+counthdvoallo+countsdvoallo)+ ' en VO)')
logg(' ')
logg('Duree totale environ ' +textduree+ ' minutes')
logg('Duree reelle (sans attente google) environ ' +textdureehorswait+ ' minutes')
logg('Veuillez appuyer sur ENTREE pour fermer la fenetre. Pensez a jeter un oeil aux fichiers trace.log et BANONDL.txt')
raw_input()
    
