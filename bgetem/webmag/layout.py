# -*- coding: utf-8 -*-
# Copyright (c) 2007-2013 NovaReto GmbH
# cklinger@novareto.de

from .interfaces import IPageTop, IFooter, INavigation, IAboveContent
from .layer import IAnonymousLayer, IWebmag

from five import grok
from grokcore.layout import Layout
from plone import api as ploneapi
from plone.app.layout.nextprevious.interfaces import INextPreviousProvider
from uvc.api import api
from uvc.shards.components import ShardsAsViews
from uvc.shards.interface import IShardedView
from zope import interface
from zope.component import getMultiAdapter
from plone.app.folder.nextprevious import NextPrevious
from Products.CMFCore.interfaces import IContentish


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


api.templatedir('templates')


class NewsPaperLayout(Layout):
    api.context(interface.Interface)
    grok.layer(IAnonymousLayer)


class Navigation(api.ViewletManager):
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
      #nextprev = INextPreviousProvider(portal['bgetem-kompakt-aktuell'])
      #nextprev = NPWebMag(portal['bgetem-kompakt-aktuell'])
      try:
         nextprev = NPWebMag(portal[pathroot])
         return {'next': nextprev.getNextItem(self.context),
                 'previous': nextprev.getPreviousItem(self.context)}
      except:
         return {'next': None, 'previous': None}


class AboveContent(api.ViewletManager):
    api.implements(IAboveContent)
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
