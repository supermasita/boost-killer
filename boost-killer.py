#!/usr/bin/python
# coding: utf-8

"""
BOOST KILLER 
https://github.com/supermasita/boost-killer

This a is a script to clean Drupal's Boost Page Cache when using "Retro mode" 
(no database).

The script requires that the Boost tag is enabled (chech "Performance/Boost" 
config). In the end of the static HTML you shoud see something like :

<!-- Page cached by Boost @ 2012-01-20 12:42:18, expires @ 2012-01-20 12:57:18 -->

This tag is used by the script to detect if the static HTML is current or should
be erased, based on the configuration you chose globally or per page/view/etc.

Questions? Suggestions? Curses? Find me at Github.
"""

import os, datetime, fnmatch

# Date variables
AHORA=datetime.datetime.now()
DEIT=AHORA.strftime("%Y-%m-%d ; %H:%M:%S")
FECHA=AHORA.strftime("%Y%m%d")
HORA=AHORA.strftime("%H%M%S")
# Name and path to list of files to check
LISTA="/var/tmp/boost_killer.lista"
# Absolut path to boost cache folder
CACHE="/var/www/html/site/cache/"
# Initialize counters
BORRADO=0
VIGENTE=0

# We create the list of files to check and (if applies) erase
LISTADO=open(LISTA, 'w')
for root, carpetas, archivos in os.walk(CACHE):
    for file in archivos:
        if fnmatch.fnmatch(file, '*.xml') or fnmatch.fnmatch(file, '*.html') or fnmatch.fnmatch(file, '*.json'):
                LISTADO.write(os.path.join(root,file)+"\n")

# Open log files
LOG=open('/var/tmp/boost_killer.log','w')
STATS=open('/var/tmp/boost_killer.stats','a')

# Log start timestamp
STATS.write(DEIT+" ; INICIO ;\n")

# We check every file
for I in open(LISTA):
        try:
                # HTML and HTML.GZ
                ARCHIVO=I.rstrip('\n')
                ARCHIVOGZ=ARCHIVO+".gz"
                FILE=open(ARCHIVO)
                # Last 83 characters from the end of the html
                FILE.seek(-83,2)
                LINEA=FILE.readline()
                # Check if there is the Boost tag
                if "Page cached by Boost" in LINEA:
                        # Parse Boost tag
                        FECHAB=LINEA[59:69].replace('-','')
                        HORAB=LINEA[70:78].replace(':','')
                        # Date is older than today? Bye bye
                        if FECHAB < FECHA :
                                os.remove(ARCHIVO)
                                os.remove(ARCHIVOGZ)
                                BORRADO=BORRADO+1
                                LOG.write(DEIT+" ; Erased ; "+ARCHIVO+"\n")
                        # Date is current but time not? Bye bye
                        elif FECHAB == FECHA and HORAB < HORA :
                                os.remove(ARCHIVO)
                                os.remove(ARCHIVOGZ)
                                BORRADO=BORRADO+1
                                LOG.write(DEIT+" ; Erased ; "+ARCHIVO+"\n")
                        else :
                                VIGENTE=VIGENTE+1
        except IOError:
                pass


# Print and write statistics
DEIT=AHORA.strftime("%Y-%m-%d ; %H:%M:%S")
print DEIT," ; Erased ; ",BORRADO
STATS.write(DEIT+" ; Erased ; %d \n" % BORRADO)
print DEIT," ; Valid ; ",VIGENTE
STATS.write(DEIT+" ; Valid ; %d \n" % VIGENTE)

# Close log files
LOG.close()
STATS.close()
