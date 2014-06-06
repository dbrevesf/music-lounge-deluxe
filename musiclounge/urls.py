#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url

from musiclounge import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^registration', views.registration, name='registration'),
    url(r'^login', views.login, name='login'),
    url(r'^logout', views.logout, name='logout'),
    url(r'^home/(?P<login>\w+)', views.home, name='home'),
    url(r'^musicalAct/(?P<id>\w+)', views.musicalAct, name='musicalAct'),
    url(r'^user/(?P<login>\w+)', views.user, name='user'),
    url(r'^updateUser', views.updateUser, name='updateUser'),
    url(r'^managerRelationship/(?P<user>\w+)', views.managerRelationship, name='managerRelationship'),
    url(r'^managerMusicalActLikes/(?P<musicalActId>\w+)', views.managerMusicalActLikes, name='managerMusicalActLikes'),
)
