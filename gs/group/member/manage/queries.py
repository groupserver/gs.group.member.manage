# coding=utf-8
import sqlalchemy as sa
from Products.XWFMailingListManager.bounceaudit import SUBSYSTEM

class BounceHistoryQuery(object):
    
    def __init__(self, context, da):
        self.auditEventTable = da.createTable('audit_event')
    
    def bounce_events(self, email):
        aet = self.auditEventTable
#        SELECT * FROM bounce_audit 
#        WHERE subsystem == SUBSYSTEM
#          AND instance_datum == email;
        s = aet.select()
        s.append_whereclause(aet.c.subsystem == SUBSYSTEM)
        s.append_whereclause(aet.c.instance_datum == email)
        s.order_by(sa.desc(aet.c.event_date))

        retval = []        
        r = s.execute()
        if r.rowcount:
            retval = [{
                'event_id':            x['id'],
                'date':                x['event_date'],
                'subsystem':           x['subsystem'],
                'code':                x['event_code'],
                'user_id':             x['user_id'],
                'instance_user_id':    x['instance_user_id'],
                'site_id':             x['site_id'],
                'group_id':            x['group_id'],
                'instanceDatum':       x['instance_datum'],
                'supplementaryDatum':  x['supplementary_datum']} for x in r]
        return retval

