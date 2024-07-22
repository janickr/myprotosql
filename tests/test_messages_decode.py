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
import packed_pb2
import oneof_pb2
import packages_submessage_pb2
import imports_parentmessage_pb2
import packages_imports_parentmessage_pb2
from mysql.connector import MySQLConnection


class TestDecodeMessages:


    def decode(self, connection, p_bytes, p_message_type):
        with connection.cursor() as cursor:
            cursor.execute("select _myproto_flatten_message(%s, %s, myproto_descriptors())", (p_bytes, p_message_type))
            return json.loads(cursor.fetchone()[0])

    def test_simple_message(self, db:  MySQLConnection):
        message = simple_message_pb2.SimpleMessage()
        message.a = 123456
        assert (self.decode(db, message.SerializeToString(), 'SimpleMessage') ==
                [
                    {
                        'path': '$',
                        'type': 'field',
                        'depth': 0,
                        'value': 123456,
                        'field_name': 'a',
                        'field_json_name': 'a',
                        'repeated': False,
                        'field_type': 'TYPE_INT32',
                        'field_number': 1
                    }
                ])

    def test_string_message(self, db:  MySQLConnection):
        message = string_message_pb2.StringMessage()
        message.b = 'Hello World!'
        assert (self.decode(db, message.SerializeToString(), 'StringMessage') ==
                [
                    {
                        "path": "$",
                        "type": "field",
                        "depth": 0,
                        "value": "Hello World!",
                        "field_name": "b",
                        "field_json_name": "b",
                        'repeated': False,
                        "field_type": "TYPE_STRING",
                        "field_number": 2
                    }
                ])

    def test_string_message_recover_from_malformed_submessage(self, db:  MySQLConnection):
        message = string_message_pb2.StringMessage()
        message.b = 'Repeated!'
        assert (self.decode(db, message.SerializeToString(), 'StringMessage') ==
                [
                    {
                        "path": "$",
                        "type": "field",
                        "depth": 0,
                        "value": "Repeated!",
                        "field_name": "b",
                        "field_json_name": "b",
                        'repeated': False,
                        "field_type": "TYPE_STRING",
                        "field_number": 2
                    }
                ])

    def test_repeated_fields_message(self, db:  MySQLConnection):
        message = repeated_fields_pb2.RepeatedFields()
        message.d = '123'
        message.e.append(1)
        message.e.append(2)
        message.e.append(3)

        assert (self.decode(db, message.SerializeToString(), 'RepeatedFields') ==
                [{'depth': 0,
                  'field_name': "d",
                  'field_json_name': "d",
                  'repeated': False,
                  'field_number': 4,
                  'field_type': "TYPE_STRING",
                  'path': '$',
                  'type': 'field',
                  'value': '123'},
                 {'depth': 0,
                  'field_name': "e",
                  'field_json_name': "e",
                  'repeated': True,
                  'field_number': 5,
                  'field_type': "TYPE_INT32",
                  'path': '$',
                  'type': 'field',
                  'value': 1},
                 {'depth': 0,
                  'field_name': "e",
                  'field_json_name': "e",
                  'repeated': True,
                  'field_number': 5,
                  'field_type': "TYPE_INT32",
                  'path': '$',
                  'type': 'field',
                  'value': 2},
                 {'depth': 0,
                  'field_name': "e",
                  'field_json_name': "e",
                  'repeated': True,
                  'field_number': 5,
                  'field_type': "TYPE_INT32",
                  'path': '$',
                  'type': 'field',
                  'value': 3}])

    def test_repeated_fields_string_message_malformed_submessage(self, db:  MySQLConnection):
        message = repeated_fields_pb2.RepeatedFields()
        message.d = 'Repeated!'
        message.e.append(1)

        assert (self.decode(db, message.SerializeToString(), 'RepeatedFields') ==
                [{'depth': 0,
                  'field_name': "d",
                  'field_json_name': "d",
                  'repeated': False,
                  'field_number': 4,
                  'field_type': "TYPE_STRING",
                  'path': '$',
                  'type': 'field',
                  'value': 'Repeated!'},
                 {'depth': 0,
                  'field_name': "e",
                  'field_json_name': "e",
                  'repeated': True,
                  'field_number': 5,
                  'field_type': "TYPE_INT32",
                  'path': '$',
                  'type': 'field',
                  'value': 1}])

    def test_repeated_fields_submessage(self, db:  MySQLConnection):
        message = repeated_fields_pb2.RepeatedFields()
        g1 = message.g.add()
        g1.a = 1
        g2 = message.g.add()
        g2.a = 2

        assert (self.decode(db, message.SerializeToString(), 'RepeatedFields') ==
                [{'depth': 0,
                  'field_json_name': 'g',
                  'field_name': 'g',
                  'field_number': 7,
                  'message_type': '.RepeatedFieldsSubMessage',
                  'path': '$',
                  'repeated': True,
                  'type': 'message'},
                 {'depth': 1,
                  'field_json_name': 'a',
                  'field_name': 'a',
                  'field_number': 1,
                  'field_type': 'TYPE_INT32',
                  'path': '$.7',
                  'repeated': False,
                  'type': 'field',
                  'value': 1},
                 {'depth': 0,
                  'field_json_name': 'g',
                  'field_name': 'g',
                  'field_number': 7,
                  'message_type': '.RepeatedFieldsSubMessage',
                  'path': '$',
                  'repeated': True,
                  'type': 'message'},
                 {'depth': 1,
                  'field_json_name': 'a',
                  'field_name': 'a',
                  'field_number': 1,
                  'field_type': 'TYPE_INT32',
                  'path': '$.7',
                  'repeated': False,
                  'type': 'field',
                  'value': 2}])


    def test_submessage(self, db:  MySQLConnection):
        message = submessage_pb2.ParentMessage()
        message.c.a = 123456

        assert (self.decode(db, message.SerializeToString(), 'ParentMessage') ==
                [
                    {'depth': 0,
                     'field_name': 'c',
                     'field_json_name': 'c',
                     'repeated': False,
                     'field_number': 3,
                     'message_type': '.SubMessage',
                     'path': '$',
                     'type': 'message'},
                    {'depth': 1,
                     'field_name': 'a',
                     'field_json_name': 'a',
                     'repeated': False,
                     'field_number': 1,
                     'field_type': 'TYPE_INT32',
                     'path': '$.3',
                     'type': 'field',
                     'value': 123456}
                ])

    def test_group(self, db:  MySQLConnection):
        message = group_pb2.GroupMessage()
        message.mygroup.a = 'a group'
        message.mygroup.b = 123456

        assert (self.decode(db, message.SerializeToString(), 'GroupMessage') ==
                [
                    {'depth': 0,
                     'field_name': 'mygroup',
                     'field_json_name': 'mygroup',
                     'repeated': False,
                     'field_number': 1,
                     'message_type': '.GroupMessage.MyGroup',
                     'path': '$',
                     'type': 'message'},
                    {'depth': 1,
                     'field_name': 'a',
                     'field_json_name': 'a',
                     'repeated': False,
                     'field_number': 1,
                     'field_type': 'TYPE_STRING',
                     'path': '$.1',
                     'type': 'field',
                     'value': 'a group'},
                    {'depth': 1,
                     'field_name': 'b',
                     'field_json_name': 'b',
                     'repeated': False,
                     'field_number': 2,
                     'field_type': 'TYPE_INT32',
                     'path': '$.1',
                     'type': 'field',
                     'value': 123456}
                ])

    def test_packages_submessage(self, db:  MySQLConnection):
        message = packages_submessage_pb2.ParentMessagePackage()
        message.c.a = 123456

        assert (self.decode(db, message.SerializeToString(), 'foo.bar.ParentMessagePackage') ==
                [
                    {'depth': 0,
                     'field_name': 'c',
                     'field_json_name': 'c',
                     'repeated': False,
                     'field_number': 3,
                     'message_type': '.foo.bar.SubMessagePackage',
                     'path': '$',
                     'type': 'message'},
                    {'depth': 1,
                     'field_name': 'a',
                     'field_json_name': 'a',
                     'repeated': False,
                     'field_number': 1,
                     'field_type': 'TYPE_INT32',
                     'path': '$.3',
                     'type': 'field',
                     'value': 123456}
                ])

    def test_imports_submessage(self, db:  MySQLConnection):
        message = imports_parentmessage_pb2.ParentMessageImports()
        message.c.a = 123456

        assert (self.decode(db, message.SerializeToString(), 'ParentMessageImports') ==
                [
                    {'depth': 0,
                     'field_name': 'c',
                     'field_json_name': 'c',
                     'repeated': False,
                     'field_number': 3,
                     'message_type': '.SubMessageImports',
                     'path': '$',
                     'type': 'message'},
                    {'depth': 1,
                     'field_name': 'a',
                     'field_json_name': 'a',
                     'repeated': False,
                     'field_number': 1,
                     'field_type': 'TYPE_INT32',
                     'path': '$.3',
                     'type': 'field',
                     'value': 123456}
                ])


    def test_submessage(self, db: MySQLConnection):
        message = packages_imports_parentmessage_pb2.ParentMessagePackageImports()
        message.c.a = 123456

        assert (self.decode(db, message.SerializeToString(), 'foo.bar.imports.parent.ParentMessagePackageImports') ==
                [
                    {'depth': 0,
                     'field_name': 'c',
                     'field_json_name': 'c',
                     'repeated': False,
                     'field_number': 3,
                     'message_type': '.foo.bar.imports.sub.SubMessagePackageImports',
                     'path': '$',
                     'type': 'message'},
                    {'depth': 1,
                     'field_name': 'a',
                     'field_json_name': 'a',
                     'repeated': False,
                     'field_number': 1,
                     'field_type': 'TYPE_INT32',
                     'path': '$.3',
                     'type': 'field',
                     'value': 123456}
                ])

    def test_oneof_submessage(self, db:  MySQLConnection):
        message = oneof_pb2.OneOfMessage()
        message.sub_message.a = 123456

        assert (self.decode(db, message.SerializeToString(), 'OneOfMessage') ==
                [
                    {'depth': 0,
                     'field_name': 'sub_message',
                     'field_json_name': 'subMessage',
                     'repeated': False,
                     'field_number': 9,
                     'message_type': '.OneOfSubMessage',
                     'path': '$',
                     'type': 'message'},
                    {'depth': 1,
                     'field_name': 'a',
                     'field_json_name': 'a',
                     'repeated': False,
                     'field_number': 1,
                     'field_type': 'TYPE_INT32',
                     'path': '$.9',
                     'type': 'field',
                     'value': 123456}
                ])

    def test_oneof_string(self, db:  MySQLConnection):
        message = oneof_pb2.OneOfMessage()
        message.name = 'a string'

        assert (self.decode(db, message.SerializeToString(), 'OneOfMessage') ==
                [
                    {'depth': 0,
                     'field_name': 'name',
                     'field_json_name': 'name',
                     'repeated': False,
                     'field_number': 4,
                     'field_type': 'TYPE_STRING',
                     'path': '$',
                     'type': 'field',
                     'value': 'a string'}
                ])

    def test_packed_repeated_fields(self, db:  MySQLConnection):
        message = packed_pb2.PackedFields()
        message.f.append(1)
        message.f.append(2)
        message.f.append(3)

        assert (self.decode(db, message.SerializeToString(), 'PackedFields') ==
                [{'depth': 0,
                  'field_name': 'f',
                  'field_json_name': 'f',
                  'repeated': True,
                  'field_number': 6,
                  'field_type': 'TYPE_INT32',
                  'path': '$',
                  'type': 'field',
                  'value': [1, 2, 3]}])
