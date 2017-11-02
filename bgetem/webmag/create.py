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
    content.create(type="Folder", title="ETEM +", container=folder)
    content.create(type="Folder", title="TitelStories", container=folder)
    # --> TitelStories Folder --->
    #
