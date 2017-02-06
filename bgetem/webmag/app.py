# -*- coding: utf-8 -*-
# Copyright (c) 2007-2013 NovaReto GmbH
# cklinger@novareto.de

import urllib
from five import grok
from uvc.api import api
from zope import interface
from .layout import BSPage as Page
from .layer import IAnonymousLayer
from .interfaces import IPageTop, IFooter
from zope.component import getMultiAdapter
from Products.CMFCore.utils import getToolByName
from plone.dexterity.interfaces import IDexterityItem
from plone.app.contenttypes.interfaces import IDocument
from plone.app.layout.globals.interfaces import IViewView


api.templatedir('templates')


class SimpleNewspaperView(api.View):
    api.name('newspaperview')
    api.context(interface.Interface)


class NewspaperView(Page):
    grok.implements(IViewView)
    api.context(interface.Interface)
    grok.layer(IAnonymousLayer)


class ContentPage(Page):
    grok.context(IDocument)
    grok.name('document_view')
    grok.layer(IAnonymousLayer)

    def update(self):
        localurl = self.context.absolute_url()
        self.image = '%s/@@images/newsimage' % localurl
        self.lineclass = 'title-border line-%s' % self.context.colorcode
        self.quoted = urllib.quote_plus(localurl)
        self.titlequoted = urllib.quote_plus(self.context.Title())

class PageHeader(api.Viewlet):
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
                if not obj.excludenextprev and not obj.id == "index.html":
                    entry['linktitle'] = "%s : %s" %(obj.category, obj.title)
                    entry['url'] = obj.absolute_url()
                    seq.append(entry)
        self.doclist = [seq[i:i+8] for i  in range(0, len(seq), 8)]
        self.ausgabe = self.context.aq_parent.Description()

class PageFooter(api.Viewlet):
    grok.layer(IAnonymousLayer)
    api.context(interface.Interface)
    api.viewletmanager(IFooter)

    def update(self):
        pathroot = self.context.absolute_url_path().split('/')[1]
        self.rechteurl = '/%s/index.html/bildrechte' %pathroot
