from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^musiclounge/', include('musiclounge.urls', namespace="musiclounge")),
    url(r'^admin/', include(admin.site.urls)),
)

