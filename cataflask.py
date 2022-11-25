# all the imports
import pymongo
import os
import time
from datetime import datetime
import re #regexp
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash

import pickle #per exportar fitxer

#encriptar
#$ sudo pip install passlib
#https://passlib.readthedocs.io/en/stable/
from passlib.hash import pbkdf2_sha256

import requests

#https://www.crummy.com/software/BeautifulSoup/bs4/doc/
from bs4 import BeautifulSoup

#BeautifulSoup no agafa contingut per pàgines amb contingut dinàmic javascript
#exemple diec
#cal paquet selenium + driver chrome (v96) mateixa versió que navegador (v96) / _________v96 ja no
#Latest stable release: ChromeDriver 101.0.4951.41 ______versió 101
#pip install selenium
#https://sites.google.com/chromium.org/driver/
#https://www.scrapingbee.com/blog/selenium-python/
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

DRIVER_PATH = 'driver/chromedriver'
FILE_TEMP = 'temp.txt'
NOT_CERCA = "No s'han trobat dades que coincideixin amb els criteris de cerca !"

#_______________________________________________________constants
MONGO = "mongodb://localhost"
DB = "cataflask"
COL_USERS = "users"
COL_MOTS = "mots"
TAGS = {'m':      'nom masculí (m)',
        'f':      'nom femení (f)',
        'pl':     'nom plural (pl)',
        'adj':    'adjectiu (adj)',
        'v':      'verb (v)',
        'interj': 'interjecció (interj)'}

#_______________________________________________________funcions
#guardar fitxer
def guarda_pickle(fitxer,ll):
    outfile = open(fitxer,'wb')
    pickle.dump(ll, outfile)
    outfile.close()

#llegir fitxer
def load_pickle(fitxer):
    #Unpickling files
    infile = open(fitxer,'rb')
    ll = pickle.load(infile)
    infile.close()
    return ll

def mongo_login(user,pwd):
    ok = False
    try:
        #connexió mongo
        con = pymongo.MongoClient(MONGO)
        print(con)
        db = con[DB] 
        col = db[COL_USERS]

        #registre user
        reg = col.find_one({"user":user})
        print(reg)

        #validem usuari i pass
        #mongo retorna None, si no troba valor
        
        if reg != None:
            #verifying the password
            #pbkdf2_sha256.verify("toomanysecrets", hash)
            if user == reg['user'] and pbkdf2_sha256.verify(pwd, reg['pwd']):
                
                #comptador
                #db.users.updateOne({ user:'user' } , { $inc:{conta:1} })
                query = { "user": user }
                update = { "$inc": { "conta": int(1) } }
                col.update_one(query, update)
                ok = True
        #tanquem mongo
        con.close()
    
    except Exception as e:
        print("* FATAL ERROR MONGO *", e)

    return ok

def mongo_existeix(usuari):
    ok = False
    try:
        #connexió mongo
        con = pymongo.MongoClient(MONGO)
        db = con[DB] 
        col = db[COL_USERS]

        #registre user
        reg = col.find_one({"user":usuari})
        print(reg)

        if reg != None:
                ok = True

        #tanquem mongo
        con.close()
    
    except Exception as e:
        print("* FATAL ERROR MONGO *", e)
    
    return ok

def mongo_users():
    try:
        #connexió mongo
        con = pymongo.MongoClient(MONGO)
        print(con)
        db = con[DB] 
        col = db[COL_USERS]

        #passem el cursor a llista
        #cursor.rewind() per tornar al principi del curso
        reg = list( col.find() )

        #tanquem mongo
        con.close()
    
    except Exception as e:
        print("* FATAL ERROR MONGO *", e)
    
    return reg

def mongo_insert_user(user,hash):
    ok = False
    try:
        #connexió mongo
        con = pymongo.MongoClient(MONGO)
        print(con)
        db = con[DB] 
        col = db[COL_USERS]

        #insert
        doc = {"user":user,"pwd":hash, "conta": int(0) }
        col.insert_one(doc)
        ok = True

        #tanquem mongo
        con.close()
    
    except Exception as e:
        print("* FATAL ERROR MONGO *", e)

    return ok

def mongo_insert_mot(docs, mot, existeix):
    ok = False
    try:
        #connexió mongo
        con = pymongo.MongoClient(MONGO)
        print(con)
        db = con[DB] 
        col = db[COL_MOTS]

        #si existeix mot, primer esborra de mongo per no duplicar
        if existeix :
            col.delete_many({ "mot": mot})

        #ready
        print('ready per insert de tots els registres...')

        #mida docs dins llistes
        print([len(doc) for doc in docs])
        
        #és una llista de llistes que contenen docs
        
        for llista in docs:
            if len(llista) > 0:
                for doc in llista:
                    #print(type(doc), end =" ")
                    col.insert_one(doc)
                #print()
        
        #col.insert_many(docs)
        ok = True  

        #tanquem mongo
        con.close()
    
    except Exception as e:
        print("* FATAL ERROR MONGO *", e)

    return ok

#consultes info
def mongo_info(consulta=None):
    dic = {}
    #try:
    #connexió mongo
    con = pymongo.MongoClient(MONGO)
    print(con)
    db = con[DB] 
    col = db[COL_MOTS]
    
    #si és consulta no busquis tots els mots
    if not consulta:
        #quantitat paraules apreses
        dic['quantitat'] = len(col.distinct('mot'))

        #paraules apreses
        dic['mots'] = col.distinct('mot')

    #consulta
    #paràmetres consulta
    else:
        for k,v in consulta.items():
            print(k, v)

        tag = consulta['tag']
        tip = consulta['tip']
        cat = consulta['cat']
        cad = consulta['cad']

        #si no hi ha res
        temp = None

        #depent paràmetre GET, consulta
        if tag != '':
            #!necessari compilar pattern amb python, el propi de mongo no anava
            #pattern = re.compile('.*[f].*')
            pattern = f".*{tag}.*"
            regex = re.compile(pattern)
            temp = col.aggregate([ {'$match': {'tags': regex}}, {'$group': {'_id': '$mot'}} ])
            print(temp)
            print(type(temp))
        elif tip != '':
            #treure [], conflicte amb regex
            tip = tip.replace('[', '').replace(']', '')
            regex = re.compile(f".*{tip}.*")
            temp = col.aggregate([ {'$match': {'tips': regex}}, {'$group': {'_id': '$mot'}} ])
        elif cat != '':
            regex = re.compile(f".*{cat}.*")
            temp = col.aggregate([ {'$match': {'cats': regex}}, {'$group': {'_id': '$mot'}} ])
        elif cad != '':
            regex = re.compile(f".*{cad}.*")
            temp = col.aggregate([ {'$match': {'mot': regex}}, {'$group': {'_id': '$mot'}} ])
        
        if temp != None:
            ll = []
            for el in temp:
                print(el)
                ll.append(el['_id'])
            dic['mots'] = ll

        else:
            dic['mots'] = ""
    #tips
    dic['tips'] = col.distinct('tips',{ 'origen':'diec' })

    #categories
    dic['cats'] = col.distinct('cats',{ 'origen':'rodamots' })

    #tanquem mongo
    con.close()
    
    #except Exception as e:
    #    print("* FATAL ERROR MONGO *", e)
    
    return dic

#consulta mot
def mongo_mot(mot):
    fitxa = {}
    try:
        #connexió mongo
        con = pymongo.MongoClient(MONGO)
        print(con)
        db = con[DB] 
        col = db[COL_MOTS]
        
        #docs mot
        tot =  col.find( {"mot": mot}  )
        #test = (list(col.find({ "mot": mot, "tags":{"$exists": True} },{ "tags": 1, "_id": 0})))
        
        #distinc filtra ja els valors i repetits, millor que find
        tags = col.distinct('tags',{ 'mot': mot })
        cats = col.distinct('cats',{ 'mot': mot })
        tips = col.distinct('tips',{ 'mot': mot })
        
        #fras = col.distinct('frasefeta',{ 'mot': mot })
        #sins = col.distinct('sinonims',{ 'mot': mot })
        
        tras = col.distinct('traduccions',{ 'mot': mot })
        ents = col.distinct('entrada',{ 'mot': mot })

        opti = col.find( {"mot":mot, "origen" : "optimot" },{ }  )
    
        #afegir a diccionari
        fitxa['tot'] = list(tot) #tot
        fitxa['tags'] = tags
        fitxa['cats'] = cats
        fitxa['tips'] = tips
        #fitxa['fras'] = fras
        #fitxa['sins'] = sins
        fitxa['tras'] = tras
        fitxa['ents'] = ents
        fitxa['opti'] = list(opti)

        #tanquem mongo
        con.close()
    
    except Exception as e:
        print("* FATAL ERROR MONGO *", e)
    
    #retornem llista enlloc d'objecte
    return fitxa

def reset_mongo():
    ok = False
    try:
        #connexió mongo
        con = pymongo.MongoClient(MONGO)
        print(con)
        db = con[DB] 
        col = db[COL_MOTS]

        col.delete_many( {} )

        #tanquem mongo
        con.close()
    
    except Exception as e:
        print("* FATAL ERROR MONGO *", e)

    return ok

def mongo_delete_mot(mot):
    ok = False
    try:
        #connexió mongo
        con = pymongo.MongoClient(MONGO)
        print(con)
        db = con[DB] 
        col = db[COL_MOTS]

        col.delete_many( { 'mot': mot } )

        #tanquem mongo
        con.close()
    
    except Exception as e:
        print("* FATAL ERROR MONGO *", e)

    return ok


#backup mongo de bd cataflask a carpeta /dump/bd
def mongodump():
    os.system('mongodump -d cataflask')

#restore de la col·leció últim dump/
#l'últim es fa quan es fa scrap d'un mot i es guarda a mongo
def restoredump():
    try:
        # ! --> r' per escapar \a
        shell = 'mongorestore --db cataflask --collection mots --verbose dump\cataflask\mots.bson --drop'
        os.system(shell)
    except Exception as e:
        print("* FATAL ERROR RESTORE *", e)

"""
Regular expression operations
https://docs.python.org/3/library/re.html
regexemail = '^(\w|\.|\_|\-)+[@](\w|\_|\-|\.)+[.]\w{2,3}$'
Use a character set: [a-zA-Z] matches one letter from A–Z in lowercase and uppercase. 
[a-zA-Z]+ matches one or more letters and ^[a-zA-Z]+$ matches only strings 
   that consist of one or more letters only 
   (^ and $ mark the begin and end of a string respectively).
"""
def valida_nom(nom):
    ok = False
    pattern = '^[a-zA-Z]+$'
    
    #comprova expressió re
    if(re.search(pattern, nom)):
        print("nom ok")
        ok = True
    return ok

"""
Should have at least one number.
Should have at least one uppercase and one lowercase character.
Should have at least one special symbol.
Mínim 8 caràcters
"""
def valida_pass(pwd):
    ok = False
    pattern = '^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!#%*?&]{8,}$'
    
    #comprova expressió re
    if(re.search(pattern, pwd)):
        print("pass ok")
        ok = True
    return ok

def valida_mot(nom):
    ok = False
    #\w     caràcters unicode inclosos dígits
    #\s     espais
    #[^]    excloure, en aquest cas \d (dígits)
    pattern = '^[\w\s-][^\d]+$'
    
    #comprova expressió re
    if(re.search(pattern, nom)):
        print("mot ok")
        ok = True
    return ok

def treu_accents(cadena):
    #mínuscules
    cadena = cadena.lower()
    #versió amb str.maketrans() i str.translate()
    #cadenes de mateixa longitud per a conversió caràcter 1 a 1
    amb = 'àáèéíïòóúü'
    sense ='aaeeiioouu'
    #taula de conversió de les dues cadenes
    taula = str.maketrans(amb,sense)
    #fer la conversió amb translate()
    return cadena.translate(taula)

def espais_guions(cadena):
    return  cadena.replace(' ', '-')

#netejar cadena de caràcters especials
def neteja(cadena):
    regex = re.compile(r'[\n\r\t]')
    cadena = regex.sub('', cadena)
    return cadena

#solució paraulògic del dia
def scrap_paraulogic():
    url = "https://vilaweb.cat/paraulogic/"
    lls = []
    ll = []
    llneta = []

    try:
        print('GET solució paraulògic...')
        pag = requests.get(url)
        soup = BeautifulSoup(pag.text, 'html.parser')
        #print(soup)

        #agafem mots
        scripts = soup.find_all('script')
        #print(scripts)
        for script in scripts:
            lls.append(str(script))
        #print(lls)
        print(len(lls))

        pos = 1 # posició de l'script on hi ha les paraules

        print(lls[pos])
        print(type(lls[pos]))
        """
        var y={"l":["b","n","h","m","i","s","o"],
        "p":{"binomi": "binomi","biso": "bisó",...
        var t={"l":["m","a","t","x","u","r","c"],
        "p":{"acar":
        """
        #cal trobar 2n "p":{ que són els mots d'avui, els altres són els d'ahir
        #posició
        ini = lls[pos].rfind('"p":{') + 4
        print('???_______',ini)
        #ara posició + 4 tenim {
        print(lls[pos][ini])

        #ara buscar } a partir d'ini
        fi = lls[pos].find('}',ini)
        print(fi)
        print(lls[pos][fi])

        #agafar string paraules entre {}
        cad = lls[pos][ini+1:fi]

        #trec doble cometes
        cad = cad.replace('"', '')
        print(cad)

        #separo per comes en llista
        ll = cad.split(',')
        print(ll)

        #només paraula després de dos punts :
        for paraula in ll:
            llneta.append( paraula[ paraula.find(':') + 2 :] )
        print(llneta)
    
    except Exception as e:
        print("* FATAL ERROR SCRAP *", e)

    print(len(llneta), 'registre/s paraulògic...')
    return llneta

#pàgina últims rodamots
def scrap_ultims():
    url = "https://rodamots.cat/mots/arxiu-ultims-mots/"
    ll = []

    try:
        print('GET últims rodamots...')
        pag = requests.get(url)
        soup = BeautifulSoup(pag.text, 'html.parser')
        #print(soup)

        #agafem mots
        items = soup.find_all(class_='mot')
        for item in items:
            mot = item.find(class_='h2').text
            #data = item.find('time').text
            #ll.append((mot,data))
            ll.append(mot)
        print(ll)
    
    except Exception as e:
        print("* FATAL ERROR SCRAP *", e)

    print(len(ll), 'registre/s...')
    return ll

#pàgina per temes, rodamots
def scrap_categories():

    url = "https://rodamots.cat/mots/arxiu-per-categories/"
    ll = []

    try:
        print('GET categories rodamots...')
        pag = requests.get(url)
        soup = BeautifulSoup(pag.text, 'html.parser')
        #print(soup)

        #agafem cats
        items = soup.find(class_='llistaindex').find_all('li')
        print(len(items))
        for item in items:
            url = item.find('a')['href']
            cat = item.text
            ll.append( (cat,url) )
        #print(ll)
    
    except Exception as e:
        print("* FATAL ERROR SCRAP *", e)

    print(len(ll), 'registre/s...')
    return ll

#utilitzo selenium i driver per clicks a pàgina, passo url
def scrap_categoria(url):
    ll = []
    
    options = Options()
    options.headless = True
    options.add_argument("--window-size=1920,1200")

    driver = webdriver.Chrome(options=options, executable_path=DRIVER_PATH)

    try:
        print('GET mots de categoria...')
        driver.get(url)

        #agafar mots 1a pàg
        items = driver.find_elements(By.CLASS_NAME,'h2')
        for el in items:
            ll.append(el.text)

        #agafar links pags
        links = driver.find_elements(By.CSS_SELECTOR ,'.page-numbers a')
        print('pàgines: ', len(links))
        
        #links a llista, menys l'últim que és repetit '->'
        pags = [link.get_property('href') for link in links][:-1]
        print(pags)

        #si resultats
        if len(pags) > 0:
            for pag in pags:
                #carregar de nou la pàgina a driver
                driver.get(pag)
                        
                #agafar mots pàg
                items = driver.find_elements(By.CLASS_NAME,'h2')
                for el in items:
                    ll.append(el.text)
                #print(ll)
            
    except Exception as e:
        print("* FATAL ERROR SCRAP *", e)

    driver.quit()
    print(len(ll), 'registre/s...')
    return ll

#cal treure accents en cerca
#per frases, cal canviar espai per '-'
def scrap_rodamots(mot):
    #rodamots mot
    mot_sense = treu_accents(mot)

    #no cantar-ne gall ni gallina
    #no-cantar-ne-gall-ni-gallina
    mot_sense = espais_guions(mot_sense)
    print(mot_sense)

    url = f"https://rodamots.cat/{mot_sense}/"
    ll = []

    try:
        print(url)
        print('GET rodamots...')
        pag = requests.get(url)
        soup = BeautifulSoup(pag.text, 'html.parser')
        #print(soup)

        #entrada = soup.find(class_="entry-title").find(class_="midleline").text
        entrada = soup.find(class_="entry-title")
        if entrada != None:
            entrada = entrada.find(class_="midleline").text
        #tag = soup.find(class_="entry-title").find(class_="tipusgram").text
        tag = soup.find(class_="entry-title")
        if tag != None:
            tag = tag.find(class_="tipusgram").text

        #agafem item per contingut item
        item = soup.find(class_='article-content')
        
        #defi = item.find(class_="definicions").find(class_="innerdef").text
        defi = item.find(class_="definicions")
        if defi != None:
            defi = defi.find(class_="innerdef").text

        #eti = item.find(class_="etimologia").find(class_="innerdef").text
        eti = item.find(class_="etimologia")
        if eti != None:
            eti = eti.find(class_="innerdef").text
        
        cites = item.find_all(class_="cita")
        cats = item.find_all(class_="cat")

        # datetime object containing current date and time
        now = datetime.now()

        doc = { "mot": mot,
                "entrada": entrada,
                "tags": tag,
                "defi": defi,
                "eti":eti,
                "cites": [cita.text for cita in cites],
                "cats": [cat.find('a').text for cat in cats],
                "origen": 'rodamots',
                "data_scrap": now.strftime("%d/%m/%Y %H:%M:%S"),
                "url_scrap": url}
        
        ll.append(doc)
        #print(doc)
    
    except Exception as e:
        print("* FATAL ERROR SCRAP *", e)

    print(len(ll), 'registre/s...')
    return ll

#diec mot, amb selenium i driver
def scrap_diec(mot):

    url = f"https://dlc.iec.cat/Results?DecEntradaText={mot}"
    ll = []
    #print(url)

    options = Options()
    options.headless = True
    options.add_argument("--window-size=1920,1200")

    driver = webdriver.Chrome(options=options, executable_path=DRIVER_PATH)
    #driver.get("https://www.nintendo.com/")
    #print(driver.page_source)

    try:
        print('GET diec...')
        #pag = requests.get(url)
        driver.get(url)
        #pag = driver.page_source

        #esperem un delay per càrrega pàgina
        time.sleep(0.5)
        
        #agafar resultats
        resultats = driver.find_elements(By.CLASS_NAME,'resultAnchor')
        print('resultats: ', len(resultats))

        #si resultats
        if len(resultats) > 0:
            for el in resultats:
                #print(el.text)
                #clicar a link i carregarà contingut defi
                el.click()
                time.sleep(0.5)
                
                #agafar  defi
                entrada = driver.find_element(By.CLASS_NAME,'title')

                defi = driver.find_element(By.CLASS_NAME,'resultDefinition')
                tags = driver.find_elements(By.CLASS_NAME,'tagline')
                tips = driver.find_elements(By.CLASS_NAME,'tip')
                print('len tags i tips',len(tags), len(tips))

                # datetime object containing current date and time
                now = datetime.now()
                                
                #print('defi diec: ',defi.text)
                doc = { "mot": mot,
                        "entrada": entrada.text,
                        "defi": defi.text,
                        "tags": list(set([tag.text for tag in tags])),
                        "tips": list(set([tip.text for tip in tips])),
                        "origen": 'diec',
                        "data_scrap": now.strftime("%d/%m/%Y %H:%M:%S"),
                        "url_scrap": url}
                ll.append(doc)

    except Exception as e:
        print("* FATAL ERROR SCRAP *", e)

    driver.quit()
    print(len(ll), 'registre/s...')
    return ll

#sinònims mot
def scrap_sinonims(mot):
    #sinònims 
    url = f"https://www.softcatala.org/diccionari-de-sinonims/paraula/{mot}/"
    ll = []
    
    try:
        print('GET dic sinònims softcatlà...')
        pag = requests.get(url)
        soup = BeautifulSoup(pag.text, 'html.parser')
        #print(soup)

        #agafar resultats
        items = soup.find(class_='diccionari-resultat')
        #print(len(items))

        ent = items.find_all('h3')
        sin = items.find_all(class_ = 'multilingue_list')

        #readapto llista, dels valors en llistes obtinguts
        llista = []
        for i in range(len(ent)):
            llista.append([ent[i], sin[i]])
            
        # datetime object containing current date and time
        now = datetime.now()

        for el in llista:

            doc = { "mot": mot,
            "entrada": el[0].text,
            "sinonims": el[1].text,
            "origen": 'softcatalà',
            "data_scrap": now.strftime("%d/%m/%Y %H:%M:%S"),
            "url_scrap": url}
            
            ll.append(doc)

    except Exception as e:
        print("* FATAL ERROR SCRAP *", e)

    print(len(ll), 'registre/s...')
    return ll

#traduccions del mot
def scrap_termes(mot):
    #sinònims 
    #url = f"https://www.termcat.cat/ca/cercaterm/{mot}?type=basic&thematic_area=&language=ca"
    url = f"https://www.termcat.cat/ca/cercaterm/{mot}?type=advanced&thematic_area=&language=ca&condition=match&fields=&category=&hierarchy="
    ll = []
    
    try:
        print('GET termcat...')
        pag = requests.get(url)
        soup = BeautifulSoup(pag.text, 'html.parser')
        #print(soup)

        #títol item
        ent = soup.find_all(class_='service-item__name')
        
        #contingut items
        items = soup.find_all(class_='service-item')
        print('items:', len(items))
        
        #per cada item
        for i in range(len(items)):

            tag = items[i].find(class_='service-item__tag')

            defi = None
            if items[i].find(class_='service-item__definitions-text') != None:
                defi = items[i].find(class_='service-item__definitions-text').text
            
            #tradu = items[i].find(class_='service-item__terms').find('ul')
            tradu = items[i].find_all(class_='service-item__term')
            print("traduccions",len(tradu))

            # datetime object containing current date and time
            now = datetime.now()

            doc = { "mot": mot,
            "entrada": ent[i].text,
            "cats": tag.text,
            "defi": defi ,
            "traduccions": [tra.text for tra in tradu],
            "origen": 'termcat',
            "data_scrap": now.strftime("%d/%m/%Y %H:%M:%S"),
            "url_scrap": url}
            
            ll.append(doc)

    except Exception as e:
        print("* FATAL ERROR SCRAP *", e)

    print(len(ll), 'registre/s...')
    return ll

#utilitzo selenium i driver per protecció uab (uab demana certificat)
def scrap_frases(mot):
    #frases fetes 
    url = f"https://dsff.uab.cat/cerca?mode=Conté&frase={mot}"
    ll = []
    
    options = Options()
    options.headless = True
    options.add_argument("--window-size=1920,1200")

    driver = webdriver.Chrome(options=options, executable_path=DRIVER_PATH)

    try:
        print('GET dic frases fetes uab...')
        driver.get(url)
        #pag = driver.page_source
            
        #agafar resultats
        frases = driver.find_elements(By.CLASS_NAME,'entry')
        print('frases: ', len(frases))

        for frase in frases:
            #print(frase.text)

            # datetime object containing current date and time
            now = datetime.now()

            doc = { "mot": mot,
                    "frasefeta": frase.text,
                    "origen": 'uab',
                    "data_scrap": now.strftime("%d/%m/%Y %H:%M:%S"),
                    "url_scrap": url}

            #ll.append(frase.text)     
            ll.append(doc)

    except Exception as e:
        print("* FATAL ERROR SCRAP *", e)

    driver.quit()
    print(len(ll), 'registre/s...')
    return ll

#fitxes optimot i altres
#cal treure accents en cerca
def scrap_optimot(mot,tipus='TOT'):
    ll = []
    mot_sense = treu_accents(mot)

    if tipus == 'TOT':
    #optimot tot
        url = f"https://aplicacions.llengua.gencat.cat/llc/AppJava/index.html?action=Principal&method=cerca_generica&input_cercar=${mot_sense}&tipusCerca=cerca.tot"

    elif tipus == 'FITXA':
        #optimot fitxes
        url = f"https://aplicacions.llengua.gencat.cat/llc/AppJava/index.html?action=Principal&method=cerca_generica&input_cercar={mot}&tipusCerca=cerca.fitxes"
    
    try:
        print(url)
        print(f"GET {tipus} optimot...")
        pag = requests.get(url)
        soup = BeautifulSoup(pag.text, 'html.parser')
        #print(soup)

        #resultats
        items = soup.find_all(class_='SCL_resultatNOSeleccionatDreta')

        for item in items:
            a = item.find('a')
            #titol = a.text
            #url = a['href']
            font = item.find(class_='text-xs2').text
            text = item.find(class_='text-xs').text
            #print([titol, url, font, text])

            # datetime object containing current date and time
            now = datetime.now()

            doc = { "mot": mot,
            "entrada": neteja(a.text),
            "url_entrada": a['href'],
            "cerca": neteja(text) ,
            "font": font,
            "origen": 'optimot',
            "data_scrap": now.strftime("%d/%m/%Y %H:%M:%S"),
            "url_scrap": url}
            
            ll.append(doc)

    except Exception as e:
        print("* FATAL ERROR SCRAP *", e)

    print(len(ll), 'registre/s...')
    return ll


#_______________________________________________________flask
app = Flask(__name__) # create the application instance :)
app.config.from_object(__name__) # load config from this file , flaskr.py

# Load default config and override config from an environment variable
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'flaskr.db'),
    SECRET_KEY='development key',
    USERNAME='admin',
    PASSWORD='default'
))
app.config.from_envvar('FLASKR_SETTINGS', silent=True)

@app.route("/")
def inici():
    return render_template('login.html')

@app.route("/home")
def home():
    if not session.get('ok'):
        abort(401)

    info = mongo_info()
    print(info)
    return render_template('loginok.html', info=info)

#amb mètode get per mot
@app.route("/fitxa", methods=['GET'])
def fitxa():
    if not session.get('ok'):
        abort(401)
    docs = []
    print(request.args)
    print(len(request.args))
    mot = request.args.get('mot', '')

    #consulta docs mot
    fitxa = mongo_mot(mot)
    print(len(fitxa))
    
    return render_template('fitxa.html', mot=mot, fitxa=fitxa)

#amb mètode get per enviar url si link categories
@app.route("/apren", methods=['GET'])
def apren():
    if not session.get('ok'):
        abort(401)
    mots = []
    print(request.args)
    print(len(request.args))
    url = request.args.get('url', '')
    error = request.args.get('error', '') #retorn error validació per get
    totok = request.args.get('totok', '') #retorn totok per get

    if (url):
        print('ok url get')
        mots = scrap_categoria(url)
    else:
        print('no url get')
        mots = scrap_ultims()
        
    cats = scrap_categories()
    return render_template('apren.html', mots=mots, cats=cats, error=error, totok=totok)

#amb mètode get per enviar url si link categories
@app.route("/apren_paraulogic", methods=['GET'])
def apren_paraulogic():
    if not session.get('ok'):
        abort(401)
    error = request.args.get('error', '') #retorn error validació per get
    totok = request.args.get('totok', '') #retorn totok per get
    mots = []
    mots = scrap_paraulogic()
    return render_template('apren_paraulogic.html', mots=mots, error=error, totok=totok)


@app.route('/scrap', methods=['POST'])
def scrap():
    if request.method == 'POST':
        
        #per saber de quina pàgina s'envia
        pag =  request.form['apren']

        mot = request.form['mot']
        session.pop('mot_existeix', None)

        #avisar si mot existeix
        info = mongo_info()
        mots = info['mots']
        if mot in mots:
            session['mot_existeix'] = True

        #valida input
        if valida_mot(mot):
            
            ll_roda = scrap_rodamots(mot)
            ll_diec = scrap_diec(mot)
            ll_term = scrap_termes(mot)
            ll_sino = scrap_sinonims(mot)
            ll_fras = scrap_frases(mot)
            ll_opti = scrap_optimot(mot,'FITXA')
            ll_optialtres = scrap_optimot(mot)

            #guardar a algun lloc per insert a mongo
            docs = [ll_roda, ll_diec, ll_term, ll_sino, ll_fras, ll_opti, ll_optialtres]
            
            #a session no hi cap, error size cookie
            #session['docs'] = docs
            
            #guardem a fitxer temporal
            fitxer = FILE_TEMP
            guarda_pickle(fitxer,docs)

            #session mot
            session['mot'] = mot
            
            #retornem resultats, pendent confirmació guardar a mongo
            return render_template('scrap.html', 
                    sopa_roda = ll_roda, 
                    sopa_diec = ll_diec, 
                    sopa_term = ll_term, 
                    sopa_sino = ll_sino, 
                    sopa_fras = ll_fras, 
                    sopa_opti = ll_opti, 
                    sopa_optialtres = ll_optialtres)
            
            #return redirect(url_for('apren'))

        else:
            error = "* FATAL ERROR * validació mot [abc, ' ', '-' ]"
        
        #pàgina d'on venia
        if pag == 'apren':        
            return redirect(url_for('apren', error=error))
        else:
            return redirect(url_for('apren_paraulogic', error=error))


@app.route("/guarda_mot")
def guarda_mot():
    error = None
    totok = None

    if not session.get('ok'):
        abort(401)
    
    #llegir fitxer temps
    docs = load_pickle(FILE_TEMP)
    print(docs)

    #sessions
    existeix = session.get('mot_existeix')
    mot = session.get('mot')

    #missatge si ok o error registre guardat
    #enviar sms
    if mongo_insert_mot(docs, mot, existeix):
        
        totok = f'* ALTA {mot} OK :) *'
        
        #backup mongodump
        mongodump()

        #session.pop('mot', None)
        #return render_template('apren.html', totok= totok)
        return redirect(url_for('apren', totok=totok))
    else:
        error = "* FATAL ERROR * l'insert ha fet figa"
    #return render_template('apren.html', error=error)
    return redirect(url_for('apren', error=error))

@app.route("/apres", methods=['GET'])
def apres():
    if not session.get('ok'):
        abort(401)
    info = {}
    consulta = {}
    print(request.args)
    print(len(request.args))

    args = len(request.args)
    
    #paràmetres GET
    consulta['tag'] = request.args.get('tag', '')
    consulta['tip'] = request.args.get('tip', '')
    consulta['cat'] = request.args.get('cat', '')
    consulta['cad'] = request.args.get('cad', '')

    error = False
    #totok = request.args.get('totok', '') #retorn totok per get

    if (args):
        print('ok consulta get')
        #fer consulta mots
        info = mongo_info(consulta)
        print(info['mots'])

        #si no resultats
        if len(info['mots']) == 0:
            error = NOT_CERCA

    else:
        print('no consulta get')
        info = mongo_info()
        print(info['mots'])

    return render_template('apres.html', info=info, TAGS=TAGS, error=error)

@app.route("/about")
def about():
    if not session.get('ok'):
        abort(401)
    return render_template('about.html')

@app.route("/users")
def users():
    if not session.get('ok'):
        abort(401)
    users = mongo_users()
    print(users)
    return render_template('users.html', llista = users)

@app.route("/login", methods=['POST'])
def login():
    error = None
    if request.method == 'POST':
        usuari = request.form['user']
        pwd = request.form['pass']

        #si user
        if mongo_login(usuari.lower(),pwd):
            #activem session i guardem
            session['ok'] = True
            session['usuari'] = usuari
            flash('You were logged in')
            return redirect(url_for('home'))
        else:
            #return redirect('loginko')
            error = "* FATAL ERROR LOGIN KO *"
            print(error)
            return render_template('login.html', error = error)

@app.route("/signup")
def signup():
    return render_template('signup.html')

@app.route("/nou_user", methods=['POST'])
def nou_user():
    error = None
    totok = None
    if request.method == 'POST':
        usuari = request.form['user']
        pwd = request.form['pass']
        rpwd = request.form['rpass']

        #verificar camp user, buit i altres
        #print(valida_nom(usuari))
        if valida_nom(usuari):
            #nom a min
            usuari = usuari.lower()

            #existeix user ?
            if not mongo_existeix(usuari):
                print('OK, user no existeix')
                
                #verificar pass
                if valida_pass(pwd):
                    print('OK PASS')

                    #pass = rpass ?
                    if pwd == rpwd:
                        #si ok, encriptar pass
                        # generate new salt, and hash a password
                        hash = pbkdf2_sha256.hash(pwd)
                        print(hash)

                        #guardar user a mongo
                        #si ok, pag login, missatge ok
                        if mongo_insert_user(usuari,hash):
                            totok = '* ALTA USUARI OK :) *'
                            return render_template('login.html', totok = totok)

                        #si error, pag signup, missatge error
                        else:
                            error = "* FATAL ERROR * l'insert ha fet figa"
                    else:
                        error = '* FATAL ERROR * pass no coincideix'
                else:
                    error = '* FATAL ERROR * validació pass'
            else:
                error = '* FATAL ERROR * usuari ja existeix'
        else:
            error = '* FATAL ERROR * validació nom'

        return render_template('signup.html', error = error)

#amb mètode get per mot
@app.route("/delete_mot", methods=['GET'])
def delete_mot():
    if not session.get('ok'):
        abort(401)
    print(request.args)
    print(len(request.args))
    mot = request.args.get('mot', '')

    mongo_delete_mot(mot)
    
    return redirect(url_for('apres'))

@app.route('/reset')
def reset():
    if not session.get('ok'):
        abort(401)
    reset_mongo()
    return redirect(url_for('home'))

@app.route('/restore')
def restore():
    if not session.get('ok'):
        abort(401)
    restoredump()
    return redirect(url_for('home'))

@app.route('/logout')
def logout():
    session.pop('ok', None)
    flash('You were logged out')
    return redirect(url_for('inici'))

@app.errorhandler(401)
def unauthorized(e):
    # note that we set the 401 status explicitly
    return render_template('401.html'), 401

@app.errorhandler(404)
def notfound(e):
    # note that we set the 401 status explicitly
    return render_template('404.html'), 404

app.run()

