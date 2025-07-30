"""
Blueprint Model Repository Populator

"""
import logging
import logging.config
import sys
import argparse
from pathlib import Path
from xuml_populate.system import System
from xuml_populate import version
import atexit

_logpath = Path("modeldb.log")
_progname = 'Blueprint model repository populator'

def clean_up():
    """Normal and exception exit activities"""
    _logpath.unlink(missing_ok=True)


def get_logger():
    """Initiate the logger"""
    log_conf_path = Path(__file__).parent / 'log.conf'  # Logging configuration is in this file
    logging.config.fileConfig(fname=log_conf_path, disable_existing_loggers=False)
    return logging.getLogger(__name__)  # Create a logger for this module


# Configure the expected parameters and actions for the argparse module
def parse(cl_input):
    parser = argparse.ArgumentParser(description=_progname)
    parser.add_argument('-s', '--system', action='store',
                        help='Name of the system package')
    parser.add_argument('-D', '--debug', action='store_true',
                        help='Debug mode'),
    parser.add_argument('-L', '--log', action='store_true',
                        help='Generate a diagnostic log file')
    parser.add_argument('-A', '--actions', action='store_true',
                        help='Parse actions'),
    parser.add_argument('-V', '--version', action='store_true',
                        help='Print the current version of the repo populator')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Verbose messages')
    return parser.parse_args(cl_input)


def main():
    # Start logging
    logger = get_logger()
    logger.info(f'{_progname} version: {version}')

    # Parse the command line args
    args = parse(sys.argv[1:])

    if args.version:
        # Just print the version and quit
        print(f'{_progname} version: {version}')
        sys.exit(0)

    if not args.log:
        # If no log file is requested, remove the log file before termination
        atexit.register(clean_up)

    # System package specified
    if args.system:
        system_pkg_path = Path(args.system).resolve()
        s = System(name=system_pkg_path.stem, system_path=system_pkg_path, parse_actions=args.actions,
                   verbose=args.verbose)

    logger.info("No problemo")  # We didn't die on an exception, basically
    if args.verbose:
        print("\nNo problemo")


if __name__ == "__main__":
    main()
