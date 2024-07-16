
import json
import build.simple_message_pb2 as simple_message_pb2
import build.string_message_pb2 as string_message_pb2
import build.repeated_fields_pb2 as repeated_fields_pb2
import build.submessage_pb2 as submessage_pb2
import build.group_pb2 as group_pb2
from mysql.connector import MySQLConnection


class TestDecodeRawMessages:

    def decode_raw(self, connection, p_bytes):
        with connection.cursor() as cursor:
            cursor.execute("select _myproto_flatten_message(%s, NULL, NULL)", (p_bytes,))
            return json.loads(cursor.fetchone()[0])

    def decode(self, connection, p_bytes, p_message_type):
        with connection.cursor() as cursor:
            cursor.execute("select _myproto_flatten_message(%s, %s, myproto_descriptors())", (p_bytes, p_message_type))
            return json.loads(cursor.fetchone()[0])

    def test_simple_message(self, db:  MySQLConnection):
        message = simple_message_pb2.SimpleMessage()
        message.a = 123456
        assert (self.decode_raw(db, message.SerializeToString()) ==
                [
                    {
                        "path": "$",
                        "type": "field",
                        "depth": 0,
                        "value": 123456,
                        "field_name": None,
                        "field_type": None,
                        "field_number": 1
                    }
                ])

    def test_string_message(self, db:  MySQLConnection):
        message = string_message_pb2.StringMessage()
        message.b = 'Hello World!'
        assert (self.decode_raw(db, message.SerializeToString()) ==
                [
                    {
                        "path": "$",
                        "type": "field",
                        "depth": 0,
                        "value": "Hello World!",
                        "field_name": None,
                        "field_type": None,
                        "field_number": 2
                    }
                ])

    def test_string_message_recover_from_malformed_submessage(self, db:  MySQLConnection):
        message = string_message_pb2.StringMessage()
        message.b = 'Repeated!'
        assert (self.decode_raw(db, message.SerializeToString()) ==
                [
                    {
                        "path": "$",
                        "type": "field",
                        "depth": 0,
                        "value": "Repeated!",
                        "field_name": None,
                        "field_type": None,
                        "field_number": 2
                    }
                ])

    def test_repeated_fields_message(self, db:  MySQLConnection):
        message = repeated_fields_pb2.RepeatedFields()
        message.d = '123'
        message.e.append(1)
        message.e.append(2)
        message.e.append(3)

        assert (self.decode_raw(db, message.SerializeToString()) ==
                [{'depth': 0,
                  'field_name': None,
                  'field_number': 4,
                  'field_type': None,
                  'path': '$',
                  'type': 'field',
                  'value': '123'},
                {'depth': 0,
                  'field_name': None,
                  'field_number': 5,
                  'field_type': None,
                  'path': '$',
                  'type': 'field',
                  'value': 1},
                 {'depth': 0,
                  'field_name': None,
                  'field_number': 5,
                  'field_type': None,
                  'path': '$',
                  'type': 'field',
                  'value': 2},
                 {'depth': 0,
                  'field_name': None,
                  'field_number': 5,
                  'field_type': None,
                  'path': '$',
                  'type': 'field',
                  'value': 3}])

    def test_repeated_fields_string_message_malformed_submessage(self, db:  MySQLConnection):
        message = repeated_fields_pb2.RepeatedFields()
        message.d = 'Repeated!'
        message.e.append(1)

        assert (self.decode_raw(db, message.SerializeToString()) ==
                [{'depth': 0,
                  'field_name': None,
                  'field_number': 4,
                  'field_type': None,
                  'path': '$',
                  'type': 'field',
                  'value': 'Repeated!'},
                {'depth': 0,
                  'field_name': None,
                  'field_number': 5,
                  'field_type': None,
                  'path': '$',
                  'type': 'field',
                  'value': 1}])

    def test_submessage(self, db:  MySQLConnection):
        message = submessage_pb2.ParentMessage()
        message.c.a = 123456

        assert (self.decode_raw(db, message.SerializeToString()) ==
                [
                    {'depth': 0,
                     'field_name': None,
                     'field_number': 3,
                     'message_type': None,
                     'path': '$',
                     'type': 'message'},
                    {'depth': 1,
                     'field_name': None,
                     'field_number': 1,
                     'field_type': None,
                     'path': '$.3',
                     'type': 'field',
                     'value': 123456}
                ])

    def test_group(self, db:  MySQLConnection):
        message = group_pb2.GroupMessage()
        message.mygroup.a = 'a group'
        message.mygroup.b = 123456

        assert (self.decode_raw(db, message.SerializeToString()) ==
                [
                    {'depth': 0,
                     'field_name': None,
                     'field_number': 1,
                     'message_type': None,
                     'path': '$',
                     'type': 'message'},
                    {'depth': 1,
                     'field_name': None,
                     'field_number': 1,
                     'field_type': None,
                     'path': '$.1',
                     'type': 'field',
                     'value': 'a group'},
                    {'depth': 1,
                     'field_name': None,
                     'field_number': 2,
                     'field_type': None,
                     'path': '$.1',
                     'type': 'field',
                     'value': 123456}
                ])

    def test_simple_message_decode(self, db:  MySQLConnection):
        message = simple_message_pb2.SimpleMessage()
        message.a = 123456
        assert (self.decode(db, message.SerializeToString(), '.SimpleMessage') ==
                [
                    {
                        "path": "$",
                        "type": "field",
                        "depth": 0,
                        "value": 123456,
                        "field_name": 'a',
                        "field_type": 'TYPE_INT32',
                        "field_number": 1
                    }
                ])