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

import packed_pb2
import repeatedv3_pb2

from conftest import MyProtoSql


class TestPackedRepeatedFields:

    def test_decode(self, myprotosql: MyProtoSql):
        message = packed_pb2.PackedFields()
        message.f.append(1)
        message.f.append(2)
        message.f.append(3)

        assert (myprotosql.decode(message.SerializeToString(), 'PackedFields') ==
                [{'depth': 0,
                  'field_name': 'f',
                  'field_json_name': 'f',
                  'repeated': True,
                  'field_number': 6,
                  'field_type': 'TYPE_INT32',
                  'path': '$',
                  'type': 'field',
                  'value': [1, 2, 3]}])

    def test_decode_raw_cannot_recognize_packing(self, myprotosql: MyProtoSql):
        message = packed_pb2.PackedFields()
        message.f.append(1)
        message.f.append(2)
        message.f.append(3)

        assert (myprotosql.decode_raw(message.SerializeToString()) ==
                [{'depth': 0,
                  'field_name': None,
                  'field_json_name': None,
                  'repeated': False,
                  'field_number': 6,
                  'field_type': 'TYPE_STRING',
                  'path': '$',
                  'type': 'field',
                  'value': '\x01\x02\x03'},
                 ])

    def test_decode_raw_jsonformat_cannot_recognize_packing(self, myprotosql: MyProtoSql):
        message = packed_pb2.PackedFields()
        message.f.append(1)
        message.f.append(2)
        message.f.append(3)

        assert myprotosql.decode_raw_jsonformat(message.SerializeToString()) == {"6": "\x01\x02\x03"}

    def test_decode_raw_jsonformat_cannot_recognize_packing_v3_repeated_are_packed_by_default(self, myprotosql: MyProtoSql):
        message = repeatedv3_pb2.RepeatedV3()
        message.f.append(1)
        message.f.append(2)
        message.f.append(3)

        assert myprotosql.decode_raw_jsonformat(message.SerializeToString()) == {"6": "\x01\x02\x03"}

    def test_decode_raw_textformat_cannot_recognize_packing(self, myprotosql: MyProtoSql):
        message = packed_pb2.PackedFields()
        message.f.append(1)
        message.f.append(2)
        message.f.append(3)

        assert myprotosql.decode_raw_textformat(message.SerializeToString()) == '6: "\x01\x02\x03"\n'

    def test_decode_raw_textformat_cannot_recognize_packing_v3_repeated_are_packed_by_default(self, myprotosql: MyProtoSql):
        message = repeatedv3_pb2.RepeatedV3()
        message.f.append(1)
        message.f.append(2)
        message.f.append(3)

        assert myprotosql.decode_raw_textformat(message.SerializeToString()) == '6: "\x01\x02\x03"\n'

    def test_decode_jsonformat(self, myprotosql: MyProtoSql):
        message = packed_pb2.PackedFields()
        message.f.append(1)
        message.f.append(2)
        message.f.append(3)

        assert (myprotosql.decode_jsonformat(message.SerializeToString(), 'PackedFields') == {"f": [1, 2, 3]})

    def test_v3_decode_jsonformat(self, myprotosql: MyProtoSql):
        message = repeatedv3_pb2.RepeatedV3()
        message.f.append(1)
        message.f.append(2)
        message.f.append(3)

        assert (myprotosql.decode_jsonformat(message.SerializeToString(), 'RepeatedV3') == {"f": [1, 2, 3]})

    def test_decode_textformat(self, myprotosql: MyProtoSql):
        message = packed_pb2.PackedFields()
        message.f.append(1)
        message.f.append(2)
        message.f.append(3)

        assert myprotosql.decode_textformat(message.SerializeToString(), 'PackedFields') == 'f: [1, 2, 3]\n'

    def test_decode_textformat_has_f_for_floats(self, myprotosql: MyProtoSql):
        message = packed_pb2.PackedFields()
        message.more_floats.append(0.0)
        message.more_floats.append(1.5)
        message.more_floats.append(2.5)

        assert myprotosql.decode_textformat(message.SerializeToString(), 'PackedFields') == 'more_floats: [0.0f, 1.5f, 2.5f]\n'

    def test_v3_decode_textformat(self, myprotosql: MyProtoSql):
        message = repeatedv3_pb2.RepeatedV3()
        message.f.append(1)
        message.f.append(2)
        message.f.append(3)

        assert myprotosql.decode_textformat(message.SerializeToString(), 'RepeatedV3') == 'f: [1, 2, 3]\n'

