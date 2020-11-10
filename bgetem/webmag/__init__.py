# -*- coding: utf-8 -*-

import logging
from nva.magazinfolder.interfaces import IMagazinFolder


logger = logging.getLogger('uvcsite.bgetem.webmag')


def log(message, summary='', severity=logging.DEBUG):
    logger.log(severity, '%s %s', summary, message)


def get_webmag(node, iface=IMagazinFolder):
    parent = node
    while parent is not None:
        if iface.providedBy(parent):
            return parent
        else:
            parent = getattr(parent, '__parent__', None)    
    return None
