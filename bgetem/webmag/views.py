# -*- coding: utf-8 -*-

from uvc.api import api
from five import grok
from zope.interface import Interface
from .layout import BSPage as Page
from .layer import IAnonymousLayer
from uvc.shards.interface import IShardedView
from uvc.shards.components import ShardsAsViews
from Products.CMFCore.utils import getToolByName
from plone.memoize import ram
from time import time
from plone import api as ploneapi


api.templatedir('templates')


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
