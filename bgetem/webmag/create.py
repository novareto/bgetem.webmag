# -*- coding: utf-8 -*-
# # Copyright (c) 2007-2013 NovaReto GmbH
# # cklinger@novareto.de
#

from uvc.api import api
from plone.api import content
from nva.magazinfolder.interfaces import IMagazinFolder
from zope.lifecycleevent.interfaces import IObjectAddedEvent


@api.subscribe(IMagazinFolder, IObjectAddedEvent)
def handle(folder, event):
    content.create(type="Folder", id="titelstories", title=u"Bühnen-Beiträge", container=folder)
    content.create(type="Folder", title=u"ETEM +", container=folder)
    content.create(type="Folder", title=u"Themen", container=folder)
    content.create(type="Folder", title=u"Kampagnen", container=folder)
    content.create(type="Folder", title=u"Medien dieser Ausgabe", container=folder)
    # --> TitelStories Folder --->
    #
