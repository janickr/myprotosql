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
import everything_pb2
from mysql.connector import MySQLConnection


class TestDecodeJsonFormat:

    def jsonformat(self, connection, p_bytes, p_message_type):
        with connection.cursor() as cursor:
            cursor.execute("select myproto_decode_to_jsonformat(%s, %s, myproto_descriptors())", (p_bytes, p_message_type))
            return json.loads(cursor.fetchone()[0])

    def test_simple_message(self, db:  MySQLConnection):
        message = simple_message_pb2.SimpleMessage()
        message.a = 123456
        assert self.jsonformat(db, message.SerializeToString(), 'SimpleMessage') == {"a": 123456}

    def test_string_message(self, db:  MySQLConnection):
        message = string_message_pb2.StringMessage()
        message.b = 'Hello World!'
        assert self.jsonformat(db, message.SerializeToString(), 'StringMessage') == {"b": "Hello World!"}

    def test_repeated_fields_message(self, db:  MySQLConnection):
        message = repeated_fields_pb2.RepeatedFields()
        message.d = '123'
        message.e.append(1)
        message.e.append(2)
        message.e.append(3)

        assert self.jsonformat(db, message.SerializeToString(), 'RepeatedFields') == {"d": "123", "e": [1, 2, 3]}


    def test_repeated_fields_one_element(self, db:  MySQLConnection):
        message = repeated_fields_pb2.RepeatedFields()
        message.d = '123'
        message.e.append(1)

        assert self.jsonformat(db, message.SerializeToString(), 'RepeatedFields') == {"d": "123", "e": [1]}

    def test_repeated_fields_submessage(self, db:  MySQLConnection):
        message = repeated_fields_pb2.RepeatedFields()
        g1 = message.g.add()
        g1.a = 1
        g2 = message.g.add()
        g2.a = 2

        assert self.jsonformat(db, message.SerializeToString(), 'RepeatedFields') == {"g": [{"a":1}, {"a":2}]}


    def test_repeated_fields_one_submessage(self, db:  MySQLConnection):
        message = repeated_fields_pb2.RepeatedFields()
        g1 = message.g.add()
        g1.a = 1

        assert self.jsonformat(db, message.SerializeToString(), 'RepeatedFields') == {"g": [{"a":1}]}



    def test_submessage(self, db:  MySQLConnection):
        message = submessage_pb2.ParentMessage()
        message.c.a = 123456

        assert self.jsonformat(db, message.SerializeToString(), 'ParentMessage') == {"c": {"a": 123456}}

    def test_group(self, db:  MySQLConnection):
        message = group_pb2.GroupMessage()
        message.mygroup.a = 'a group'
        message.mygroup.b = 123456

        assert self.jsonformat(db, message.SerializeToString(), 'GroupMessage') == {"mygroup": {"a": "a group", "b": 123456}}

    def test_oneof_submessage(self, db: MySQLConnection):
        message = oneof_pb2.OneOfMessage()
        message.sub_message.a = 123456

        assert self.jsonformat(db, message.SerializeToString(), 'OneOfMessage') == {"subMessage": {"a": 123456}}

    def test_oneof_string(self, db: MySQLConnection):
        message = oneof_pb2.OneOfMessage()
        message.name = 'a string'

        assert self.jsonformat(db, message.SerializeToString(), 'OneOfMessage') == {"name": "a string"}

    def test_packed_repeated_fields(self, db:  MySQLConnection):
        message = packed_pb2.PackedFields()
        message.f.append(1)
        message.f.append(2)
        message.f.append(3)

        assert (self.jsonformat(db, message.SerializeToString(), 'PackedFields') == {"f": [1, 2, 3]})

    def test_packed_repeatedv3_fields(self, db:  MySQLConnection):
        message = repeatedv3_pb2.RepeatedV3()
        message.f.append(1)
        message.f.append(2)
        message.f.append(3)

        assert (self.jsonformat(db, message.SerializeToString(), 'RepeatedV3') == {"f": [1, 2, 3]})

    def test_everything(self, db:  MySQLConnection):
        message = everything_pb2.ComplexNestedMessage()
        message.all_varint.a_signed_int32=123456
        message.all_varint.a_signed_zigzag_int32=-789123
        message.all_varint.an_unsigned_int32=4294967295
        message.all_varint.a_signed_int64=123456789
        message.all_varint.a_signed_zigzag_int64=-123456789
        message.all_varint.an_unsigned_int64=18446744073709551615
        message.all_varint.a_boolean=True
        message.all_fixed_32.an_unsigned_int32=4294967295
        message.all_fixed_32.a_signed_int32=-12
        message.all_fixed_32.a_float=12.375
        message.all_fixed_64.an_unsigned_int64=18446744073709551615
        message.all_fixed_64.a_signed_int64=-4294967295
        message.all_fixed_64.a_double=1234567.7654321
        message.all_len.a_string='A nice string'
        message.all_len.some_bytes=bytes.fromhex('010203040506070809')
        message.level1.level2.level3.a_string='nested'

        assert (self.jsonformat(db, message.SerializeToString(), 'foo.bar.test.everything.ComplexNestedMessage') ==
                {
                    'allVarint': {
                        'aSignedInt32': 123456,
                        'aSignedZigzagInt32': -789123,
                        'anUnsignedInt32': 4294967295,
                        'aSignedInt64': 123456789,
                        'aSignedZigzagInt64': -123456789,
                        'anUnsignedInt64': 18446744073709551615,
                        'aBoolean': True
                    },
                     'allFixed32': {
                         'anUnsignedInt32': 4294967295,
                         'aSignedInt32': -12,
                         'aFloat': 12.375,
                     },
                     'allFixed64': {
                         'anUnsignedInt64': 18446744073709551615,
                         'aSignedInt64': -4294967295,
                         'aDouble': 1234567.7654321,
                     },
                    'allLen': {
                        'aString': 'A nice string',
                        'someBytes': '\x01\x02\x03\x04\x05\x06\x07\x08\t'
                    },
                    'level1': {'level2': {'level3': {'aString': 'nested'}}}
                 })

