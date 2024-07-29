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

import everything_pb2

from conftest import MyProtoSql


class TestAllFieldTypes:

    def test_decode_jsonformat(self, myprotosql: MyProtoSql):
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

        assert (myprotosql.decode_jsonformat(message.SerializeToString(), 'foo.bar.test.everything.ComplexNestedMessage') ==
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
                        'someBytes': 'AQIDBAUGBwgJ'
                    },
                    'level1': {'level2': {'level3': {'aString': 'nested'}}}
                 })

    def test_decode_textformat(self, myprotosql: MyProtoSql):
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

        assert (myprotosql.decode_textformat(message.SerializeToString(), 'foo.bar.test.everything.ComplexNestedMessage') ==
                ('all_fixed_32: {\n'
                 ' an_unsigned_int32: 4294967295\n'
                 ' a_signed_int32: -12\n'
                 ' a_float: 12.375f\n'
                 '}\n'
                 'all_fixed_64: {\n'
                 ' an_unsigned_int64: 18446744073709551615\n'
                 ' a_signed_int64: -4294967295\n'
                 ' a_double: 1234567.7654321f\n'
                 '}\n'
                 'all_varint: {\n'
                 ' a_signed_int32: 123456\n'
                 ' a_signed_zigzag_int32: -789123\n'
                 ' an_unsigned_int32: 4294967295\n'
                 ' a_signed_int64: 123456789\n'
                 ' a_signed_zigzag_int64: -123456789\n'
                 ' an_unsigned_int64: 18446744073709551615\n'
                 ' a_boolean: true\n'
                 '}\n'
                 'all_len: {\n'
                 ' a_string: "A nice string"\n'
                 ' some_bytes: "\\x01\\x02\\x03\\x04\\x05\\x06\\x07\\x08\\x09"\n'
                 '}\n'
                 'level1: {\n'
                 ' level2: {\n'
                 '  level3: {\n'
                 '   a_string: "nested"\n'
                 '  }\n'
                 ' }\n'
                 '}\n'))
