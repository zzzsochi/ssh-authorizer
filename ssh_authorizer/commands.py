from .helpers import SSHController, SCPController
from .helpers import get_authorized_keys, set_authorized_keys
from .helpers import load_local_keys


def help():
    from .__init__ import __doc__ as doc
    print(doc)


def get(user, host, port, raw):
    if not raw:
        keys = [k for k in get_authorized_keys(user=user, host=host, port=port) if k]
        print("Found {} keys:\n".format(len(keys)))
        for n, key in enumerate(keys):
            if key:
                print('{}: {}'.format(n + 1, key))

    else:
        keys = get_authorized_keys(user=user, host=host, port=port)
        print('\n'.join(keys))

    return


def add(user, host, port, key_files):
    local_keys = load_local_keys(key_files)

    ssh_controller = SSHController(user, host, port)
    remote_keys = get_authorized_keys(controller=ssh_controller)

    new_keys = []

    for key_file in key_files:
        key = local_keys[key_file]

        if key not in remote_keys:
            new_keys.append(key)

    if new_keys:
        keys = remote_keys + new_keys

        scp_controller = SCPController(user, host, port)
        scp_controller.password = ssh_controller.password

        set_authorized_keys(keys, controller=scp_controller)


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
