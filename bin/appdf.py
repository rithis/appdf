import os
import sys

current_dir = os.path.dirname(os.path.realpath(__file__))
lib_dir = os.path.realpath(os.path.join(current_dir, "..", "lib"))
sys.path.insert(0, lib_dir)

import argparse
import appdf


def parse_args():
    argument_parser = argparse.ArgumentParser(description="AppDF publisher")

    argument_parser.add_argument("file", metavar="FILE", help="AppDF file")
    argument_parser.add_argument("--username", help="Google Play username")
    argument_parser.add_argument("--password", help="Google Play password")
    argument_parser.add_argument("--validate", "-v", action="store_true",
                                 help="Validate AppDF schema")
    argument_parser.add_argument("--debug-dir",
                                 help="Directory for browser screenshots")

    return argument_parser.parse_args()


def main():
    args = parse_args()

    app = appdf.parsers.GooglePlay(args.file)
    app.parse()

    if args.validate:
        app.validate()

    publisher = appdf.publishers.GooglePlay(app, args.username, args.password,
                                            args.debug_dir)
    publisher.publish()


if __name__ == "__main__":
    main()
