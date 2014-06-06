#!/usr/bin/env python
# -*- coding: utf-8 -*-

#
# IMPORTS
#
from math import sqrt
from musiclounge import models
from random import randint
from unicodedata import normalize

import Image
import pprint
import math
import os


#
# CONSTANTS AND DEFINITIONS
#
IMAGE_URL = 'musiclounge/static/images/'
MESSAGES = ["The real trouble with reality is that there's no background music.",
            "War doesn't determine who's right. War determines who's left.",
            "You can't be late until you show up.",
            "Knowledge is realizing that the street is one-way, wisdom is looking both directions anyway",
            "Keep smiling, it makes people wonder what you're up to.",
            "Borrow money from pessimists - they don't expect it back. ",
            "A conscience is what hurts when all your other parts feel so good. ",
            "Don't drink and drive you might spill your beer"]


#
# CODE
#
def addFriend(user, friend):
	"""
	This method implements the relation of friends between two users.

	@params user, friend: Primary keys of User table.
	@type user, friend: string

	@rtype: boolean
	@return: True, if success, false, if not.
	"""
	# check relationship
	rel = getRelationship(user, friend)

	if rel != "FRI" and rel != "ENE":
	
		#get user
		user = getUser(user)

		#get friend
		friend = getUser(friend)

		# create dbObject of friendship relation
		dbObj = models.Friendship(user=user, friend=friend)

		# save object in database
		dbObj.save()

	return True
# def addFriend()


def blockUser(user, blocked, reason):
	"""
	This method implements the blocking between two users.

	@params user, blocked: Primary keys of User table.
	@type user, login: string

	@rtype: boolean
	@return: True, if success, false, if not.
	"""
	# check relationship
	rel = getRelationship(user, blocked)

	# user was friends: remove it
	if rel == "FRI":

		# get the object and remove it from database
		dbObj = models.Friendship.objects.filter(user__login=user, 
			                                  friend__login=blocked)
		
		dbObj[0].delete()

	if rel != "ENE":
		
		#get user
		user = getUser(user)

		#get friend
		enemy = getUser(blocked)

		# insert the relation of blocking
		dbObj = models.Blocking(blocker=user, blocked=enemy)

		# save object in database
		dbObj.save()

		# get reason
		if reason == 'S':
			reason = 'Spammer'
		elif reason == 'A':
			reason = 'Abusive Content'
		elif reason == 'P':
			reason = 'Personal Reasons'

		# insert reason in database
		dbObj2 = models.BlockingReason(blocking=dbObj, reason=reason)

		# save object in database
		dbObj2.save()

	return True	
# def blockUser()


def checkAllreadyUser(login):
	"""
	This method check if the user identified by login is allready
	registered in Music Lounge

	@param login: The primary key of User table
	@type login: string

	@rtype: boolean
	@returns: True if user exists, false if not.
	"""
	# try to get the user from database
	user = models.User.objects.filter(login=login)
	
	# user exists: return true
	if user:
		return True

	# user doesn't exists: return false
	else:
		return False
# def checkAllreadyUser()


def createUser(data):
	"""
	This method insert a new user in database.

	@param data: New user's data to insert in database.
	@type data: Dictionary

	@rtype: boolean
	@returns: Create was sucessful, return True, else, False
	"""

	# name was sent, use it
	if 'name' in data and data['name']:
		name = data['name']
		firstName = data["name"].split(" ")
	
	# city was sent, use it
	if 'city' in data and data['city']:
		city = data['city']
	
	# login was sent, use it
	if 'login' in data and data['login']:
		login = data['login']
	
	# login wasn't sent: return False
	else:
		return False

	# create object
	dbObj = models.User(name=name, login=login, city=city, firstName=firstName[0])

	# save object in db
	dbObj.save()

	# save image
	size = 128, 128
	img = ""	
	
	if 'userImage' in data and data['userImage']:

		try:
			img = data['userImage']
			imgFile = open(IMAGE_URL+login+"_img", "w")
			imgFile.write(img.read())
			imgFile.close() 
			img = Image.open(IMAGE_URL+login+"_img")
		except:
			img = Image.open(IMAGE_URL+"generic.png")
	else:
		img = Image.open(IMAGE_URL+"generic.png")
	
	img.thumbnail(size, Image.ANTIALIAS)
	img.save(IMAGE_URL+login+"_img", "png")

	# return True
	return True
# def creatUser()


def dislikeMusicalAct(requester, musicalActId):
	"""
	This method remove the like information from database

	@param requester: primary key of user's table to requester
	@type requester: string

	@param musicalActId: Primary key of musical act's table
	@type musicalActId: string

	@rtype: boolean
	@returns: True
	"""
	# get the object from table
	dbObj = models.MusicalActRate.objects.get(musicalAct__id=musicalActId, user__login=requester)

	# delete object from database
	dbObj.delete()

	# return true
	return True
# def diskeMusicalAct()


def getEverybody():
	"""
	This method gets all the users registered in database.

	@rtype: list
	@returns: A list of all users
	"""
	# get users
	users = models.User.objects.all().order_by('login')
	
	# return users
	return users
# def getEverybody()


def getEveryMusicalActs():
	"""
	This method gets all musical acts registered in database;

	@rtype: list
	@returns: A list of all musical acts
	"""
	# get musical acts
	bandas = models.MusicalAct.objects.all().order_by('title')

	# return musical acts
	return bandas
# def getEveryMusicalActs()


def getKey(item):
	"""
	This method is used in list sort when each element of this list has two
	elements. Then, this method is called to sort method be executed on the
	second element of the list.
	"""
	return item[1]
# def getKey()


def getMusicalAct(id):
	"""
	This method get the musical act identified by it's id.

	@param id: The primary key of musical act
	@type id: Integer

	@rtype: db object / empty list
	@returns: Musical act object or a empty list
	"""
	# try to get musical act
	musicalAct = models.MusicalAct.objects.filter(id=id)
	
	# musical act exists: return it
	if musicalAct:
		return musicalAct[0]

	# musical act doesn't exists: return empty list
	else:
		return []
# def getMusicalAct():


def getMusicalActStatistics(id, matrix):
	"""
	This method get the statistics from an specific musical act represented
	by id.

	@param id: Primary key from musical act table
	@type id: string

	@rtype: dictionary
	@returns: A dictionary containing the statistics
	"""	
	# initialize list
	statistics = []

	# get all the likes
	likes = models.MusicalActRate.objects.filter(musicalAct__id=id)
	
	# get number of likes
	numberOfLikes = len(likes)
	statistics.append({"label": "Number Of Likes", "value": numberOfLikes})

	# get most similar musical act
	mostSimilar = getSimilarMusicalActs(id, matrix)[0]
	statistics.append({"label": "Most Similar Musical Act", "value": mostSimilar[0].title})

	rates = []
	for like in likes:
		rates.append(like.rate)

	# get the average rate 
	avgRate = round(float(sum(rates))/float(len(rates)), 2)
	statistics.append({"label": "Average Value of Rates", "value": avgRate})	

	# get the maximum rate
	maxRate = max(rates)
	statistics.append({"label": "Maximum Value of Rates", "value": maxRate})

	# get the minimum rate
	minRate = min(rates)
	statistics.append({"label": "Minimum Value of Rates", "value": minRate})

	# get the standard desviation
	sumPot = 0
	variancia = 0
	for rate in rates:
		sumPot += math.pow((rate-avgRate),2)
	variancy = round(float(sumPot)/float(len(rates)), 2)
	stdDevRates = round(float(math.sqrt(variancy)), 2)
	statistics.append({"label": "Standard Deviaton of Rates", "value": stdDevRates})

    # return the statistics
	return statistics
# def getMusicalActStatistics()


def getMusicalActSugestion(login, matrix):
	"""
	This method gets the musical act sugestion which is represented by a list,
	where each position represents a musical act and it's value represents the
	force of it's musical act based in user's 'musical taste'.

	@param login: The primary key of User table
	@type login: string

	@param matrix: The music act sugestion matrix
	@type: list

	@rtype: list
	@returns: A list containing the sugestion.
	"""
	# get the musical acts liked by user
	acts = getUserMusicalActs(login);

	# initiate variables
	sugestoes = {}
	resultado = []
	myActs = []
	lista = []
	erro = False
	
	# set zero for each element of lists
	for i in range(1, 356):
		sugestoes[str(i)] = 0
		resultado.append(0)
	
	# assign the id's musical acts liked by user to a list
	for act in acts:
		myActs.append(act.musicalAct_id)

	# get the 'force' of relation of each musical act with the matrix
	for act in acts:
		for j in range(1,356):
			if (matrix[str(act.musicalAct_id)][str(j)] > 1) and (j not in myActs):
				sugestoes[str(j)] += matrix[str(act.musicalAct_id)][str(j)]

	# build the sugestion list
	for i in range(1, 356):
		if sugestoes[str(i)] != 0:
			lista.append([i, sugestoes[str(i)]])
	

	# sort the sugestion list to show the most relevant
	lista = sorted(lista, key=getKey, reverse=True)

	# return the sugestion
	return lista
# def getMusicalActSugestion()


def getMusicalActSugestionMatrix():
	"""
	This method builds the matrix of musical act sugestion based on
	colaborative ranking algorithm used by Amazon.

	Algorithm:

		For each musical act X in musical acts:
			For each user that liked the musical act X:
				For each musical act Y liked by user:
					If X != Y:
						Increment MATRIX[X][Y]
		return MATRIX

	This algorithm returns a matrix that has the relation of all 
	musical act registered in database. Everytime that an user likes
	a musical act X and Y, MATRIX[X][Y] is incremented.

	"""
	# initialize variables
	matrix = {}		
	matrix2 = {}

	# get all musical acts
	allMusicalActs = models.MusicalAct.objects.all()
	
	# assign zero to all elements of matrix
	for i in range(1, 356):
		matrix2 = {}
		for j in range(1, 356):
			matrix2[str(j)] = 0
		matrix[str(i)] = matrix2

	# for each act in all musical acts
	for act in allMusicalActs:

		# get users that like the act
		usersThatLike = models.MusicalActRate.objects.filter(musicalAct__id=act.id, rate__gt=3)

		# for each user that like the act
		for user in usersThatLike:

			# get the user's musical acts
			userActs = getUserMusicalActs(user.user_id)

			# for each act like by user
			for uAct in userActs:

				# musical act row != musical act column
				if uAct.musicalAct_id != act.id:

					# increment the musical act position in matrix
					matrix[str(act.id)][str(uAct.musicalAct_id)] += 1

	# return matrix
	return matrix
# def getMusicalActSugestionMatrix()


def getRelationship(requester, user):
	"""
	This method checks if requester and user are friends, enemies or just
	don't have any relationship.

	@param requester, user: Primary keys of User tables
	@type requester, user: string

	@rype: string
	@retuns: the tags FRI (friends), ENE (enemies), NOT (nothing)
	"""
	# not enemies nor friends: return NOT
	response = "NOT"

	# get friends of requester
	friends = getUserFriends(requester)

	# check if user is friend
	for friend in friends:

		if friend.friend.login == user:

			response = "FRI"

	# get enemies of requester
	enemies = getUserEnemies(requester)

	# check if user is enemy
	for enemy in enemies:

		if enemy.blocked.login == user:

			response = "ENE"

	# return relationship
	return response
# def getRelationship()
	

def getSimilarity(vec1, vec2):
	"""
	This method calculates the cosine similarity between two vectors.

	@param vec1: vector 1
	@type vec1: list

	@param vec2: vector 2
	@type vec2: list

	@rtype: float
	@returns: the cosine similarity between vec1 e vec2
	"""
	# initialize variables
	soma1=0
	soma2=0
	soma3=0

	# apply the cosine similarity algorithm
	for i in range(0, len(vec1)):
		a = vec1[i] + 1
		b = vec2[i] + 1
		soma1 += a*b
		soma2 += a*a
		soma3 += b*b

	numerador = soma1
	denominador = math.sqrt(soma2) * math.sqrt(soma3)
	resultado = 0
	if denominador != 0:
		resultado = numerador/denominador

	# return the similarity
	return resultado
# def def getSimilarity()


def getSimilarMusicalActs(musicalActId, matrix):
	"""
	This method gets the 10 similarest musical acts of a musical act
	represented by musicalActId.

	@param musicalActId: Primary key from muscal act table
	@type musicalActId: string

	@param matrix: recomendation matrix
	@type matrix: dictionary

	@rtype: list
	@returns: a list with the top 10 similarest musical acts.
	"""
	# get list of musical acts from matrix
	similarList = []
	for i in range(1, 356):
		musicalAct = getMusicalAct(i)
		similarList.append((musicalAct, int(matrix[str(musicalActId)][str(i)])))

	# sort list
	topTen = sorted(similarList, key=getKey, reverse=True)

	# return the top 10
	return topTen[0:10]
# def getSimilarMusicalActs()


def getTopTenMusicalActs():
	"""
	This method get the top 10 musical acts in musiclounge.

	@rtype: list
	@returns: the list with the 10 most liked musical acts.
	"""
	# initialize list
	topTen = []

	# get the likes
	for i in range(1, 356):
		likes = len(models.MusicalActRate.objects.filter(musicalAct__id=i))
		topTen.append((i, likes))

	# sort list
	topTen = sorted(topTen, key=getKey, reverse=True)

	# return the list
	return topTen[0:10]
# def getTopTenMusicalActs()


def getUser(login):
	"""
	This method get the user identified by login.

	@param login: The primary key of User's table.
	@type login: string

	@rtype: User's object 
	@returns: The object from User's table
	"""
	#get user
	user = models.User.objects.filter(login=login)

	#user exists: return it
	if user:
		return user[0]

	# user doesn't exists: return nothing
	else:
		return None
# def getUser()


def getUserEnemies(login):
	"""
	This method gets all users which was blocked by the user identified by login
	
	@param login: The primary key of User table
	@type login: string	

	@rtype: list
	@returns: A list of all enemies
	"""
	# get enemies
	enemies = models.Blocking.objects.filter(blocker=login)

	# return enemies
	return enemies
# def getUserEnemies()


def getUserFriends(login):
	"""
	This method gets user's friends from database

	@param login: The primary key of User table
	@type login: string

	@rtype: list
	@returns: A list of all friends
	"""
	# get friends
	friends = models.Friendship.objects.filter(user__login=login).order_by('friend')

	# return list
	return friends
# def getUserFriends()


def getUserFriendsSugestion(login, cache):
	"""
	This method get the user's friends sugestion. It's based on the
	the concept of cosine similarity between two musical act sugestion.
	The closer the result is 1, the more similar are the users.

	@param login: The primary key of User table
	@type login: string

	@param cache: This param contains the cached information, where the 
	matrix of sugestion was archived. This is needed to improve performance
	to Music Lounge
	@type cache: 

	@rtype: list
	@returns: The list containing the friends sugestion
	"""
	# initialize variables
	vectorList = []
	similaridade = []
	listFriendsLogin = []
	listEnemiesLogin = []	
	vector1 = []
	vector2 = []
	for i in range(0, 366):
		vector1.append(1)
		vector2.append(1)

	# get the user's music sugestion 
	myMusicVector = getMusicalActSugestion(login, cache['matrix'])
	
	# get the user's friends
	myFriends = getUserFriends(login)
	
	# get the user's enemies
	myEnemies = getUserEnemies(login)

	# build the list of user's friends to not include them in recomendation
	for friend in myFriends:
		listFriendsLogin.append(friend.friend.login)

	# build the list of user's enemies to not include them in recomendation
	for enemy in myEnemies:
		listEnemiesLogin.append(enemy.blocked.login)

	# get all users
	everybody = getEverybody()

	# for each user registered:
	for user in everybody:

		# user doesn't a friend or enemy or himself
		if user.login not in listFriendsLogin and user.login not in listEnemiesLogin and user.login != login :

			# musical act sugestion was made: use it
			if (str(user.login)+"_vetorMusical") in cache:

				vector = cache[str(user.login)+"_vetorMusical"]

			# musical act sugestion was made: make it
			else:
				vector = getMusicalActSugestion(user.login, cache['matrix'])
			
			# build the vectors to be compared
			for element in myMusicVector:
				vector1[int(element[0])] = int(element[1])

			for element in vector:
				vector2[int(element[0])] = int(element[1])

			# calculate the cosine similarity
			sim = getSimilarity(vector1, vector2)

			# build the response
			similaridade.append({"login": user.login, 
				                 "firstName": user.firstName,
				                 "compatibilidade": sim})

	# sort the response
	similaridade = sorted(similaridade, reverse=True)[0:10]

	# return friends sugestion
	return similaridade
# def getUserFriendsSugestion()


def getUserMessage(login):
	"""
	This method generates messages to show in user's home view  based
	on it's behavior in Music Lounge.

	@param login: Primary key of user's table
	@type login: string

	@rtype: Dictionary
	@returns: A Dictionary containing the message and it's type.
	"""
	# get all users
	allUsers = models.User.objects.all()

	# try to get blocking reasons:
	blockings = models.BlockingReason.objects.filter(blocking__blocked__login=login)

	# get blockings by allUsers
	percentage = round(float(len(blockings))/float(len(allUsers)), 2)

	# instantiate the reason list
	reasonList = []

	# there is blockings: store it's reasons
	if blockings:
		for blocking in blockings:
			reasonList.append(blocking.reason)

	# get the count of reasons
	s = 0
	a = 0
	p = 0
	
	if reasonList:
		s = reasonList.count("Spammer")
		a = reasonList.count("Abusive Content")
		p = reasonList.count("Personal Reasons")

	message = {}

	# select the message based on blocking reasons or ramdomic choose one
	if (percentage > 0.3):
		if (s>a) and (s>p) :
			message["text"] = "Take care with sending spams!!! Many people may not be pleased with that !"
			message["type"] = "warning"
		elif (a>s) and (a>p):
			message["text"] = "Take care with what you post here !!! Be respectful with your Music Lounge Mates!"
			message["type"] = "warning"
		elif (p>a) and (p>s):		
			message["text"] = "Be nice with your Music Lounge Mates!!! They're here to enjoy too !"
			message["type"] = "warning"
	else:
		index = randint(0, len(MESSAGES)-1)
		message["text"] = MESSAGES[index]
		message["type"] = "cool"

	# return the message dicts
	return message


def getUserMusicalActs(login):
	"""
	This method gets the musical acts chosen by the user identified by login.

	@param login: The primary key of User table
	@type login: string	

	@rtype: list
	@returns: A list of all musical acts
	"""
	# get musical acts liked by the user
	musicalActs = models.MusicalActRate.objects.filter(user__login=login).order_by('musicalAct')

	# return musicalActs
	return musicalActs
# def getUserMusicalActs()


def getUserStatistics(requester):
	"""
	This method calculate severous statistics from user.

	@param requester: primary key of user's table to requester
	@type requester: string

	@rtype: Dictionary
	@returns: Dictionary containing the calculated statistics
	"""
	# initialize variable
	statistics = []

	# get user data
	user = models.User.objects.get(login=requester)
	#statistics.append({"label": "User", "value": user})

	# get number of friends
	numberOfFriends = len(models.Friendship.objects.filter(user__login=requester))
	statistics.append({"label": "Number Of Friends", "value":numberOfFriends, "free" : True})

	# get number of users
	numberOfUsers = len(models.User.objects.all())
	statistics.append({"label": "Number of Users", "value":numberOfUsers, "free" : True})

	# get percentual of users that are friends
	percentualFriendsUser = round(float(numberOfFriends)/float(numberOfUsers)*100, 2)
	statistics.append({"label": "Percentage of Users Who Are Friends (%)", "value": percentualFriendsUser, "free" : True})

	# get friends that are from user's city
	friendsFromCity = len(models.Friendship.objects.filter(user__login=requester, 
		                                                   user__city=user.city))
	statistics.append({"label":"Friends From Same City", "value": friendsFromCity, "free" : True})


	# get number of musical acts liked
	numberOfMusicalActsLiked = len(models.MusicalActRate.objects.filter(user__login=requester))
	statistics.append({"label":"Number Of Liked Musical Acts", "value":numberOfMusicalActsLiked, "free" : True})

	# get all musical acts
	numberOfMusicalActs = len(models.MusicalAct.objects.all())
	statistics.append({"label":"Number Of Musical Acts", "value":numberOfMusicalActs, "free" : True})

	# get percentual of musical acts liked
	percentualMusicalActUser = round(float(numberOfMusicalActsLiked)/float(numberOfMusicalActs)*100, 2)
	statistics.append({"label":"Percentage of Musical Acts That I Liked (%)", "value":percentualMusicalActUser, "free" : True})

	# get number of people that you blocked
	numberOfMyEnemies = len(models.Blocking.objects.filter(blocker__login=requester))
	statistics.append({"label":"Number Of Blocked Users", "value": numberOfMyEnemies, "free" : False})

	# get percentual of enemies
	percentualEnemiesUser = round(float(numberOfMyEnemies)/float(numberOfUsers)*100, 2)
	statistics.append({"label":"Percentage of Users That I Blocked (%)", "value": percentualEnemiesUser, "free" : False})

	# get reasons
	allMyBlockingReasons = models.BlockingReason.objects.filter(blocking__blocker__login=requester)

	# get number of each my reasons
	reasonS = 0
	reasonA = 0
	reasonP = 0
	for blocking in allMyBlockingReasons:
		if blocking.reason == "Spammer":
			reasonS += 1
		elif blocking.reason == "Abusive Content":
			reasonA += 1
		elif blocking.reason == "Personal Reasons":
			reasonP += 1
	statistics.append({"id": "my", "label": "Spammer", "value":reasonS, "free" : False})
	statistics.append({"id": "my", "label": "Abusive Content", "value":reasonA, "free" : False})
	statistics.append({"id": "my", "label": "Personal Reasons", "value":reasonP, "free" : False})

	# get number of people that blocked you
	numberOfIdiots = len(models.Blocking.objects.filter(blocked__login=requester))
	statistics.append({"label":"Number Of Users Who Blocked Me", "value":numberOfIdiots, "free" : False})

	# get percentual of idiots
	percentualIdiotsUser = round(float(numberOfIdiots)/float(numberOfUsers)*100, 2)
	statistics.append({"label":"Percentage of Users That Blocked Me (%)", "value": percentualIdiotsUser, "free" : False})

	# get their reasons
	allTheirBlockingReasons = models.BlockingReason.objects.filter(blocking__blocked__login=requester)

	# get number of each their reasons
	reasonS = 0
	reasonA = 0
	reasonP = 0
	for blocking in allTheirBlockingReasons:
		if blocking.reason == "Spammer":
			reasonS += 1
		elif blocking.reason == "Abusive Content":
			reasonA += 1
		elif blocking.reason == "Personal Reasons":
			reasonP += 1

	statistics.append({"id": "their", "label": "Spammer", "value":reasonS, "free" : False})
	statistics.append({"id": "their", "label": "Abusive Content", "value":reasonA, "free" : False})
	statistics.append({"id": "their", "label": "Personal Reasons", "value":reasonP, "free" : False})

	return statistics
# def getUserStatistics()


def likeMusicalAct(requester, musicalActId, rate):
	"""
	This method send to database the information that the requester likes
	the musical act and set it a rate value.

	@param requester: primary key of user's table to requester
	@type requester: string

	@param musicalActId: Primary key of musical act's table
	@type musicalActId: string

	@param rate: the value (0 to 5) attributed by user to musical act
	@type rate: Integer

	@rtype: boolean
	@returns: True
	"""
	# get musical act
	musicalAct = getMusicalAct(musicalActId)

	# get user from requester
	user = getUser(requester)

	# build the object to MusicalActRate table
	dbObj = models.MusicalActRate(musicalAct=musicalAct, user=user, rate=rate)

	# save object in database
	dbObj.save()

	# return true
	return True
# def likeMusicalAct()


def updateUser(data):
	"""
	This method update a user in database.

	@param data: Data to update user in database
	@type data: Dictionary

	@rtype: boolean
	@returns: Update was sucessful, return True, else, False
	"""

	# name was sent, use it
	if 'name' in data and data['name']:
		name = data['name']
		firstName = data["name"].split(" ")
	
	# city was sent, use it
	if 'city' in data and data['city']:
		city = data['city']
	
	# login was sent, use it
	if 'login' in data and data['login']:
		login = data['login']
	
	# login wasn't sent: return False
	else:
		return False

	# create object
	dbObj = models.User.objects.get(login=login)
	dbObj.name = name
	dbObj.firstName = firstName[0]
	dbObj.city = city

	# save object in db
	dbObj.save()

	# save image
	size = 128, 128
	img = ""	
	
	if 'userImage' in data and data['userImage']:
		try:
			img = data['userImage']
			imgFile = open(IMAGE_URL+login+"_img", "w")
			imgFile.write(img.read())
			imgFile.close() 
			img = Image.open(IMAGE_URL+login+"_img")
		except:
			img = Image.open(IMAGE_URL+"generic.png")
	else:
		img = Image.open(IMAGE_URL+"generic.png")
	
	img.thumbnail(size, Image.ANTIALIAS)
	img.save(IMAGE_URL+login+"_img", "png")

	# return True
	return True
# def updateUser()
	

def unblockUser(user, blocked):
	"""
	This method implements the unblocking between two users.

	@params user, blocked: Primary keys of User table.
	@type user, login: string

	@rtype: boolean
	@return: True, if success, false, if not.
	"""
	# check relationship
	rel = getRelationship(user, blocked)

	# if they're enemies: delete this relation
	if rel == "ENE":
		
		# get the relation of blocking
		dbObj = models.Blocking.objects.get(blocker=user, blocked=blocked)

		# get the blocking
		blocking = models.Blocking.objects.filter(blocker=user, blocked=blocked)

		# get the reason of blocking
		dbObj2 = models.BlockingReason.objects.get(blocking=blocking)
		
		# delete objects in database
		dbObj.delete()
		dbObj2.delete()

	return True	
# def unblockUser()