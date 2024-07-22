
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
from mysql.connector import MySQLConnection


class TestDecodeRawMessages:

    def decode_raw(self, connection, p_bytes):
        with connection.cursor() as cursor:
            cursor.execute("select _myproto_flatten_message(%s, NULL, NULL)", (p_bytes,))
            return json.loads(cursor.fetchone()[0])

    def test_simple_message(self, db:  MySQLConnection):
        message = simple_message_pb2.SimpleMessage()
        message.a = 123456
        assert (self.decode_raw(db, message.SerializeToString()) ==
                [
                    {
                        'path': '$',
                        'type': 'field',
                        'depth': 0,
                        'value': 123456,
                        'field_name': None,
                        'field_json_name': None,
                        'repeated': False,
                        'field_type': None,
                        'field_number': 1
                    }
                ])

    def test_string_message(self, db:  MySQLConnection):
        message = string_message_pb2.StringMessage()
        message.b = 'Hello World!'
        assert (self.decode_raw(db, message.SerializeToString()) ==
                [
                    {
                        'path': '$',
                        'type': 'field',
                        'depth': 0,
                        'value': 'Hello World!',
                        'field_name': None,
                        'field_json_name': None,
                        'repeated': False,
                        'field_type': None,
                        'field_number': 2
                    }
                ])

    def test_string_message_recover_from_malformed_submessage(self, db:  MySQLConnection):
        message = string_message_pb2.StringMessage()
        message.b = 'Repeated!'
        assert (self.decode_raw(db, message.SerializeToString()) ==
                [
                    {
                        'path': '$',
                        'type': 'field',
                        'depth': 0,
                        'value': 'Repeated!',
                        'field_name': None,
                        'field_json_name': None,
                        'repeated': False,
                        'field_type': None,
                        'field_number': 2
                    }
                ])

    def test_repeated_fields_message(self, db:  MySQLConnection):
        message = repeated_fields_pb2.RepeatedFields()
        message.d = '123'
        message.e.append(1)
        message.e.append(2)
        message.e.append(3)

        assert (self.decode_raw(db, message.SerializeToString()) ==
                [{'depth': 0,
                  'field_name': None,
                  'field_json_name': None,
                  'repeated': False,
                  'field_number': 4,
                  'field_type': None,
                  'path': '$',
                  'type': 'field',
                  'value': '123'},
                 {'depth': 0,
                  'field_name': None,
                  'field_json_name': None,
                  'repeated': False,
                  'field_number': 5,
                  'field_type': None,
                  'path': '$',
                  'type': 'field',
                  'value': 1},
                 {'depth': 0,
                  'field_name': None,
                  'field_json_name': None,
                  'repeated': False,
                  'field_number': 5,
                  'field_type': None,
                  'path': '$',
                  'type': 'field',
                  'value': 2},
                 {'depth': 0,
                  'field_name': None,
                  'field_json_name': None,
                  'repeated': False,
                  'field_number': 5,
                  'field_type': None,
                  'path': '$',
                  'type': 'field',
                  'value': 3}])

    def test_repeated_fields_string_message_malformed_submessage(self, db:  MySQLConnection):
        message = repeated_fields_pb2.RepeatedFields()
        message.d = 'Repeated!'
        message.e.append(1)

        assert (self.decode_raw(db, message.SerializeToString()) ==
                [{'depth': 0,
                  'field_name': None,
                  'field_json_name': None,
                  'repeated': False,
                  'field_number': 4,
                  'field_type': None,
                  'path': '$',
                  'type': 'field',
                  'value': 'Repeated!'},
                 {'depth': 0,
                  'field_name': None,
                  'field_json_name': None,
                  'repeated': False,
                  'field_number': 5,
                  'field_type': None,
                  'path': '$',
                  'type': 'field',
                  'value': 1}])

    def test_repeated_fields_submessage(self, db:  MySQLConnection):
        message = repeated_fields_pb2.RepeatedFields()
        g1 = message.g.add()
        g1.a = 1
        g2 = message.g.add()
        g2.a = 2

        assert (self.decode_raw(db, message.SerializeToString()) ==
                [{'depth': 0,
                  'field_json_name': None,
                  'field_name': None,
                  'field_number': 7,
                  'message_type': None,
                  'path': '$',
                  'repeated': False,
                  'type': 'message'},
                 {'depth': 1,
                  'field_json_name': None,
                  'field_name': None,
                  'field_number': 1,
                  'field_type': None,
                  'path': '$.7',
                  'repeated': False,
                  'type': 'field',
                  'value': 1},
                 {'depth': 0,
                  'field_json_name': None,
                  'field_name': None,
                  'field_number': 7,
                  'message_type': None,
                  'path': '$',
                  'repeated': False,
                  'type': 'message'},
                 {'depth': 1,
                  'field_json_name': None,
                  'field_name': None,
                  'field_number': 1,
                  'field_type': None,
                  'path': '$.7',
                  'repeated': False,
                  'type': 'field',
                  'value': 2}])

    def test_submessage(self, db:  MySQLConnection):
        message = submessage_pb2.ParentMessage()
        message.c.a = 123456

        assert (self.decode_raw(db, message.SerializeToString()) ==
                [
                    {'depth': 0,
                     'field_name': None,
                     'field_json_name': None,
                     'repeated': False,
                     'field_number': 3,
                     'message_type': None,
                     'path': '$',
                     'type': 'message'},
                    {'depth': 1,
                     'field_name': None,
                     'field_json_name': None,
                     'repeated': False,
                     'field_number': 1,
                     'field_type': None,
                     'path': '$.3',
                     'type': 'field',
                     'value': 123456}
                ])

    def test_group(self, db:  MySQLConnection):
        message = group_pb2.GroupMessage()
        message.mygroup.a = 'a group'
        message.mygroup.b = 123456

        assert (self.decode_raw(db, message.SerializeToString()) ==
                [
                    {'depth': 0,
                     'field_name': None,
                     'field_json_name': None,
                     'repeated': False,
                     'field_number': 1,
                     'message_type': None,
                     'path': '$',
                     'type': 'message'},
                    {'depth': 1,
                     'field_name': None,
                     'field_json_name': None,
                     'repeated': False,
                     'field_number': 1,
                     'field_type': None,
                     'path': '$.1',
                     'type': 'field',
                     'value': 'a group'},
                    {'depth': 1,
                     'field_name': None,
                     'field_json_name': None,
                     'repeated': False,
                     'field_number': 2,
                     'field_type': None,
                     'path': '$.1',
                     'type': 'field',
                     'value': 123456}
                ])

    def test_oneof_submessage(self, db:  MySQLConnection):
        message = oneof_pb2.OneOfMessage()
        message.sub_message.a = 123456

        assert (self.decode_raw(db, message.SerializeToString()) ==
                [
                    {'depth': 0,
                     'field_name': None,
                     'field_json_name': None,
                     'repeated': False,
                     'field_number': 9,
                     'message_type': None,
                     'path': '$',
                     'type': 'message'},
                    {'depth': 1,
                     'field_name': None,
                     'field_json_name': None,
                     'repeated': False,
                     'field_number': 1,
                     'field_type': None,
                     'path': '$.9',
                     'type': 'field',
                     'value': 123456}
                ])

    def test_oneof_string(self, db:  MySQLConnection):
        message = oneof_pb2.OneOfMessage()
        message.name = 'a string'

        assert (self.decode_raw(db, message.SerializeToString()) ==
                [
                    {'depth': 0,
                     'field_name': None,
                     'field_json_name': None,
                     'repeated': False,
                     'field_number': 4,
                     'field_type': None,
                     'path': '$',
                     'type': 'field',
                     'value': 'a string'}
                ])

    def test_packed_repeated_fields(self, db:  MySQLConnection):
        message = packed_pb2.PackedFields()
        message.f.append(1)
        message.f.append(2)
        message.f.append(3)

        assert (self.decode_raw(db, message.SerializeToString()) ==
                [{'depth': 0,
                  'field_name': None,
                  'field_json_name': None,
                  'repeated': False,
                  'field_number': 6,
                  'field_type': None,
                  'path': '$',
                  'type': 'field',
                  'value': '\x01\x02\x03'},
                 ])
