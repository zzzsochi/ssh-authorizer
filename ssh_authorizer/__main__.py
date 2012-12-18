
"""
ssh-authorizer help
ssh-authorizer get zzz@dev.durakov.net
ssh-authorizer add zzz@dev.durakov.net key1 key2...
ssh-authorizer del zzz@dev.durakov.net id1 id2...
ssh-authorizer test zzz@dev.durakov.net key1 key2...
"""

import sys
import logging

from .helpers import parse_ssh_string
from .commands import help, get, add, delete, test

logging.basicConfig(level=logging.ERROR)

commands = ['help', 'get', 'add', 'del', 'test']


def invalid_command(command):
    logging.error('command "{}" not implemented: {}'.format(command, sys.argv))
    print("Usage: ssh_keys {help,get,add,del,test} [--raw] ...")
    print("{}: invalid command: '{}'".format(sys.argv[0], command))
    print("Choose from: {}.".format(command, ', '.join(commands)))
    sys.exit(1)


def main():
    argv = sys.argv[1:]

    if not argv or argv[0] == 'help':
        logging.debug('command "help" used: {}'.format(sys.argv))
        help()
        sys.exit(0)

    command = argv[0]

    if len(argv) < 2:
        help()
        sys.exit(1)

    if command == 'get':
        logging.debug('command "get" used: {}'.format(sys.argv))

        if len(argv) > 2 and argv[1] == '--raw':
            raw = True
            del argv[1]
        else:
            raw = False

        user, host, port = parse_ssh_string(argv[1])
        get(user, host, port, raw)

    elif command == 'add':
        logging.debug('command "add" used: {}'.format(sys.argv))
        user, host, port = parse_ssh_string(argv[1])
        add(user, host, port, argv[2:])

    elif command == 'del':
        logging.debug('command "del" used: {}'.format(sys.argv))
        user, host, port = parse_ssh_string(argv[1])
        delete(user, host, port, [int(i) for i in argv[2:]])

    elif command == 'test':
        logging.debug('command "test" used: {}'.format(sys.argv))
        user, host, port = parse_ssh_string(argv[1])
        test(user, host, port, argv[2:])

    else:
        invalid_command(command)

if __name__ == '__main__':
    main()
