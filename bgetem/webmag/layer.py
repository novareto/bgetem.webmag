# -*- coding: utf-8 -*-

from zope.component.hooks import getSite
from zope.component import getMultiAdapter
from zope.interface import directlyProvidedBy, directlyProvides, Interface
from zope.publisher.interfaces.browser import IBrowserRequest
from Products.CMFCore.interfaces import ISiteRoot
from zope.traversing.interfaces import IBeforeTraverseEvent
from ZPublisher.interfaces import IPubAfterTraversal
from five import grok
from plone.app.contenttypes.interfaces import IFolder
from Products.CMFCore.interfaces import ISiteRoot
from ZPublisher.pubevents import IPubAfterTraversal


class IWebmag(IFolder, ISiteRoot):
    pass


class IAnonymousLayer(IBrowserRequest):
    pass


def switch_skin(content, event):
    print "IA AM CALLED FORM", content
    site = getSite()
    request = event.request
    if '__ac' not in request.get('HTTP_COOKIE', ''):
        ifaces = [IAnonymousLayer] + list(directlyProvidedBy(request))
        directlyProvides(request, *ifaces)
    else:
        print "ANON REQ"
