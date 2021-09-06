# Koji callback for sending notifications about events to the fedmsg message bus
# Copyright (c) 2009-2019 Red Hat, Inc.
#
# Source: https://pagure.io/koji-fedmsg-plugin/
#
# Authors:
#     Ralph Bean <rbean@redhat.com>
#     Mike Bonnet <mikeb@redhat.com>

import logging
import re
import time

from koji.context import context
from koji.plugin import callbacks
from koji.plugin import callback
from koji.plugin import ignore_error
import fedora_messaging.api
import fedora_messaging.exceptions
import kojihub


MAX_KEY_LENGTH = 255
log = logging.getLogger(__name__)


def camel_to_dots(name):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1.\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1.\2', s1).lower()


def serialize_datetime_in_task(task):
    date_fields = [
        "completion_time", "create_time", "start_time", "buildtime",
        "creation_ts", "creation_time",
    ]
    for date_key in date_fields:
        if task.get(date_key) is None:
            continue
        if isinstance(task[date_key], (float, int)):
            continue
        task[date_key] = time.mktime(task[date_key].timetuple())


def get_message_body(topic, *args, **kws):
    msg = {}

    if topic == 'package.list.change':
        msg['tag'] = kws['tag']['name']
        msg['package'] = kws['package']['name']
        msg['action'] = kws['action']
        if 'owner' in kws:
            msg['owner'] = kojihub.get_user(kws['owner'])['name']
        else:
            msg['owner'] = None
        msg['block'] = kws.get('block', None)
        msg['extra_arches'] = kws.get('extra_arches', None)
        msg['force'] = kws.get('force', None)
        msg['update'] = kws.get('update', None)
    elif topic == 'task.state.change':
        info = kws['info']
        serialize_datetime_in_task(info)

        # Stuff in information about descendant tasks
        task = kojihub.Task(info['id'])
        info['children'] = []
        for child_orig in task.getChildren():
            child = child_orig.copy()
            serialize_datetime_in_task(child)
            info['children'].append(child)

        # Send the whole info dict along because it might have useful info.
        # For instance, it contains the mention of what format createAppliance
        # is using (raw or qcow2).
        msg['info'] = info
        msg['method'] = kws['info']['method']
        msg['attribute'] = kws['attribute']
        msg['old'] = kws['old']
        msg['new'] = kws['new']
        msg['id'] = kws['info']['id']

        # extract a useful identifier from the request string
        request = kws.get('info', {}).get('request', ['/'])
        msg['srpm'] = request[0].split('/')[-1]

        if 'owner_name' in info:
            msg['owner'] = info['owner_name']
        elif 'owner_id' in info:
            msg['owner'] = kojihub.get_user(info['owner_id'])['name']
        elif 'owner' in info:
            msg['owner'] = kojihub.get_user(info['owner'])['name']
        else:
            msg['owner'] = None

    elif topic == 'build.state.change':
        info = kws['info']
        msg['name'] = info['name']
        msg['version'] = info['version']
        msg['release'] = info['release']
        msg['epoch'] = info.get('epoch')
        msg['attribute'] = kws['attribute']
        msg['old'] = kws['old']
        msg['new'] = kws['new']
        msg['build_id'] = info.get('id', None)
        msg['task_id'] = info.get('task_id', None)

        if msg['task_id']:
            task = kojihub.Task(msg['task_id'])
            msg['request'] = task.getRequest()
        else:
            msg['request'] = None

        if 'owner_name' in info:
            msg['owner'] = info['owner_name']
        elif 'owner_id' in info:
            msg['owner'] = kojihub.get_user(info['owner_id'])['name']
        elif 'owner' in info:
            msg['owner'] = kojihub.get_user(info['owner'])['name']
        else:
            msg['owner'] = None

    elif topic == 'import':
        # TODO -- import is currently unused.
        # Should we remove it?
        msg['type'] = kws['type']
    elif topic in ('tag', 'untag'):
        msg['tag'] = kws['tag']['name']
        build = kws['build']
        msg['name'] = build['name']
        msg['version'] = build['version']
        msg['release'] = build['release']
        msg['user'] = kws['user']['name']
        msg['owner'] = kojihub.get_user(kws['build']['owner_id'])['name']
        msg['tag_id'] = kws['tag']['id']
        msg['build_id'] = kws['build']['id']
    elif topic == 'repo.init':
        msg['tag'] = kws['tag']['name']
        msg['tag_id'] = kws['tag']['id']
        msg['repo_id'] = kws['repo_id']
    elif topic == 'repo.done':
        msg['tag'] = kws['repo']['tag_name']
        msg['tag_id'] = kws['repo']['tag_id']
        msg['repo_id'] = kws['repo']['id']
    elif topic == 'rpm.sign':
        if 'attribute' in kws:
            # v1.10.1 and earlier
            msg['attribute'] = kws['attribute']
            msg['old'] = kws['old']
            msg['new'] = kws['new']
            msg['info'] = kws['info']
        else:
            # v1.11.0 (and maybe higher, but who knows)
            msg['sigkey'] = kws['sigkey']
            msg['sighash'] = kws['sighash']
            msg['build'] = kws['build']
            msg['rpm'] = kws['rpm']
            serialize_datetime_in_task(msg['build'])
            serialize_datetime_in_task(msg['rpm'])

    return msg


# This callback gets run for every koji event that starts with "post"
@callback(*[
    c for c in list(callbacks.keys())
    if c.startswith('post') and c not in [
        'postImport',  # This is kind of useless; also noisy.
        # This one is special, and is called every time, so ignore it.
        # Added here https://pagure.io/koji/pull-request/148
        'postCommit',
    ]
])
@ignore_error
def queue_message(cbtype, *args, **kws):
    if cbtype.startswith('post'):
        msgtype = cbtype[4:]
    else:
        msgtype = cbtype[3:]

    # Short-circuit ourselves for task events.  They are very spammy and we are
    # only interested in state changes to scratch builds (parent tasks).
    if cbtype == 'postTaskStateChange':
        # only state changes
        if not kws.get('attribute', None) == 'state':
            return
        # only parent tasks
        if kws.get('info', {}).get('parent'):
            return
        # only scratch builds
        request = kws.get('info', {}).get('request', [{}])[-1]
        if not isinstance(request, dict) or not request.get('scratch'):
            return

    topic = camel_to_dots(msgtype)
    body = get_message_body(topic, *args, **kws)

    # We need this to distinguish between messages from primary koji
    # and the secondary hubs off for s390 and ppc.
    body['instance'] = 'primary'

    # Don't publish these uninformative rpm.sign messages if there's no actual
    # sigkey present.  Koji apparently adds a dummy sig value when rpms are
    # first imported and there's no need to spam the world about that.
    if topic == 'rpm.sign' and (body.get('info', {}).get('sigkey') == '' or
                                body.get('sigkey') == ''):
        return

    # Also, do not want to send a message on volume_id changes
    if topic == 'build.state.change' and body.get('attribute') == 'volume_id':
        return

    # Last thing to do before publishing: scrub some problematic fields
    # These fields are floating points which get json-encoded differently on
    # rhel and fedora.
    problem_fields = ['weight', 'start_ts', 'create_ts', 'completion_ts']

    def scrub(obj):
        if isinstance(obj, list):
            return [scrub(item) for item in obj]
        if isinstance(obj, dict):
            return dict([
                (k, scrub(v))
                for k, v in list(obj.items())
                if k not in problem_fields
            ])
        return obj

    body = scrub(body)

    # Queue the message for later.
    # It will only get sent after postCommit is called.
    messages = getattr(context, 'fedmsg_plugin_messages', [])
    messages.append(dict(topic=topic, msg=body))
    context.fedmsg_plugin_messages = messages


# Meanwhile, postCommit actually sends messages.
@callback('postCommit')
@ignore_error
def send_messages(cbtype, *args, **kws):
    messages = getattr(context, 'fedmsg_plugin_messages', [])

    for message in messages:
        try:
            msg = fedora_messaging.api.Message(
                topic="buildsys.{}".format(message['topic']),
                body=message['msg']
            )
            fedora_messaging.api.publish(msg)
        except fedora_messaging.exceptions.PublishReturned as e:
            log.warning(
                "Fedora Messaging broker rejected message %s: %s", msg.id, e
            )
        except fedora_messaging.exceptions.ConnectionException as e:
            log.warning("Error sending message %s: %s", msg.id, e)
        except Exception:
            log.exception("Un-expected error sending fedora-messaging message")
