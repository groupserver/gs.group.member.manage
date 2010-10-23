# coding=utf-8
from math import ceil
from zope.component import createObject
from zope.interface import implements
from zope.formlib import form
from Products.XWFCore.odict import ODict
from Products.XWFCore.XWFUtils import comma_comma_and
from Products.GSGroup.mailinglistinfo import GSMailingListInfo
from gs.content.form.radio import radio_widget
from gs.group.member.leave.leaver import GroupLeaver
from Products.GSGroupMember.groupMembersInfo import GSGroupMembersInfo
from gs.group.member.manage.statusformfields import MAX_POSTING_MEMBERS
from gs.group.member.manage.actions import GSMemberStatusActions
from gs.group.member.manage.interfaces import IGSGroupMemberManager
from gs.group.member.manage.interfaces import IGSManageMembersForm
from gs.group.member.manage.utils import addAdmin, removeAdmin, addModerator, removeModerator
from gs.group.member.manage.utils import moderate, unmoderate, addPostingMember, removePostingMember
from gs.group.member.manage.utils import addPtnCoach, removePtnCoach, withdrawInvitation

MAX_TO_SHOW = 20

class GSGroupMemberManager(object):
    implements(IGSGroupMemberManager)
    
    def __init__(self, group, page, showOnly=None):
        self.group = group
        self.showOnly = showOnly
        self.page = int(page)
        self.totalPages = 0
        self.firstPageLink = self.prevPageLink = self.nextPageLink = self.lastPageLink = None
        self.siteInfo = createObject('groupserver.SiteInfo', group)
        self.groupInfo = createObject('groupserver.GroupInfo', group)
        self.mailingListInfo = createObject('groupserver.MailingListInfo', group)
        self.groupIsModerated = self.mailingListInfo.is_moderated
        self.postingIsSpecial = (self.groupInfo.group_type == 'announcement')
        self.__membersInfo = self.__members = None
        self.__membersRequested = self.__membersToShow = None
        self.__memberStatusActions = self.__form_fields = None
        self.toChange = self.cancelledChanges = {}
        self.changesByMember = {}
        self.changesByAction = {}
        self.changeLog = ODict()
        self.summary = ''''''

    @property
    def isLargeGroup(self):
        retval = False
        if self.membersInfo.fullMemberCount > MAX_TO_SHOW:
            retval = True
        return retval
    
    @property
    def membersInfo(self):
        if self.__membersInfo == None:
            self.__membersInfo = GSGroupMembersInfo(self.group)
        return self.__membersInfo

    @property
    def membersToShow(self):
        if self.__membersToShow == None:
            numRequested = len(self.membersRequested)
            if numRequested > MAX_TO_SHOW:
                currentBatch = self.page - 1
                startIndex = MAX_TO_SHOW * currentBatch
                endIndex = startIndex + MAX_TO_SHOW - 1
                self.__membersToShow = self.membersRequested[startIndex:endIndex]
                self.totalPages = int(ceil(float(numRequested)/MAX_TO_SHOW))
                self.firstPageLink = (self.page > 1) and 1 or 0
                self.lastPageLink = (self.page < self.totalPages) and self.totalPages or 0
                self.prevPageLink = (self.page > 1) and (self.page - 1) or 0
                self.nextPageLink = (self.page < self.totalPages) and (self.page + 1) or 0
            else:
                self.__membersToShow = self.membersRequested
        return self.__membersToShow

    @property
    def membersRequested(self):
        if self.__membersRequested == None:
            if not self.showOnly:
                self.__membersRequested = self.membersInfo.members
            elif len(self.showOnly.split(' ')) > 1:
                userIds = self.showOnly.split(' ')
                self.__membersRequested = \
                  [ m for m in self.membersInfo.members if m.id in userIds ]
            elif self.showOnly in [m.id for m in self.membersInfo.members]:
                self.__membersRequested = \
                  [ m for m in self.membersInfo.members if m.id==self.showOnly ]
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
        return self.__membersRequested
    
    @property
    def memberStatusActions(self):
        if self.__memberStatusActions == None:
            self.__memberStatusActions = \
              [ GSMemberStatusActions(m, self.membersInfo)
                for m in self.membersToShow ]
        return self.__memberStatusActions
    
    @property
    def form_fields(self):
        if self.__form_fields == None:
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
        changes = filter(lambda k:data.get(k), data.keys())
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
        actions = ['ptnCoach','groupAdminAdd','groupAdminRemove',
          'moderatorAdd','moderatorRemove','moderatedAdd','moderatedRemove',
          'postingMemberAdd','postingMemberRemove','remove','withdraw']
        for a in actions:
            aLength = len(a)
            requests = [ k.split('-%s' % a)[0] for k in changes 
                if k[-aLength:] == a ]
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
        for mId in actions.get('remove',[]):
            for a in filter(lambda x:(x!='remove' and x!='ptnCoachToRemove'), actions.keys()):
                members = actions.get(a,[])
                if mId in members:
                    members.remove(mId)
                    self.toChange[a] = members

    def cleanPtnCoach(self):
        ''' If more than one ptnCoach was specified, then cancel the change.'''
        ptnCoachToAdd = self.toChange.get('ptnCoach',[])
        if ptnCoachToAdd and (len(ptnCoachToAdd)>1):
            self.cancelledChanges['ptnCoach'] = ptnCoachToAdd
            self.toChange.pop('ptnCoach')
        elif len(ptnCoachToAdd)==1:
            self.toChange['ptnCoach'] = ptnCoachToAdd[0]
            # The only reason to do this would be so we can explicitly log that the
            # previous PtnCoach has been removed. Do we bother? I don't think so.
            #if self.groupInfo.ptn_coach:
            #    self.toChange['ptnCoachToRemove'] = True
    
    def cleanPosting(self):
        ''' Check for the number of posting members exceeding the maximum.'''
        if self.postingIsSpecial:
            listInfo = GSMailingListInfo(self.groupInfo.groupObj)
            numCurrentPostingMembers = len(listInfo.posting_members)
            numPostingMembersToRemove = len(self.toChange.get('postingMemberRemove',[]))
            numPostingMembersToAdd = len(self.toChange.get('postingMemberAdd',[]))
            totalPostingMembersToBe = \
              (numCurrentPostingMembers - numPostingMembersToRemove + numPostingMembersToAdd) 
            if totalPostingMembersToBe > MAX_POSTING_MEMBERS:
                numAddedMembersToCut = (totalPostingMembersToBe-MAX_POSTING_MEMBERS)
                membersToAdd = self.toChange['postingMemberAdd']
                addedMembersToCut = membersToAdd[-numAddedMembersToCut:]
                self.cancelledChanges['postingMember'] = addedMembersToCut
                index = (len(membersToAdd)-len(addedMembersToCut))
                self.toChange['postingMemberAdd'] = membersToAdd[:index]
    
    def cleanModeration(self):
        ''' Check for members being set as both a moderator and moderated.'''
        toBeModerated = self.toChange.get('moderatedAdd',[])
        toBeModerators = self.toChange.get('moderatorAdd',[])
        doubleModerated = \
          [ mId for mId in toBeModerators if mId in toBeModerated ]
        if doubleModerated:
            self.cancelledChanges['doubleModeration'] = doubleModerated
        for mId in doubleModerated:
            toBeModerated.remove(mId)
            toBeModerators.remove(mId)
        if toBeModerated:
            self.toChange['moderatedAdd'] = toBeModerated
        elif self.toChange.has_key('moderatedAdd'):
            self.toChange.pop('moderatedAdd')
        if toBeModerators:
            self.toChange['moderatorAdd'] = toBeModerators
        elif self.toChange.has_key('moderatorAdd'):
            self.toChange.pop('moderatorAdd')
    
    def organiseChanges(self):
        for a in ['remove','postingMemberRemove','ptnCoachToRemove','ptnCoach']:
            if self.toChange.get(a,None):
                self.changesByAction[a] = self.toChange.pop(a)
        for k in self.toChange.keys():
            mIds = self.toChange[k]
            for mId in mIds:
                if not self.changesByMember.has_key(mId):
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
        if self.cancelledChanges.has_key('ptnCoach'):
            attemptedChangeIds = self.cancelledChanges['ptnCoach']
            attemptedChangeUsers = \
              [ createObject('groupserver.UserFromId', self.group, a)
                for a in attemptedChangeIds ]
            attemptedNames = [a.name for a in attemptedChangeUsers ]
            self.summary += '<p>The Participation Coach was <b>not changed</b>, '\
              'because there can be only one and you specified %d (%s).</p>' %\
              (len(attemptedChangeIds), comma_comma_and(attemptedNames))
        
    def summariseDoubleModeration(self):
        if self.cancelledChanges.has_key('doubleModeration'):
            attemptedChangeIds = self.cancelledChanges['doubleModeration']
            attemptedChangeUsers = \
              [ createObject('groupserver.UserFromId', self.group, a)
                for a in attemptedChangeIds ]
            memberMembers = len(attemptedChangeIds)==1 and 'member was' or 'members were'
            self.summary += '<p>The moderation level of the following %s '\
              '<b>not changed</b>, because members cannot be both ' \
              'moderated and moderators:</p><ul>' % memberMembers
            for m in attemptedChangeUsers:
                self.summary += '<li><a href="%s">%s</a></li>' %\
                  (m.url, m.name)
            self.summary += '</ul>'
        
    def summarisePostingMember(self):
        if self.cancelledChanges.has_key('postingMember'):
            attemptedChangeIds = self.cancelledChanges['postingMember']
            attemptedChangeUsers = \
              [ createObject('groupserver.UserFromId', self.group, a)
                for a in attemptedChangeIds ]
            indefiniteArticle = len(attemptedChangeIds)==1 and 'a ' or ''
            memberMembers = len(attemptedChangeIds)==1 and 'member' or 'members'
            self.summary += '<p>The following %s <b>did not become</b> %s'\
              'posting %s, because otherwise the maximum of %d ' \
              'posting members would have been exceeded:</p><ul>' %\
               (memberMembers, indefiniteArticle, 
                memberMembers, MAX_POSTING_MEMBERS)
            for m in attemptedChangeUsers:
                self.summary += '<li><a href="%s">%s</a></li>' %\
                  (m.url, m.name)
            self.summary += '</ul>'
        
    def removeMembers(self):
        ''' Remove all the members to be removed.'''
        for memberId in self.changesByAction.get('remove',[]):
            userInfo = createObject('groupserver.UserFromId', self.group, memberId)
            leaver = GroupLeaver(self.groupInfo, userInfo)
            self.changeLog[memberId] = leaver.removeMember()
        
    def removePostingMembers(self):
        ''' Remove all the posting members to be removed. '''
        for memberId in self.changesByAction.get('postingMemberRemove',[]):
            userInfo = createObject('groupserver.UserFromId', self.group, memberId)
            change = removePostingMember(self.groupInfo, userInfo)
            if not self.changeLog.has_key(memberId):
                self.changeLog[memberId] = [change]
            else:
                self.changeLog[memberId].append(change)
        
    def removePtnCoach(self):
        if self.changesByAction.get('ptnCoachToRemove', False):
            change, oldCoachId = removePtnCoach(self.groupInfo)
            if change:
                if not self.changeLog.has_key(oldCoachId):
                    self.changeLog[oldCoachId] = [change]
                else:
                    self.changeLog[oldCoachId].append(change)
                    
    def addPtnCoach(self):
        ptnCoachToAdd = self.changesByAction.get('ptnCoach', None)
        if ptnCoachToAdd:
            userInfo = createObject('groupserver.UserFromId', self.group, ptnCoachToAdd)
            change = addPtnCoach(self.groupInfo, userInfo)
            if not self.changeLog.has_key(ptnCoachToAdd):
                self.changeLog[ptnCoachToAdd] = [change]
            else:
                self.changeLog[ptnCoachToAdd].append(change)
    
    def makeChangesByMember(self):
        for memberId in self.changesByMember.keys():
            userInfo = createObject('groupserver.UserFromId', self.group, memberId)
            actions = self.changesByMember[memberId]
            if not self.changeLog.has_key(memberId):
                self.changeLog[memberId] = []
            if 'withdraw' in actions:
                self.changeLog[memberId].append(withdrawInvitation(self.groupInfo, userInfo))
            if 'groupAdminAdd' in actions:
                self.changeLog[memberId].append(addAdmin(self.groupInfo, userInfo))
            if 'groupAdminRemove' in actions:
                self.changeLog[memberId].append(removeAdmin(self.groupInfo, userInfo))
            if 'moderatorAdd' in actions:
                self.changeLog[memberId].append(addModerator(self.groupInfo, userInfo))
            if 'moderatorRemove' in actions:
                self.changeLog[memberId].append(removeModerator(self.groupInfo, userInfo))
            if 'moderatedAdd' in actions:
                self.changeLog[memberId].append(moderate(self.groupInfo, userInfo))
            if 'moderatedRemove' in actions:
                self.changeLog[memberId].append(unmoderate(self.groupInfo, userInfo))
            if 'postingMemberAdd' in actions:
                self.changeLog[memberId].append(addPostingMember(self.groupInfo, userInfo))
    
    def finishSummary(self):
        for memberId in self.changeLog.keys():
            userInfo = createObject('groupserver.UserFromId', self.group, memberId)
            self.summary += '<p><a href="%s">%s</a> has undergone '\
              'the following changes:</p><ul>' % (userInfo.url, userInfo.name)
            for change in self.changeLog[memberId]:
                self.summary += '<li>%s</li>' % change
            self.summary += '</ul>'

