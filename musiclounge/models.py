#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.db import models


class User(models.Model):
	name =  models.CharField(max_length=255, null=True)
	firstName = models.CharField(max_length=255, null=True)
	login = models.CharField(max_length=255, primary_key=True)
	city = models.CharField(max_length=255, null=True)

	def __str__(self):
		return self.login

class MusicalAct(models.Model): 
	id = models.AutoField(primary_key=True)
	title =  models.CharField(max_length=255)
	uri =  models.CharField(max_length=255, null = True)
	country =  models.CharField(max_length=255, null=True)
	genre =  models.CharField(max_length=255, null=True)
	summary = models.TextField(null=True)

	def __str__(self):
		return self.title

class Musician(models.Model):
	name = models.CharField(max_length=255, null=True)
	genre = models.CharField(max_length=255, null=True)
	birthDate = models.DateTimeField(null=True)
	musicalAct = models.ForeignKey(MusicalAct, related_name="musicalAct")

	def __str__(self):
		return self.name

class Blocking(models.Model):	
	blocker = models.ForeignKey(User, related_name="blocker")
	blocked = models.ForeignKey(User, related_name="blocked")

	def __str__(self):
		return self.blocking.name


class Friendship(models.Model):
	user = models.ForeignKey(User, related_name="user")
	friend = models.ForeignKey(User, related_name="friend")

	def __str__(self):
		return self.friend.name

class MusicalActRate(models.Model):
	musicalAct = models.ForeignKey(MusicalAct)
	user = models.ForeignKey(User)
	rate = models.IntegerField(default=0)

	def __str__(self):
		return self.rate

class BlockingReason(models.Model):
	blocking = models.ForeignKey(Blocking, related_name="blocking")
	reason = models.CharField(max_length=255, null=True)

	def __str__(self):
		return self.reason




