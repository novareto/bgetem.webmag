# -*- coding: utf-8 -*-
# Copyright (c) 2007-2013 NovaReto GmbH
# cklinger@novareto.de

import tweepy
from tweepy import OAuthHandler

from plone import api as papi
from uvc.api import api
from uvc.shards import BaseShard as Shard
from zope.component import getUtility
from collective.prettydate.interfaces import IPrettyDate
import twitter
import logging
from ttp import ttp
logger = logging.getLogger('nva.bgetemwebmag')
api.templatedir('templates')


class BaseShard(Shard):
    api.baseclass()

    @property
    def css(self):
        return self._namespace.get('class', '')


class DocumentShard(BaseShard):
    api.name('document')

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
            banner['subject'] = obj.category
            banner['title'] = obj.newstitle
            banner['lineclass'] = 'title-border line-%s' % obj.colorcode
            banner['description'] = obj.description
            banner['richtext'] = ''
            if obj.text:
                banner['richtext'] = obj.text.output
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


class EditorialShard(BaseShard):
    api.name('editorial')
    tweet_url = "https://twitter.com/DGUVKompakt/status/"
    
    def tweets(self, count):        
        consumer_key = 'noCXFV6QYjtiQ9yX6QYz1fhCi'
        consumer_secret = 'u9HiILFmGgxZHs1bOEpXCObOWDW4FHkIArFlgdstGH94fQjBye'
        access_token = '2583843280-5xcsF1g14HTIeVovvw28Z6RkNMdCzZYaoIgXfZh'
        access_secret = '0r2rTTy9yaeWXb74qbG1XrTvXjCt82hPRlL3nl5agbXmK'
 
        auth = OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_secret)
 
        api = tweepy.API(auth)

        for status in tweepy.Cursor(api.user_timeline, user_id="@DGUVKompakt").items(count):
            yield status

    def getSocialContent(self):
        results = self.getAllTweets()
        sc = []
        for i in results:
            entry = {}
            entry['name'] = i.user.name
            entry['screen_name'] = '@%s' %i.user.screen_name
            twparser = ttp.Parser()
            mytext = twparser.parse(i.text)
            entry['title'] = mytext.html
            entry['description'] = ''
            entry['desc_html'] = False
            entry['url'] = self.getTweetUrl(i)
            datum = i.created_at.split(' ')
            formdatum = '%s %s %s %s' %(datum[2], datum[1], datum[5], datum[3])
            try:
	        entry['date'] = datetime.strptime(formdatum, '%d %b %Y %H:%M:%S').strftime('%d.%m.%Y %H:%M')
            except:
	        entry['date'] = formdatum
            entry['thumb'] = self.getAvatar(i)
            sc.append(entry)
        return sc

    def getAvatar(self, result):
	if result.retweeted:
	    retweet = result.retweeted_status
	    return retweet.user.profile_image_url
	return result.user.profile_image_url

    def getTweetUrl(self, result):
         if result.urls:
             return result.urls[0].url
         return ''

    def getDate(self, result):
         date_utility = getUtility(IPrettyDate)
         date = date_utility.date(result.created_at)
         return date

    def getAllTweets(self):
        tw = twitter.Api(consumer_key='noCXFV6QYjtiQ9yX6QYz1fhCi',
		         consumer_secret='u9HiILFmGgxZHs1bOEpXCObOWDW4FHkIArFlgdstGH94fQjBye',
		         access_token_key='2583843280-5xcsF1g14HTIeVovvw28Z6RkNMdCzZYaoIgXfZh',
		         access_token_secret='0r2rTTy9yaeWXb74qbG1XrTvXjCt82hPRlL3nl5agbXmK')
        tw_user = '@DGUVKompakt'
        max_results = 2

        try:
            results = tw.GetUserTimeline(tw_user, count=max_results)
            logger.info("%s results obtained." % len(results))
        except Exception, e:
            logger.info("Something went wrong: %s." % e)
            results = []
        return results

    def banner(self):
        doc = self._namespace.get('myeditorial')
        obj = self.context.get(doc)
        banner = {}
        if obj:
            banner['tweets'] = list(self.tweets(2))
            banner['tweets'] = self.getSocialContent()
            banner['subject'] = obj.category
            banner['lineclass'] = 'title-border line-%s' % obj.colorcode
            banner['newstext'] = obj.newstext
            banner['url'] = obj.absolute_url()
            banner['banner_image'] = None
            if getattr(obj, 'newsimage', False):
	        banner['banner_image'] = ('%s/@@images/newsimage' %obj.absolute_url())
	    banner['newstitle'] = obj.newstitle
            banner['newsrichtext'] = None
            if obj.newsrichtext:
	        banner['newsrichtext'] = obj.newsrichtext.output
        return banner


class RichTextShard(BaseShard):
    api.name('richtext')

    def banner(self):
        doc = self._namespace.get('document')
        obj = self.context.get(doc)
        banner = {}
        if obj:
            banner['subject'] = obj.category
            banner['lineclass'] = 'title-border line-%s' % obj.colorcode
            if obj.newsrichtext:
                banner['newsrichtext'] = obj.newsrichtext.output
            banner['url'] = obj.absolute_url()
        return banner


class EventListShard(BaseShard):
    api.name('eventlist')

    def banner(self):
        folder = self._namespace.get('eventfolder')
        obj = self.context.get(folder)
        eventlist = []
        for i in obj.getFolderContents():
            if i.portal_type == 'Event':
                event = {}
                event['eventtext'] = i.Title.decode('utf-8')
                if i.start.date() == i.end.date():
                    event['date'] = i.start.strftime("%d.%m.%Y")
                else:
                    if i.start.year == i.end.year:
                        if i.start.month == i.end.month:
                            event['date'] = "%s. - %s" % (
                                i.start.day, i.end.strftime("%d.%m.%Y"))
                        else:
                            event['date'] = "%s - %s" % (
                                i.start.strftime("%d.%m"),
                                i.end.strftime("%d.%m.%Y"))
                    else:
                        event['date'] = "%s - %s" % (
                            i.start.strftime("%d.%m.%Y"),
                            i.end.strftime("%d.%m.%Y"))
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
