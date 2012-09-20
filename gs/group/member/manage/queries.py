# coding=utf-8
import sqlalchemy as sa
from gs.group.member.bounce.audit import SUBSYSTEM
from gs.database import getSession, getTable


class BounceHistoryQuery(object):

    def __init__(self, context):
        self.auditEventTable = getTable('audit_event')

    def bounce_events(self, email):
        aet = self.auditEventTable
#        SELECT * FROM bounce_audit
#        WHERE subsystem == SUBSYSTEM
#          AND instance_datum == email;
        s = aet.select(order_by=sa.desc(aet.c.event_date))
        s.append_whereclause(aet.c.subsystem == SUBSYSTEM)
        s.append_whereclause(aet.c.instance_datum == email)

        session = getSession()

        retval = []
        r = session.execute(s)
        if r.rowcount:
            retval = [{
                'event_id': x['id'],
                'date': x['event_date'],
                'subsystem': x['subsystem'],
                'code': x['event_code'],
                'user_id': x['user_id'],
                'instance_user_id': x['instance_user_id'],
                'site_id': x['site_id'],
                'group_id': x['group_id'],
                'instanceDatum': x['instance_datum'],
                'supplementaryDatum': x['supplementary_datum']} for x in r]
        return retval
