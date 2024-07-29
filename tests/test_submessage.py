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

import submessage_pb2

from conftest import MyProtoSql


class TestSubmessage:

    def test_decode(self, myprotosql: MyProtoSql):
        message = submessage_pb2.ParentMessage()
        message.c.a = 123456

        assert (myprotosql.decode(message.SerializeToString(), 'ParentMessage') ==
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

    def test_decode_raw(self, myprotosql: MyProtoSql):
        message = submessage_pb2.ParentMessage()
        message.c.a = 123456

        assert (myprotosql.decode_raw(message.SerializeToString()) ==
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

    def test_decode_raw_jsonformat(self, myprotosql: MyProtoSql):
        message = submessage_pb2.ParentMessage()
        message.c.a = 123456

        assert myprotosql.decode_raw_jsonformat(message.SerializeToString()) == {"3": {"1": 123456}}

    def test_decode_raw_textformat(self, myprotosql: MyProtoSql):
        message = submessage_pb2.ParentMessage()
        message.c.a = 123456

        assert myprotosql.decode_raw_textformat(message.SerializeToString()) == '3: {\n 1: 123456\n}\n'

    def test_decode_jsonformat(self, myprotosql: MyProtoSql):
        message = submessage_pb2.ParentMessage()
        message.c.a = 123456

        assert myprotosql.decode_jsonformat(message.SerializeToString(), 'ParentMessage') == {"c": {"a": 123456}}

    def test_decode_textformat(self, myprotosql: MyProtoSql):
        message = submessage_pb2.ParentMessage()
        message.c.a = 123456

        assert myprotosql.decode_textformat(message.SerializeToString(), 'ParentMessage') == 'c: {\n a: 123456\n}\n'
