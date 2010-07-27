# coding=utf-8
from AccessControl import getSecurityManager
from zope.component import createObject
from zope.interface import implements
from zope.formlib import form
from Products.XWFCore.odict import ODict
from Products.XWFCore.XWFUtils import comma_comma_and, getOption
from Products.GSGroup.mailinglistinfo import GSMailingListInfo
from Products.GSGroup.changebasicprivacy import radio_widget
from gs.group.member.leave.leaver import GroupLeaver
from gs.group.member.leave.audit import LeaveAuditor, LEAVE
from Products.GSGroupMember.groupMembersInfo import GSGroupMembersInfo
from gs.group.member.manage.statusformfields import MAX_POSTING_MEMBERS
from gs.group.member.manage.actions import GSMemberStatusActions
from gs.group.member.manage.interfaces import IGSGroupMemberManager
from gs.group.member.manage.interfaces import IGSMemberActionsSchema, IGSManageMembersForm

class GSGroupMemberManager(object):
    implements(IGSGroupMemberManager)
    
    def __init__(self, group):
        self.group = group
        self.siteInfo = createObject('groupserver.SiteInfo', group)
        self.groupInfo = createObject('groupserver.GroupInfo', group)
        self.__membersInfo = self.__memberStatusActions = None
        self.__postingIsSpecial = self.__form_fields = None
    
    @property
    def membersInfo(self):
        if self.__membersInfo == None:
            self.__membersInfo = GSGroupMembersInfo(self.group)
        return self.__membersInfo
    
    @property
    def memberStatusActions(self):
        if self.__memberStatusActions == None:
            self.__memberStatusActions = \
              [ GSMemberStatusActions(m, 
                  self.groupInfo, self.siteInfo)
                for m in self.membersInfo.members ]
        return self.__memberStatusActions
    
    @property
    def postingIsSpecial(self):
        if self.__postingIsSpecial == None:
            self.__postingIsSpecial = \
              self.memberStatusActions[0].status.postingIsSpecial
        return self.__postingIsSpecial
    
    @property
    def form_fields(self):
        if self.__form_fields == None:
            fields = \
              form.Fields(IGSManageMembersForm)
            for m in self.memberStatusActions:
                fields = \
                  form.Fields(
                    fields
                    +
                    form.Fields(m.form_fields)
                  )
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
        toChange = filter(lambda k:data.get(k), data.keys())
        changesByAction, changesByMember, cancelledChanges = self.marshallChanges(toChange)
        retval = self.set_data(changesByAction, changesByMember, cancelledChanges)
        
        # Reset the caches so that we get the member
        # data afresh when the form reloads.
        self.__membersInfo = None
        self.__memberStatusActions = None
        self.__form_fields = None
        return retval

    def marshallChanges(self, toChange):
        changes = {}
        if 'ptnCoachRemove' in toChange:
            changes['ptnCoachToRemove'] = True
            toChange.remove('ptnCoachRemove')
        for k in toChange:
            memberId, action = k.split('-')
            if changes.has_key(action):
                changes[action].append(memberId)
            else:
                changes[action] = [memberId]
        toChange, cancelledChanges = self.sanitiseChanges(changes)
        changesByAction, changesByMember = self.organiseChanges(toChange) 
        retval = (changesByAction, changesByMember, cancelledChanges)
        return retval
    
    def sanitiseChanges(self, toChange):
        # For members to be removed, cancel all other actions.
        cancelledChanges = {}
        for mId in toChange.get('remove',[]):
            for a in filter(lambda x:(x!='remove') and (x!='ptnCoachToRemove'), toChange.keys()):
                members = toChange.get(a,[])
                if mId in members:
                    members.remove(mId)
                    toChange[a] = members
        
        toChange, cancelledChanges = self.cleanPtnCoach(toChange, cancelledChanges)
        toChange, cancelledChanges = self.cleanPosting(toChange, cancelledChanges)
        toChange, cancelledChanges = self.cleanModeration(toChange, cancelledChanges)
        retval = (toChange, cancelledChanges)
        return retval

    def cleanPtnCoach(self, toChange, cancelledChanges):
        # Check if a member to be removed is also the Ptn Coach, and update removal if req'd.
        if self.groupInfo.ptn_coach and (self.groupInfo.ptn_coach in toChange.get('remove',[])):
            toChange['ptnCoachToRemove'] = True
        # If more than one ptnCoach was specified, then cancel the change.
        ptnCoachToAdd = toChange.get('ptnCoach',[])
        if ptnCoachToAdd and (len(ptnCoachToAdd)>1):
            cancelledChanges['ptnCoach'] = ptnCoachToAdd
            toChange.pop('ptnCoach')
        elif len(ptnCoachToAdd)==1:
            toChange['ptnCoach'] = ptnCoachToAdd[0]
            if self.groupInfo.ptn_coach:   # Update Ptn Coach removal if req'd.
                toChange['ptnCoachToRemove'] = True
        retval = (toChange, cancelledChanges)
        return retval
    
    def cleanPosting(self, toChange, cancelledChanges):
        ''' Check for the number of posting members exceeding the maximum.'''
        if self.postingIsSpecial:
            listInfo = GSMailingListInfo(self.groupInfo.groupObj)
            numCurrentPostingMembers = len(listInfo.posting_members)
            numPostingMembersToRemove = len(toChange.get('postingMemberRemove',[]))
            numPostingMembersToAdd = len(toChange.get('postingMemberAdd',[]))
            totalPostingMembersToBe = \
              (numCurrentPostingMembers - numPostingMembersToRemove + numPostingMembersToAdd) 
            if totalPostingMembersToBe > MAX_POSTING_MEMBERS:
                numAddedMembersToCut = (totalPostingMembersToBe-MAX_POSTING_MEMBERS)
                membersToAdd = toChange['postingMemberAdd']
                addedMembersToCut = membersToAdd[-numAddedMembersToCut:]
                cancelledChanges['postingMember'] = addedMembersToCut
                index = (len(membersToAdd)-len(addedMembersToCut))
                toChange['postingMemberAdd'] = membersToAdd[:index]
        retval = (toChange, cancelledChanges)
        return retval
    
    def cleanModeration(self, toChange, cancelledChanges):
        ''' Check for members being set as both a moderator and moderated.'''
        toBeModerated = toChange.get('moderatedAdd',[])
        toBeModerators = toChange.get('moderatorAdd',[])
        doubleModerated = \
          [ mId for mId in toBeModerators if mId in toBeModerated ]
        if doubleModerated:
            cancelledChanges['doubleModeration'] = doubleModerated
        for mId in doubleModerated:
            toBeModerated.remove(mId)
            toBeModerators.remove(mId)
        if toBeModerated:
            toChange['moderatedAdd'] = toBeModerated
        elif toChange.has_key('moderatedAdd'):
            toChange.pop('moderatedAdd')
        if toBeModerators:
            toChange['moderatorAdd'] = toBeModerators
        elif toChange.has_key('moderatorAdd'):
            toChange.pop('moderatorAdd')
        retval = (toChange, cancelledChanges)
        return retval
    
    def organiseChanges(self, toChange):
        changesByAction = {}
        changesByMember = {}
        for a in ['remove','postingMemberRemove','ptnCoachToRemove','ptnCoach']:
            if toChange.get(a,None):
                changesByAction[a] = toChange.pop(a)
        for k in toChange.keys():
            mIds = toChange[k]
            for mId in mIds:
                if not changesByMember.has_key(mId):
                    changesByMember[mId] = [k]
                else:
                    changesByMember[mId].append(k)
        retval = (changesByAction, changesByMember)
        return retval

    def set_data(self, changesByAction, changesByMember, cancelledChanges):
        retval = ''''''
        changeLog = ODict()
        
        # 0. Summarise actions not taken.
        if cancelledChanges.has_key('ptnCoach'):
            attemptedChangeIds = cancelledChanges['ptnCoach']
            attemptedChangeUsers = \
              [ createObject('groupserver.UserFromId', self.group, a)
                for a in attemptedChangeIds ]
            attemptedNames = [a.name for a in attemptedChangeUsers ]
            retval += '<p>The Participation Coach was <b>not changed</b>, '\
              'because there can be only one and you specified %d (%s).</p>' %\
              (len(attemptedChangeIds), comma_comma_and(attemptedNames))
        if cancelledChanges.has_key('doubleModeration'):
            attemptedChangeIds = cancelledChanges['doubleModeration']
            attemptedChangeUsers = \
              [ createObject('groupserver.UserFromId', self.group, a)
                for a in attemptedChangeIds ]
            memberMembers = len(attemptedChangeIds)==1 and 'member was' or 'members were'
            retval += '<p>The moderation level of the following %s '\
              '<b>not changed</b>, because members cannot be both ' \
              'moderated and moderators:</p><ul>' % memberMembers
            for m in attemptedChangeUsers:
                retval += '<li><a href="%s">%s</a></li>' %\
                  (m.url, m.name)
            retval += '</ul>'
        if cancelledChanges.has_key('postingMember'):
            attemptedChangeIds = cancelledChanges['postingMember']
            attemptedChangeUsers = \
              [ createObject('groupserver.UserFromId', self.group, a)
                for a in attemptedChangeIds ]
            indefiniteArticle = len(attemptedChangeIds)==1 and 'a ' or ''
            memberMembers = len(attemptedChangeIds)==1 and 'member' or 'members'
            retval += '<p>The following %s <b>did not become</b> %s'\
              'posting %s, because otherwise the maximum of %d ' \
              'posting members would have been exceeded:</p><ul>' %\
               (memberMembers, indefiniteArticle, 
                memberMembers, MAX_POSTING_MEMBERS)
            for m in attemptedChangeUsers:
                retval += '<li><a href="%s">%s</a></li>' %\
                  (m.url, m.name)
            retval += '</ul>'

        # 1. Remove all the members to be removed.
        for memberId in changesByAction.get('remove',[]):
            changeLog[memberId] = self.removeMember(memberId)
        
        # 2. Remove all the posting members to be removed.
        for memberId in changesByAction.get('postingMemberRemove',[]):
            change = self.removePostingMember(memberId)
            if not changeLog.has_key(memberId):
                changeLog[memberId] = [change]
            else:
                changeLog[memberId].append(change)
        
        # 3. If there's a ptn coach to be removed, do it now.
        if changesByAction.get('ptnCoachToRemove', False):
            oldCoachId, change = self.removePtnCoach()
            if oldCoachId:
                if not changeLog.has_key(oldCoachId):
                    changeLog[oldCoachId] = [change]
                else:
                    changeLog[oldCoachId].append(change)
        
        # 4. If there's a ptn coach to add, do it now.
        ptnCoachToAdd = changesByAction.get('ptnCoach', None)
        if ptnCoachToAdd:
            change = self.addPtnCoach(ptnCoachToAdd)
            if not changeLog.has_key(ptnCoachToAdd):
                changeLog[ptnCoachToAdd] = [change]
            else:
                changeLog[ptnCoachToAdd].append(change)
        
        # 5. Make other changes member by member.
        for memberId in changesByMember.keys():
            userInfo = \
              createObject('groupserver.UserFromId', 
                self.group, memberId)
            auditor = StatusAuditor(self.group, userInfo)
            actions = changesByMember[memberId]
            if not changeLog.has_key(memberId):
                changeLog[memberId] = []
            if 'groupAdminAdd' in actions:
                changeLog[memberId].append(self.addAdmin(memberId, auditor))
            if 'groupAdminRemove' in actions:
                changeLog[memberId].append(self.removeAdmin(memberId, auditor))
            if 'moderatorAdd' in actions:
                changeLog[memberId].append(self.addModerator(memberId, auditor))
            if 'moderatorRemove' in actions:
                changeLog[memberId].append(self.removeModerator(memberId, auditor))
            if 'moderatedAdd' in actions:
                changeLog[memberId].append(self.moderate(memberId, auditor))
            if 'moderatedRemove' in actions:
                changeLog[memberId].append(self.unmoderate(memberId, auditor))
            if 'postingMemberAdd' in actions:
                changeLog[memberId].append(self.addPostingMember(memberId, auditor))

        # 6. Format the feedback.
        for memberId in changeLog.keys():
            userInfo = \
              createObject('groupserver.UserFromId', 
                self.group, memberId)
            retval += '<p><a href="%s">%s</a> has undergone '\
              'the following changes:</p><ul>' % (userInfo.url, userInfo.name)
            for change in changeLog[memberId]:
                retval += '<li>%s</li>' % change
            retval += '</ul>'
        return retval
        