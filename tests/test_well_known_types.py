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

import well_known_types_pb2
import string_message_pb2

from conftest import MyProtoSql
from google.protobuf.struct_pb2 import NullValue


class TestWellKnownTypes:

    def test_simple_decode_raw_textformat(self, myprotosql: MyProtoSql):
        message = well_known_types_pb2.WellKnownTypes()
        message.a_timestamp.seconds = 1724267449
        message.a_timestamp.nanos = 1000000
        message.a_duration.seconds = 10
        message.a_duration.nanos = 1000000
        message.a_empty.Clear()
        message.a_nullvalue = NullValue.NULL_VALUE
        message.a_struct.fields.get_or_create('a string').string_value = 'lala'
        message.a_value.string_value = 'string'
        message.a_fieldmask.paths.append('a.b.c')
        message.a_fieldmask.paths.append('d.e')
        message.a_listvalue.values.add().string_value = 'this is a string haha'
        message.a_listvalue.values.add().string_value = 'and another one'
        message.a_boolvalue.value = True
        message.a_bytesvalue.value = bytes.fromhex('000000000000C03F00002040')
        message.a_doublevalue.value = 1.2
        message.a_floatvalue.value = 1.2
        message.a_int32value.value = 1
        message.a_int64value.value = 2
        message.a_stringvalue.value = 'hiphip'
        message.a_uint32value.value = 5
        message.a_uint64value.value = 6
        assert (myprotosql.decode_raw_textformat(message.SerializeToString()) ==
                ('1: {\n'
                 ' 1: 1724267449\n'
                 ' 2: 1000000\n'
                 '}\n'
                 '2: {\n'
                 ' 1: 10\n'
                 ' 2: 1000000\n'
                 '}\n'
                 '4: {\n'
                 '}\n'
                 '5: 0\n'
                 '6: {\n'
                 ' 1: {\n'
                 '  1: "a string"\n'
                 '  2: {\n'
                 '   3: "lala"\n'
                 '  }\n'
                 ' }\n'
                 '}\n'
                 '7: {\n'
                 ' 3: "string"\n'
                 '}\n'
                 '8: {\n'
                 ' 1: "a.b.c"\n'
                 ' 1: "d.e"\n'
                 '}\n'
                 '9: {\n'
                 ' 1: {\n'
                 '  3: "this is a string haha"\n'
                 ' }\n'
                 ' 1: {\n'
                 '  3: "and another one"\n'
                 ' }\n'
                 '}\n'
                 '10: {\n'
                 ' 1: 1\n'
                 '}\n'
                 '11: {\n'
                 ' 1: "\\x00\\x00\\x00\\x00\\x00\\x00\\xC0?\\x00\\x00 @"\n'
                 '}\n'
                 '12: {\n'
                 ' 1: 4608083138725491507\n'
                 '}\n'
                 '13: {\n'
                 ' 1: 1067030938\n'
                 '}\n'
                 '14: {\n'
                 ' 1: 1\n'
                 '}\n'
                 '15: {\n'
                 ' 1: 2\n'
                 '}\n'
                 '16: {\n'
                 ' 1: "hiphip"\n'
                 '}\n'
                 '17: {\n'
                 ' 1: 5\n'
                 '}\n'
                 '18: {\n'
                 ' 1: 6\n'
                 '}\n')
                )

    def test_simple_decode_raw_jsonformat(self, myprotosql: MyProtoSql):
        message = well_known_types_pb2.WellKnownTypes()
        message.a_timestamp.seconds = 1724267449
        message.a_timestamp.nanos = 1000000
        message.a_duration.seconds = 10
        message.a_duration.nanos = 1000000
        message.a_empty.Clear()
        message.a_nullvalue = NullValue.NULL_VALUE
        message.a_struct.fields.get_or_create('a string').string_value = 'lala'
        message.a_value.string_value = 'string'
        message.a_fieldmask.paths.append('a.b.c')
        message.a_fieldmask.paths.append('d.e')
        message.a_listvalue.values.add().string_value = 'this is a string haha'
        message.a_boolvalue.value = True
        message.a_bytesvalue.value = bytes.fromhex('000000000000C03F00002040')
        message.a_doublevalue.value = 1.2
        message.a_floatvalue.value = 1.2
        message.a_int32value.value = 1
        message.a_int64value.value = 2
        message.a_stringvalue.value = 'hiphip'
        message.a_uint32value.value = 5
        message.a_uint64value.value = 6
        assert (myprotosql.decode_raw_jsonformat(message.SerializeToString()) ==
                {'1': {'1': 1724267449, '2': 1000000},
                 '2': {'1': 10, '2': 1000000},
                 '4': {},
                 '5': 0,
                 '6': {'1': {'1': 'a string', '2': {'3': 'lala'}}},
                 '7': {'3': 'string'},
                 '8': {'1': ['a.b.c', 'd.e']},
                 '9': {'1': {'3': 'this is a string haha'}},
                 '10': {'1': 1},
                 '11': {'1': 'AAAAAAAAwD8AACBA'},
                 '12': {'1': 4608083138725491507},
                 '13': {'1': 1067030938},
                 '14': {'1': 1},
                 '15': {'1': 2},
                 '16': {'1': 'hiphip'},
                 '17': {'1': 5},
                 '18': {'1': 6}}
                )

    def test_decode_textformat(self, myprotosql: MyProtoSql):
        message = well_known_types_pb2.WellKnownTypes()
        message.a_timestamp.seconds = 1724267449
        message.a_timestamp.nanos = 1000000
        message.a_duration.seconds = 10
        message.a_duration.nanos = 1000000
        message.a_empty.Clear()
        message.a_nullvalue = NullValue.NULL_VALUE
        message.a_value.string_value = 'string'
        message.a_fieldmask.paths.append('a.b.c')
        message.a_fieldmask.paths.append('d.e')
        message.a_boolvalue.value = True
        message.a_bytesvalue.value = bytes.fromhex('000000000000C03F00002040')
        message.a_doublevalue.value = 1.2
        message.a_floatvalue.value = 1.25
        message.a_int32value.value = 1
        message.a_int64value.value = 2
        message.a_stringvalue.value = 'hiphip'
        message.a_uint32value.value = 5
        message.a_uint64value.value = 6
        assert (myprotosql.decode_textformat(message.SerializeToString(), 'WellKnownTypes') ==
                ('a_timestamp: {\n'
                 ' seconds: 1724267449\n'
                 ' nanos: 1000000\n'
                 '}\n'
                 'a_duration: {\n'
                 ' seconds: 10\n'
                 ' nanos: 1000000\n'
                 '}\n'
                 'a_empty: {\n'
                 '}\n'
                 'a_nullvalue: NULL_VALUE\n'
                 'a_value: {\n'
                 ' string_value: "string"\n'
                 '}\n'
                 'a_fieldmask: {\n'
                 ' paths: "a.b.c"\n'
                 ' paths: "d.e"\n'
                 '}\n'
                 'a_boolvalue: {\n'
                 ' value: true\n'
                 '}\n'
                 'a_bytesvalue: {\n'
                 ' value: "\\x00\\x00\\x00\\x00\\x00\\x00\\xC0?\\x00\\x00 @"\n'
                 '}\n'
                 'a_doublevalue: {\n'
                 ' value: 1.2f\n'
                 '}\n'
                 'a_floatvalue: {\n'
                 ' value: 1.25f\n'
                 '}\n'
                 'a_int32value: {\n'
                 ' value: 1\n'
                 '}\n'
                 'a_int64value: {\n'
                 ' value: 2\n'
                 '}\n'
                 'a_stringvalue: {\n'
                 ' value: "hiphip"\n'
                 '}\n'
                 'a_uint32value: {\n'
                 ' value: 5\n'
                 '}\n'
                 'a_uint64value: {\n'
                 ' value: 6\n'
                 '}\n')
                )

    def test_decode_struct_textformat(self, myprotosql: MyProtoSql):
        message = well_known_types_pb2.WellKnownTypes()
        message.a_struct.fields.get_or_create('a field').string_value = 'one'
        message.a_struct.fields.get_or_create('another field').string_value = 'two'
        assert (myprotosql.decode_textformat(message.SerializeToString(), 'WellKnownTypes') ==
                ('a_struct: {\n'
                 ' fields: {\n'
                 '  key: "a field"\n'
                 '  value: {\n'
                 '   string_value: "one"\n'
                 '  }\n'
                 ' }\n'
                 ' fields: {\n'
                 '  key: "another field"\n'
                 '  value: {\n'
                 '   string_value: "two"\n'
                 '  }\n'
                 ' }\n'
                 '}\n')
                )

    def test_decode_listvalue_textformat(self, myprotosql: MyProtoSql):
        message = well_known_types_pb2.WellKnownTypes()
        message.a_listvalue.values.add().string_value = 'one'
        message.a_listvalue.values.add().number_value = 2.25
        message.a_listvalue.values.add().bool_value = True
        assert (myprotosql.decode_textformat(message.SerializeToString(), 'WellKnownTypes') ==
                ('a_listvalue: {\n'
                 ' values: {\n'
                 '  string_value: "one"\n'
                 ' }\n'
                 ' values: {\n'
                 '  number_value: 2.25f\n'
                 ' }\n'
                 ' values: {\n'
                 '  bool_value: true\n'
                 ' }\n'
                 '}\n')
                )

    def test_decode_any_textformat(self, myprotosql: MyProtoSql):
        string_message = string_message_pb2.StringMessage()
        string_message.b = 'this is a String in a StringMessage'
        message = well_known_types_pb2.WellKnownTypes()
        message.a_any.type_url = 'StringMessage'
        message.a_any.value = string_message.SerializeToString()
        assert (myprotosql.decode_textformat(message.SerializeToString(), 'WellKnownTypes') ==
                ('a_any: {\n'
                 ' type_url: "StringMessage"\n'
                 ' value: "\\x12#this is a String in a StringMessage"\n'
                 '}\n')
                )

    def test_decode_any_jsonformat(self, myprotosql: MyProtoSql):
        string_message = string_message_pb2.StringMessage()
        string_message.b = 'this is a String in a StringMessage'
        message = well_known_types_pb2.WellKnownTypes()
        message.a_any.type_url = 'StringMessage'
        message.a_any.value = string_message.SerializeToString()
        assert (myprotosql.decode_jsonformat(message.SerializeToString(), 'WellKnownTypes') ==
                {'aAny': {'@type': 'StringMessage',
                          'value': 'EiN0aGlzIGlzIGEgU3RyaW5nIGluIGEgU3RyaW5nTWVzc2FnZQ=='}}
                )

    def test_decode_jsonformat(self, myprotosql: MyProtoSql):
        message = well_known_types_pb2.WellKnownTypes()
        message.a_timestamp.seconds = 1724267449
        message.a_timestamp.nanos = 1000000
        message.a_duration.seconds = 10
        message.a_duration.nanos = 1000000
        message.a_empty.Clear()
        message.a_nullvalue = NullValue.NULL_VALUE
        message.a_struct.fields.get_or_create('a string').string_value = 'lala'
        message.a_value.string_value = 'string'
        message.a_fieldmask.paths.append('a.b.c')
        message.a_fieldmask.paths.append('d.e')
        message.a_listvalue.values.add().string_value = 'haha'
        message.a_boolvalue.value = True
        message.a_bytesvalue.value = bytes.fromhex('000000000000C03F00002040')
        message.a_doublevalue.value = 1.2
        message.a_floatvalue.value = 1.25
        message.a_int32value.value = 1
        message.a_int64value.value = 2
        message.a_stringvalue.value = 'hiphip'
        message.a_uint32value.value = 5
        message.a_uint64value.value = 6
        assert (myprotosql.decode_jsonformat(message.SerializeToString(), 'WellKnownTypes') ==
                {
                    "aTimestamp": "2024-08-21T19:10:49.001Z",
                    "aDuration": "10.001s",
                    "aEmpty": {},
                    "aNullvalue": None,
                    "aStruct": {
                        "a string": "lala"
                    },
                    "aValue": "string",
                    "aFieldmask": "a.b.c,d.e",
                    "aListvalue": [
                        "haha"
                    ],
                    "aBoolvalue": True,
                    "aBytesvalue": "AAAAAAAAwD8AACBA",
                    "aDoublevalue": 1.2,
                    "aFloatvalue": 1.25,
                    "aInt32value": 1,
                    "aInt64value": 2,
                    "aStringvalue": "hiphip",
                    "aUint32value": 5,
                    "aUint64value": 6
                }
                )

    def test_decode_struct_jsonformat(self, myprotosql: MyProtoSql):
        message = well_known_types_pb2.WellKnownTypes()
        message.a_struct.fields.get_or_create('a field').string_value = 'one'
        message.a_struct.fields.get_or_create('another field').string_value = 'two'
        assert (myprotosql.decode_jsonformat(message.SerializeToString(), 'WellKnownTypes') ==
                {'aStruct': {'a field': 'one', 'another field': 'two'}})

    def test_decode_listvalue_jsonformat(self, myprotosql: MyProtoSql):
        message = well_known_types_pb2.WellKnownTypes()
        message.a_listvalue.values.add().string_value = 'one'
        message.a_listvalue.values.add().number_value = 2.25
        message.a_listvalue.values.add().bool_value = True
        assert (myprotosql.decode_jsonformat(message.SerializeToString(), 'WellKnownTypes') ==
                {'aListvalue': ['one', 2.25, True]} )

    def test_decode_fieldmask_to_camelcase_jsonformat(self, myprotosql: MyProtoSql):
        message = well_known_types_pb2.WellKnownTypes()
        message.a_fieldmask.paths.append('a_cool_path.with_snake.case')
        message.a_fieldmask.paths.append('d.e')
        message.a_fieldmask.paths.append('another.path.a_nice_field_name')
        assert (myprotosql.decode_jsonformat(message.SerializeToString(), 'WellKnownTypes') ==
                {"aFieldmask": "aCoolPath.withSnake.case,d.e,another.path.aNiceFieldName"})