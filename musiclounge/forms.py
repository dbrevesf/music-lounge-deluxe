#!/usr/bin/python
# -*- coding: utf-8 -*-

from django import forms as dforms
from musiclounge import models


class User(dforms.Form):
	name =  dforms.CharField(widget=dforms.TextInput(attrs={'class' : 'form-control',
		                                                   'placeholder': 'Enter your name'}))
	login = dforms.CharField(widget=dforms.TextInput(attrs={'class' : 'form-control',
		                                                   'placeholder': 'Enter your login'}))
	city = dforms.CharField(widget=dforms.TextInput(attrs={'class' : 'form-control',
		                                                   'placeholder': 'Enter your city'}))
	userImage = dforms.ImageField(required=False)


class Login(dforms.Form):
	login = dforms.CharField(widget=dforms.TextInput(attrs={'class' : 'form-control',
		                                                   'placeholder': 'Enter your Login'}))


class MusicalAct(dforms.Form): 
	title =  dforms.CharField(max_length=255)
	uri =  dforms.CharField(max_length=255)
	country =  dforms.CharField(max_length=255)
	genre =  dforms.CharField(max_length=255)


class Musician(dforms.Form):
	name = dforms.CharField(max_length=255)
	genre = dforms.CharField(max_length=255)
	birthdate = dforms.DateField()
	musicalAct = dforms.ModelMultipleChoiceField(queryset=models.MusicalAct.objects.all())


class Blocking(dforms.Form):	
	blocked = dforms.ModelMultipleChoiceField(queryset=models.User.objects.all())
	

class Friendship(dforms.Form):
	friend = dforms.ModelMultipleChoiceField(queryset=models.User.objects.all())


class MusicalActRate(dforms.Form):
	atomusical = dforms.ModelMultipleChoiceField(queryset=models.MusicalAct.objects.all())
	nota = dforms.IntegerField()


class BlockingReason(dforms.Form):
	REASONS = ((u'1', u'spammer'),
			  (u'2', u'conteúdo abusivo'),
			  (u'3', u'motivos pessoais'),
			  (u'4', u'outras'))

	reason = dforms.ModelMultipleChoiceField(queryset=REASONS)




