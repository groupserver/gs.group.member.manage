# -*- coding: utf-8 -*-
############################################################################
#
# Copyright © 2014, 2015 OnlineGroups.net and Contributors.
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
from __future__ import absolute_import, unicode_literals, print_function
from math import ceil
from operator import attrgetter
from zope.cachedescriptors.property import Lazy
from zope.component import createObject
from zope.i18n import translate
from zope.formlib import form
from Products.XWFCore.odict import ODict
from Products.GSGroup.mailinglistinfo import GSMailingListInfo
from gs.content.form.base import radio_widget
from gs.group.member.base.info import GroupMembersInfo
from gs.group.member.leave.base.leaver import GroupLeaver
from gs.group.type.announcement.interfaces import IGSAnnouncementGroup
from gs.group.member.manage import MANY
from .actions import GSMemberStatusActions
from .statusformfields import MAX_POSTING_MEMBERS
from .interfaces import IGSManageMembersForm
from .utils import (
    addAdmin, removeAdmin, addModerator, removeModerator, moderate, unmoderate, addPostingMember,
    removePostingMember, addPtnCoach, removePtnCoach, withdrawInvitation)
from . import GSMessageFactory as _


class GSGroupMemberManager(object):
    def __init__(self, group, page, showOnly=None):
        self.group = group
        self.showOnly = showOnly
        self.page = int(page)
        self.totalPages = 0
        self.toChange = self.cancelledChanges = {}
        self.changesByMember = {}
        self.changesByAction = {}
        self.changeLog = ODict()
        self.summary = ''''''
        self.firstPageLink = self.prevPageLink = self.nextPageLink = None
        self.lastPageLink = None
        # --=mpj17=-- These are deliberately not @Lazy.
        # See self.make_changes
        self.__membersInfo = self.__members = None
        self.__membersRequested = self.__membersToShow = None
        self.__memberStatusActions = self.__form_fields = None

    @Lazy
    def siteInfo(self):
        retval = createObject('groupserver.SiteInfo', self.group)
        return retval

    @Lazy
    def groupInfo(self):
        retval = createObject('groupserver.GroupInfo', self.group)
        return retval

    @Lazy
    def mailingListInfo(self):
        retval = createObject('groupserver.MailingListInfo', self.group)
        return retval

    @Lazy
    def groupIsModerated(self):
        retval = self.mailingListInfo.is_moderated
        return retval

    @Lazy
    def postingIsSpecial(self):
        retval = ((IGSAnnouncementGroup.providedBy(self.group)) or
                  (self.groupInfo.group_type == 'announcement'))
        return retval

    @Lazy
    def isLargeGroup(self):
        retval = False
        if (len(self.membersInfo.fullMembers) >= MANY):
            retval = True
        return retval

    @property
    def membersInfo(self):
        if self.__membersInfo is None:
            self.__membersInfo = GroupMembersInfo(self.group)
        return self.__membersInfo

    @property
    def membersToShow(self):
        if self.__membersToShow is None:
            numRequested = len(self.membersRequested)
            if numRequested > MANY:
                currentBatch = self.page - 1
                startIndex = MANY * currentBatch
                endIndex = startIndex + MANY
                self.__membersToShow =\
                    self.membersRequested[startIndex:endIndex]
                n = float(numRequested) / MANY
                self.totalPages = int(ceil(n))
                self.firstPageLink = 1 if (self.page > 1) else 0
                self.lastPageLink = self.totalPages if (self.page < self.totalPages) else 0
                self.prevPageLink = (self.page - 1) if (self.page > 1) else 0
                self.nextPageLink = (self.page + 1) if (self.page < self.totalPages) else 0
            else:
                self.__membersToShow = self.membersRequested
        return self.__membersToShow

    @property
    def membersRequested(self):
        if self.__membersRequested is None:
            if not self.showOnly:
                self.__membersRequested = self.membersInfo.members
            elif len(self.showOnly.split(' ')) > 1:
                userIds = set(self.showOnly.split(' '))
                toDisplay = userIds.intersection(self.membersInfo.members.allMemberIds)
                self.__membersRequested = [createObject('groupserver.UserFromId', self.group, uId)
                                           for uId in toDisplay]
            elif self.showOnly in [m.id for m in self.membersInfo.members]:
                self.__membersRequested = \
                    [m for m in self.membersInfo.members
                     if m.id == self.showOnly]
            elif self.showOnly == 'posting' and self.postingIsSpecial:
                self.__membersRequested = self.membersInfo.postingMembers
            elif self.showOnly == 'invited':
                self.__membersRequested = self.membersInfo.invitedMembers
            elif self.showOnly == 'managers':
                self.__membersRequested = self.membersInfo.managers
            elif self.showOnly == 'moderated':
                self.__membersRequested = self.membersInfo.moderatees
            elif self.showOnly == 'unverified':
                self.__membersRequested = self.membersInfo.unverifiedMembers
            else:
                self.__membersRequested = []
        retval = list(self.__membersRequested)
        retval.sort(key=attrgetter('name'))
        return retval

    @property
    def memberStatusActions(self):
        if self.__memberStatusActions is None:
            self.__memberStatusActions = [GSMemberStatusActions(m, self.membersInfo)
                                          for m in self.membersToShow]
        return self.__memberStatusActions

    @property
    def form_fields(self):
        if self.__form_fields is None:
            fields = form.Fields(IGSManageMembersForm)
            for m in self.memberStatusActions:
                fields = form.Fields(fields + form.Fields(m.form_fields))
            fields['ptnCoachRemove'].custom_widget = radio_widget
            self.__form_fields = fields
        return self.__form_fields

    def make_changes(self, data):
        '''Set the membership data

        DESCRIPTION
            Updates the status of members within the group.

        ARGUMENTS
            A dict. The keys must match the IDs of the attributes in
            the manage members form (which should not be too hard, as
            this is done automatically by Formlib).

        SIDE EFFECTS
            Resets the member and form fields caches.
        '''
        changes = [k for k in list(data.keys()) if data.get(k)]
        self.marshallChanges(changes)
        self.set_data()

        # Reset the caches so that we get the member
        # data afresh when the form reloads.
        self.__membersInfo = None
        self.__membersToShow = None
        self.__membersRequested = None
        self.__memberStatusActions = None
        self.__form_fields = None
        return self.summary

    def marshallChanges(self, changes):
        if 'ptnCoachRemove' in changes:
            self.toChange['ptnCoachToRemove'] = True
            changes.remove('ptnCoachRemove')
        actions = [
            'ptnCoach', 'groupAdminAdd', 'groupAdminRemove', 'moderatorAdd', 'moderatorRemove',
            'moderatedAdd', 'moderatedRemove', 'postingMemberAdd', 'postingMemberRemove', 'remove',
            'withdraw']
        for a in actions:
            aLength = len(a)
            requests = [k.split('-%s' % a)[0] for k in changes
                        if k[-aLength:] == a]
            if requests:
                self.toChange[a] = requests
        self.sanitiseChanges()
        self.organiseChanges()

    def sanitiseChanges(self):
        ''' Sanity-check and clean up all the requested changes. '''
        self.cleanRemovals()
        self.cleanPtnCoach()
        self.cleanPosting()
        self.cleanModeration()

    def cleanRemovals(self):
        ''' For members to be removed, cancel all other actions.'''
        actions = self.toChange
        f = lambda x: (x != 'remove') and (x != 'ptnCoachToRemove')
        for mId in actions.get('remove', []):
            for a in filter(f, list(actions.keys())):
                members = actions.get(a, [])
                if mId in members:
                    members.remove(mId)
                    self.toChange[a] = members

    def cleanPtnCoach(self):
        ''' If more than one ptnCoach was specified, then cancel the
        change.'''
        ptnCoachToAdd = self.toChange.get('ptnCoach', [])
        if ptnCoachToAdd and (len(ptnCoachToAdd) > 1):
            self.cancelledChanges['ptnCoach'] = ptnCoachToAdd
            self.toChange.pop('ptnCoach')
        elif len(ptnCoachToAdd) == 1:
            self.toChange['ptnCoach'] = ptnCoachToAdd[0]
            # The only reason to do this would be so we can explicitly log
            # that the previous PtnCoach has been removed. Do we bother? I
            # don't think so.
            #if self.groupInfo.ptn_coach:
            #    self.toChange['ptnCoachToRemove'] = True

    def cleanPosting(self):
        ''' Check for the number of posting members exceeding the
        maximum.'''
        if self.postingIsSpecial:
            listInfo = GSMailingListInfo(self.groupInfo.groupObj)
            numCurrentPostingMembers = len(listInfo.posting_members)
            numPostingMembersToRemove = \
                len(self.toChange.get('postingMemberRemove', []))
            numPostingMembersToAdd = \
                len(self.toChange.get('postingMemberAdd', []))
            totalPostingMembersToBe = \
                (numCurrentPostingMembers - numPostingMembersToRemove
                 + numPostingMembersToAdd)
            if totalPostingMembersToBe > MAX_POSTING_MEMBERS:
                numAddedMembersToCut = \
                    (totalPostingMembersToBe - MAX_POSTING_MEMBERS)
                membersToAdd = self.toChange['postingMemberAdd']
                addedMembersToCut = membersToAdd[-numAddedMembersToCut:]
                self.cancelledChanges['postingMember'] = addedMembersToCut
                index = (len(membersToAdd) - len(addedMembersToCut))
                self.toChange['postingMemberAdd'] = membersToAdd[:index]

    def cleanModeration(self):
        ''' Check for members being set as both a moderator and
        moderated.'''
        toBeModerated = self.toChange.get('moderatedAdd', [])
        toBeModerators = self.toChange.get('moderatorAdd', [])
        doubleModerated = \
            [mId for mId in toBeModerators if mId in toBeModerated]
        if doubleModerated:
            self.cancelledChanges['doubleModeration'] = doubleModerated
        for mId in doubleModerated:
            toBeModerated.remove(mId)
            toBeModerators.remove(mId)
        if toBeModerated:
            self.toChange['moderatedAdd'] = toBeModerated
        elif 'moderatedAdd' in self.toChange:
            self.toChange.pop('moderatedAdd')
        if toBeModerators:
            self.toChange['moderatorAdd'] = toBeModerators
        elif 'moderatorAdd' in self.toChange:
            self.toChange.pop('moderatorAdd')

    def organiseChanges(self):
        '''Organise self.toChange into self.changesByMember and self.changesByAction'''
        actions = ['remove', 'postingMemberRemove', 'ptnCoachToRemove', 'ptnCoach']
        for a in actions:
            if self.toChange.get(a, None):
                self.changesByAction[a] = self.toChange.pop(a)
        for k, mIds in list(self.toChange.items()):
            for mId in mIds:
                if mId not in self.changesByMember:
                    self.changesByMember[mId] = [k]
                else:
                    self.changesByMember[mId].append(k)

    def set_data(self):
        self.summariseCancellations()
        self.removeMembers()
        self.removePostingMembers()
        self.removePtnCoach()
        self.addPtnCoach()
        self.makeChangesByMember()
        self.finishSummary()

    def summariseCancellations(self):
        ''' Summarise actions not taken. '''
        self.summariseCancelledPtnCoach()
        self.summariseDoubleModeration()
        self.summarisePostingMember()

    def summariseCancelledPtnCoach(self):
        if 'ptnCoach' in self.cancelledChanges:
            attemptedChangeIds = self.cancelledChanges['ptnCoach']
            attemptedChangeUsers = [createObject('groupserver.UserFromId', self.group, a)
                                    for a in attemptedChangeIds]
            items = ['<li><a href="%s">%s</a></li>' % (m.url, m.name)
                     for m in attemptedChangeUsers]
            names = '<ul>\n{0}</ul>'.format('\n'.join(items))
            s = _('change-cancelled-ptn-coach',
                  '<p>The Participation Coach was <b>unchanged</b>, because there can be only one '
                  'and you specified ${n}:</p> ${userNames}',
                  mapping={'n': len(attemptedChangeIds),
                           'userNames': names})
            self.summary += translate(s)

    def summariseDoubleModeration(self):
        if 'doubleModeration' in self.cancelledChanges:
            attemptedChangeIds = self.cancelledChanges['doubleModeration']
            attemptedChangeUsers = [createObject('groupserver.UserFromId', self.group, a)
                                    for a in attemptedChangeIds]
            if (len(attemptedChangeIds) == 1):
                s = _('change-cancelled-double-moderation-1',
                      '<p>The moderation level of ${userName} is <b>unchanged</b>, '
                      'because a group member cannot be both moderated and a moderator.</p>',
                      mapping={'userName': attemptedChangeUsers[0].name})
            else:  # > 1
                items = ['<li><a href="%s">%s</a></li>' % (m.url, m.name)
                         for m in attemptedChangeUsers]
                names = '<ul>\n{0}</ul>'.format('\n'.join(items))
                s = _('change-cancelled-double-moderation-m',
                      '<p>The moderation level of the following members are <b>unchanged</b>, '
                      'because a group member cannot be both moderated and a moderator:</p>'
                      '${userNames}',
                      mapping={'userNames': names})
            self.summary += translate(s)

    def summarisePostingMember(self):
        if 'postingMember' in self.cancelledChanges:
            attemptedChangeIds = self.cancelledChanges['postingMember']
            attemptedChangeUsers = [createObject('groupserver.UserFromId', self.group, a)
                                    for a in attemptedChangeIds]
            if (len(attemptedChangeIds) == 1):
                s = _('change-cancelled-posting-1',
                      '<p>The member ${userName} <b>remains a non-posting member,</b> because '
                      'otherwise the maximum of ${n} posting members would have been exceeded.</p>',
                      mapping={'n': MAX_POSTING_MEMBERS,
                               'userName': attemptedChangeUsers[0].name})
            else:  # > 1
                items = ['<li><a href="%s">%s</a></li>' % (m.url, m.name)
                         for m in attemptedChangeUsers]
                names = '<ul>\n{0}</ul>'.format('\n'.join(items))
                s = _('change-cancelled-posting-n',
                      '<p>The following members <b>remain non-posting members,</b> because '
                      'otherwise the maximum of ${n} posting members would have been exceeded:</p>'
                      '${userNames}',
                      mapping={'n': MAX_POSTING_MEMBERS,
                               'userNames': names})
            self.summary += translate(s)

    def removeMembers(self):
        ''' Remove all the members to be removed.'''
        for memberId in self.changesByAction.get('remove', []):
            userInfo = createObject('groupserver.UserFromId', self.group,
                                    memberId)
            leaver = GroupLeaver(self.groupInfo, userInfo)
            self.changeLog[memberId] = leaver.removeMember()

    def removePostingMembers(self):
        ''' Remove all the posting members to be removed. '''
        for memberId in self.changesByAction.get('postingMemberRemove', []):
            userInfo = createObject('groupserver.UserFromId', self.group,
                                    memberId)
            change = removePostingMember(self.groupInfo, userInfo)
            if memberId not in self.changeLog:
                self.changeLog[memberId] = [change]
            else:
                self.changeLog[memberId].append(change)

    def removePtnCoach(self):
        if self.changesByAction.get('ptnCoachToRemove', False):
            change, oldCoachId = removePtnCoach(self.groupInfo)
            if change:
                if oldCoachId not in self.changeLog:
                    self.changeLog[oldCoachId] = [change]
                else:
                    self.changeLog[oldCoachId].append(change)

    def addPtnCoach(self):
        ptnCoachToAdd = self.changesByAction.get('ptnCoach', None)
        if ptnCoachToAdd:
            userInfo = createObject('groupserver.UserFromId', self.group,
                                    ptnCoachToAdd)
            change = addPtnCoach(self.groupInfo, userInfo)
            if ptnCoachToAdd not in self.changeLog:
                self.changeLog[ptnCoachToAdd] = [change]
            else:
                self.changeLog[ptnCoachToAdd].append(change)

    def makeChangesByMember(self):
        for memberId in list(self.changesByMember.keys()):
            userInfo = createObject('groupserver.UserFromId', self.group,
                                    memberId)
            actions = self.changesByMember[memberId]
            if memberId not in self.changeLog:
                self.changeLog[memberId] = []
            if 'withdraw' in actions:
                wi = withdrawInvitation(self.groupInfo, userInfo)
                self.changeLog[memberId].append(wi)
            if 'groupAdminAdd' in actions:
                aa = addAdmin(self.groupInfo, userInfo)
                self.changeLog[memberId].append(aa)
            if 'groupAdminRemove' in actions:
                ra = removeAdmin(self.groupInfo, userInfo)
                self.changeLog[memberId].append(ra)
            if 'moderatorAdd' in actions:
                am = addModerator(self.groupInfo, userInfo)
                self.changeLog[memberId].append(am)
            if 'moderatorRemove' in actions:
                rm = removeModerator(self.groupInfo, userInfo)
                self.changeLog[memberId].append(rm)
            if 'moderatedAdd' in actions:
                m = moderate(self.groupInfo, userInfo)
                self.changeLog[memberId].append(m)
            if 'moderatedRemove' in actions:
                u = unmoderate(self.groupInfo, userInfo)
                self.changeLog[memberId].append(u)
            if 'postingMemberAdd' in actions:
                apm = addPostingMember(self.groupInfo, userInfo)
                self.changeLog[memberId].append(apm)

    def finishSummary(self):
        for memberId in list(self.changeLog.keys()):
            userInfo = createObject('groupserver.UserFromId', self.group,
                                    memberId)
            userName = '<a href="%s">%s</a>' % (userInfo.url, userInfo.name)
            c = '\n'.join(['<li>%s</li>' % change
                           for change in self.changeLog[memberId]])
            changes = '<ul>\n{0}</ul>'.format(c)
            s = _('change-summary',
                  '<p>${userName} has undergone the following changes:</p>${changes}',
                  mapping={'userName': userName, 'changes': changes})
            self.summary += translate(s)
