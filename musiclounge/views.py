#!/usr/bin/python
# -*- coding: utf-8 -*-


#
# IMPORTS
#
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.core.urlresolvers import reverse
from django.views.decorators.http import require_http_methods
from musiclounge import api
from musiclounge import forms


#
# CODE
#
def musicalAct(request, id):
	"""
	This method implements the view which shows up informations about
	musical act represented by id.

	@param id: The primary key of musicalAct model.  
	@type id: string

	@param request: The http request to view
	@type request: django.http.response.HttpResponse

	@returns: A http response 
	@rtype: django.http.response.HttpResponse
	"""
	# assign context
	context = {}

	# build the response
	response = render(request, 'home.html', context)
	
	# return the response
	return response


def home(request, login):
	"""
	This method implements the view of user's home identified
	by login.

	@param request: The http request to view
	@type request: django.http.response.HttpResponse

	@param login: User's primary key
	@type login: string

	@returns: A http response 
	@rtype: django.http.response.HttpResponse
	"""	

	# insert login in context
	context = {'login': login}

	# initialize lists
	musicalActSugestion = []
	musicalActSugestionComplete = []
	musicalActs = []
	friends = []
	friendSugestion = []

	# admin wants to login: show everything
	if login == 'admin':

		# assign admin boolean variable
		context['admin'] = True

		# get everybody
		friends = api.getEverybody()

		# get all musical acts
		musicalActs = api.getEveryMusicalActs()

	# ordinary user login: get it's data
	else:

		# get user's friends
		friends = api.getUserFriends(login)

		# get user's musical acts
		musicalActs = api.getUserMusicalActs(login)

		# sugestion matrix was allready calculated: use it
		if 'matrix' in request.session:
			musicalActSugestion = api.getMusicalActSugestion(login, request.session['matrix'])
			friendSugestion = api.getUserFriendsSugestion(login, request.session)

		# sugestion matrix wasn't calculated: calculate it
		else:

			# get sugestion matrix
			matrix = api.getMusicalActSugestionMatrix()

			# assign this matrix to cache
			request.session["matrix"] = matrix

			# get user's music sugestion 
			musicalActSugestion = api.getMusicalActSugestion(login, request.session['matrix'])
			
			# get user's friends sugestion 
			friendSugestion = api.getUserFriendsSugestion(login, request.session)

	# user have friends: assign it to context
	if friends:
		context['friends'] = friends

	# user have musical acts: assign it to context
	if musicalActs:
		context['musicalActs'] = musicalActs

	# user have music sugestion: assign it to context
	if musicalActSugestion:

		# assign the sugestion list to cache
		request.session[str(login)+"_musicalActList"] = musicalActSugestion

		# there's more than 10 musical acts: limit it
		if len(musicalActSugestion) > 10:

			for i in range(0, 10):

				# get the musical act through it's id
				act = api.getMusicalAct(musicalActSugestion[i][0])

				# build the response dictionary
				sugestionDict = {"musicalAct": act,
				        		 "rate": musicalActSugestion[i][1]}

				# insert dict in list
				musicalActSugestionComplete.append(sugestionDict)
		
		# there's less than 10 musical acts: send all of them
		else:

			for sugestion in musicalActSugestion:
				
				ato = api.getMusicalAct(sugestion[0])
				nota = {"banda": ato,
				        "nota": sugestion[1]}
				musicalActSugestionComplete.append(nota)

		# insert the sugestion in context
		context['musicalActSugestion'] = musicalActSugestionComplete

	# user have friends sugestion: assignt it to context
	if friendSugestion:

		# assign the list to cache
		request.session[str(login)+"_vetorFrieds"] = friendSugestion

		# insert sugestion to context
		context['friendSugestion'] = friendSugestion
	
	# build the http response 
	response = render(request, 'home.html', context)

	# return response
	return response


def index(request):
	"""
	This method implements the view of index.

	@param request: The http request to view
	@type request: django.http.response.HttpResponse

	@returns: A http response 
	@rtype: django.http.response.HttpResponse
	"""	
	# calculate sugestion matrix to improve performance to Music Lounge
	matrix = api.getMusicalActSugestionMatrix()

	# assign the matrix to cache
	request.session["matrix"] = matrix

	# set expiration time to cache
	request.session.set_expiry(3600)

	# return http response
	return render(request, 'index.html', {})


def login(request):
	"""
	This method implements the view of login page.

	@param request: The http request to view
	@type request: django.http.response.HttpResponse

	@returns: A http response 
	@rtype: django.http.response.HttpResponse
	"""	
	# get the form object
	form = forms.Login()

	# assign form to context
	context =  {'form': form}
	
	# data was sent: get the posted data
	if request.method == 'POST': 

		# assign the data posted to the form object
		form = forms.Login(request.POST)

		# data sent is valid: work on it
		if form.is_valid(): 

			# get login
			login = form.cleaned_data['login']

			# check if user exists
			check = api.checkAllreadyUser(login)

			# user exists: redirect him to home
			if check:

				# build the response
				response = HttpResponseRedirect(reverse('musiclounge:home', 
								kwargs={'login': login}))

			# user doesn't exist: show error message
			else:

				# assign form and error message to context
				context =  {'form': form, 'error_message': 'Usuario inexistente'}

				# build the response
				response = render(request, 'login.html', context)				

		# data sent isn't valid: show error message
		else:

			# assign form and error message to context
			context =  {'form': form, 'error_message': 'Entrada inválida'}	
			
			# build the response
			response = render(request, 'login.html', context)
	else:

		# build the response
		response = render(request, 'login.html', context)

	# return the response
	return response


def registration(request):
	"""
	This method implements the view that new users will realize
	the registration in Music Lounge

	@param request: The http request to view
	@type request: django.http.response.HttpResponse

	@returns: A http response 
	@rtype: django.http.response.HttpResponse
	"""	

	print request.FILES

	# get the form object
	form = forms.User()

	# assign form object to context
	context =  {'form': form}

	# data was sent: get the data posted
	if request.method == 'POST': 

		# assign the post to the form object
		form = forms.User(request.POST, request.FILES)

		# data sent is valid: work on it
		if form.is_valid():

			# check if user allready exists
			check = api.checkAllreadyUser(form.cleaned_data['login'])

			# user exists: return a message informing it
			if check:

				# add error message to the context
				context = {'form': form, 'error_message': 'Usuario existente'}

				# build the http response
				response = render(request, 'signin.html', context)

			# user doesn't exist: create user and redirect to home
			else:

				# create user
				api.createUser(form.cleaned_data)

				# build the http response redirecting to home
				response = HttpResponseRedirect(reverse('musiclounge:home', 
				       		kwargs={'login': form.cleaned_data['login']}))

		# data sent is invalid: return error message
		else:

			# build the context with error message
			context = {'form': form, 'error_message': 'Preenchimento incorreto'}

			# build the http response redirecting to registration page
			response = render(request, 'signin.html', context)
	
	# nothing was sent: show the registration page
	else:

		# build the http response
		response = render(request, 'signin.html', context)

	# return the http response
	return response


def user(request, id):
	"""
	This method implements the view of user info page identified by id.

	@param request: The http request to view
	@type request: django.http.response.HttpResponse

	@returns: A http response 
	@rtype: django.http.response.HttpResponse
	"""	
	# assign context
	context = {}
	
	# get user's friends
	friends = api.getUserFriends(id)

	# get user's musical acts
	musicalActs = api.getUserMusicalActs(id)

	# user has frieds: assign it to context
	if friends:
		context['friends'] = friends

	# user has musical acts: assign it to context
	if musicalActs:
		context['musicalActs'] = musicalActs

	# build the response
	response = render(request, 'profile.html', context)

	# return the response
	return response

