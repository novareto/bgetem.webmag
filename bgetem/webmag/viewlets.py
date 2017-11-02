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
from .views import NewspaperView
from zope.interface import Interface

from . import get_webmag
from .views import NewspaperView
from nva.magazinfolder.interfaces import IAnonymousLayer
from .interfaces import IPageTop, IFooter, INavigation, IAboveContent


api.templatedir('templates')


def grouper(size, values):
    return zip(*(iter(values),) * size)


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
