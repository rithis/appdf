from argparse import ArgumentParser
import appdf_parser
from publishers import google_play

argument_parser = ArgumentParser(description="AppDF publisher")
argument_parser.add_argument("file", metavar="FILE", help="AppDF file")
argument_parser.add_argument("--username", help="Google Play username")
argument_parser.add_argument("--password", help="Google Play password")
argument_parser.add_argument("--validate", "-v", action="store_true",
                             help="Validate AppDF schema")
args = argument_parser.parse_args()

appdf = appdf_parser.parse(args.file, args.validate)
google_play.publish(appdf, args.username, args.password)
