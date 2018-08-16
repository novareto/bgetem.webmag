# -*- coding: utf-8 -*-
# Copyright (c) 2007-2013 NovaReto GmbH
# cklinger@novareto.de

#import tweepy
#from tweepy import OAuthHandler

import requests
import json
from plone import api as papi
from uvc.api import api
from uvc.shards import BaseShard as Shard
from zope.component import getUtility
from zope.component import getMultiAdapter
from collective.prettydate.interfaces import IPrettyDate
import twitter
import logging
from ttp import ttp
from DateTime import DateTime
logger = logging.getLogger('nva.bgetemwebmag')
api.templatedir('templates')


class BaseShard(Shard):
    api.baseclass()

    @property
    def css(self):
        return self._namespace.get('class', '')

class SelectShard(BaseShard):
    api.name('myselect')

    def render(self):
        view = getMultiAdapter(
             (self.context, self.request),
              name="document")
        html = view().banner(view, self._namespace.get('document')) 
        return html
        #return 'Hallo Welt'

class DocumentShard(BaseShard):
    api.name('document')

    def banner(self):
        doc = self._namespace.get('document')
        if '/' in doc:
            doclist = doc.split('/')
            folder = self.context.get(doclist[0])
            obj = folder.get(doclist[1])
        else:
            folder = self.context.get('themen')
            obj = folder.get(doc)
        banner = {}
        if obj:
            banner['title'] = obj.title
            if hasattr(obj, 'newstitle'):
                if obj.newstitle:
                     banner['title'] = obj.newstitle
            banner['description'] = obj.description
            if hasattr(obj, 'newstext'):
                if obj.newstext:
                     banner['description'] = obj.newstext
            if hasattr(obj, 'titleimage'):
                if obj.titleimage:
                    imgobj = obj.titleimage.to_object
                    banner['banner_image'] = ('%s/@@images/image' %
                                               imgobj.absolute_url())
                if obj.newsimage:
                    banner['banner_image'] = ('%s/@@images/newsimage' %
                                              obj.absolute_url())
            else:
                banner['banner_image'] = ('%s/@@images/newsimage' %
                                          obj.absolute_url())
            banner['url'] = obj.absolute_url()
            banner['imgtitle'] = obj.newstitle
            banner['category'] = obj.category
            banner['cssclass'] = '%s' % obj.colorcode
        return banner


class FooterShard(BaseShard):
    api.name('footer')

    def banner(self):
        doc = self._namespace.get('document')
        if '/' in doc:
            doclist = doc.split('/')
            folder = self.context.get(doclist[0])
            obj = folder.get(doclist[1])
        else:
            obj = self.context.get(doc)
        banner = {}
        if obj:
            banner['banner_image'] = None
            if getattr(obj, 'newsimage', False):
                banner['banner_image'] = ('%s/@@images/newsimage' %
                                          obj.absolute_url())
            banner['title'] = obj.title
            banner['richtext'] = ''
            if obj.text:
                banner['richtext'] = obj.text.output
        return banner


class StoryShard(BaseShard):
    api.name('story')

    def banner(self):
        doc = self._namespace.get('mystory')
        obj = self.context.get(doc)
        banner = {}
        if obj:
            banner['title'] = obj.title
            banner['description'] = obj.description
            banner['banner_image'] = ('%s/@@images/newsimage' %
                                      obj.absolute_url())
            banner['url'] = obj.absolute_url()
            banner['newstitle'] = obj.newstitle
        return banner


class RichTextShard(BaseShard):
    api.name('richtext')

    def banner(self):
        doc = self._namespace.get('document')
        folder = self.context.get('themen')
        obj = folder.get(doc)
        banner = {}
        if obj:
            banner['category'] = obj.category
            banner['lineclass'] = 'title-border line-%s' % obj.colorcode
            if obj.newsrichtext:
                banner['newsrichtext'] = obj.newsrichtext.output
            banner['url'] = obj.absolute_url()
        return banner


class EventListShard(BaseShard):
    api.name('eventlist')

    def eventsummary(self):
        doc = self._namespace.get('eventfolder')
        folder = self.context.get('themen')
        termine = folder.get(doc)
        return termine.sumUrl
        
    def banner(self):
        doc = self._namespace.get('eventfolder')
        folder = self.context.get('themen')
        termine = folder.get(doc)
        url = termine.remoteUrl
        headers = {'Accept':'application/json'}
        results = requests.get(url, headers = headers)
        data = results.json()
        eventlist = []
        if data.get('items'):
            for i in data.get('items')[:5]:
                if i.get('@type') == 'Event':
                    termindata = requests.get(i.get('@id'), headers=headers)
                    termin = termindata.json()
                    event = {}
                    event['eventtext'] = termin.get('title')
                    event['date'] = DateTime(termin.get('startDate')).strftime("%d.%m.%Y")
                    event['location'] = termin.get('location')
                    event['url'] = termin.get('@id')
                    eventlist.append(event)
        return eventlist


class TitleShard(BaseShard):
    api.name('title')
    name = "TEST"

    def banner(self):
        return self._namespace.get('var', '') * 4


class NewsListingShard(BaseShard):
    api.name('newslisting')
    name = "News Listing"

    def get_news(self):
        print papi.content.find(portal_type='Document')
        return papi.content.find(portal_type='Document')


class ImageShard(BaseShard):
    api.name('image')

    def banner(self):
        """ return banner of this object """
        image = self._namespace.get('image', 'NN')
        obj = self.context.get(image)
        if obj:
            banner = {}
            if getattr(obj, 'newsimage', False):
                banner['banner_image'] = '%s/@@images/newsimage' \
                    % obj.absolute_url()
            if obj.newstitle:
                banner['banner_title'] = obj.newstitle
            if obj.newstext:
                banner['banner_description'] = obj.newstext
            if obj.newsrichtext:
                banner['banner_text'] = obj.newsrichtext.output
            banner['banner_link'] = obj.absolute_url()
            #banner['banner_linktext'] = obj.Title()
            if obj.newsurl:
                to_obj = obj.newsurl.to_object
                if to_obj:
                    banner['banner_link'] = to_obj.absolute_url()
                    banner['banner_linktext'] = to_obj.Title()
            if hasattr(obj, 'newslinktitle'):
                banner['banner_linktext'] = obj.newslinktitle
            if getattr(obj, 'banner_fontcolor', False):
                banner['banner_fontcolor'] = obj.banner_fontcolor
            print banner
            return banner
