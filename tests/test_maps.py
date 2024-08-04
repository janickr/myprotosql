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

import maps_pb2

from conftest import MyProtoSql


class TestMaps:

    def test_simple_decode_raw_textformat(self, myprotosql: MyProtoSql):
        message = maps_pb2.Maps()
        message.simple[1] = 'one'
        assert (myprotosql.decode_raw_textformat(message.SerializeToString()) ==
                '1: {\n'
                ' 1: 1\n'
                ' 2: "one"\n'
                '}\n'
                )

    def test_simple_decode_raw_jsonformat(self, myprotosql: MyProtoSql):
        message = maps_pb2.Maps()
        message.simple[1] = 'one'
        assert (myprotosql.decode_raw_jsonformat(message.SerializeToString()) ==
                {'1': {'1': 1, '2': 'one'}})

    def test_simple_decode_textformat(self, myprotosql: MyProtoSql):
        message = maps_pb2.Maps()
        message.simple[1] = 'one'
        assert (myprotosql.decode_textformat(message.SerializeToString(), 'Maps') ==
                'simple: {\n'
                ' key: 1\n'
                ' value: "one"\n'
                '}\n'
                )

    def test_simple_decode_jsonformat(self, myprotosql: MyProtoSql):
        message = maps_pb2.Maps()
        message.simple[1] = 'one'
        assert (myprotosql.decode_jsonformat(message.SerializeToString(), 'Maps') ==
                {'simple': {'1': 'one'}})


    def test_message_decode_raw_textformat(self, myprotosql: MyProtoSql):
        message = maps_pb2.Maps()
        message.messages.get_or_create('a string').a_value = 'one'
        assert (myprotosql.decode_raw_textformat(message.SerializeToString()) ==
                '2: {\n'
                ' 1: "a string"\n'
                ' 2: {\n'
                '  1: "one"\n'
                ' }\n'
                '}\n'
                )

    def test_message_decode_raw_jsonformat(self, myprotosql: MyProtoSql):
        message = maps_pb2.Maps()
        message.messages.get_or_create('a string').a_value = 'one'
        assert (myprotosql.decode_raw_jsonformat(message.SerializeToString()) ==
                {'2': {'1': 'a string', '2': { '1': 'one' }}})

    def test_message_decode_textformat(self, myprotosql: MyProtoSql):
        message = maps_pb2.Maps()
        message.messages.get_or_create('a string').a_value = 'one'
        assert (myprotosql.decode_textformat(message.SerializeToString(), 'Maps') ==
                'messages: {\n'
                ' key: "a string"\n'
                ' value: {\n'
                '  a_value: "one"\n'
                ' }\n'
                '}\n'
                )

    def test_message_decode_jsonformat(self, myprotosql: MyProtoSql):
        message = maps_pb2.Maps()
        message.messages.get_or_create('a string').a_value = 'one'
        assert (myprotosql.decode_jsonformat(message.SerializeToString(), 'Maps') ==
                {'messages': {'a string': { 'aValue': 'one'}}})


    def test_enums_decode_raw_textformat(self, myprotosql: MyProtoSql):
        message = maps_pb2.Maps()
        message.enums['one'] = maps_pb2.EnumValue.VAL1
        assert (myprotosql.decode_raw_textformat(message.SerializeToString()) ==
                '3: {\n'
                ' 1: "one"\n'
                ' 2: 1\n'
                '}\n'
                )

    def test_enums_decode_raw_jsonformat(self, myprotosql: MyProtoSql):
        message = maps_pb2.Maps()
        message.enums['one'] = maps_pb2.EnumValue.VAL1
        assert (myprotosql.decode_raw_jsonformat(message.SerializeToString()) ==
                {'3': {'1': 'one', '2': 1 }})

    def test_enums_decode_textformat(self, myprotosql: MyProtoSql):
        message = maps_pb2.Maps()
        message.enums['one'] = maps_pb2.EnumValue.VAL1
        assert (myprotosql.decode_textformat(message.SerializeToString(), 'Maps') ==
                'enums: {\n'
                ' key: "one"\n'
                ' value: VAL1\n'
                '}\n'
                )

    def test_enums_decode_jsonformat(self, myprotosql: MyProtoSql):
        message = maps_pb2.Maps()
        message.enums['one'] = maps_pb2.EnumValue.VAL1
        assert (myprotosql.decode_jsonformat(message.SerializeToString(), 'Maps') ==
                {'enums': {'one': 'VAL1'}})

    def test_snake_cased_name_decode_jsonformat(self, myprotosql: MyProtoSql):
        message = maps_pb2.Maps()
        message.a_snake_cased_name['one'] = maps_pb2.EnumValue.VAL1
        assert (myprotosql.decode_jsonformat(message.SerializeToString(), 'Maps') ==
                {'aSnakeCasedName': {'one': 'VAL1'}})

    def test_snake_cased_name_with_json_name_decode_jsonformat(self, myprotosql: MyProtoSql):
        message = maps_pb2.Maps()
        message.a_snake_cased_name_with_json_name['one'] = maps_pb2.EnumValue.VAL1
        assert (myprotosql.decode_jsonformat(message.SerializeToString(), 'Maps') ==
                {'anotherName': {'one': 'VAL1'}})
