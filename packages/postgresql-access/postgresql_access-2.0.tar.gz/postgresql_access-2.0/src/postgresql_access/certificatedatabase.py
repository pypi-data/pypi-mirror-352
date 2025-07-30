#!/usr/bin/env python3
import os
import pwd
from typing import Mapping

import psycopg2

"""
object wrapper for psycopg2
"""

def _current_user():
    """get current linux user"""
    return pwd.getpwuid(os.geteuid()).pw_name


class CertificateDatabase:

    def __init__(self,*,host:str,database:str,user:str,application_name:str,client_cert:str,client_key:str,
                 root_cert:str):
        self.app_name = 'Python app'
        self.schema = None
        self.port = 5432
        self.host = host
        self.database = database
        self.user = user
        self.application_name = application_name
        self.client_cert = client_cert
        self.client_key = client_key
        self.root_cert = root_cert
        files = (self.client_cert,self.client_key,self.root_cert)
        missing = [f for f in files if not os.path.exists(f)]
        if missing:
            raise ValueError(f"Missing configuration file(s): {','.join(missing)}")
        permissions = [f for f in files if not os.access(f,os.R_OK)]
        if permissions:
            raise ValueError(f"No read access file(s): {','.join(permissions)}")


    def connect(self):
        """Connect to database, set schema if present, return connection"""
        connect_string = f"""host='{self.host}' dbname='{self.database}' user='{self.user}'  port={self.port}"""
        try:
            conn = psycopg2.connect(connect_string, application_name=self.application_name,
                                    sslmode='verify-full',
                                    sslcert=self.client_cert,
                                    sslkey=self.client_key,sslrootcert=self.root_cert)
        except psycopg2.OperationalError as oe:
            if 'no password' in str(oe):
                raise ValueError(f"Invalid certificates or key for user {self.user}, or not authorized by server")
            raise
        if self.schema is not None:
            with conn.cursor() as cursor:
                cursor.execute(f"set search_path to {self.schema}")
            conn.commit()

        return conn

    @staticmethod
    def create_from_dict(data:Mapping,application_name:str):
        h = data['host']
        d = data['database']
        u = data.get('user',_current_user())
        cc = data['client certificate']
        rc = data['root certificate']
        ck = data['client key']
        return CertificateDatabase(host=h, database=d, user=u, application_name=application_name, client_cert=cc,
                                   client_key=ck, root_cert=rc)

