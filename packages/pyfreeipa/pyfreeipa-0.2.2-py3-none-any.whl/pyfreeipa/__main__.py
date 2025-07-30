"""
A generic wrapper script for the pyfreeipa Api class
"""
import json
import sys
from pyfreeipa.Api import Api
from pyfreeipa.configuration import CONFIG


def main():
    """
    @brief      This provides a wrapper for the pyfreeipa module

    @return     { description_of_the_return_value }
    """

    if CONFIG['command'] == 'dumpconfig':
        print(json.dumps(CONFIG, indent=2, sort_keys=True))
        sys.exit(0)

    # Define API session
    ipaapi = Api(
        host=CONFIG['ipaserver']['host'],
        username=CONFIG['ipaserver']['user'],
        password=CONFIG['ipaserver']['password'],
        port=CONFIG['ipaserver']['port'],
        verify_ssl=CONFIG['ipaserver']['verify_ssl'],
        verify_method=CONFIG['ipaserver']['verify_method'],
        verify_warnings=CONFIG['ipaserver']['verify_warnings'],
        dryrun=CONFIG['dryrun']
    )

    if CONFIG['command'] == 'connectiontest':
        print(
            "Test connection to %s" %
            CONFIG['ipaserver']['host']
        )

        response = ipaapi.ping()
        if response.ok:
            print(
                'Successfully pinged as %s on %s' %
                (
                    CONFIG['ipaserver']['user'],
                    CONFIG['ipaserver']['host']
                )
            )
            result = response.json()['result']
            print(result['summary'])
        else:
            print(
                'Failed to ping as %s in to %s, reason "%s: %s"' %
                (
                    CONFIG['ipaserver']['user'],
                    CONFIG['ipaserver']['host'],
                    response.status_code,
                    response.reason
                )
            )

    else:
        print("No command provided")


if __name__ == "__main__":
    main()
