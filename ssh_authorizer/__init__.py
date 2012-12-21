"""Manager for remote ~/.ssh/authorized_keys.

Usage: ssh-authorizer {help,get,add,del,test} [--raw] ssh_string ...

command:
        help:       Print this help.

        get:        Display remote authorized_keys.
        get --raw:  Display without formating.

        add:        Add keys to remote authorized_keys.
        del:        Delete keys from remote authorized_keys.
        test:       Test keys exist in remote authorized_keys.

ssh_string:     String with connect info: [user@]host[:port].
                By default user is current system user, port=22.

keys:           For commands "add" and "test" this is list of files with keys.
                If empty -- "~/ssh/id_rsa.pub" used.

keys:           For commad "del" this is key indeces for delete.
                See "get" without "--raw".

Examples:

ssh-authorizer get username@hostname
    Get authorized_keys in host hostname for user username.

ssh-authorizer add user@host
    Add your local "~/ssh/id_rsa.pub" to remote "~/ssh/authorized_keys".

ssh-authorizer add user@host key.pub key2.pub
    Add "key.pub" "key2.pub" to remote "~/ssh/authorized_keys".

ssh-authorizer del user@host 1 3
    Delete fist and third keys from remote "~/ssh/authorized_keys".

ssh-authorizer test user@host key.pub key2.pub
    "key.pub" "key2.pub" already in remote "~/ssh/authorized_keys"? Check it.

TODO:

ssh-authorizer del user@host
    Delete your "~/ssh/id_rsa.pub" from remote "~/ssh/authorized_keys".

ssh-authorizer del user@host zzz@macbook
    Delete key "zzz@macbook" from remote "~/ssh/authorized_keys".

get --short:  Like "get", but without key hashes.

Human readable errors.
"""
