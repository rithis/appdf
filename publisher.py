from argparse import ArgumentParser
import appdf_parser
import publishers

argument_parser = ArgumentParser(description="AppDF publisher")
argument_parser.add_argument("file", metavar="FILE", help="AppDF file")
argument_parser.add_argument("--username", help="Google Play username")
argument_parser.add_argument("--password", help="Google Play password")
argument_parser.add_argument("--validate", "-v", action="store_true",
                             help="Validate AppDF schema")
argument_parser.add_argument("--debug-dir",
                             help="Directory for browser screenshots")
args = argument_parser.parse_args()

appdf = appdf_parser.parse(args.file, args.validate)
publisher = publishers.GooglePlay(args.username, args.password, args.debug_dir)
publisher.publish(appdf)
