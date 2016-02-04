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
from zope.cachedescriptors.property import Lazy
from zope.component import adapts
from zope.interface import implements
from zope.formlib import form
from zope.schema import Bool, Choice
from zope.schema.vocabulary import SimpleTerm, SimpleVocabulary
from gs.content.form.base import radio_widget
from Products.GSGroupMember.interfaces import IGSGroupMembershipStatus
from .interfaces import IGSStatusFormFields, IGSMemberActionsSchema
from . import GSMessageFactory as _

MAX_POSTING_MEMBERS = 5


class GSStatusFormFields(object):
    adapts(IGSGroupMembershipStatus)
    implements(IGSStatusFormFields)

    def __init__(self, status):
        if not IGSGroupMembershipStatus.providedBy(status):
            m = '%s is not a GSGroupMembershipStatus' % status
            raise TypeError(m)

        self.status = status
        self.userInfo = status.userInfo
        self.groupInfo = status.groupInfo
        self.siteInfo = status.siteInfo

    # AM: We're unable to get the logged-in user
    #   in this context. Ideally we would grab
    #   the logged-in user and use their status
    #   to determine whether some actions can be
    #   taken, but that's not currently possible.
    #   Further comments below, where relevant.

    @Lazy
    def allFields(self):
        retval = [self.ptnCoach, self.groupAdmin, self.postingMember,
                  self.moderator, self.moderate, self.remove, self.withdraw]
        return retval

    @Lazy
    def validFields(self):
        retval = [_f for _f in self.allFields if _f]
        return retval

    @Lazy
    def form_fields(self):
        fields = form.Fields(IGSMemberActionsSchema)
        for f in self.validFields:
            fields = form.Fields(fields + form.Fields(f))
            retval = fields.omit('dummy')
        return retval

    @Lazy
    def groupAdmin(self):
        retval = False
        if ((self.status.isSiteAdmin
                or self.status.isNormalMember or self.status.isPtnCoach
                or self.status.isPostingMember or self.status.isModerator)
            and not (self.status.isGroupAdmin or self.status.isModerated
                     or self.status.isOddlyConfigured)):
            t = _('action-group-admin-make', 'Make ${userName} a Group Administrator',
                  mapping={'userName': self.userInfo.name})
            retval = Bool(__name__='%s-groupAdminAdd' % self.userInfo.id,
                          title=t, description=t, required=False)
        # AM: Admins shouldn't be able to revoke the group-admin
        #   status of other admins of the same or higher rank.
        #elif self.status.isGroupAdmin and self.adminUserStatus.isSiteAdmin:
        elif self.status.isGroupAdmin:
            t = _('action-group-admin-revoke',
                  'Remove the Group Administrator privileges from ${userName}',
                  mapping={'userName': self.userInfo.name})
            retval = Bool(__name__='%s-groupAdminRemove' % self.userInfo.id,
                          title=t, description=t, required=False)
        return retval

    @Lazy
    def ptnCoach(self):
        retval = False
        if (not(self.status.postingIsSpecial)
            and (self.status.isNormalMember or self.status.isSiteAdmin
                 or self.status.isGroupAdmin or self.status.isModerator)
            and not (self.status.isPtnCoach or self.status.isModerated
                     or self.status.isOddlyConfigured)):
            t = _('action-ptn-coach', 'Make ${userName} the Participation Coach',
                  mapping={'userName': self.userInfo.name})
            ptnCoachTerm = SimpleTerm(True, True, t)
            ptnCoachVocab = SimpleVocabulary([ptnCoachTerm])
            n = '%s-ptnCoach' % self.userInfo.id
            retval = form.Fields(Choice(__name__=n,
                                        vocabulary=ptnCoachVocab,
                                        required=False),
                                 custom_widget=radio_widget)
        return retval

    @Lazy
    def moderator(self):
        retval = False
        if (self.status.groupIsModerated
            and not (self.status.isModerator or self.status.isModerated
                     or self.status.isInvited or self.status.isUnverified
                     or self.status.isOddlyConfigured)):
            t = _('action-moderator-make',
                  'Make ${userName} a Moderator for this group',
                  mapping={'userName': self.userInfo.name})
            retval = Bool(__name__='%s-moderatorAdd' % self.userInfo.id,
                          title=t, description=t, required=False)
        elif self.status.groupIsModerated and self.status.isModerator:
            t = _('action-moderator-revoke',
                  'Revoke Moderator status from ${userName}',
                  mapping={'userName': self.userInfo.name})
            retval = Bool(__name__='%s-moderatorRemove' % self.userInfo.id,
                          title=t, description=t, required=False)
        return retval

    @Lazy
    def moderate(self):
        retval = False
        if self.status.groupIsModerated and self.status.isNormalMember:
            t = _('action-moderated-make',
                  'Start moderating messages from ${userName}',
                  mapping={'userName': self.userInfo.name})
            retval = Bool(__name__='%s-moderatedAdd' % self.userInfo.id,
                          title=t, description=t, required=False)
        elif self.status.groupIsModerated and self.status.isModerated:
            t = _('action-moderated-revoke',
                  'Stop moderating messages from ${userName}',
                  mapping={'userName': self.userInfo.name})
            retval = Bool(__name__='%s-moderatedRemove' % self.userInfo.id,
                          title=t, description=t, required=False)
        return retval

    @Lazy
    def postingMember(self):
        retval = False
        if (self.status.postingIsSpecial and
            (self.status.numPostingMembers < MAX_POSTING_MEMBERS)
            and not (self.status.isPostingMember or self.status.isUnverified
                     or self.status.isOddlyConfigured)):
            t = _('action-posting-make',
                  'Make ${userName} a posting member',
                  mapping={'userName': self.userInfo.name})
            retval = Bool(__name__='%s-postingMemberAdd' % self.userInfo.id,
                          title=t, description=t, required=False)
        elif self.status.postingIsSpecial and self.status.isPostingMember:
            n = '%s-postingMemberRemove' % self.userInfo.id
            t = _('action-posting-revoke',
                  'Revoke posting-member privilages from ${userName}',
                  mapping={'userName': self.userInfo.name})
            retval = Bool(__name__=n, title=t, description=t,
                          required=False)
        return retval

    @Lazy
    def remove(self):
        retval = False
        # AM: Admins shouldn't be able to remove other
        #   admins of the same or higher rank.
        #if not self.status.isSiteAdmin and \
        #  not(self.status.isGroupAdmin and \
        #      self.adminUserStatus.isGroupAdmin):
        if ((not self.status.isSiteAdmin) and (not self.status.isGroupAdmin)
                and (not self.status.isInvited)):
            t = _('action-remove',
                  'Remove ${userName} from the group',
                  mapping={'userName': self.userInfo.name})
            retval = Bool(__name__='%s-remove' % self.userInfo.id,
                          title=t, description=t, required=False)
        return retval

    @Lazy
    def withdraw(self):
        retval = False
        if self.status.isInvited:
            t = _('action-withdraw',
                  'Withdraw the invitation sent to ${userName}',
                  mapping={'userName': self.userInfo.name})
            retval = Bool(__name__='%s-withdraw' % self.userInfo.id,
                          title=t, description=t, required=False)
        return retval
