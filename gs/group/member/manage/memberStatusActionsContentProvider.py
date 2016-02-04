# -*- coding: utf-8 -*-
############################################################################
#
# Copyright © 2014 OnlineGroups.net and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
############################################################################
from __future__ import absolute_import, unicode_literals
from zope.app.pagetemplate import ViewPageTemplateFile
from zope.contentprovider.interfaces import (UpdateNotCalled)
from . import GSMessageFactory as _


class GSMemberStatusActionsContentProvider(object):
    '''Display a group member\'s status and actions to take'''

    def __init__(self, context, request, view):
        self.__parent__ = self.view = view
        self.__updated = False

        self.context = context
        self.request = request

    def update(self):
        self.__updated = True

    def render(self):
        if not self.__updated:
            raise UpdateNotCalled
        pageTemplate = ViewPageTemplateFile(self.pageTemplateFileName)
        retval = pageTemplate(self,
                              view=self)
        return retval

    @staticmethod
    def get_labels(status):
        # --=mpj17=-- Ugly cut-n-paste software engineering from Products.GSGroup
        statuses = []
        if status.isSiteAdmin:
            statuses.append(_('status-site-admin', 'Site Administrator'))
        if status.isGroupAdmin:
            statuses.append(_('status-group-admin', 'Group Administrator'))
        if status.isPtnCoach:
            statuses.append(_('status-ptn-coach', 'Participation Coach'))
        if status.postingIsSpecial and status.isPostingMember:
            statuses.append(_('status-posting-member', 'Posting Member'))
        if status.isModerator:
            statuses.append(_('status-moderator', 'Moderator'))
        if status.isModerated:
            statuses.append(_('status-moderated', 'Moderated Member'))
        if status.isBlocked:
            statuses.append(_('status-blocked', 'Blocked Member'))
        if status.isConfused:
            label = _('status-confused', 'Invited Member (despite already being in the group)')
            statuses.append(label)
        elif status.isInvited:
            statuses.append(_('status-invited', 'Invited Member'))

        if status.isUnverified:
            statuses.append(_('status-unverified', 'Lacks a verified email addresses'))

        if statuses == []:
            assert status.isNormalMember
            statuses.append(_('status-normal', 'Normal Member'))
        if status.isOddlyConfigured:
            statuses.insert(0, _('status-odd', 'Oddly Configured Member'))
        return statuses
