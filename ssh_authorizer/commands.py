import sys

import sh

from .helpers import SSHController, SCPController
from .helpers import get_authorized_keys, set_authorized_keys
from .helpers import load_local_keys


def help():
    from .__init__ import __doc__ as doc
    print(doc)


def get(user, host, port, raw):
    if not raw:
        try:
            keys = [k for k in get_authorized_keys(user=user, host=host, port=port) if k]
        except sh.ErrorReturnCode_1:
            sys.exit(1)

        if keys:
            print("Found {} keys:\n".format(len(keys)))
        else:
            print("Not found keys.")

        for n, key in enumerate(keys):
            if key:
                print('{}: {}'.format(n + 1, key))

    else:
        try:
            keys = get_authorized_keys(user=user, host=host, port=port)
        except sh.ErrorReturnCode_1:
            sys.exit(1)

        print('\n'.join(keys))

    return


def add(user, host, port, key_files):
    local_keys = load_local_keys(key_files)

    ssh_controller = SSHController(user, host, port)

    try:
        remote_keys = get_authorized_keys(controller=ssh_controller)
    except sh.ErrorReturnCode_1:
        sys.exit(1)

    new_keys = []

    for key_file in key_files:
        key = local_keys[key_file]

        if key not in remote_keys:
            new_keys.append(key)

    if new_keys:
        keys = remote_keys + new_keys

        scp_controller = SCPController(user, host, port)
        scp_controller.password = ssh_controller.password

        try:
            set_authorized_keys(keys, controller=scp_controller)
        except sh.ErrorReturnCode_1:
            sys.exit(1)


def delete(user, host, port, key_ids):
    ssh_controller = SSHController(user, host, port)
    remote_keys = [k for k in get_authorized_keys(controller=ssh_controller) if k]

    for key_id in sorted(key_ids, reverse=True):
        del remote_keys[key_id - 1]

    scp_controller = SCPController(user, host, port)
    scp_controller.password = ssh_controller.password
    set_authorized_keys(remote_keys, controller=scp_controller)


def test(user, host, port, key_files):
    local_keys = load_local_keys(key_files)
    remote_keys = [k for k in get_authorized_keys(user=user, host=host, port=port) if k]

    oks = []

    for key_file in key_files:
        ok = local_keys[key_file] in remote_keys
        oks.append(ok)
        print('{}: {}'.format(key_file, 'ok' if ok else 'fail'))

    return not int(all(oks))
