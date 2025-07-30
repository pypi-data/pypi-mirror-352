"""
Process command line arguments and/or load configuration file
mostly used by the test scripts
"""
import argparse
import sys
import os.path
from typing import Union
import yaml


def do_args():
    """
    @brief      { function_description }

    @return     { description_of_the_return_value }
    """
    # Parse command line arguments and modify config
    parser = argparse.ArgumentParser(
        prog='pyfreeipa.py',
        description='Python FreeIPA tools'
    )

    # Command line arguments
    parser.add_argument(
        "-v",
        "--verbose",
        dest='verbose',
        help="Increase output to stderr and stdout",
        action="store_true"
    )

    parser.add_argument(
        "-q",
        "--quiet",
        dest='quiet',
        help="Reduce output to stderr and stdout",
        action="store_true"
    )

    parser.add_argument(
        "-d",
        "--dry_run",
        dest='dryrun',
        help="Do a dry run, no changes written to IPA server",
        action="store_true"
    )

    parser.add_argument(
        "-f",
        "--file",
        default='pyfreeipa.conf.yaml',
        dest='file',
        help="Specify a configuration file",
    )

    parser.add_argument(
        '-s',
        '--server',
        default=None,
        type=str,
        dest='server',
        help="Hostname of IPA server"
    )

    parser.add_argument(
        '-u',
        '--user',
        default=None,
        type=str,
        dest='user',
        help="The username used to connect to the IPA server"
    )

    parser.add_argument(
        '-p',
        '--password',
        default=None,
        type=str,
        dest='password',
        help="The password used to conenct to the IPA server"
    )

    parser.add_argument(
        '--uid',
        default=None,
        type=str,
        nargs='+',
        dest='uid',
        help=(
            "Passes a unique identifier, such as a uid of a user,"
            "or the uniqueid of an otptoken. Multiple uids can be specified."
        )
    )

    parser.add_argument(
        '--group',
        default=None,
        type=str,
        nargs='+',
        dest='group',
        help="The name of a group to use, multiple groups can be specified"
    )

    parser.add_argument(
        '--port',
        default=None,
        type=str,
        dest='port',
        help="The password used to conenct to the IPA server"
    )

    parser.add_argument(
        '--version',
        default=None,
        type=str,
        dest='version',
        help="The IPA server API version"
    )

    parser.add_argument(
        '--verify_ssl',
        default=None,
        type=bool,
        dest='verify_ssl',
        help=(
            "If true the SSL certificate of the"
            " IPA server will be verified"
        )
    )

    parser.add_argument(
        '--verify_warnings',
        default=None,
        type=bool,
        dest='verify_warnings',
        help=(
            "If false warnings about the SSL state of "
            "the IPA server will be silenced"
        )
    )

    parser.add_argument(
        '--verify_method',
        default=None,
        type=Union[bool, str],
        dest='verify_method',
        help=(
            "The method used to validate the SSL state of "
            "the IPA server"
        )
    )

    # Positional commands
    parser.add_argument(
        dest='command',
        help='Command help',
        default=None,
        nargs='?',
        type=str,
        choices=[
            'dumpconfig',
            'connectiontest'
        ]
    )

    return parser.parse_args()

# Create the CONFIG to be imported elsewhere
# Set defaults
CONFIG = {
    'ipaserver': {
        'host': 'ipaserver.example.org',
        'user': 'username',
        'password': None,
        'port': 443,
        'version': 2.228,
        'verify_ssl': True,
        'verify_method': True,
        'verify_warnings': True
    },
    'otptoken': {
        'managedby': [],
        'ownermanagedby': True
    }
}


ARGS = do_args()

# Override configuration defaults with values from the config file
if os.path.isfile(ARGS.file):
    with open(ARGS.file, 'r') as configfile:
        CONFIG.update(yaml.load(configfile))

# Override configuration loaded from file with command line arguments
if ARGS.server:
    CONFIG['ipaserver']['host'] = ARGS.server

if ARGS.user:
    CONFIG['ipaserver']['user'] = ARGS.user

if ARGS.password:
    CONFIG['ipaserver']['password'] = ARGS.password

if ARGS.port:
    CONFIG['ipaserver']['port'] = ARGS.port

if ARGS.version:
    CONFIG['ipaserver']['version'] = ARGS.version

# This one can be bool or str values
if ARGS.verify_method is not None:
    CONFIG['ipaserver']['verify_method'] = ARGS.verify_method

if ARGS.verify_ssl is not None:
    CONFIG['ipaserver']['verify_ssl'] = ARGS.verify_ssl

if ARGS.verify_warnings is not None:
    CONFIG['ipaserver']['verify_warnings'] = ARGS.verify_warnings

# If there's no config file, write one
if not os.path.isfile(ARGS.file):
    print(
        "The configuration file %s was missing,"
        " wrote default configuration to file" %
        ARGS.file
    )
    with open(ARGS.file, 'w') as configfile:
        yaml.dump(vars(CONFIG), configfile, default_flow_style=False)
    sys.exit(0)

# Set state from command line
CONFIG['command'] = ARGS.command
CONFIG['dryrun'] = ARGS.dryrun
CONFIG['groups'] = None
if ARGS.group:
    cleangroups = []
    for group in ARGS.group:
        if ',' in group:
            for splitgroup in group.split(','):
                cleangroups.append(splitgroup)
        else:
            cleangroups.append(group)

    CONFIG['groups'] = sorted(set(cleangroups))

CONFIG['users'] = None
if ARGS.uid:
    cleanusers = []
    for user in ARGS.uid:
        if ',' in user:
            for splituser in user.split(','):
                cleanusers.append(splituser)
        else:
            cleanusers.append(user)

    CONFIG['users'] = sorted(set(cleanusers))

if CONFIG['otptoken']['managedby']:
    if not isinstance(CONFIG['otptoken']['managedby'], list):
        CONFIG['otptoken']['managedby'] = [CONFIG['otptoken']['managedby']]
