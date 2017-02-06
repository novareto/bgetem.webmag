import logging
logger = logging.getLogger('uvcsite.bgetem.webmag')

def log(message, summary='', severity=logging.DEBUG):
    logger.log(severity, '%s %s', summary, message)
