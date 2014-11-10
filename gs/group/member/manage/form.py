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
from zope.formlib import form
from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile
from gs.group.base import GroupForm
from .manager import GSGroupMemberManager


class GSManageGroupMembersForm(GroupForm):
    pageTemplateFileName = 'browser/templates/manage_members.pt'
    template = ZopeTwoPageTemplateFile(pageTemplateFileName)

    def __init__(self, group, request):
        super(GSManageGroupMembersForm, self).__init__(group, request)
        self.groupName = self.groupInfo.name
        self.label = 'Manage the Members of %s' % self.groupName
        self.showOnly = request.form.get('showOnly', '')
        self.page = request.form.get('page', '1')
        self.__form_fields = None

    @property
    def form_fields(self):
        # Deliberately not a @Lazy property. See handle_change below.
        if self.__form_fields is None:
            if (not(self.memberManager.postingIsSpecial)
                    and not('form.ptnCoachRemove' in self.request.form)
                    and not(self.groupInfo.ptn_coach)):
                self.request.form['form.ptnCoachRemove'] = 'True'
            if self.showOnly or not(self.memberManager.membersToShow):
                retval = self.memberManager.form_fields.omit('ptnCoachRemove')
            else:
                retval = self.memberManager.form_fields
            self.__form_fields = retval
        return self.__form_fields

    def setUpWidgets(self, ignore_request=False, data={}):
        self.adapters = {}
        self.widgets = form.setUpWidgets(
            self.form_fields, self.prefix, self.context,
            self.request, form=self, data=data,
            ignore_request=ignore_request)
        for widget in self.widgets:
            widget._displayItemForMissingValue = False
        assert self.widgets

    @form.action(label='Change', failure='handle_change_action_failure')
    def handle_change(self, action, data):
        self.status = self.memberManager.make_changes(data)
        # Reset the form_fields cache so that the
        # page reloads with the updated widgets
        self.__form_fields = None

    def handle_change_action_failure(self, action, data, errors):
        if len(errors) == 1:
            self.status = '<p>There is an error:</p>'
        else:
            self.status = '<p>There are errors:</p>'

    @Lazy
    def memberManager(self):
        retval = GSGroupMemberManager(self.groupInfo.groupObj,
                                      self.page, self.showOnly)
        return retval
