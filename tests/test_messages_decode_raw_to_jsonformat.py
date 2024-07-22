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
import simple_message_pb2
import string_message_pb2
import repeated_fields_pb2
import submessage_pb2
import group_pb2
import oneof_pb2
import packed_pb2
import repeatedv3_pb2
from mysql.connector import MySQLConnection


class TestDecodeRawJsonFormat:

    def jsonformat(self, connection, p_bytes):
        with connection.cursor() as cursor:
            cursor.execute("select myproto_decode_to_jsonformat(%s, NULL, NULL)", (p_bytes, ))
            return json.loads(cursor.fetchone()[0])

    def test_simple_message(self, db:  MySQLConnection):
        message = simple_message_pb2.SimpleMessage()
        message.a = 123456
        assert self.jsonformat(db, message.SerializeToString()) == {"1": 123456}

    def test_string_message(self, db:  MySQLConnection):
        message = string_message_pb2.StringMessage()
        message.b = 'Hello World!'
        assert self.jsonformat(db, message.SerializeToString()) == {"2": "Hello World!"}

    def test_repeated_fields_message(self, db:  MySQLConnection):
        message = repeated_fields_pb2.RepeatedFields()
        message.d = '123'
        message.e.append(1)
        message.e.append(2)
        message.e.append(3)

        assert self.jsonformat(db, message.SerializeToString()) == {"4": "123", "5": [1, 2, 3]}


    def test_repeated_fields_one_element(self, db:  MySQLConnection):
        message = repeated_fields_pb2.RepeatedFields()
        message.d = '123'
        message.e.append(1)

        assert self.jsonformat(db, message.SerializeToString()) == {"4": "123", "5": 1}

    def test_repeated_fields_submessage(self, db:  MySQLConnection):
        message = repeated_fields_pb2.RepeatedFields()
        g1 = message.g.add()
        g1.a = 1
        g2 = message.g.add()
        g2.a = 2

        assert self.jsonformat(db, message.SerializeToString()) == {"7": [{"1":1}, {"1":2}]}

    def test_repeated_fields_one_submessage(self, db:  MySQLConnection):
        message = repeated_fields_pb2.RepeatedFields()
        g1 = message.g.add()
        g1.a = 1

        assert self.jsonformat(db, message.SerializeToString()) == {"7": {"1":1}}



    def test_submessage(self, db:  MySQLConnection):
        message = submessage_pb2.ParentMessage()
        message.c.a = 123456

        assert self.jsonformat(db, message.SerializeToString()) == {"3": {"1": 123456}}

    def test_group(self, db:  MySQLConnection):
        message = group_pb2.GroupMessage()
        message.mygroup.a = 'a group'
        message.mygroup.b = 123456

        assert self.jsonformat(db, message.SerializeToString()) == {"1": {"1": "a group", "2": 123456}}

    def test_oneof_submessage(self, db: MySQLConnection):
        message = oneof_pb2.OneOfMessage()
        message.sub_message.a = 123456

        assert self.jsonformat(db, message.SerializeToString()) == {"9": {"1": 123456}}

    def test_oneof_string(self, db: MySQLConnection):
        message = oneof_pb2.OneOfMessage()
        message.name = 'a string'

        assert self.jsonformat(db, message.SerializeToString()) == {"4": "a string"}


    def test_packed_repeated_fields_cannot_be_recognized_as_such(self, db:  MySQLConnection):
        message = packed_pb2.PackedFields()
        message.f.append(1)
        message.f.append(2)
        message.f.append(3)

        assert self.jsonformat(db, message.SerializeToString()) == {"6": "\x01\x02\x03"}

    def test_packed_repeatedv3_fields_cannot_be_recognized_as_such_because_they_are_packed_by_default(self, db:  MySQLConnection):
        message = repeatedv3_pb2.RepeatedV3()
        message.f.append(1)
        message.f.append(2)
        message.f.append(3)

        assert self.jsonformat(db, message.SerializeToString()) == {"6": "\x01\x02\x03"}

