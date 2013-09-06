# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright © 2013 OnlineGroups.net and Contributors.
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
from zope.component import createObject
from zope.cachedescriptors.property import Lazy
from gs.group.member.viewlet import GroupAdminViewlet
SOME = 127  # TODO: Make SOME an option


class MembersListViewlet(GroupAdminViewlet):
    '''Base class'''

    @Lazy
    def memberCount(self):
        acl_users = self.context.acl_users
        assert acl_users, 'Aquisition bites'
        userGroupId = '%s_member' % self.groupInfo.id
        userGroup = acl_users.getGroupById(userGroupId)
        retval = len(userGroup.getUsers())
        return retval

    @Lazy
    def isModerated(self):
        mailingListInfo = createObject('groupserver.MailingListInfo',
                                       self.context)
        retval = mailingListInfo.is_moderated
        return retval


class FewMembersListViewlet(MembersListViewlet):

    @Lazy
    def show(self):
        retval = self.memberCount < (SOME // 8)
        return retval


class OptionsMembersListViewlet(MembersListViewlet):

    @Lazy
    def show(self):
        retval = self.memberCount >= (SOME // 8)
        return retval

    @Lazy
    def many(self):
        retval = (self.memberCount > 0) and (self.memberCount < SOME)
        return retval

    @Lazy
    def link(self):
        retval = self.many_link if self.many else self.some_link
        return retval

    @Lazy
    def many_link(self):
        # FIXME: Create a new Manage Many Members page
        m = u'{0.relativeURL}/admingroup/manage_many_members'
        retval = m.format(self.groupInfo)
        return retval

    @Lazy
    def some_link(self):
        m = u'{0.relativeURL}/managemembers.html'
        retval = m.format(self.groupInfo)
        return retval
