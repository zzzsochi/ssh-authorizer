import os
import logging
from getpass import getpass
from tempfile import NamedTemporaryFile

from sh import ssh, scp


def parse_ssh_string(ssh_string):
    """
        >>> parse_ssh_string('user@host:13')
        ('user', 'host', 13)
        >>> parse_ssh_string('user@host')
        ('user', 'host', 22)
        >>> parse_ssh_string('host:13')[1:]
        ('host', 13)
        >>> parse_ssh_string('host')[1:]
        ('host', 22)
        >>> import os
        >>> os_user = os.environ.get('USER')
        >>> parse_ssh_string('host:13')[0] == os_user
        True
        >>> parse_ssh_string('host')[0] == os_user
        True
    """

    user = os.environ.get('USER')
    port = 22

    if '@' in ssh_string:
        user, ssh_string = ssh_string.split('@')

    if ':' in ssh_string:
        host, port = ssh_string.split(':')
        port = int(port)
    else:
        host = ssh_string

    return user, host, port


def load_local_keys(key_files):
    logging.debug('load local keys: {}'.format(key_files))
    if not key_files:
        key_files.append(os.path.expanduser('~/.ssh/id_rsa.pub'))

    local_keys = {}

    for key_file in key_files:
        with open(os.path.expanduser(key_file), 'rt') as f:
            key_data = f.read().strip()
            local_keys[key_file] = key_data

    logging.debug('loaded local keys: {}'.format(local_keys))
    return local_keys


class Controller(object):
    out = b''
    error = b''
    password = None
    user = None
    host = None
    port = 22

    def __init__(self, user, host, port=22):
        self.user = user
        self.host = host
        self.port = port or 22

    def __call__(self, *args, **kwargs):
        logging.info('run command: "{}"'.format(self.process.ran))

    def out_iteract(self, char, stdin):
        if isinstance(char, str):
            self.out += char.encode('utf8')
        else:
            self.out += char

        if self.out.decode('utf-8', errors='ignore').endswith('password: '):
            self.clear()
            stdin.put(self.get_password() + '\n')

    def err_iteract(self, char, stdin):
        if isinstance(char, str):
            self.out += char.encode('utf8')
        else:
            self.out += char

    def get_password(self):
        logging.debug('request password')

        if not self.password:
            prompt = 'Need password for {}@{}:{}: '.format(self.user, self.host, self.port)
            self.password = getpass(prompt)

        return self.password

    def clear(self):
        self.out = b''
        self.error = b''

    def wait(self):
        return self.process.wait()


class SSHController(Controller):
    def __call__(self, *args, **kwargs):
        self.process = ssh(
                            '-o UserKnownHostsFile=/dev/null',
                            '-o StrictHostKeyChecking=no',
                            '-o LogLevel=quiet',
                            '{}@{}'.format(self.user, self.host), '-p', self.port,
                            *args,
                            _out=self.out_iteract, _out_bufsize=0, _tty_in=True,
                            _err=self.err_iteract, **kwargs)

        super().__call__(*args, **kwargs)


class SCPController(Controller):
    def __call__(self, local_file, remote_file, **kwargs):
        self.process = scp(
                            '-o UserKnownHostsFile=/dev/null',
                            '-o StrictHostKeyChecking=no',
                            '-o LogLevel=quiet',
                            '-P', self.port,
                            local_file,
                            '{}@{}:{}'.format(self.user, self.host, remote_file),
                            _out=self.out_iteract, _out_bufsize=0, _tty_in=True,
                            _err=self.err_iteract, **kwargs)

        super().__call__(local_file, remote_file, **kwargs)


def get_authorized_keys(controller=None, user=None, host=None, port=None):
    if not controller and (user and host):
        controller = SSHController(user, host, port)
    elif not controller:
        raise ValueError('Must set controller or user and host.')

    try:
        controller('cat ~/.ssh/authorized_keys')
        controller.wait()
    except Exception:
        logging.critical(controller.out.decode('utf8', errors='ignore'))
        raise

    out = controller.out.decode('utf8', errors='ignore')
    return [line.strip() for line in out.split('\n')]


def set_authorized_keys(keys, controller=None, user=None, host=None, port=None):
    if not controller and (user and host):
        controller = SCPController(user, host, port)
    elif not controller:
        raise ValueError('Must set controller or user and host.')

    with NamedTemporaryFile('w+b', buffering=0) as tmp:
        data = '\n'.join(keys)
        tmp.write(data.encode('utf8'))

        if data and data[-1] != '\n':
            tmp.write(b'\n')

        try:
            controller(tmp.name, '~/.ssh/authorized_keys')
            controller.wait()
        except Exception:
            logging.critical(controller.out.decode('utf8', errors='ignore'))
            raise
