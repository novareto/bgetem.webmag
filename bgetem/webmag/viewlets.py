# -*- coding: utf-8 -*-

import urllib

from Products.CMFCore.utils import getToolByName
from five import grok
from plone.app.contenttypes.interfaces import IDocument
from plone.app.layout.globals.interfaces import IViewView
from plone.dexterity.interfaces import IDexterityItem
from uvc.api import api
from zope import interface
from zope.component import getMultiAdapter
from zope.interface import Interface

from .views import NewspaperView
from .interfaces import IPageTop, IFooter, INavigation, IAboveContent
from nva.magazinfolder.interfaces import IAnonymousLayer


api.templatedir('templates')


class Navigation(api.Viewlet):
    grok.order(10)
    grok.viewletmanager(INavigation)
    grok.context(Interface)


class PageHeader(api.Viewlet):
    grok.order(10)
    grok.layer(IAnonymousLayer)
    api.context(interface.Interface)
    api.viewletmanager(IPageTop)

    def update(self):
        api.Viewlet.update(self)
        self.catalog = getToolByName(self.context, 'portal_catalog')
        fc = self.context.aq_parent.getFolderContents()
        seq = []
        for i in fc:
            entry = {}
            obj = i.getObject()
            if obj.portal_type == "Document":
                if not getattr(obj, 'excludenextprev', False) and not obj.id == "index.html":
                    entry['linktitle'] = "%s : %s" % (
                        getattr(obj, "category", "No Category"), obj.title)
                    entry['url'] = obj.absolute_url()
                    seq.append(entry)
        self.doclist = [seq[i:i+8] for i  in range(0, len(seq), 8)]
        self.ausgabe = self.context.aq_parent.Description()


class EtemPlus(api.Viewlet):
    grok.order(10)
    grok.viewletmanager(IAboveContent)
    grok.context(Interface)
    grok.view(NewspaperView)
    dokumente = []

    def update(self):
        self.dokumente = [x for x in self.context['etem'].values()]


class Carousel(api.Viewlet):
    grok.order(20)
    grok.viewletmanager(IPageTop)
    grok.context(Interface)
    bilder = []

    def update(self):
        self.bilder = [x for x in self.context['titelstories'].values()]


class Campaign(api.Viewlet):
    grok.order(10)
    grok.viewletmanager(IFooter)
    grok.context(Interface)

        
class PageFooter(api.Viewlet):
    grok.order(20)
    grok.layer(IAnonymousLayer)
    api.context(interface.Interface)
    api.viewletmanager(IFooter)

    def update(self):
        pathroot = self.context.absolute_url_path().split('/')[1]
        self.rechteurl = '/%s/index.html/bildrechte' % pathroot
