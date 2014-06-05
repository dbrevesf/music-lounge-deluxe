#!/usr/bin/python
# -*- coding: utf-8 -*-

from django import forms as dforms
from musiclounge import models


class User(dforms.Form):
	name =  dforms.CharField(widget=dforms.TextInput(attrs={'class' : 'form-control',
		                                                   'placeholder': 'Enter your name'}), label='Name: ')
	login = dforms.CharField(widget=dforms.TextInput(attrs={'class' : 'form-control',
		                                                   'placeholder': 'Enter your login'}), label='Login: ')
	city = dforms.CharField(widget=dforms.TextInput(attrs={'class' : 'form-control',
		                                                   'placeholder': 'Enter your city'}), required=False, label='City: ')
	userImage = dforms.ImageField(required=False)


class Login(dforms.Form):
	login = dforms.CharField(widget=dforms.TextInput(attrs={'class' : 'form-control',
		                                                   'placeholder': 'Enter your Login'}), label='Login: ')


class MusicalAct(dforms.Form): 
	title =  dforms.CharField(widget=dforms.TextInput(attrs={'class' : 'form-control',
		                                                   'placeholder': 'Enter the title'}), label='Name: ')
	uri =  dforms.CharField(widget=dforms.TextInput(attrs={'class' : 'form-control',
		                                                   'placeholder': 'Enter the URI'}), label='URI: ')
	country =  dforms.CharField(widget=dforms.TextInput(attrs={'class' : 'form-control',
		                                                   'placeholder': 'Enter the country'}), label='Country: ')
	genre =  dforms.CharField(widget=dforms.TextInput(attrs={'class' : 'form-control',
		                                                   'placeholder': 'Enter the genre'}), label='Genre: ')
	summary = dforms.CharField(widget=dforms.Textarea(attrs={'class' : 'form-control',
		                                                     'placeholder': 'Enter the summary',
		                                                     'rows': 10,
                              								 'cols': 160}), label='Summary: ')


class Musician(dforms.Form):
	name = dforms.CharField(max_length=255, label='Name: ')
	genre = dforms.CharField(max_length=255, label='Genre: ')
	birthdate = dforms.DateField(label='Birth Date: ')
	musicalAct = dforms.ModelMultipleChoiceField(label='Musical Acts: ', queryset=models.MusicalAct.objects.all())


class Blocking(dforms.Form):	
	blocked = dforms.ModelMultipleChoiceField(queryset=models.User.objects.all(), label='Users: ')
	

class Friendship(dforms.Form):
	friend = dforms.ModelMultipleChoiceField(queryset=models.User.objects.all(), label='Users: ')


class MusicalActRate(dforms.Form):
	atomusical = dforms.ModelMultipleChoiceField(queryset=models.MusicalAct.objects.all(), label='Musical Acts: ')
	nota = dforms.IntegerField(label='Rate: ')


class BlockingReason(dforms.Form):
	REASONS = ((u'1', u'spammer'),
			  (u'2', u'conteúdo abusivo'),
			  (u'3', u'motivos pessoais'),
			  (u'4', u'outras'))

	reason = dforms.ModelMultipleChoiceField(queryset=REASONS)




