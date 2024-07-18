import json
import simple_message_pb2
import string_message_pb2
import repeated_fields_pb2
import submessage_pb2
import group_pb2
import oneof_pb2
from mysql.connector import MySQLConnection


class TestDecodeRawJsonFormat:

    def jsonformat(self, connection, p_bytes):
        with connection.cursor() as cursor:
            cursor.execute("select myproto_decode_to_jsonformat(%s, NULL, NULL)", (p_bytes, ))
            return json.loads(cursor.fetchone()[0])

    def test_simple_message(self, db:  MySQLConnection):
        message = simple_message_pb2.SimpleMessage()
        message.a = 123456
        assert self.jsonformat(db, message.SerializeToString()) == {"1": 123456}

    def test_string_message(self, db:  MySQLConnection):
        message = string_message_pb2.StringMessage()
        message.b = 'Hello World!'
        assert self.jsonformat(db, message.SerializeToString()) == {"2": "Hello World!"}

    def test_repeated_fields_message(self, db:  MySQLConnection):
        message = repeated_fields_pb2.RepeatedFields()
        message.d = '123'
        message.e.append(1)
        message.e.append(2)
        message.e.append(3)

        assert self.jsonformat(db, message.SerializeToString()) == {"4": "123", "5": [1, 2, 3]}


    def test_submessage(self, db:  MySQLConnection):
        message = submessage_pb2.ParentMessage()
        message.c.a = 123456

        assert self.jsonformat(db, message.SerializeToString()) == {"3": {"1": 123456}}

    def test_group(self, db:  MySQLConnection):
        message = group_pb2.GroupMessage()
        message.mygroup.a = 'a group'
        message.mygroup.b = 123456

        assert self.jsonformat(db, message.SerializeToString()) == {"1": {"1": "a group", "2": 123456}}

    def test_oneof_submessage(self, db: MySQLConnection):
        message = oneof_pb2.OneOfMessage()
        message.sub_message.a = 123456

        assert self.jsonformat(db, message.SerializeToString()) == {"9": {"1": 123456}}

    def test_oneof_string(self, db: MySQLConnection):
        message = oneof_pb2.OneOfMessage()
        message.name = 'a string'

        assert self.jsonformat(db, message.SerializeToString()) == {"4": "a string"}
