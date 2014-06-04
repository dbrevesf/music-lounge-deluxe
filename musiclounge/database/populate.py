#!/usr/bin/env python
# -*- coding: utf-8 -*-

#
# IMPORTS
#
import Image
import os
import MySQLdb
import sys
import xml.dom.minidom
import wikipedia

sys.path.append("/home/daniel/Disciplinas/MC536/socialnetwork/")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "socialnetwork.settings")

from django.core import management
from django.db import connection
from musiclounge import models
from subprocess import call
from unicodedata import normalize
from urllib import unquote


#
# DEFINITIONS
#
FRIENDSHIP_XML = '../database/xmls/knows.xml'
MUSIC_XML = '../database/xmls/likesMusic.xml'
USER_XML = '../database/xmls/person.xml'
IMAGE_URL = '../static/images/'


#
# CODE
#

def getXMLStructure(path):
    """
    This method reads a xml file and return the data structure containing
    each node of xml.

    @param path: The path to the file where the xms is in.
    @type path: String
      
    @returns: XML structure
    @rtype: xmlObject
    """
    x = xml.dom.minidom.parse(path)
    nos = x.documentElement
    xmlStructure = [no for no in nos.childNodes if no.nodeType == \
                  x.ELEMENT_NODE]

    return xmlStructure
# def getXMLStructure()


def populateUserTable():
    """
    This method reads a xml file containing users and insert on database

    @returns: nothing
    @rtype: none
    """
    # get XML structure
    xmlStructure = getXMLStructure(USER_XML)

    for node in xmlStructure:
        
        # get the name 
        name =  node.getAttribute('name')

        # get the first name
        firstName = name.split(' ')[0]
        
        # get the login
        login =  (node.getAttribute('uri'))[38::]
        
        # get the city
        city = node.getAttribute('hometown')
        
        # build the db object    
        dbObj = models.User(name=name, firstName=firstName, login=login, city=city)

        # save the object in db
        dbObj.save()

        # save user profile image
        size = 64, 64
        img = ""
        try:
            img = Image.open(IMAGE_URL+login+"_img")
        except:
            img = Image.open(IMAGE_URL+"generic.png")
        if img:
            img.thumbnail(size, Image.ANTIALIAS)
            img.save(IMAGE_URL+login+"_img", "png")
        print "- Usuario " + str(login) + " inserido."

    print "- Usuario populado"


def populateFriendshipTable():
    """
    This method reads a xml file containing users friendship relations 
    and insert on database

    @returns: nothing
    @rtype: none
    """
    # get XML structure
    xmlStructure = getXMLStructure(FRIENDSHIP_XML)
    
    for node in xmlStructure:

        # get the user
        user =  (node.getAttribute('person'))[38:]

        # get the friend
        friend = (node.getAttribute('colleague'))[38:]
        
        # get the User db object
        user =  models.User.objects.filter(login=user)[0]

        # get the User db object for friend
        friend =  models.User.objects.filter(login=friend)[0]

        # build the db object
        dbObj =  models.Friendship(user=user, friend=friend)

        # save the object in db
        dbObj.save()

        print "- Usuario " + str(user) + " conhece " + str(friend) + " inserido"

    print "- Conhece populado"


def populateMusicTables():
    """
    This method reads a xml file containing users rating of musical acts
    and insert in both MusicalAct and MusicalActRating tables. This method 
    also consult an external database to get the correct URI from each musical
    act in the XML. This is required because many users insert incorrect URI 
    when they signed up.

    @returns: nothing
    @rtype: none
    """

    # get XML structure
    xmlStructure = getXMLStructure(MUSIC_XML)
    
    # create musical act list 
    musicalActList = []

    # connect to external db
    db = MySQLdb.connect(host='localhost',
                         user='root',
                         passwd='loste', 
                         db="urlRelations")

    # instantiate a cursor
    cursor = db.cursor()

    for node in xmlStructure:

        # get user
        user = (node.getAttribute('person'))[38:]

        # get it's rate
        rate = int(node.getAttribute('rating'))
        
        # get musical act URI
        musicalActURI = normalize('NFKD', unquote(
                        unicode(node.getAttribute('colleague')))).encode(
                        'ASCII','ignore').lower()

        # select the correct URI                
        cursor.execute("SELECT destination, summary FROM urls WHERE origin = %s", (musicalActURI))

        # get the data from select
        data = cursor.fetchone()
        
        # URI exists: work on it
        if data:

            # get summary
            summary = data[1]

            # get uri
            uri = data[0]

            # get the title
            title = normalize('NFKD', unquote(unicode(uri[29:]))).encode('ASCII', 'ignore')

            # musical act already exists: get it
            if uri in musicalActList:

                print "+ Ato Musical já inserido"
                
                # get the musical act
                musicalAct =  models.MusicalAct.objects.filter(uri=uri)[0]
            
            # musical act doesn't exists: create it
            else:

                # build the db object 
                musicalAct =  models.MusicalAct(uri=uri, title=title, summary=summary)
                
                # save the object in db
                musicalAct.save()

                # save musical act image
                size = 64, 64
                try:
                    img = Image.open(IMAGE_URL+str(musicalAct.id)+"_img")
                except:
                    img = Image.open(IMAGE_URL+"genericMusic.jpg")
                    img.thumbnail(size, Image.ANTIALIAS)
                    img.save(IMAGE_URL+str(musicalAct.id)+"_img", "png")
                
                # insert the URI in musicalActList
                musicalActList.append(uri)
                print "- Ato Musical " + uri + " inserido"

            # get the user object
            user =  models.User.objects.filter(login=user)[0]

            # build the db object 
            dbObj =  models.MusicalActRate(musicalAct=musicalAct, user=user, rate=rate)
            
            # save the object in db
            dbObj.save()

            print "- Nota " + str(rate) + " atribuida ao ato musical " + uri + " pelo usuario " + str(user)

    print "- MusicalAct populado"
    print "- MusicalActRate populado"


def recreateDb():
    """
    This method drop and create the database
    """
    print("Dropping and creating database " + "musiclounge")
    
    # conect to database
    cursor = connection.cursor()

    # execute the query
    cursor.execute("DROP DATABASE " +  "musiclounge" + "; CREATE DATABASE " + "musiclounge" + "; USE " + "musiclounge" + ";")

    print("Done")



def main():
    """
    This method executes all the other methods required to populate the databse
    """
    
    # recreate the database
    recreateDb();

    print("Syncing DB")

    #sync database with django
    management.call_command('syncdb', interactive=False)



    #populate user table
    populateUserTable()

    #populate friendship table
    populateFriendshipTable()

    #populate music acts and rating tables
    populateMusicTables()


# call the main
main()