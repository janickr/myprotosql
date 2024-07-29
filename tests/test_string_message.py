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

import string_message_pb2

from conftest import MyProtoSql


class TestStringMessage:

    def test_decode_raw(self, myprotosql: MyProtoSql):
        message = string_message_pb2.StringMessage()
        message.b = 'Hello World!'
        assert (myprotosql.decode_raw(message.SerializeToString()) ==
                [
                    {
                        'path': '$',
                        'type': 'field',
                        'depth': 0,
                        'value': 'Hello World!',
                        'field_name': None,
                        'field_json_name': None,
                        'repeated': False,
                        'field_type': 'TYPE_STRING',
                        'field_number': 2
                    }
                ])

    def test_decode_raw_recover_from_malformed_submessage(self, myprotosql: MyProtoSql):
        message = string_message_pb2.StringMessage()
        message.b = 'Repeated!'
        assert (myprotosql.decode_raw(message.SerializeToString()) ==
                [
                    {
                        'path': '$',
                        'type': 'field',
                        'depth': 0,
                        'value': 'Repeated!',
                        'field_name': None,
                        'field_json_name': None,
                        'repeated': False,
                        'field_type': 'TYPE_STRING',
                        'field_number': 2
                    }
                ])

    def test_decode_raw_recover_from_malformed_submessage_wiretype_would_be_6(self, myprotosql: MyProtoSql):
        message = string_message_pb2.StringMessage()
        message.b = 'nested'
        assert (myprotosql.decode_raw(message.SerializeToString()) ==
                [
                    {
                        'path': '$',
                        'type': 'field',
                        'depth': 0,
                        'value': 'nested',
                        'field_name': None,
                        'field_json_name': None,
                        'repeated': False,
                        'field_type': 'TYPE_STRING',
                        'field_number': 2
                    }
                ])

    def test_decode(self, myprotosql: MyProtoSql):
        message = string_message_pb2.StringMessage()
        message.b = 'Hello World!'
        assert (myprotosql.decode(message.SerializeToString(), 'StringMessage') ==
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

    def test_decode_recover_from_malformed_submessage(self, myprotosql: MyProtoSql):
        message = string_message_pb2.StringMessage()
        message.b = 'Repeated!'
        assert (myprotosql.decode(message.SerializeToString(), 'StringMessage') ==
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

    def test_decode_raw_textformat(self, myprotosql: MyProtoSql):
        message = string_message_pb2.StringMessage()
        message.b = 'Hello World!'
        assert myprotosql.decode_raw_textformat(message.SerializeToString()) == '2: "Hello World!"\n'

    def test_decode_raw_jsonformat(self, myprotosql: MyProtoSql):
        message = string_message_pb2.StringMessage()
        message.b = 'Hello World!'
        assert myprotosql.decode_raw_jsonformat(message.SerializeToString()) == {"2": "Hello World!"}

    def test_decode_jsonformat(self, myprotosql: MyProtoSql):
        message = string_message_pb2.StringMessage()
        message.b = 'Hello World!'
        assert myprotosql.decode_jsonformat(message.SerializeToString(), 'StringMessage') == {"b": "Hello World!"}

    def test_decode_textformat(self, myprotosql: MyProtoSql):
        message = string_message_pb2.StringMessage()
        message.b = 'Hello World!'
        assert myprotosql.decode_textformat(message.SerializeToString(), 'StringMessage') == 'b: "Hello World!"\n'
