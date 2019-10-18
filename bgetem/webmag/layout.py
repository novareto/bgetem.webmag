# -*- coding: utf-8 -*-
# Copyright (c) 2007-2013 NovaReto GmbH
# cklinger@novareto.de

from .interfaces import IPageTop, IFooter, INavigation, IAboveContent, IBelowContent

from five import grok
from grokcore.layout import Layout
from plone import api as ploneapi
from uvc.api import api
from uvc.shards.components import ShardsAsViews
from uvc.shards.interface import IShardedView
from zope import interface
from Products.CMFCore.interfaces import ISiteRoot
from zope.component import getMultiAdapter
from plone.app.folder.nextprevious import NextPrevious
from Products.CMFCore.interfaces import IContentish
from nva.magazinfolder.interfaces import IAnonymousLayer


api.templatedir('templates')


class NPWebMag(NextPrevious):

    def getData(self, obj):
        """ return the expected mapping, see `INextPreviousProvider` """
        gNN = getattr(obj, 'excludenextprev', False)
        if gNN:
            return None
        if not self.security.checkPermission('View', obj):
            return None
        elif not IContentish.providedBy(obj):
            # do not return a not contentish object
            # such as a local workflow policy for example (#11234)
            return None

        ptype = obj.portal_type
        url = obj.absolute_url()
        if ptype in self.vat:       # "use view action in listings"
            url += '/view'
        return dict(
            id=obj.getId(),
            url=url,
            title=obj.Title(),
            description=obj.Description(),
            portal_type=ptype
        )


class NewsPaperLayout(Layout):
    api.context(interface.Interface)
    grok.layer(IAnonymousLayer)

    def getAcquisitionChain(self, context):
        inner = context.aq_inner
        iter = inner
        while iter is not None:
            yield iter
            if ISiteRoot.providedBy(iter):
                break
            if not hasattr(iter, "aq_parent"):
                raise RuntimeError("Parent traversing interrupted by object: " + str(parent))
            iter = iter.aq_parent
    
    def update(self):
        self.og_title = ''
        self.og_description = ''
        self.og_image = ''
        self.og_url = self.context.absolute_url()
        if self.context.title:
            self.og_title = self.context.title
        if hasattr(self.context, 'newstitle'):
            if self.context.newstitle:
                self.og_title = self.context.newstitle
        if self.context.description:
            self.og_description = self.context.description
        if hasattr(self.context, 'newstext'):
            if self.context.newstext:
                self.og_description = self.context.newstext
        if hasattr(self.context, 'titleimage'):
            if self.context.titleimage:
                self.og_image = '%s/@@images/image' %self.context.titleimage.to_object.absolute_url()
        if hasattr(self.context, 'newsimage'):
            if self.context.newsimage:
                self.og_image = '%s/@@images/newsimage' %self.context.absolute_url()
        if self.context.portal_type == 'Magazinfolder':                
            if hasattr(self.context, 'defaultimage'):
                if self.context.defaultimage:
                    self.og_image = '%s/@@images/defaultimage' %self.context.absolute_url()
        if not self.og_image:        
            parentobjects = self.getAcquisitionChain(self.context)
            for i in parentobjects:
                if i.portal_type == 'Magazinfolder':
                    if i.defaultimage:
                        self.og_image = '%s/@@images/defaultimage' %i.absolute_url()
                        return


class NavigationManager(api.ViewletManager):
    api.name('navigation')
    api.implements(INavigation)
    api.context(interface.Interface)
    grok.layer(IAnonymousLayer)


class PageTop(api.ViewletManager):
    api.implements(IPageTop)
    api.context(interface.Interface)
    grok.layer(IAnonymousLayer)

    def nextprevious(self):
        portal = ploneapi.portal.get()
        pathroot = self.context.absolute_url_path().split('/')[1]
        try:  # BBB
            nextprev = NPWebMag(portal[pathroot])
            return {'next': nextprev.getNextItem(self.context),
                    'previous': nextprev.getPreviousItem(self.context)}
        except:
            return {'next': None, 'previous': None}


class AboveContent(api.ViewletManager):
    api.implements(IAboveContent)
    api.context(interface.Interface)
    grok.layer(IAnonymousLayer)


class BelowContent(api.ViewletManager):
    api.implements(IBelowContent)
    api.context(interface.Interface)
    grok.layer(IAnonymousLayer)


class Footer(api.ViewletManager):
    api.implements(IFooter)
    api.context(interface.Interface)
    grok.layer(IAnonymousLayer)


class BSPage(api.Page):
    api.implements(IShardedView)
    shards = ShardsAsViews()
    api.baseclass()

    layoutClass = NewsPaperLayout

    def _get_layout(self):
        return self.layoutClass(self.request, self.context)

    def application_url(self):
        context = self.context.aq_inner
        portal_state = getMultiAdapter(
            (context, self.request), name=u'plone_portal_state')
        return portal_state.portal_url()
