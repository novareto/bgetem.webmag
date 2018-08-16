# -*- coding: utf-8 -*-
from five import grok
from nva.magazinfolder.interfaces import IAnonymousLayer, IMagazinFolder
from plone.api import portal
from plone.app.contenttypes.interfaces import IDocument
from plone.app.layout.globals.interfaces import IViewView
from plone.dexterity.interfaces import IDexterityItem
from uvc.api import api
from zope import interface
from plone.api import content
from plone import api as ploneapi
from .views import NewspaperView
from zope.interface import Interface

from . import get_webmag
from .views import NewspaperView
from nva.magazinfolder.interfaces import IAnonymousLayer
from .interfaces import IPageTop, IFooter, INavigation, IAboveContent, IBelowContent
from nva.magazinartikel.interfaces import get_sparte

api.templatedir('templates')


def grouper(size, values):
    return zip(*(iter(values),) * size)


class PageHeader(api.Viewlet):
    grok.order(10)
    grok.layer(IAnonymousLayer)
    api.context(interface.Interface)
    api.viewletmanager(IPageTop)

    def update(self):
        self.magurl = ploneapi.portal.get().absolute_url()
        

class Navigation(api.Viewlet):
    grok.order(10)
    grok.viewletmanager(INavigation)
    grok.context(Interface)
    #grok.view(NewspaperView)
    navitems = {}

    def update(self):
        rc = {}
        for brain in content.find(self.context, portal_type='Document'):
            document = brain.getObject()  # BBB
            if document.category:
                if document.category not in rc.keys():
                    rc[document.category] = []
                rc[document.category].append(
                    dict(title=document.title, url=document.absolute_url())
                )
        self.navitems = rc


class EtemPlus(api.Viewlet):
    grok.order(10)
    grok.viewletmanager(IAboveContent)
    grok.context(IMagazinFolder)
    grok.view(NewspaperView)
    dokumente = []

    def update(self):
        webmag = get_webmag(self.context)
        values = (x for x in webmag['etem'].values())
        seq = []
        for i in values:
            seq.append(i)
        size = 4
        groups = [seq[i:i+size] for i  in range(0, len(seq), size)]
        #groups = grouper(size=4, values=values)
        self.groups = groups

    def sparte(self, obj):
        vocab = get_sparte(self.context)
        sparten = obj.sparte
        mysparten = []
        for i in sparten:
            mysparten.append(vocab.getTerm(i).title)
        branchen = ', '.join(mysparten)
        return branchen

    def image(self, obj):
        print obj
        banner = ''
        if hasattr(obj, 'titleimage'):
            if obj.titleimage:
                imgobj = obj.titleimage.to_object
                banner = '%s/@@images/image' % imgobj.absolute_url()
            else:
                if obj.newsimage:
                    banner = '%s/@@images/newsimage' % obj.absolute_url()
        else:
            if obj.newsimage:
                banner = '%s/@@images/newsimage' % obj.absolute_url()
        return banner

    def description(self, obj):
        desc = obj.description
        if hasattr(obj, 'newstext'):
            if obj.newstext:
                desc = obj.newstext
        return desc


class Carousel(api.Viewlet):
    grok.order(20)
    grok.viewletmanager(IPageTop)
    grok.context(IMagazinFolder)
    grok.view(NewspaperView)
    bilder = []

    def update(self):
        webmag = get_webmag(self.context)
        self.bilder = [x for x in webmag['titelstories'].values()]

    def image(self, obj):
        print obj
        if hasattr(obj, 'titleimage'):
            if obj.titleimage:
                imgobj = obj.titleimage.to_object
                banner = '%s/@@images/image' % imgobj.absolute_url()
                print banner
            else:
                banner = '%s/@@images/newsimage' % obj.absolute_url()
        else:
            banner = '%s/@@images/newsimage' % obj.absolute_url()
        return banner


class Campaign(api.Viewlet):
    grok.order(10)
    grok.viewletmanager(IFooter)
    grok.context(IMagazinFolder)
    grok.view(NewspaperView)
    dokumente = []

    def update(self):
        webmag = get_webmag(self.context)
        kampagnen = webmag['kampagnen']

        if kampagnen.relatedItems:
            self.dokumente = [x for x in kampagnen.relatedItems[0].to_object.values()]
        else:
            self.dokumente = [x for x in webmag['kampagnen'].values()]

    def image(self, obj):
        if hasattr(obj, 'titleimage'):
            if obj.titleimage:
                imgobj = obj.titleimage.to_object
                banner = '%s/@@images/image' % imgobj.absolute_url()
            else:
                banner = '%s/@@images/newsimage' % obj.absolute_url()
        else:
            banner = '%s/@@images/newsimage' % obj.absolute_url()
        return banner


class InfoBox(api.Viewlet):
    grok.order(20)
    grok.layer(IAnonymousLayer)
    api.context(interface.Interface)
    api.viewletmanager(IFooter)


class PageFooter(api.Viewlet):
    grok.order(20)
    grok.layer(IAnonymousLayer)
    api.context(interface.Interface)
    api.viewletmanager(IFooter)

    def update(self):
        pathroot = self.context.absolute_url_path().split('/')[1]
        self.rechteurl = '/%s/bildrechte' % pathroot
