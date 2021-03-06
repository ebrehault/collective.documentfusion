# -*- coding: utf-8 -*-
"""Init and utils."""
import logging

logger = logging.getLogger('collective.documentfusion')

from zope.i18nmessageid import MessageFactory

_ = MessageFactory('collective.documentfusion')


def initialize(context):
    """Initializer called when used as a Zope 2 product."""
