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

import simple_message_pb2

from conftest import MyProtoSql


class TestSimpleMessage:

    def test_decode(self, myprotosql: MyProtoSql):
        message = simple_message_pb2.SimpleMessage()
        message.a = 123456
        assert (myprotosql.decode(message.SerializeToString(), 'SimpleMessage') ==
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

    def test_decode_raw(self, myprotosql: MyProtoSql):
        message = simple_message_pb2.SimpleMessage()
        message.a = 123456
        assert (myprotosql.decode_raw(message.SerializeToString()) ==
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

    def test_decode_raw_jsonformat(self, myprotosql: MyProtoSql):
        message = simple_message_pb2.SimpleMessage()
        message.a = 123456
        assert myprotosql.decode_raw_jsonformat(message.SerializeToString()) == {"1": 123456}

    def test_decode_raw_textformat(self, myprotosql: MyProtoSql):
        message = simple_message_pb2.SimpleMessage()
        message.a = 123456
        assert myprotosql.decode_raw_textformat(message.SerializeToString()) == '1: 123456\n'

    def test_decode_jsonformat(self, myprotosql: MyProtoSql):
        message = simple_message_pb2.SimpleMessage()
        message.a = 123456
        assert myprotosql.decode_jsonformat(message.SerializeToString(), 'SimpleMessage') == {"a": 123456}

    def test_decode_textformat(self, myprotosql: MyProtoSql):
        message = simple_message_pb2.SimpleMessage()
        message.a = 123456
        assert myprotosql.decode_textformat(message.SerializeToString(), 'SimpleMessage') == 'a: 123456\n'
