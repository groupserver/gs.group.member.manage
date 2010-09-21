# coding=utf-8
try:
    from five.formlib.formbase import PageForm
except ImportError:
    from Products.Five.formlib.formbase import PageForm
from zope.component import createObject
from zope.formlib import form
from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile
from gs.group.member.manage.manager import GSGroupMemberManager

class GSManageGroupMembersForm(PageForm):
    pageTemplateFileName = 'browser/templates/manage_members.pt'
    template = ZopeTwoPageTemplateFile(pageTemplateFileName)
        
    def __init__(self, context, request):
        PageForm.__init__(self, context, request)
        self.context = context
        self.request = request
        self.siteInfo = createObject('groupserver.SiteInfo', context)
        self.groupInfo = createObject('groupserver.GroupInfo', context)
        self.groupName = self.groupInfo.name
        self.label = u'Manage the Members of %s' % self.groupName
        self.showOnly = request.form.get('showOnly','')
        self.page = request.form.get('page','1')
        self.__memberManager = self.__membersInfo = None
        self.__memberStatusActions = None
        self.__form_fields = None

    @property
    def form_fields(self):
        if self.__form_fields == None:
            if not(self.memberManager.postingIsSpecial) and \
              not(self.request.form.has_key('form.ptnCoachRemove')) and \
              not(self.groupInfo.ptn_coach):
                self.request.form['form.ptnCoachRemove'] = u'True'
            if self.showOnly or not(self.memberManager.membersToShow):
                self.__form_fields = self.memberManager.form_fields.omit('ptnCoachRemove')
            else:
                self.__form_fields = self.memberManager.form_fields
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
        
    @form.action(label=u'Change', failure='handle_change_action_failure')
    def handle_change(self, action, data):
        self.status = self.memberManager.make_changes(data)
        # Reset the form_fields cache so that the
        # page reloads with the updated widgets
        self.__form_fields = None

    def handle_change_action_failure(self, action, data, errors):
        if len(errors) == 1:
            self.status = u'<p>There is an error:</p>'
        else:
            self.status = u'<p>There are errors:</p>'
        
    @property
    def memberManager(self):
        if self.__memberManager == None:
            self.__memberManager = \
               GSGroupMemberManager(self.groupInfo.groupObj, 
                                    self.page, self.showOnly)
        return self.__memberManager

