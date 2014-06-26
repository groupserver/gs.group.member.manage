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
from __future__ import absolute_import, unicode_literals
from zope.cachedescriptors.property import Lazy
from zope.interface import implements
from zope.component import createObject
from zope.schema.vocabulary import SimpleTerm
from zope.schema.interfaces import IVocabulary, IVocabularyTokenized
from zope.interface.common.mapping import IEnumerableMapping
from gs.group.member.base import get_group_userids
from gs.profile.email.base.emailuser import EmailUser


class MembersToManage(object):
    implements(IVocabulary, IVocabularyTokenized)
    __used_for__ = IEnumerableMapping

    def __init__(self, context):
        self.context = context

    @Lazy
    def memberIds(self):
        retval = get_group_userids(self.context, self.context.getId())
        return retval

    def get_email_user(self, userId):
        ui = createObject('groupserver.UserFromId', self.context, userId)
        retval = EmailUser(self.context, ui)
        return retval

    @property
    def members(self):
        '''Get the members of the the group'''
        for memberId in self.memberIds:
            retval = self.get_email_user(memberId)
            yield retval

    @staticmethod
    def get_display_name(emailUser):
        userInfo = emailUser.userInfo
        addrs = emailUser.get_addresses()
        addr = addrs[0] if addrs else 'No email address!'
        r = '{0} (<code class="email">{1}</code>)'
        retval = r.format(userInfo.name, addr)
        return retval

    def __iter__(self):
        """See zope.schema.interfaces.IIterableVocabulary"""
        for eu in self.members:
            uid = eu.userInfo.id
            term = SimpleTerm(uid, uid, self.get_display_name(eu))
            yield(term)

    def __len__(self):
        """See zope.schema.interfaces.IIterableVocabulary"""
        return len(self.members)

    def __contains__(self, value):
        """See zope.schema.interfaces.IBaseVocabulary"""
        retval = value in self.memberIds
        assert type(retval) == bool
        return retval

    def getQuery(self):
        """See zope.schema.interfaces.IBaseVocabulary"""
        return None

    def getTerm(self, value):
        """See zope.schema.interfaces.IBaseVocabulary"""
        return self.getTermByToken(value)

    def getTermByToken(self, token):
        """See zope.schema.interfaces.IVocabularyTokenized"""
        if token not in self:
            raise LookupError(token)
        eu = self.get_email_user(token)
        retval = SimpleTerm(token, token, self.get_display_name(eu))
        return retval
