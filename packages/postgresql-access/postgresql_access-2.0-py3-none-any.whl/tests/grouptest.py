#!/usr/bin/env python3
import argparse
import configparser
import logging

import keyring
from keyring import backend

from postgresql_access import postgresql_access_logger
from postgresql_access.database import DatabaseConfig


def main():
#    for kr in backend.get_all_keyring():
#        print(kr)
    kr = keyring.get_keyring()
    print(kr)
    logging.basicConfig()
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-l', '--loglevel', default='WARN', help="Python logging level")
    parser.add_argument('config',help="ini style config")

    args = parser.parse_args()
    postgresql_access_logger.setLevel(getattr(logging,args.loglevel))
    cp = configparser.ConfigParser()
    with open(args.config) as f:
        cp.read_file(f)

    db = DatabaseConfig(config=cp)
    c = db.connect(application_name="access test")
    with c.cursor() as cursor:
        cursor.execute('select now()')
        print(cursor.fetchone()[0])


if __name__ == "__main__":
    main()
