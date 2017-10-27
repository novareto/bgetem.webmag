# -*- coding: utf-8 -*-

from Products.CMFCore.utils import getToolByName
from five import grok
from plone import api as ploneapi
from plone.app.contenttypes.interfaces import IDocument
from plone.app.layout.globals.interfaces import IViewView
from plone.memoize import ram
from time import time
from uvc.api import api
from uvc.shards.components import ShardsAsViews
from uvc.shards.interface import IShardedView
from zope.interface import Interface

from .layout import BSPage as Page
from nva.magazinfolder.interfaces import IAnonymousLayer


api.templatedir('templates')


class SimpleNewspaperView(api.View):
    api.name('newspaperview')
    api.context(Interface)


class NewspaperView(Page):
    grok.implements(IViewView)
    api.context(Interface)
    grok.layer(IAnonymousLayer)


class ContentPage(Page):
    grok.context(IDocument)
    grok.name('document_view')
    grok.layer(IAnonymousLayer)

    def update(self):
        localurl = self.context.absolute_url()
        self.image = '%s/@@images/newsimage' % localurl
        self.lineclass = 'title-border line-%s' % getattr(
            self.context, 'colorcode', 'grey')
        self.quoted = urllib.quote_plus(localurl)
        self.titlequoted = urllib.quote_plus(self.context.Title())


class Titelview(Page):
    api.context(Interface)
    grok.layer(IAnonymousLayer)


class MyTitelview(Page):
    api.context(Interface)
    grok.layer(IAnonymousLayer)


class KompaktTitelview(Page):
    api.context(Interface)
    grok.layer(IAnonymousLayer)


class Bildrechte(Page):
    api.context(Interface)
    grok.layer(IAnonymousLayer)

    @property
    def portal_catalog(self):
        return getToolByName(self.context, 'portal_catalog')

    def getImageBrains(self):
        folderid = self.context.aq_parent.id
        path = '/magazin/%s/medien-dieser-ausgabe' %folderid
        return self.portal_catalog(path=path, portal_type = 'Image')

    def update(self):
        brains = self.getImageBrains()
        self.bildrechte = []
        bildrechte = []
        for i in brains:
            entry = {}
            obj = i.getObject()
            if obj.Rights():
                entry['title'] = obj.Description()
                entry['url'] = obj.absolute_url() + '/@@images/image/thumb'
                entry['rights'] = obj.Rights()
                if not obj.id == u'titelbild':
                    bildrechte.append(entry)
        bildrechte.sort()
        self.bildrechte = bildrechte


class Kompaktarchiv(Page):
    api.context(Interface)
    grok.layer(IAnonymousLayer)

    def update(self):
        folders = [u'dezember-2016',
                   u'november-2016',
                   u'oktober-2016',
                   u'september-2016',
                   ]
        archiv = []
        for i in folders:
           portal = ploneapi.portal.get()
           obj = getattr(portal, i)
           magazin = {}
           if obj:
               magazin['title'] = obj.description
               magazin['url'] = obj.absolute_url()+'/index.html/kompakttitelview'
               magazin['imgurl'] = obj.absolute_url() + '/medien-dieser-ausgabe/titelbild/@@images/image/thumb'
               print magazin['imgurl']
               titelobj = getattr(obj, u'titelstory')
               magazin['storytitle'] = titelobj.title
               archiv.append(magazin)
        self.archiv = archiv

#class DocumentView(api.Page):
#    api.implements(IShardedView)
#    api.context(Interface)
#    shards = ShardsAsViews()
#
#    def update(self):
#        self.mydoc = self.request.get('mydoc')
