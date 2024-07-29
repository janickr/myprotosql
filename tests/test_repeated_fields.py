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

import repeated_fields_pb2

from conftest import MyProtoSql


class TestRepeatedFields:

    def test_decode_message(self, myprotosql: MyProtoSql):
        message = repeated_fields_pb2.RepeatedFields()
        message.d = '123'
        message.e.append(1)
        message.e.append(2)
        message.e.append(3)

        assert (myprotosql.decode(message.SerializeToString(), 'RepeatedFields') ==
                [{'depth': 0,
                  'field_name': "d",
                  'field_json_name': "d",
                  'repeated': False,
                  'field_number': 4,
                  'field_type': "TYPE_STRING",
                  'path': '$',
                  'type': 'field',
                  'value': '123'},
                 {'depth': 0,
                  'field_name': "e",
                  'field_json_name': "e",
                  'repeated': True,
                  'field_number': 5,
                  'field_type': "TYPE_INT32",
                  'path': '$',
                  'type': 'field',
                  'value': 1},
                 {'depth': 0,
                  'field_name': "e",
                  'field_json_name': "e",
                  'repeated': True,
                  'field_number': 5,
                  'field_type': "TYPE_INT32",
                  'path': '$',
                  'type': 'field',
                  'value': 2},
                 {'depth': 0,
                  'field_name': "e",
                  'field_json_name': "e",
                  'repeated': True,
                  'field_number': 5,
                  'field_type': "TYPE_INT32",
                  'path': '$',
                  'type': 'field',
                  'value': 3}])

    def test_decode_string_message_malformed_submessage(self, myprotosql: MyProtoSql):
        message = repeated_fields_pb2.RepeatedFields()
        message.d = 'Repeated!'
        message.e.append(1)

        assert (myprotosql.decode(message.SerializeToString(), 'RepeatedFields') ==
                [{'depth': 0,
                  'field_name': "d",
                  'field_json_name': "d",
                  'repeated': False,
                  'field_number': 4,
                  'field_type': "TYPE_STRING",
                  'path': '$',
                  'type': 'field',
                  'value': 'Repeated!'},
                 {'depth': 0,
                  'field_name': "e",
                  'field_json_name': "e",
                  'repeated': True,
                  'field_number': 5,
                  'field_type': "TYPE_INT32",
                  'path': '$',
                  'type': 'field',
                  'value': 1}])

    def test_decode_submessage(self, myprotosql: MyProtoSql):
        message = repeated_fields_pb2.RepeatedFields()
        g1 = message.g.add()
        g1.a = 1
        g2 = message.g.add()
        g2.a = 2

        assert (myprotosql.decode(message.SerializeToString(), 'RepeatedFields') ==
                [{'depth': 0,
                  'field_json_name': 'g',
                  'field_name': 'g',
                  'field_number': 7,
                  'message_type': '.RepeatedFieldsSubMessage',
                  'path': '$',
                  'repeated': True,
                  'type': 'message'},
                 {'depth': 1,
                  'field_json_name': 'a',
                  'field_name': 'a',
                  'field_number': 1,
                  'field_type': 'TYPE_INT32',
                  'path': '$.7',
                  'repeated': False,
                  'type': 'field',
                  'value': 1},
                 {'depth': 0,
                  'field_json_name': 'g',
                  'field_name': 'g',
                  'field_number': 7,
                  'message_type': '.RepeatedFieldsSubMessage',
                  'path': '$',
                  'repeated': True,
                  'type': 'message'},
                 {'depth': 1,
                  'field_json_name': 'a',
                  'field_name': 'a',
                  'field_number': 1,
                  'field_type': 'TYPE_INT32',
                  'path': '$.7',
                  'repeated': False,
                  'type': 'field',
                  'value': 2}])

    def test_decode_raw(self, myprotosql: MyProtoSql):
        message = repeated_fields_pb2.RepeatedFields()
        message.d = '123'
        message.e.append(1)
        message.e.append(2)
        message.e.append(3)

        assert (myprotosql.decode_raw(message.SerializeToString()) ==
                [{'depth': 0,
                  'field_name': None,
                  'field_json_name': None,
                  'repeated': False,
                  'field_number': 4,
                  'field_type': 'TYPE_STRING',
                  'path': '$',
                  'type': 'field',
                  'value': '123'},
                 {'depth': 0,
                  'field_name': None,
                  'field_json_name': None,
                  'repeated': False,
                  'field_number': 5,
                  'field_type': None,
                  'path': '$',
                  'type': 'field',
                  'value': 1},
                 {'depth': 0,
                  'field_name': None,
                  'field_json_name': None,
                  'repeated': False,
                  'field_number': 5,
                  'field_type': None,
                  'path': '$',
                  'type': 'field',
                  'value': 2},
                 {'depth': 0,
                  'field_name': None,
                  'field_json_name': None,
                  'repeated': False,
                  'field_number': 5,
                  'field_type': None,
                  'path': '$',
                  'type': 'field',
                  'value': 3}])

    def test_decode_raw_string_message_malformed_submessage(self, myprotosql: MyProtoSql):
        message = repeated_fields_pb2.RepeatedFields()
        message.d = 'Repeated!'
        message.e.append(1)

        assert (myprotosql.decode_raw(message.SerializeToString()) ==
                [{'depth': 0,
                  'field_name': None,
                  'field_json_name': None,
                  'repeated': False,
                  'field_number': 4,
                  'field_type': 'TYPE_STRING',
                  'path': '$',
                  'type': 'field',
                  'value': 'Repeated!'},
                 {'depth': 0,
                  'field_name': None,
                  'field_json_name': None,
                  'repeated': False,
                  'field_number': 5,
                  'field_type': None,
                  'path': '$',
                  'type': 'field',
                  'value': 1}])

    def test_decode_raw_submessage(self, myprotosql: MyProtoSql):
        message = repeated_fields_pb2.RepeatedFields()
        g1 = message.g.add()
        g1.a = 1
        g2 = message.g.add()
        g2.a = 2

        assert (myprotosql.decode_raw(message.SerializeToString()) ==
                [{'depth': 0,
                  'field_json_name': None,
                  'field_name': None,
                  'field_number': 7,
                  'message_type': None,
                  'path': '$',
                  'repeated': False,
                  'type': 'message'},
                 {'depth': 1,
                  'field_json_name': None,
                  'field_name': None,
                  'field_number': 1,
                  'field_type': None,
                  'path': '$.7',
                  'repeated': False,
                  'type': 'field',
                  'value': 1},
                 {'depth': 0,
                  'field_json_name': None,
                  'field_name': None,
                  'field_number': 7,
                  'message_type': None,
                  'path': '$',
                  'repeated': False,
                  'type': 'message'},
                 {'depth': 1,
                  'field_json_name': None,
                  'field_name': None,
                  'field_number': 1,
                  'field_type': None,
                  'path': '$.7',
                  'repeated': False,
                  'type': 'field',
                  'value': 2}])

    def test_decode_raw_jsonformat(self, myprotosql: MyProtoSql):
        message = repeated_fields_pb2.RepeatedFields()
        message.d = '123'
        message.e.append(1)
        message.e.append(2)
        message.e.append(3)

        assert myprotosql.decode_raw_jsonformat(message.SerializeToString()) == {"4": "123", "5": [1, 2, 3]}

    def test_repeated_fields_one_element(self, myprotosql: MyProtoSql):
        message = repeated_fields_pb2.RepeatedFields()
        message.d = '123'
        message.e.append(1)

        assert myprotosql.decode_raw_jsonformat(message.SerializeToString()) == {"4": "123", "5": 1}

    def test_decode_raw_jsonformat_submessage(self, myprotosql: MyProtoSql):
        message = repeated_fields_pb2.RepeatedFields()
        g1 = message.g.add()
        g1.a = 1
        g2 = message.g.add()
        g2.a = 2

        assert myprotosql.decode_raw_jsonformat(message.SerializeToString()) == {"7": [{"1":1}, {"1":2}]}

    def test_decode_raw_jsonformat_one_submessage(self, myprotosql: MyProtoSql):
        message = repeated_fields_pb2.RepeatedFields()
        g1 = message.g.add()
        g1.a = 1

        assert myprotosql.decode_raw_jsonformat(message.SerializeToString()) == {"7": {"1":1}}

    def test_decode_raw_textformat(self, myprotosql: MyProtoSql):
        message = repeated_fields_pb2.RepeatedFields()
        message.d = '123'
        message.e.append(1)
        message.e.append(2)
        message.e.append(3)

        assert myprotosql.decode_raw_textformat(message.SerializeToString()) == '4: "123"\n5: 1\n5: 2\n5: 3\n'

    def test_decode_jsonformat_message(self, myprotosql: MyProtoSql):
        message = repeated_fields_pb2.RepeatedFields()
        message.d = '123'
        message.e.append(1)
        message.e.append(2)
        message.e.append(3)

        assert myprotosql.decode_jsonformat(message.SerializeToString(), 'RepeatedFields') == {"d": "123", "e": [1, 2, 3]}

    def test_decode_jsonformat_one_element(self, myprotosql: MyProtoSql):
        message = repeated_fields_pb2.RepeatedFields()
        message.d = '123'
        message.e.append(1)

        assert myprotosql.decode_jsonformat(message.SerializeToString(), 'RepeatedFields') == {"d": "123", "e": [1]}

    def test_decode_jsonformat_submessage(self, myprotosql: MyProtoSql):
        message = repeated_fields_pb2.RepeatedFields()
        g1 = message.g.add()
        g1.a = 1
        g2 = message.g.add()
        g2.a = 2

        assert myprotosql.decode_jsonformat(message.SerializeToString(), 'RepeatedFields') == {"g": [{"a":1}, {"a":2}]}

    def test_decode_jsonformat_one_submessage(self, myprotosql: MyProtoSql):
        message = repeated_fields_pb2.RepeatedFields()
        g1 = message.g.add()
        g1.a = 1

        assert myprotosql.decode_jsonformat(message.SerializeToString(), 'RepeatedFields') == {"g": [{"a":1}]}

    def test_decode_textformat(self, myprotosql: MyProtoSql):
        message = repeated_fields_pb2.RepeatedFields()
        message.d = '123'
        message.e.append(1)
        message.e.append(2)
        message.e.append(3)

        assert myprotosql.decode_textformat(message.SerializeToString(), 'RepeatedFields') == 'd: "123"\ne: 1\ne: 2\ne: 3\n'


    def test_textformat_has_f_for_floats(self, myprotosql: MyProtoSql):
        message = repeated_fields_pb2.RepeatedFields()
        message.more_floats.append(0.0)
        message.more_floats.append(1.5)
        message.more_floats.append(1.25)

        assert (myprotosql.decode_textformat(message.SerializeToString(), 'RepeatedFields') ==
                'more_floats: 0.0f\n'
                'more_floats: 1.5f\n'
                'more_floats: 1.25f\n')

