#  Copyright (c) 2024. Janick Reynders
#
#  This file is part of Myprotosql.
#
#  Myprotosql is free software: you can redistribute it and/or modify it under the terms of the
#  GNU Lesser General Public License as published by the Free Software Foundation, either
#  version 3 of the License, or (at your option) any later version.
#
#  Myprotosql is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
#  without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#  See the GNU Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public License along with Myprotosql.
#  If not, see <https://www.gnu.org/licenses/>.
import json

import pytest
import mysql.connector

import sys
sys.path.append("../build")

@pytest.fixture(scope="session")
def db():
    return mysql.connector.connect(
        user='test_db',
        password='test_db',
        host='127.0.0.1',
        database='test_db')


@pytest.fixture(scope="session")
def myprotosql(db):
    return MyProtoSql(db)

class MyProtoSql():

    def __init__(self, db):
        self.db = db
    def decode(self, p_bytes, p_message_type):
        with self.db.cursor() as cursor:
            cursor.execute("select _myproto_flatten_message(%s, %s, myproto_descriptors())", (p_bytes, p_message_type))
            return json.loads(cursor.fetchone()[0])

    def decode_raw(self, p_bytes):
        with self.db.cursor() as cursor:
            cursor.execute("select _myproto_flatten_message(%s, NULL, NULL)", (p_bytes,))
            return json.loads(cursor.fetchone()[0])

    def decode_raw_textformat(self, p_bytes):
        with self.db.cursor() as cursor:
            cursor.execute("select myproto_decode_to_textformat(%s, NULL, NULL)", (p_bytes, ))
            return cursor.fetchone()[0]

    def decode_raw_jsonformat(self, p_bytes):
        with self.db.cursor() as cursor:
            cursor.execute("select myproto_decode_to_jsonformat(%s, NULL, NULL)", (p_bytes, ))
            return json.loads(cursor.fetchone()[0])

    def decode_jsonformat(self, p_bytes, p_message_type):
        with self.db.cursor() as cursor:
            cursor.execute("select myproto_decode_to_jsonformat(%s, %s, myproto_descriptors())", (p_bytes, p_message_type))
            return json.loads(cursor.fetchone()[0])

    def decode_textformat(self, p_bytes, p_message_type):
        with self.db.cursor() as cursor:
            cursor.execute("select myproto_decode_to_textformat(%s, %s, myproto_descriptors())", (p_bytes, p_message_type))
            return cursor.fetchone()[0]