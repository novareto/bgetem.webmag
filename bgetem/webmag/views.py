# -*- coding: utf-8 -*-
import urllib
from DateTime import DateTime
from datetime import datetime
from zope.interface import Interface
from Products.CMFCore.utils import getToolByName
from five import grok
from uvc.api import api
from plone import api as ploneapi
from .layout import BSPage as Page
from zope.interface import Interface
from zope.component import getMultiAdapter
from Products.CMFCore.utils import getToolByName
from plone.app.contenttypes.interfaces import IDocument
from nva.magazinartikel.interfaces import IMagazinartikel, get_sparte
from nva.magazinfolder.interfaces import IAnonymousLayer
from plone.app.layout.globals.interfaces import IViewView
from nva.magazinfolder.interfaces import IMagazinFolder
from nva.magazinartikel.interfaces import IMagazinartikel
from chameleon import PageTemplate
from grokcore.chameleon import components

api.templatedir('templates')

from uvc.shards.shard import resolve_shard
from uvc.shards.shard import query_shard
from chameleon.astutil import Symbol

class SelectorView(api.View):
    api.context(Interface)

    def render(self):
        if ploneapi.user.is_anonymous():
            if 'vorschau-etem.bgetem.de' in self.request.get('URL'):
                url = ploneapi.portal.get().absolute_url() + '/vorschau'
                return self.redirect(url)
            else:
                pcat = getToolByName(self.context, 'portal_catalog')
                brains = pcat(portal_type='Magazinfolder', review_state="published", sort_on="effective", sort_order="descending")
                obj = brains[0].getObject()
                url = obj.absolute_url()
                return self.redirect(url)
        else:
            url = ploneapi.portal.get().absolute_url() + '/folder_contents'
            return self.redirect(url)

class Vorschau(api.View):
    api.context(Interface)

    def render(self):
        pcat = getToolByName(self.context, 'portal_catalog')
        brains = pcat(portal_type='Magazinfolder', review_state="preview", sort_on="modified", sort_order="descending")
        if brains:
            obj = brains[0].getObject()
            url = obj.absolute_url()
            return self.redirect(url)
        return u"Keine Ausgabe für Vorschauansicht gefunden"

class BildnachweisView(api.View):
    api.context(Interface)

    def render(self):
        pcat = getToolByName(self.context, 'portal_catalog')
        brains = pcat(portal_type='Magazinfolder', review_state="published", sort_on="effective", sort_order="descending")
        obj = brains[0].getObject()
        url = obj.absolute_url() + '/bildrechte'
        return self.redirect(url)

class Index(api.View):
    grok.name('view')
    grok.implements(IViewView)
    api.context(IMagazinFolder)
    grok.layer(IAnonymousLayer)

    def render(self):
        view = getMultiAdapter(
                (self.context, self.request),
                name="newspaperview")
        return view()

class NewspaperView(Page):
    grok.implements(IViewView)
    api.context(Interface)
    grok.layer(IAnonymousLayer)

    def shardrender(self, obj):
        namespace = {}
        namespace['context'] = self.context
        namespace['request'] = self.request
        namespace['document'] = obj.id
        shard_factory = self.shards.get(obj.kindofshard)
        shard = shard_factory(namespace)
        return resolve_shard(shard)

    def themencontents(self):
        folder = self.context.get('themen')
        contentlist = []
        fc = folder.getFolderContents()
        for i in fc:
            contentlist.append(i.getObject())
        return contentlist
        
class WebmagSearch(Page):
    api.context(Interface)
    grok.layer(IAnonymousLayer)

    def extract(self):
        value = self.request.form.get('value', None)
        themen = self.request.form.get('themen', None)
        search = bool(value or themen)
        if search:
            return value, themen
        return None

    def search(self, value, themen):
        return []
    
    def update(self):
        extracted = self.extract()
        if extracted is not None:
            value, themen = extracted
            self.results = self.search(value, themen)
        else:
            self.results = []

        self.themen = (
            "Kompakt",
            "Mensch & Praxis",
            "Gesundheit",
            "Service",
            "Kampagne",
        )
    
class ContentPage(Page):
    grok.context(IMagazinartikel)
    grok.name('document_view')
    grok.layer(IAnonymousLayer)

    def update(self):
        themen = self.context.aq_parent
        magazin = themen.aq_parent
        self.ausgabe = magazin.description
        localurl = self.context.absolute_url()
        self.image = '%s/@@images/newsimage' % localurl
        self.lineclass = 'title-border line-%s' % getattr(
            self.context, 'colorcode', 'grey')
        self.quoted = urllib.quote_plus(localurl)
        self.titlequoted = urllib.quote_plus(self.context.Title())


class ThemenCollectionPage(Page):
    api.context(IMagazinFolder)
    grok.name('themen_collection')
    grok.layer(IAnonymousLayer)

    def update(self):
        buehne = self.context.get('titelstories')
        fc = buehne.getFolderContents()
        folder = self.context.get('themen')
        fc += folder.getFolderContents()
        self.artlist = []
        for i in fc:
            obj = i.getObject()
            banner = {}
            if obj:
                banner['title'] = obj.title
                if hasattr(obj, 'newstitle'):
                    if obj.newstitle:
                        banner['title'] = obj.newstitle
                banner['description'] = obj.description
                if hasattr(obj, 'newstext'):
                    if obj.newstext:
                        banner['description'] = obj.newstext
                if hasattr(obj, 'titleimage'):
                    if obj.titleimage:
                        imgobj = obj.titleimage.to_object
                        banner['banner_image'] = ('%s/@@images/image' %
                                                   imgobj.absolute_url())
                    if obj.newsimage:
                        banner['banner_image'] = ('%s/@@images/newsimage' %
                                                  obj.absolute_url())
                else:
                    banner['banner_image'] = ('%s/@@images/newsimage' %
                                              obj.absolute_url())
                if hasattr(obj, 'listimage'):
                    if obj.listimage:
                        banner['banner_image'] = ('%s/@@images/listimage' %
                                                  obj.absolute_url())
                banner['url'] = obj.absolute_url() + '/document_view'
                banner['target'] = '_self'
                if obj.portal_type == 'Link':
                    if hasattr(obj, 'sumUrl'):
                        banner['url'] = obj.sumUrl
                        banner['target'] = '_blank'
                try:
                    banner['category'] = obj.category
                except:
                    banner['category'] = ''
            self.artlist.append(banner)

class EtemCollectionPage(Page):
    api.context(IMagazinFolder)
    grok.name('etem_collection')
    grok.layer(IAnonymousLayer)

    def update(self):
        folder = self.context.get('etem')
        fc = folder.getFolderContents()
        self.artlist = []
        for i in fc:
            obj = i.getObject()
            banner = {}
            if obj:
                banner['title'] = obj.title
                if hasattr(obj, 'newstitle'):
                    if obj.newstitle:
                        banner['title'] = obj.newstitle
                banner['description'] = obj.description
                if hasattr(obj, 'newstext'):
                    if obj.newstext:
                        banner['description'] = obj.newstext
                if hasattr(obj, 'titleimage'):
                    if obj.titleimage:
                        imgobj = obj.titleimage.to_object
                        banner['banner_image'] = ('%s/@@images/image' %
                                                   imgobj.absolute_url())
                    if obj.newsimage:
                        banner['banner_image'] = ('%s/@@images/newsimage' %
                                                  obj.absolute_url())
                else:
                    banner['banner_image'] = ('%s/@@images/newsimage' %
                                              obj.absolute_url())
                banner['url'] = obj.absolute_url() + '/document_view'
                branchen = []
                for i in obj.sparte:
                    branchen.append(get_sparte(self.context).getTerm(i).title)
                try:
                    banner['category'] = ', '.join(branchen)
                except:
                    banner['category'] = ''
            self.artlist.append(banner)

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
    api.context(IMagazinFolder)
    grok.layer(IAnonymousLayer)

    @property
    def portal_catalog(self):
        return getToolByName(self.context, 'portal_catalog')

    def getImageBrains(self):
        folder = self.context.get('medien-dieser-ausgabe')
        fc = folder.getFolderContents()
        return fc

    def update(self):
        brains = self.getImageBrains()
        self.bildrechte = []
        bildrechte = []
        for i in brains:
            entry = {}
            obj = i.getObject()
            if obj.portal_type == 'Image':
                entry['title'] = obj.Title()
                entry['description'] = obj.Description()
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
                titelobj = getattr(obj, u'titelstory')
                magazin['storytitle'] = titelobj.title
                archiv.append(magazin)
        self.archiv = archiv
