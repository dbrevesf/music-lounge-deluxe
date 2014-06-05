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


	# get user data
	user = api.getUser(login)

	# user exists: assign it
	if user:

		# format data to send to form
		data = {}
		data["name"] = user.name
		data["login"] = user.login
		data["city"] = user.city

		# create form
		form = forms.User(data)

		# block login field
		form.fields['login'].widget.attrs['readonly'] = True 

		# assign form to context
		context["userForm"] = form
		context["user"] = user		
	
	# get user message
	message = api.getUserMessage(login)

	# message is ready: assign it in context
	if message:
		context["message"] = message

	# build the http response 
	response = render(request, 'home.html', context)

	# return response
	return response
# def home()


def index(request):
	"""
	This method implements the view of index.

	@param request: The http request to view
	@type request: django.http.response.HttpResponse

	@returns: A http response 
	@rtype: django.http.response.HttpResponse
	"""	
	# User is logged: redirect him to his home
	if 'userLogin' in request.session:
		response = HttpResponseRedirect(reverse('musiclounge:home', 
				       		kwargs={'login': request.session['userLogin']}))
		return response

	else:	
		# calculate sugestion matrix to improve performance to Music Lounge
		matrix = api.getMusicalActSugestionMatrix()

		# assign the matrix to cache
		request.session["matrix"] = matrix

		# set expiration time to cache
		request.session.set_expiry(3600)

		# return http response
		return render(request, 'index.html', {})
# def index()


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

				# assign user id to session variable
				request.session["userLogin"] = login

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
# def login()


def logout(request):
	"""
	This method implements the logout function of Music Lounge. Besides 
	leaving, he also clears the cache.
	"""
	# get user which is loggin out
	user = request.session["userLogin"]

	# clean the cache
	request.session.flush()

	# assign context
	context = {"user": user}

	# build the response
	response = render(request, 'logout.html', context)
	
	# return the response
	return response
# def logout()


def managerRelationship(request, user):
	"""
	This method implements the all the management of relationships
	between two users.

	@param blocked: The user's login which the relationship will be executed
	@type blocked: string

	@param request: The http request to view
	@type request: django.http.response.HttpResponse

	@returns: A http response 
	@rtype: django.http.response.HttpResponse
	"""
	
	# get requester
	requester = request.session["userLogin"]

	# button was pressed: deal with it
	if "button" in request.POST:

		# requester wants to add user as a friend: add him
		if request.POST["button"] == "Add User":
			api.addFriend(requester, user)

		# requester wants to block user: block him
		if request.POST["button"] == "Block User":
			api.blockUser(requester, user, request.POST["reason"][0])

		# requester wants to unblock user: unblock him
		if request.POST["button"] == "Unblock User":
			api.unblockUser(requester, user)

	# build the http response redirecting to home
	response = HttpResponseRedirect(reverse('musiclounge:user', 
	       		kwargs={'login': user}))

	return response
# def managerRelationship()


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
	context = {"requester": request.session["userLogin"]}

	# get the musical act
	musicalAct = api.getMusicalAct(id)

	# assign musical act to context
	if musicalAct:
		
		# format data to send to form
		data = {}
		data['title'] = musicalAct.title
		data['uri'] = musicalAct.uri
		data['country'] = musicalAct.country
		data['genre'] = musicalAct.genre
		data['summary'] = musicalAct.summary

		# create form
		musicalActForm = forms.MusicalAct(data)

		# user isn't admin: block the fields
		if request.session["userLogin"] != "admin":
			musicalActForm.fields['title'].widget.attrs['readonly'] = True 
			musicalActForm.fields['uri'].widget.attrs['readonly'] = True 
			musicalActForm.fields['country'].widget.attrs['readonly'] = True 
			musicalActForm.fields['genre'].widget.attrs['readonly'] = True 
			musicalActForm.fields['summary'].widget.attrs['readonly'] = True 
			musicalActForm.fields['title'].widget.attrs['placeholder'] = "Not informed" 
			musicalActForm.fields['uri'].widget.attrs['placeholder'] = "Not informed"  
			musicalActForm.fields['country'].widget.attrs['placeholder'] = "Not informed"  
			musicalActForm.fields['genre'].widget.attrs['placeholder'] = "Not informed" 
			musicalActForm.fields['summary'].widget.attrs['placeholder'] = "Not informed" 

		# assign to context
		context['musicalAct'] = musicalAct
		context['musicalActForm'] = musicalActForm

	# build the response
	response = render(request, 'musicalact.html', context)
	
	# return the response
	return response
# def musicalAct()


def registration(request):
	"""
	This method implements the view that new users will realize
	the registration in Music Lounge

	@param request: The http request to view
	@type request: django.http.response.HttpResponse

	@returns: A http response 
	@rtype: django.http.response.HttpResponse
	"""	

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
				response = render(request, 'signup.html', context)

			# user doesn't exist: create user and redirect to home
			else:

				# get image 	
				if 'image' in request.FILES:				
				 	form.cleaned_data['userImage'] = request.FILES['image']

				# create user
				api.createUser(form.cleaned_data)

				# set login to cache
				request.session["userLogin"] = form.cleaned_data['login']

				# build the http response redirecting to home
				response = HttpResponseRedirect(reverse('musiclounge:home', 
				       		kwargs={'login': form.cleaned_data['login']}))

		# data sent is invalid: return error message
		else:

			# build the context with error message
			context = {'form': form, 'error_message': 'Preenchimento incorreto'}

			# build the http response redirecting to registration page
			response = render(request, 'signup.html', context)
	
	# nothing was sent: show the registration page
	else:

		# build the http response
		response = render(request, 'signup.html', context)

	# return the http response
	return response
# def registration()


def updateUser(request):
	"""
	This method implements the user's update function.

	@param request: The http request to view
	@type request: django.http.response.HttpResponse

	@returns: A http response 
	@rtype: django.http.response.HttpResponse
	"""
	
	# initialize context
	context = {}

	if request.method == "POST":

		# assign the post to the form object
		userForm = forms.User(request.POST, request.FILES)

		# data sent is valid: work on it
		if userForm.is_valid():

			# get image 	
			if 'image' in request.FILES:				
			 	userForm.cleaned_data['userImage'] = request.FILES['image']

			# create user
			api.updateUser(userForm.cleaned_data)


			# build the http response redirecting to home
			response = HttpResponseRedirect(reverse('musiclounge:home', 
			       		kwargs={'login': userForm.cleaned_data['login']}))

	else:

		response = HttpResponseRedirect(reverse('musiclounge:home', 
			       		kwargs={'login': request.session['userLogin']}))
	# return the response
	return response
# def updateUser() 


def user(request, login):
	"""
	This method implements the view of user info page identified by id.

	@param request: The http request to view
	@type request: django.http.response.HttpResponse

	@returns: A http response 
	@rtype: django.http.response.HttpResponse
	"""	
	# get requester
	requester = request.session["userLogin"]

	# assign context
	context = {"requester": requester}

	# get user profile
	user = api.getUser(login)

	# get user's friends
	friends = api.getUserFriends(login)

	# get user's musical acts
	musicalActs = api.getUserMusicalActs(login)

	# profile existis: assign it to contex
	if user:
		context['user'] = user

	# user has frieds: assign it to context
	if friends:
		context['friends'] = friends

	# user has musical acts: assign it to context
	if musicalActs:
		context['musicalActs'] = musicalActs


	# format data to send to form
	data = {}
	data["name"] = user.name
	data["login"] = user.login
	data["city"] = user.city

	# create form
	form = forms.User(data)

	# disable forms
	form.fields['name'].widget.attrs['readonly'] = True 
	form.fields['login'].widget.attrs['readonly'] = True 
	form.fields['city'].widget.attrs['readonly'] = True 

	# assign form to context
	context["form"] = form

	# check if user and requester are friends
	relationship = api.getRelationship(requester, user.login)

	# assign to context
	context["relationship"] = relationship

	# get form to blocking
	blockForm = forms.BlockingReason()

	# assign to context
	context["blockForm"] = blockForm

	# build the response
	response = render(request, 'profile.html', context)

	# return the response
	return response
# def user()
