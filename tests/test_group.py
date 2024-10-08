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

import group_pb2

from conftest import MyProtoSql


class TestGroup:

    def test_decode(self, myprotosql: MyProtoSql):
        message = group_pb2.GroupMessage()
        message.mygroup.a = 'a group'
        message.mygroup.b = 123456

        assert (myprotosql.decode(message.SerializeToString(), 'GroupMessage') ==
                [{'depth': 0,
                  'field_json_name': 'mygroup',
                  'field_name': 'mygroup',
                  'field_number': 1,
                  'field_type': 'TYPE_GROUP',
                  'message_type': '.GroupMessage.MyGroup',
                  'path': '$',
                  'repeated': False,
                  'type': 'start message'},
                 {'depth': 1,
                  'field_json_name': 'a',
                  'field_name': 'a',
                  'field_number': 1,
                  'field_type': 'TYPE_STRING',
                  'field_type_name': None,
                  'path': '$.1',
                  'repeated': False,
                  'type': 'field',
                  'value': 'a group'},
                 {'depth': 1,
                  'field_json_name': 'b',
                  'field_name': 'b',
                  'field_number': 2,
                  'field_type': 'TYPE_INT32',
                  'field_type_name': None,
                  'path': '$.1',
                  'repeated': False,
                  'type': 'field',
                  'value': 123456},
                 {'depth': 0,
                  'field_json_name': 'a',
                  'field_name': 'mygroup',
                  'field_number': 1,
                  'field_type': 'TYPE_GROUP',
                  'message_type': '.GroupMessage.MyGroup',
                  'path': '$',
                  'repeated': False,
                  'type': 'end message'}])

    def test_decode_raw(self, myprotosql: MyProtoSql):
        message = group_pb2.GroupMessage()
        message.mygroup.a = 'a group'
        message.mygroup.b = 123456

        assert (myprotosql.decode_raw(message.SerializeToString()) ==
                [{'depth': 0,
                  'field_json_name': None,
                  'field_name': None,
                  'field_number': 1,
                  'field_type': None,
                  'message_type': None,
                  'path': '$',
                  'repeated': False,
                  'type': 'start message'},
                 {'depth': 1,
                  'field_json_name': None,
                  'field_name': None,
                  'field_number': 1,
                  'field_type': 'TYPE_STRING',
                  'field_type_name': None,
                  'path': '$.1',
                  'repeated': False,
                  'type': 'field',
                  'value': 'a group'},
                 {'depth': 1,
                  'field_json_name': None,
                  'field_name': None,
                  'field_number': 2,
                  'field_type': None,
                  'field_type_name': None,
                  'path': '$.1',
                  'repeated': False,
                  'type': 'field',
                  'value': 123456},
                 {'depth': 0,
                  'field_json_name': None,
                  'field_name': None,
                  'field_number': 1,
                  'field_type': None,
                  'message_type': None,
                  'path': '$',
                  'repeated': False,
                  'type': 'end message'}])

    def test_decode_raw_jsonformat(self, myprotosql: MyProtoSql):
        message = group_pb2.GroupMessage()
        message.mygroup.a = 'a group'
        message.mygroup.b = 123456

        assert myprotosql.decode_raw_jsonformat(message.SerializeToString()) == {"1": {"1": "a group", "2": 123456}}

    def test_decode_raw_textformat(self, myprotosql: MyProtoSql):
        message = group_pb2.GroupMessage()
        message.mygroup.a = 'a group'
        message.mygroup.b = 123456

        assert myprotosql.decode_raw_textformat(message.SerializeToString()) == '1: {\n 1: "a group"\n 2: 123456\n}\n'

    def test_decode_jsonformat(self, myprotosql: MyProtoSql):
        message = group_pb2.GroupMessage()
        message.mygroup.a = 'a group'
        message.mygroup.b = 123456

        assert myprotosql.decode_jsonformat(message.SerializeToString(), 'GroupMessage') == {"mygroup": {"a": "a group", "b": 123456}}

    def test_decode_textformat(self, myprotosql: MyProtoSql):
        message = group_pb2.GroupMessage()
        message.mygroup.a = 'a group'
        message.mygroup.b = 123456

        assert myprotosql.decode_textformat(message.SerializeToString(), 'GroupMessage') == 'mygroup: {\n a: "a group"\n b: 123456\n}\n'
