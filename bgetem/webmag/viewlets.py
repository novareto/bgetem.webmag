# -*- coding: utf-8 -*-


from five import grok
from uvc.api import api
from zope import interface
from plone.api import content
from .views import NewspaperView
from zope.interface import Interface

from nva.magazinfolder.interfaces import IAnonymousLayer
from .interfaces import IPageTop, IFooter, INavigation, IAboveContent


api.templatedir('templates')


class PageHeader(api.Viewlet):
    grok.order(10)
    grok.layer(IAnonymousLayer)
    api.context(interface.Interface)
    api.viewletmanager(IPageTop)


class Navigation(api.Viewlet):
    grok.order(10)
    grok.viewletmanager(INavigation)
    grok.context(Interface)
    grok.view(NewspaperView)
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
    grok.context(Interface)
    grok.view(NewspaperView)
    dokumente = []

    def update(self):
        self.dokumente = [x for x in self.context['etem'].values()]


class Carousel(api.Viewlet):
    grok.order(20)
    grok.viewletmanager(IPageTop)
    grok.context(Interface)
    grok.view(NewspaperView)
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
