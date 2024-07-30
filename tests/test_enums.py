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

import enums_pb2

from conftest import MyProtoSql


class TestEnums:

    def test_decode_raw_textformat(self, myprotosql: MyProtoSql):
        message = enums_pb2.Enums()
        message.a_single_enum = enums_pb2.AnEnum.ANOTHER_VALUE
        assert (myprotosql.decode_raw_textformat(message.SerializeToString()) == '1: 1\n')

    def test_decode_raw_jsonformat(self, myprotosql: MyProtoSql):
        message = enums_pb2.Enums()
        message.a_single_enum = enums_pb2.AnEnum.ANOTHER_VALUE
        assert (myprotosql.decode_raw_jsonformat(message.SerializeToString()) == { '1': 1 })

    def test_decode_raw_textformat_repeated(self, myprotosql: MyProtoSql):
        message = enums_pb2.Enums()
        message.a_list.append(enums_pb2.AnEnum.ANOTHER_VALUE)
        message.a_list.append(enums_pb2.AnEnum.A_VALUE)
        assert (myprotosql.decode_raw_textformat(message.SerializeToString()) ==
                '2: 1\n'
                '2: 0\n')

    def test_decode_raw_jsonformat_repeated(self, myprotosql: MyProtoSql):
        message = enums_pb2.Enums()
        message.a_list.append(enums_pb2.AnEnum.ANOTHER_VALUE)
        message.a_list.append(enums_pb2.AnEnum.A_VALUE)
        assert (myprotosql.decode_raw_jsonformat(message.SerializeToString()) == { '2': [1, 0] })

    def test_decode(self, myprotosql: MyProtoSql):
        message = enums_pb2.Enums()
        message.a_single_enum = enums_pb2.AnEnum.ANOTHER_VALUE
        assert (myprotosql.decode(message.SerializeToString(), 'Enums') ==
                [{'depth': 0,
                  'field_json_name': 'aSingleEnum',
                  'field_name': 'a_single_enum',
                  'field_number': 1,
                  'field_type': 'TYPE_ENUM',
                  'path': '$',
                  'repeated': False,
                  'type': 'field',
                  'value': 'ANOTHER_VALUE'}])

    def test_decode_textformat(self, myprotosql: MyProtoSql):
        message = enums_pb2.Enums()
        message.a_single_enum = enums_pb2.AnEnum.ANOTHER_VALUE
        assert (myprotosql.decode_textformat(message.SerializeToString(), 'Enums') == 'a_single_enum: ANOTHER_VALUE\n')

    def test_decode_jsonformat(self, myprotosql: MyProtoSql):
        message = enums_pb2.Enums()
        message.a_single_enum = enums_pb2.AnEnum.ANOTHER_VALUE
        assert (myprotosql.decode_jsonformat(message.SerializeToString(), 'Enums') ==  {'aSingleEnum': 'ANOTHER_VALUE'})

    def test_decode_textformat_repeated(self, myprotosql: MyProtoSql):
        message = enums_pb2.Enums()
        message.a_list.append(enums_pb2.AnEnum.ANOTHER_VALUE)
        message.a_list.append(enums_pb2.AnEnum.A_VALUE)
        assert (myprotosql.decode_textformat(message.SerializeToString(), 'Enums') ==
                'a_list: ANOTHER_VALUE\n'
                'a_list: A_VALUE\n')

    def test_decode_jsonformat_repeated(self, myprotosql: MyProtoSql):
        message = enums_pb2.Enums()
        message.a_list.append(enums_pb2.AnEnum.ANOTHER_VALUE)
        message.a_list.append(enums_pb2.AnEnum.A_VALUE)
        assert (myprotosql.decode_jsonformat(message.SerializeToString(), 'Enums') ==  {'aList': ['ANOTHER_VALUE', 'A_VALUE']})

    def test_decode_textformat_packed_repeated(self, myprotosql: MyProtoSql):
        message = enums_pb2.Enums()
        message.a_packed_list.append(enums_pb2.AnEnum.ANOTHER_VALUE)
        message.a_packed_list.append(enums_pb2.AnEnum.A_VALUE)
        assert (myprotosql.decode_textformat(message.SerializeToString(), 'Enums') ==
                'a_packed_list: [ANOTHER_VALUE, A_VALUE]\n')

    def test_decode_jsonformat_packed_repeated(self, myprotosql: MyProtoSql):
        message = enums_pb2.Enums()
        message.a_packed_list.append(enums_pb2.AnEnum.ANOTHER_VALUE)
        message.a_packed_list.append(enums_pb2.AnEnum.A_VALUE)
        assert (myprotosql.decode_jsonformat(message.SerializeToString(), 'Enums') ==  {'aPackedList': ['ANOTHER_VALUE', 'A_VALUE']})

