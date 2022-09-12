#Regular expression operations
#https://docs.python.org/3/library/re.html
#regexemail = '^(\w|\.|\_|\-)+[@](\w|\_|\-|\.)+[.]\w{2,3}$'

import re

pattern = '^[a-zA-Z]+$'
nom = 'kk'

#comprova expressió re, flag ascii per no accents
if re.search(pattern, nom, flags=re.A):
    print("nom ok")
else:
    print('nom fatal')

pattern = '[A-Za-z0-9@#$%^&+=]{8,}'
pattern = '^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!#%*?&]{8,}$'
pwd = 'aAaa6aa*'

if re.search(pattern, pwd):
    print("pass ok")
else:
    print('pass fatal')

#____________________________________
#https://blog.tiraquelibras.com/?p=1041#Cifrar_contrasena

import hashlib
import os

pwd = 'q1w2e3r4t5'        
clau = pwd.encode('utf-8')
print(pwd, clau)

hash = hashlib.md5(clau)
print(hash)
print(dir(hash.hexdigest()))

md5 = hashlib.md5(clau).hexdigest()
print("Hash MD5: %s" % str(md5))

sha1 = hashlib.sha1(clau).hexdigest()
print("Hash SHA1: %s" % str(sha1))

sha224 = hashlib.sha224(clau).hexdigest()
print("Hash SHA224: %s" % str(sha224))

sha256 = hashlib.sha256(clau).hexdigest()
print("Hash SHA256: %s" % str(sha256))

sha384 = hashlib.sha384(clau).hexdigest()
print("Hash SHA384: %s" % str(sha384))

sha512 = hashlib.sha512(clau).hexdigest()
print("Hash SHA512: %s" % str(sha512))



#https://nitratine.net/blog/post/how-to-hash-passwords-in-python/#
#https://levelup.gitconnected.com/python-salting-your-password-hashes-3eb8ccb707f9
#https://docs.python.org/3/library/hashlib.html


salt = os.urandom(32)
#plaintext = 'hellow0rld'.encode()

pwd = 'q1w2e3r4t5'        
clau = pwd.encode('utf-8')
print(pwd, clau)

hash = hashlib.pbkdf2_hmac('sha256', clau, salt, 10000)
print('hash ->',hash)

pwd2 = 'q1w2e3r4t5'        
clau2 = pwd2.encode('utf-8')
print(pwd2, clau2)

hash2 = hashlib.pbkdf2_hmac('sha256', clau2, salt, 10000)
print('hash2 ->',hash2)

print('hash  hex->',hash.hex())
print('hash2 hex->',hash2.hex())

print(hash == hash2)


#_______________________________
#$ sudo pip install passlib
from passlib.hash import pbkdf2_sha256

# generate new salt, and hash a password
hash = pbkdf2_sha256.hash("toomanysecrets")
print(hash)

# verifying the password
print(pbkdf2_sha256.verify("toomanysecrets", hash))
print(pbkdf2_sha256.verify("joshua", hash))

"""
#______________________________________
#https://www.scrapingbee.com/blog/selenium-python/

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

DRIVER_PATH = 'driver/chromedriver'

options = Options()
options.headless = True
options.add_argument("--window-size=1920,1200")

driver = webdriver.Chrome(options=options, executable_path=DRIVER_PATH)
driver.get("https://www.nintendo.com/")
print(driver.page_source)
driver.quit()
"""

print("------------------------")
cadena = "\nfr\n \xa0colline\n \n"
cad2 = "Tossal, el\r\n\t\t\t\t\t\t\t\r\n\t\t\t\t\t\t\t\r\n\t\t\t\t\t\t\t\r\n\t\t\t\t\t\t\t\n"
print(cadena)
print(cad2)

regex = re.compile(r'[\n\r\t]')
cadena = regex.sub('', cadena)
cad2 = regex.sub('',cad2)
print(cadena)
print(cad2)

ll = [
    {'paraula': 'tossal',
     'entrada': 'tossal',
     'tags': ' m ',
     'definició': '\nElevació del terreny no gaire alta ni de pendent gaire rost, en una plana o aïllada d’altres muntanyes.\n«Primer se muda un tossal que un natural»: significa que el geni o caràcter de les persones és difícil de canviar (Urgell).\n', 'etimologia': '\nDe tossa, d’origen incert, probablement d’un preromà hispànic taucia, ‘rabassa’.\n',
     'cites': ['Xano-xano, rebent la carícia del sol, va arribar per fi al peu del tossal del castell i en restà una mica decebut. Tot i que tenia bones torres, semblava un mas amb parra i tot a la porta. Enric Valor, «El Castell del Sol», dins Rondalles valencianes 7 (València: Tàndem/Albatros, 1995)\n', 'La muntanya del Vedat, que no és verdadera muntanya sinó muntanyeta o tossal, s’eleva —s’eleva poc, ja que no arriba més amunt dels cent cinquanta metres— com una illa més fosca enmig de la mar plana de tarongers, i Salvador pujant els revolts de la carretera comprovava que també allí la vegetació estava massa seca, l’herba escassa era tota de color gris i els margallons groguejaven… Joan F. Mira, Purgatori (Barcelona: Proa, 2003)\n'],
     'cats': ['accidents geogràfics'], 
     'origen': 'rodamots', 
     'data_scrap': '10/01/2022 12:16:36', 
     'url_scrap': 'https://rodamots.cat/tossal/'}]

print(type(ll),len(ll))
ll = dict(ll[0])
print(type(ll),len(ll))
print(ll)