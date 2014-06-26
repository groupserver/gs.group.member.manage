# -*- coding: utf-8 -*-
##############################################################################
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
##############################################################################
from __future__ import absolute_import, unicode_literals
from zope.interface import Attribute
from zope.interface.interface import Interface
from zope.schema import List, Text, Bool, Choice
from zope.schema.vocabulary import SimpleTerm, SimpleVocabulary


class IGSManageGroupMembersForm(Interface):
    groupInfo = Attribute("""A groupInfo instance""")
    siteInfo = Attribute("""A siteInfo instance""")
    memberManager = Attribute("""A GSGroupMemberManager instance""")
    form_fields = Attribute("""The fields to be displayed in a form""")


class IGSManageMembersForm(Interface):
    """ One user-independent field."""
    ptnCoachRemove = Choice(vocabulary=SimpleVocabulary([SimpleTerm(True,
        True, 'No participation coach')]),
      required=False)


class IGSGroupMemberManager(Interface):
    groupInfo = Attribute("""A groupInfo instance""")
    siteInfo = Attribute("""A siteInfo instance""")
    membersInfo = Attribute("""A GSGroupMembersInfo instance""")
    memberStatusActions = \
        Attribute("A list of GSMemberStatusActions instances")
    form_fields = Attribute("""The fields to be displayed in a form""")


class IGSMemberStatusActions(Interface):
    userInfo = Attribute("""A userInfo instance""")
    groupInfo = Attribute("""A groupInfo instance""")
    siteInfo = Attribute("""A siteInfo instance""")
    status = Attribute("""A GSGroupMembershipStatus instance""")
    form_fields = Attribute("""The fields to be displayed in a """
      """form to change the membership status of this user""")


class IGSMemberStatusActionsContentProvider(Interface):
    """The content provider for the actions available to change """
    """a group member's status within the group"""
    statusActions = List(title='Instances',
      description='GSMemberStatusActions instances',
      required=True)
    widgets = List(title='Widgets',
      description='Form Widgets',
      required=True)
    pageTemplateFileName = Text(title="Page Template File Name",
      description='The name of the ZPT file that is used to render the '
        'group member\'s status and the appropriate form widgets.',
      required=False,
      default="browser/templates/statusActionsContentProvider.pt")


class IGSStatusFormFields(Interface):
    """ An adapter to take a member's status within a group, and
        give us the appropriate form_fields to alter the status,
        also depending on the status of the logged-in administrator.
    """
    status = Attribute("""A GSGroupMembershipStatus instance""")
    userInfo = Attribute("""A userInfo instance""")
    groupInfo = Attribute("""A groupInfo instance""")
    siteInfo = Attribute("""A siteInfo instance""")
    adminUserInfo = Attribute("A userInfo instance for the logged-in "
                                "administrator")
    adminUserStatus = Attribute("A GSGroupMembershipStatus instance for the "
                                "logged-in administrator")
    form_fields = Attribute("The fields to be displayed in a form to change "
                            "the membership status of this user")
    groupAdmin = Bool(title='Make fn a Group Administrator (or Unmake)',
      description='Make fn a Group Administrator (or Unmake)',
      required=False)
    ptnCoach = Bool(title='Make fn the Participation Coach (or Unmake)',
      description='Make fn the Participation Coach (or Unmake)',
      required=False)
    moderator = Bool(title='Make fn a Moderator (or Unmake)',
      description='Make fn a Moderator (or Unmake)',
      required=False)
    moderate = Bool(title='Moderate fn (or Unmoderate)',
      description='Moderate fn (or Unmoderate)',
      required=False)
    postingMember = Bool(title='Make fn a Posting Member (or Unmake)',
      description='Make fn a Posting Member (or Unmake)',
      required=False)
    remove = Bool(title='Remove fn from the Group',
      description='Remove fn from the Group',
      required=False)


class IGSMemberActionsSchema(Interface):
    """ Dummy interface to get the schema started."""
    dummy = Bool(title='Dummy',
      description='Is this a dummy value?',
      required=False)


class IGSManageManyMembers(Interface):
    'The Manage Many Members schema'
    members = List(title='Members to manage',
                      description='The members of this group to manage.',
                      value_type=Choice(title='Group members',
                                  vocabulary='groupserver.ManyGroupMembers'),
                      required=True)
