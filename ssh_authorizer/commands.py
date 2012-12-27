import sys
import logging

import sh

from .helpers import SSHController, SCPController
from .helpers import NoSuchFileError
from .helpers import get_authorized_keys
from .helpers import set_authorized_keys
from .helpers import create_authorized_keys_file
from .helpers import load_local_keys


def help():
    from .__init__ import __doc__ as doc
    print(doc)


def get(user, host, port, raw):
    if not raw:
        ssh_controller = SSHController(user, host, port)

        try:
            keys = [k for k in get_authorized_keys(controller=ssh_controller) if k]
        except sh.ErrorReturnCode_1:
            sys.exit(1)
        except NoSuchFileError:
            keys = []

        if len(keys) == 1:
            print("{c.user}@{c.host}:{c.port} - found one key:\n".format(c=ssh_controller))
        elif keys:
            print("{c.user}@{c.host}:{c.port} - found {} keys:\n".format(len(keys), c=ssh_controller))
        else:
            print("{c.user}@{c.host}:{c.port} - not found keys".format(c=ssh_controller))

        for n, key in enumerate(keys):
            if key:
                print('{}: {}'.format(n + 1, key))

    else:
        ssh_controller = SSHController(user, host, port)

        try:
            keys = get_authorized_keys(controller=ssh_controller)
        except sh.ErrorReturnCode_1:
            sys.exit(1)
        except NoSuchFileError:
            keys = []

        print('\n'.join(keys))

    return


def add(user, host, port, key_files):
    local_keys = load_local_keys(key_files)

    ssh_controller = SSHController(user, host, port)

    try:
        remote_keys = get_authorized_keys(ssh_controller)
    except sh.ErrorReturnCode_1:
        sys.exit(1)
    except NoSuchFileError:
        create_authorized_keys_file(ssh_controller)
        remote_keys = []

    new_keys = []
    already_keys = []

    for key_file in key_files:
        key = local_keys[key_file]

        if key not in remote_keys:
            new_keys.append(key)
        else:
            already_keys.append(key_file)

    if already_keys:
        logging.info('{c.user}@{c.host}:{c.port} - already in authorized_keys: "{}"'
                        .format('", "'.join(already_keys), c=ssh_controller))

    if new_keys:
        keys = remote_keys + new_keys

        scp_controller = SCPController(user, host, port)
        scp_controller.password = ssh_controller.password

        try:
            set_authorized_keys(scp_controller, keys)
        except sh.ErrorReturnCode_1:
            sys.exit(1)


def delete(user, host, port, key_ids):
    ssh_controller = SSHController(user, host, port)

    try:
        remote_keys = [k for k in get_authorized_keys(ssh_controller) if k]
    except NoSuchFileError:
        logging.critical('{c.user}@{c.host}:{c.port} - error: not found authorized_keys'
                            .format(c=ssh_controller))
        sys.exit(1)

    try:
        for key_id in sorted(key_ids, reverse=True):
            del remote_keys[key_id - 1]
    except IndexError:
        logging.critical('{c.user}@{c.host}:{c.port} - error: not found key indexes'
                            .format(c=ssh_controller))
        sys.exit(1)

    scp_controller = SCPController(user, host, port)
    scp_controller.password = ssh_controller.password
    set_authorized_keys(scp_controller, remote_keys)


def test(user, host, port, key_files):
    local_keys = load_local_keys(key_files)

    ssh_controller = SSHController(user, host, port)

    try:
        remote_keys = [k for k in get_authorized_keys(ssh_controller) if k]
    except NoSuchFileError:
        logging.info('{c.user}@{c.host}:{c.port} - not found authorized_keys'
                            .format(c=ssh_controller))
        remote_keys = []

    oks = []

    for key_file in key_files:
        ok = local_keys[key_file] in remote_keys
        oks.append(ok)
        print('{}: {}'.format(key_file, 'ok' if ok else 'fail'))

    return not int(all(oks))
