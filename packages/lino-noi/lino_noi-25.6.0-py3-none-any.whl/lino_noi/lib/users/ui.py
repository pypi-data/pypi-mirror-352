# -*- coding: UTF-8 -*-
# Copyright 2015-2024 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

from lino.modlib.users.ui import *

from lino.api import _

from lino.core import actions
from lino_xl.lib.working.roles import Worker

from lino.modlib.users.actions import SendWelcomeMail
from lino.modlib.office.roles import OfficeUser
#from .models import VerifyUser


class UserDetail(UserDetail):
    """Layout of User Detail in Lino Noi."""

    main = "general #contact calendar dashboard.WidgetsByUser working.SummariesByUser memo.MentionsByTarget"

    general = dd.Panel("""
    general1:30 general2:30 general3:30
    SocialAuthsByUser #tickets.SubscriptionsByUser groups.MembershipsByUser topics.InterestsByPartner
    """,
                       label=_("General"))

    # skills.OffersByEndUser

    calendar = dd.Panel("""
    event_type
    cal.SubscriptionsByUser
    # cal.MembershipsByUser
    """,
                        label=dd.plugins.cal.verbose_name,
                        required_roles=dd.login_required(OfficeUser))

    general1 = """
    username user_type:20
    first_name last_name
    initials nickname
    person company #user_site
    """

    general2 = """
    language:10 id
    email mail_mode
    notify_myself open_session_on_new_ticket
    status
    """

    general3 = """
    created:12 modified:12
    date_format time_zone
    start_date end_date
    """


# Users.detail_layout = UserDetail()
