# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright © 2013, 2016 OnlineGroups.net and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
from __future__ import unicode_literals, absolute_import, print_function
from pytz import UTC
from datetime import datetime
from zope.cachedescriptors.property import Lazy
from zope.component import createObject
from zope.component.interfaces import IFactory
from zope.interface import implementer, implementedBy
from Products.XWFCore.XWFUtils import munge_date
from Products.CustomUserFolder.userinfo import userInfo_to_anchor
from Products.GSGroup.groupInfo import groupInfo_to_anchor
from Products.GSAuditTrail import IAuditEvent, BasicAuditEvent, AuditQuery
from Products.GSAuditTrail.utils import event_id_from_data

SUBSYSTEM = 'groupserver.GSGroupMemberStatus'
import logging
log = logging.getLogger(SUBSYSTEM)

UNKNOWN = '0'  # Unknown is always "0"
GAIN = '1'
LOSE = '2'


@implementer(IFactory)
class StatusAuditEventFactory(object):
    """A Factory for member status events."""
    title = 'GroupServer Group Status Audit Event Factory'
    description = 'Creates a GroupServer event auditor for group status changes'

    def __call__(self, context, event_id, code, date, userInfo, instanceUserInfo, siteInfo,
                 groupInfo, instanceDatum='', supplementaryDatum='', subsystem=''):
        """Create an event"""
        assert subsystem == SUBSYSTEM, 'Subsystems do not match'

        if (code == GAIN):
            event = GainStatusEvent(context, event_id, date, userInfo, instanceUserInfo, siteInfo,
                                    groupInfo, instanceDatum)
        elif (code == LOSE):
            event = LoseStatusEvent(context, event_id, date, userInfo, instanceUserInfo, siteInfo,
                                    groupInfo, instanceDatum)
        else:
            event = BasicAuditEvent(context, event_id, UNKNOWN, date, userInfo, instanceUserInfo,
                                    siteInfo, groupInfo, instanceDatum, supplementaryDatum,
                                    SUBSYSTEM)
        assert event
        return event

    def getInterfaces(self):
        return implementedBy(BasicAuditEvent)


@implementer(IAuditEvent)
class GainStatusEvent(BasicAuditEvent):
    'An audit-trail event representing a group member gaining aparticular status within the group'
    def __init__(self, context, id, d, userInfo, instanceUserInfo, siteInfo, groupInfo,
                 instanceDatum):
        """ Create a gain-status event"""
        super(GainStatusEvent, self).__init__(context, id, GAIN, d, userInfo, instanceUserInfo,
                                              siteInfo, groupInfo, instanceDatum, None, SUBSYSTEM)

    def __unicode__(self):
        r = '{0} ({1}) gave {2} ({3}) the status of {4} in {5} ({6}) on {7} ({8}).'
        retval = r.format(
            self.userInfo.name, self.userInfo.id,
            self.instanceUserInfo.name, self.instanceUserInfo.id,
            self.instanceDatum,
            self.groupInfo.name, self.groupInfo.id,
            self.siteInfo.name, self.siteInfo.id)
        return retval

    @property
    def xhtml(self):
        cssClass = 'audit-event groupserver-group-member-%s' % self.code
        retval = '<span class="%s">Given the status of %s in %s</span>' % \
            (cssClass, self.instanceDatum, groupInfo_to_anchor(self.groupInfo))

        if self.instanceUserInfo.id != self.userInfo.id:
            retval = '%s &#8212; %s' % (retval, userInfo_to_anchor(self.userInfo))
        retval = '%s (%s)' % (retval, munge_date(self.context, self.date))
        return retval


@implementer(IAuditEvent)
class LoseStatusEvent(BasicAuditEvent):
    'An audit-trail event representing a group member losing aparticular status within a group'
    def __init__(self, context, id, d, userInfo, instanceUserInfo, siteInfo, groupInfo,
                 instanceDatum):
        """ Create a lose-status event"""
        super(LoseStatusEvent, self).__init__(context, id, LOSE, d, userInfo, instanceUserInfo,
                                              siteInfo, groupInfo, instanceDatum, None, SUBSYSTEM)

    @property
    def adminRemoved(self):
        retval = False
        if self.userInfo.id and self.userInfo.id != self.instanceUserInfo.id:
            retval = True
        return retval

    def __unicode__(self):
        if self.adminRemoved:
            retval = '%s (%s) removed the status of %s from %s (%s) in %s (%s) on %s (%s).' % (
                self.userInfo.name, self.userInfo.id,
                self.instanceDatum,
                self.instanceUserInfo.name, self.instanceUserInfo.id,
                self.groupInfo.name, self.groupInfo.id,
                self.siteInfo.name, self.siteInfo.id)
        else:
            retval = '%s (%s) lost the status of %s in %s (%s) on %s (%s).' % (
                self.instanceUserInfo.name, self.instanceUserInfo.id,
                self.instanceDatum,
                self.groupInfo.name, self.groupInfo.id,
                self.siteInfo.name, self.siteInfo.id)
        retval = retval.encode('ascii', 'ignore')
        return retval

    @property
    def xhtml(self):
        cssClass = 'audit-event groupserver-group-member-%s' % self.code
        retval = '<span class="%s">Lost the status of %s in %s</span>' % (
            cssClass, self.instanceDatum, groupInfo_to_anchor(self.groupInfo))

        if self.instanceUserInfo.id != self.userInfo.id:
            retval = '%s &#8212; %s' % (retval, userInfo_to_anchor(self.userInfo))
        retval = '%s (%s)' % (retval, munge_date(self.context, self.date))
        return retval


class StatusAuditor(object):
    """An auditor for group status."""
    def __init__(self, context, instanceUserInfo):
        """Create a status auditor.
        """
        self.context = context
        self.instanceUserInfo = instanceUserInfo

    @Lazy
    def userInfo(self):
        retval = createObject('groupserver.LoggedInUser', self.context)
        return retval

    @Lazy
    def siteInfo(self):
        retval = createObject('groupserver.SiteInfo', self.context)
        return retval

    @Lazy
    def groupInfo(self):
        retval = createObject('groupserver.GroupInfo', self.context)
        return retval

    @Lazy
    def factory(self):
        retval = StatusAuditEventFactory()
        return retval

    @Lazy
    def queries(self):
        retval = AuditQuery()
        return retval

    def info(self, code, instanceDatum='', supplementaryDatum=''):
        """Log an info event to the audit trail.
            * Creates an ID for the new event,
            * Writes the instantiated event to the audit-table, and
            * Writes the event to the standard Python log.
        """
        d = datetime.now(UTC)
        eventId = event_id_from_data(self.userInfo, self.instanceUserInfo, self.siteInfo, code,
                                     instanceDatum,
                                     '%s-%s' % (self.groupInfo.name, self.groupInfo.id))

        e = self.factory(self.context, eventId, code, d, self.userInfo, self.instanceUserInfo,
                         self.siteInfo, self.groupInfo, instanceDatum, None, SUBSYSTEM)

        self.queries.store(e)
        log.info(e)
        return e
