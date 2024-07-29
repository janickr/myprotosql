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

import oneof_pb2

from conftest import MyProtoSql


class TestOneOf:

    def test_decode_submessage(self, myprotosql: MyProtoSql):
        message = oneof_pb2.OneOfMessage()
        message.sub_message.a = 123456

        assert (myprotosql.decode(message.SerializeToString(), 'OneOfMessage') ==
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

    def test_decode_string(self, myprotosql: MyProtoSql):
        message = oneof_pb2.OneOfMessage()
        message.name = 'a string'

        assert (myprotosql.decode(message.SerializeToString(), 'OneOfMessage') ==
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

    def test_decode_raw_submessage(self, myprotosql: MyProtoSql):
        message = oneof_pb2.OneOfMessage()
        message.sub_message.a = 123456

        assert (myprotosql.decode_raw(message.SerializeToString()) ==
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

    def test_decode_raw_string(self, myprotosql: MyProtoSql):
        message = oneof_pb2.OneOfMessage()
        message.name = 'a string'

        assert (myprotosql.decode_raw(message.SerializeToString()) ==
                [
                    {'depth': 0,
                     'field_name': None,
                     'field_json_name': None,
                     'repeated': False,
                     'field_number': 4,
                     'field_type': 'TYPE_STRING',
                     'path': '$',
                     'type': 'field',
                     'value': 'a string'}
                ])

    def test_decode_raw_jsonformat_submessage(self, myprotosql: MyProtoSql):
        message = oneof_pb2.OneOfMessage()
        message.sub_message.a = 123456

        assert myprotosql.decode_raw_jsonformat(message.SerializeToString()) == {"9": {"1": 123456}}

    def test_decode_raw_jsonformat_string(self, myprotosql: MyProtoSql):
        message = oneof_pb2.OneOfMessage()
        message.name = 'a string'

        assert myprotosql.decode_raw_jsonformat(message.SerializeToString()) == {"4": "a string"}

    def test_decode_raw_textformat_submessage(self, myprotosql: MyProtoSql):
        message = oneof_pb2.OneOfMessage()
        message.sub_message.a = 123456

        assert myprotosql.decode_raw_textformat(message.SerializeToString()) == '9: {\n 1: 123456\n}\n'

    def test_decode_raw_textformat_string(self, myprotosql: MyProtoSql):
        message = oneof_pb2.OneOfMessage()
        message.name = 'a string'

        assert myprotosql.decode_raw_textformat(message.SerializeToString()) == '4: "a string"\n'

    def test_decode_jsonformat_submessage(self, myprotosql: MyProtoSql):
        message = oneof_pb2.OneOfMessage()
        message.sub_message.a = 123456

        assert myprotosql.decode_jsonformat(message.SerializeToString(), 'OneOfMessage') == {"subMessage": {"a": 123456}}

    def test_decode_jsonformat_string(self, myprotosql: MyProtoSql):
        message = oneof_pb2.OneOfMessage()
        message.name = 'a string'

        assert myprotosql.decode_jsonformat(message.SerializeToString(), 'OneOfMessage') == {"name": "a string"}

    def test_decode_textformat_submessage(self, myprotosql: MyProtoSql):
        message = oneof_pb2.OneOfMessage()
        message.sub_message.a = 123456

        assert myprotosql.decode_textformat(message.SerializeToString(), 'OneOfMessage') == 'sub_message: {\n a: 123456\n}\n'

    def test_decode_textformat_string(self, myprotosql: MyProtoSql):
        message = oneof_pb2.OneOfMessage()
        message.name = 'a string'

        assert myprotosql.decode_textformat(message.SerializeToString(), 'OneOfMessage') == 'name: "a string"\n'

