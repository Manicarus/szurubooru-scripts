import argparse
import configparser
import appdirs
import os
import shutil
import pprint
import dryable
from distutils.util import strtobool

APPNAME = 'szuru-toolkit'

class UserInput:
    def __init__(self):
        self.config_file_path  = ''
        self.failsafe_dir_path = ''
        self.local_temp_path   = ''
        self.booru_address     = ''
        self.booru_api_token   = ''
        self.booru_api_url     = ''
        self.booru_offline     = ''
        self.booru_headers     = ''
        self.sankaku_url       = ''
        self.query             = ''
        self.preferred_booru   = ''
        self.fallback_booru    = ''
        self.rating            = ''
        self.tags              = []
        self.source            = []

        # Default values
        config_file = 'config.ini'
        config_dir = appdirs.user_config_dir(APPNAME, appauthor=False)
        config_file_path = os.path.join(config_dir, config_file)

        failsafe_dir = 'failsafe'
        data_dir = appdirs.user_data_dir(APPNAME, appauthor=False)
        failsafe_dir_path = os.path.join(data_dir, failsafe_dir)

        self.config_file_path = config_file_path
        self.failsafe_dir_path = failsafe_dir_path

    def parse_input(self):
        """
        Parse the user input to the script auto_tagger.py and set the object attributes accordingly.
        """

        # Default values
        default_source_path = os.getcwd()

        # Create the parser
        parser = argparse.ArgumentParser(description='This script will automagically tag your szurubooru posts based on your input query.')

        # Add the arguments
        parser.add_argument(
            '--sankaku_url', dest='sankaku_url',
            help='Fetch tags from specified Sankaku URL instead of searching IQDB.'
        )
        parser.add_argument(
            'query', nargs='?',
            help='Specify a single post id to tag or a szuru query. E.g. \'date:today tag-count:0\''
        )
        parser.add_argument(
            '-s', '--source', nargs='*',
            default=[default_source_path],
            help='List of source directory or filename (default=<current working directory>)'
        )
        parser.add_argument(
            '-t', '--tags', nargs='*',
            default=[],
            help='Upload images with provided tags'
        )
        parser.add_argument(
            '--safe',
            action='store_true',
            help='Upload images with safe flag, otherwise images are marked unsafe'
        )
        parser.add_argument(
            '--remove',
            action='store_true',
            help='Remove images after upload is complete. Ignored when dry-run'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Execute without creating/removing anything'
        )

        # Execute the parse_args() method
        args = parser.parse_args()

        self.sankaku_url = args.sankaku_url
        self.query       = args.query
        self.source      = args.source
        self.remove      = args.remove
        self.rating      = 'safe' if args.safe else 'unsafe'
        self.tags        = args.tags

        # Activate/deactivate dryable decorator
        dryable.set(args.dry_run)

    def parse_config(self):
        """
        Parse the user config and set the object attributes accordingly.
        """

        if not os.path.isfile(self.config_file_path):
            print('Could not find configuration file:', self.config_file_path)

        config = configparser.ConfigParser()
        config.read(self.config_file_path)

        self.booru_address   = config['szurubooru']['address']
        self.booru_api_url   = self.booru_address + '/api'
        self.booru_api_token = config['szurubooru']['api_token']
        self.booru_headers   = {'Accept': 'application/json', 'Authorization': 'Token ' + self.booru_api_token}
        self.booru_offline   = strtobool(config['szurubooru']['offline'])
        self.preferred_booru = config['options'].get('preferred_booru', 'danbooru')
        self.fallback_booru  = config['options'].get('fallback_booru', 'sankaku')
        self.local_temp_path = config['options'].get('local_temp_path', 'tmp')

        config_failsafe_dir = config['options']['failsafe_directory']
        if config_failsafe_dir:
            self.failsafe_dir_path = config_failsafe_dir

    def describe(self):
        """
        Prints the currently assigned attributes of the object.
        """

        data = {
            'booru_address'   : self.booru_address,
            'booru_api_url'   : self.booru_api_url,
            'booru_api_token' : self.booru_api_token,
            'booru_headers'   : self.booru_headers,
            'booru_offline'   : self.booru_offline,
            'preferred_booru' : self.preferred_booru,
            'fallback_booru'  : self.fallback_booru,
            'tags'            : self.tags,
            'source'          : self.source,
            'failsafe_dir_path'   : self.failsafe_dir_path,
        }

        print()
        print('Configuration :')
        pprint.PrettyPrinter().pprint(data)
