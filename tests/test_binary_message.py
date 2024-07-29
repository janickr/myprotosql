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

import binary_message_pb2

from conftest import MyProtoSql


class TestBytesMessage:

    def test_decode_raw(self, myprotosql: MyProtoSql):
        message = binary_message_pb2.BinaryMessage()
        message.binary = bytes.fromhex('FF0000000000C03F00002040')
        assert (myprotosql.decode_raw(message.SerializeToString()) ==
                [
                    {
                        'path': '$',
                        'type': 'field',
                        'depth': 0,
                        'value': '/wAAAAAAwD8AACBA',
                        'field_name': None,
                        'field_json_name': None,
                        'repeated': False,
                        'field_type': 'TYPE_BYTES',
                        'field_number': 7
                    }
                ])

    def test_decode(self, myprotosql: MyProtoSql):
        message = binary_message_pb2.BinaryMessage()
        message.binary = bytes.fromhex('FF0000000000C03F00002040')
        assert (myprotosql.decode(message.SerializeToString(), 'BinaryMessage') ==
                [
                    {
                        "path": "$",
                        "type": "field",
                        "depth": 0,
                        "value": '/wAAAAAAwD8AACBA',
                        "field_name": "binary",
                        "field_json_name": "binary",
                        'repeated': False,
                        "field_type": "TYPE_BYTES",
                        "field_number": 7
                    }
                ])


    def test_decode_raw_textformat_is_escaped(self, myprotosql: MyProtoSql):
        message = binary_message_pb2.BinaryMessage()
        message.binary = bytes.fromhex('FF0000000000C03F00002040')
        assert myprotosql.decode_raw_textformat(message.SerializeToString()) == '7: "\\xFF\\x00\\x00\\x00\\x00\\x00\\xC0?\\x00\\x00 @"\n'

    def test_decode_raw_jsonformat_is_base64_encoded(self, myprotosql: MyProtoSql):
        message = binary_message_pb2.BinaryMessage()
        message.binary = bytes.fromhex('FF0000000000C03F00002040')
        assert myprotosql.decode_raw_jsonformat(message.SerializeToString()) == {"7": "/wAAAAAAwD8AACBA"}

    def test_decode_jsonformat_is_base64_encoded(self, myprotosql: MyProtoSql):
        message = binary_message_pb2.BinaryMessage()
        message.binary = bytes.fromhex('000000000000C03F00002040')
        assert myprotosql.decode_jsonformat(message.SerializeToString(), 'BinaryMessage') == {"binary": "AAAAAAAAwD8AACBA"}

    def test_decode_textformatis_escaped(self, myprotosql: MyProtoSql):
        message = binary_message_pb2.BinaryMessage()
        message.binary = bytes.fromhex('000000000000C03F00002040')
        assert myprotosql.decode_textformat(message.SerializeToString(), 'BinaryMessage') == 'binary: "\\x00\\x00\\x00\\x00\\x00\\x00\\xC0?\\x00\\x00 @"\n'
