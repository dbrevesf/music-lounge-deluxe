#!/usr/bin/env python
# -*- coding: utf-8 -*-

#
# IMPORTS
#
from unicodedata import normalize
from urllib import unquote

import MySQLdb
import os
import sys
import xml.dom.minidom
import wikipedia

#
# DEFINITIONS
#
MUSIC_XML = "../database/xmls/likesMusic.xml"
sys.path.append("/home/daniel/Disciplinas/MC536/musiclounge/")


#
# CODE
#

def connectToDb():
    """
    This method makes the connection with database

    @rtype: dbObject
    @returns: a dbObject to execute queries in database
    """

    # connect to db
    db = MySQLdb.connect(host='localhost',
                          user='root',
                          passwd='loste')
    return db
# def connectToDb()


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
# getXMLStructure()    


def main():
    """
    This method executes all the other methods required to populate the databse
    """
    # connect to db
    db = connectToDb()

    # recreate db
    recreateDb(db)

    # populate table
    populateUrlsRelationTable(db)
# def main()


def populateUrlsRelationTable(db):
    """
    This method get each URI of xml and search it in wikipedia package
    to get it's correct URI
    """
    # instantiate cursor
    cursor = db.cursor()
    
    # get the xml structure
    xmlStructure = getXMLStructure(MUSIC_XML)

    # create musical act list
    musicalActList = []

    for node in xmlStructure:

        # get the uri
        uri = normalize('NFKD', unquote(unicode(node.getAttribute('colleague')))).encode('ASCII','ignore').lower()
        
        # get the title
        title = uri[29:]
        
        # search for wikipedia page
        try:
            wiki = wikipedia.page(title)
            page = True
        except:
            # if there is ambiguous page, search for <act>_(band)
            try:
                wiki = wikipedia.page(title+"_(band)")
                page = True
            except:
                print "+ Página inexistente"


        # there is a page 
        if page:

            # there is a summary: format it
            summary = ""
            if wiki.summary:
                summary = normalize('NFKD', unquote(unicode(wiki.summary))).encode('ASCII','ignore').lower().replace("'", "").replace("\n", "").replace('"', '')

            # insert it in db
            cursor.execute('INSERT IGNORE INTO urls (origin, destination, summary) VALUES ("' + uri + '", "' + wiki.url + '", "' + summary + '")')
            # addUri = "INSERT IGNORE INTO urls (origin, destination) VALUES (%s, %s)"
            # dataUri = (uri, wiki.url)
            # cursor.execute(addUri % dataUri)
            db.commit()
            print "+ URL " + uri + " relacionada com " + wiki.url
# populateUrlsRelationTable()


def recreateDb(db):
    """
    This method drop and create the database
    """

    # instantiate cursor
    cursor = db.cursor()

    # drop database if exists
    print "+ Apagando banco, se existir ..."
    cursor.execute("DROP DATABASE IF EXISTS urlRelations")
    db.commit()

    # create database
    print "+ Criando banco..."
    cursor.execute("CREATE DATABASE urlRelations;")
    db.commit()

    # set use of database
    print "+ Escolhendo banco..."
    cursor.execute("USE urlRelations;")
    db.commit()

    # create tables
    print "+ Criando tabelas..."
    cursor.execute("CREATE TABLE urls(origin varchar(100) not null," + 
                   " destination varchar(100), " + 
                   " summary text,"
                   "primary key (origin));")
    db.commit()
# def recreateDb()


# call the main
main()
