# The contents of this file are subject to the Common Public Attribution
# License Version 1.0. (the "License"); you may not use this file except in
# compliance with the License. You may obtain a copy of the License at
# http://code.reddit.com/LICENSE. The License is based on the Mozilla Public
# License Version 1.1, but Sections 14 and 15 have been added to cover use of
# software over a computer network and provide for limited attribution for the
# Original Developer. In addition, Exhibit A has been modified to be consistent
# with Exhibit B.
#
# Software distributed under the License is distributed on an "AS IS" basis,
# WITHOUT WARRANTY OF ANY KIND, either express or implied. See the License for
# the specific language governing rights and limitations under the License.
#
# The Original Code is reddit.
#
# The Original Developer is the Initial Developer.  The Initial Developer of
# the Original Code is reddit Inc.
#
# All portions of the code written by reddit are Copyright (c) 2006-2012 reddit
# Inc. All Rights Reserved.
###############################################################################

from pylons import request
from pylons.i18n import _

from r2.models import Account, Message
from r2.lib.db import queries


user_added_messages = {
    "moderator_invite": {
        "pm": {
            "subject": _("invitation to moderate %(url)s"),
            "msg": _("**gadzooks! you are invited to become a moderator of [%(title)s](%(url)s)!**\n\n"
                     "*to accept*, visit the [moderators page for %(url)s](%(url)s/about/moderators) and click \"accept\".\n\n"
                     "*otherwise,* if you did not expect to receive this, you can simply ignore this invitation or report it."),
        },
        "modmail": {
            "subject": _("moderator invited"),
            "msg": _("%(user)s has been invited by %(author)s to moderate %(url)s."),
        },
    },
    "accept_moderator_invite": {
        "modmail": {
            "subject": _("moderator added"),
            "msg": _("%(user)s has accepted an invitation to become moderator of %(url)s."),
        },
    },
    "contributor": {
        "pm": {
            "subject": _("you are an approved submitter"),
            "msg": _("you have been added as an approved submitter to [%(title)s](%(url)s)."),
        },
    },
    "banned": {
        "pm": {
            "subject": _("you've been banned"),
            "msg": _("you have been banned from posting to [%(title)s](%(url)s)."),
        },
    },
    "traffic": {
        "pm": {
            "subject": _("you can view traffic on a promoted link"),
            "msg": _('you have been added to the list of users able to see [traffic for the sponsored link "%(title)s"](%(traffic_url)s).'),
        },
    },
}


def notify_user_added(rel_type, author, user, target):
    msgs = user_added_messages.get(rel_type)
    if not msgs:
        return

    srname = target.path.rstrip("/")
    d = {
        "url": srname,
        "title": "%s: %s" % (srname, target.title),
        "author": "/u/" + author.name,
        "user": "/u/" + user.name,
    }

    if "pm" in msgs and author != user:
        subject = msgs["pm"]["subject"] % d
        msg = msgs["pm"]["msg"] % d

        if rel_type == "banned" and not user.has_interacted_with(target):
            return

        if rel_type in ("banned", "moderator_invite"):
            # send the message from the subreddit
            item, inbox_rel = Message._new(author, user, subject, msg, request.ip,
                                           sr=target, from_sr=True)
        else:
            item, inbox_rel = Message._new(author, user, subject, msg, request.ip)

        queries.new_message(item, inbox_rel)

    if "modmail" in msgs:
        subject = msgs["modmail"]["subject"] % d
        msg = msgs["modmail"]["msg"] % d

        if rel_type == "moderator_invite":
            modmail_author = Account.system_user()
        else:
            modmail_author = author

        item, inbox_rel = Message._new(modmail_author, target, subject, msg,
                                       request.ip, sr=target)
        queries.new_message(item, inbox_rel)
