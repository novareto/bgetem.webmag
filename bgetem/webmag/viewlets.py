# -*- coding: utf-8 -*-

import urllib

from Products.CMFCore.utils import getToolByName
from five import grok
from nva.magazinfolder.interfaces import IAnonymousLayer, IMagazinFolder
from plone.api import portal
from plone.app.contenttypes.interfaces import IDocument
from plone.app.layout.globals.interfaces import IViewView
from plone.dexterity.interfaces import IDexterityItem
from uvc.api import api
from zope import interface
from zope.component import getMultiAdapter
from zope.interface import Interface

from . import get_webmag
from .views import NewspaperView
from .interfaces import IPageTop, IFooter, INavigation, IAboveContent


api.templatedir('templates')


def grouper(size, values):
    return zip(*(iter(values),) * size)


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
    grok.context(IMagazinFolder)
    grok.view(NewspaperView)
    dokumente = []

    def update(self):
        webmag = get_webmag(self.context)
        values = (x for x in webmag['etem'].values())
        groups = grouper(size=4, values=values)
        self.groups = groups


class Carousel(api.Viewlet):
    grok.order(20)
    grok.viewletmanager(IPageTop)
    grok.context(IMagazinFolder)
    grok.view(NewspaperView)
    bilder = []

    def update(self):
        import pdb
        pdb.set_trace()
        webmag = get_webmag(self.context)
        self.bilder = [x for x in webmag['titelstories'].values()]


class Campaign(api.Viewlet):
    grok.order(10)
    grok.viewletmanager(IFooter)
    grok.context(IMagazinFolder)
    grok.view(NewspaperView)

        
class PageFooter(api.Viewlet):
    grok.order(20)
    grok.layer(IAnonymousLayer)
    api.context(interface.Interface)
    api.viewletmanager(IFooter)

    def update(self):
        pathroot = self.context.absolute_url_path().split('/')[1]
        self.rechteurl = '/%s/index.html/bildrechte' % pathroot
