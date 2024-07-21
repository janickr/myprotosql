import json
import simple_message_pb2
import string_message_pb2
import repeated_fields_pb2
import submessage_pb2
import group_pb2
import oneof_pb2
import packed_pb2
from mysql.connector import MySQLConnection


class TestDecodeJsonFormat:

    def jsonformat(self, connection, p_bytes, p_message_type):
        with connection.cursor() as cursor:
            cursor.execute("select myproto_decode_to_jsonformat(%s, %s, myproto_descriptors())", (p_bytes, p_message_type))
            return json.loads(cursor.fetchone()[0])

    def test_simple_message(self, db:  MySQLConnection):
        message = simple_message_pb2.SimpleMessage()
        message.a = 123456
        assert self.jsonformat(db, message.SerializeToString(), '.SimpleMessage') == {"a": 123456}

    def test_string_message(self, db:  MySQLConnection):
        message = string_message_pb2.StringMessage()
        message.b = 'Hello World!'
        assert self.jsonformat(db, message.SerializeToString(), '.StringMessage') == {"b": "Hello World!"}

    def test_repeated_fields_message(self, db:  MySQLConnection):
        message = repeated_fields_pb2.RepeatedFields()
        message.d = '123'
        message.e.append(1)
        message.e.append(2)
        message.e.append(3)

        assert self.jsonformat(db, message.SerializeToString(), '.RepeatedFields') == {"d": "123", "e": [1, 2, 3]}


    def test_repeated_fields_one_element(self, db:  MySQLConnection):
        message = repeated_fields_pb2.RepeatedFields()
        message.d = '123'
        message.e.append(1)

        assert self.jsonformat(db, message.SerializeToString(), '.RepeatedFields') == {"d": "123", "e": [1]}

    def test_repeated_fields_submessage(self, db:  MySQLConnection):
        message = repeated_fields_pb2.RepeatedFields()
        g1 = message.g.add()
        g1.a = 1
        g2 = message.g.add()
        g2.a = 2

        assert self.jsonformat(db, message.SerializeToString(), '.RepeatedFields') == {"g": [{"a":1}, {"a":2}]}


    def test_repeated_fields_one_submessage(self, db:  MySQLConnection):
        message = repeated_fields_pb2.RepeatedFields()
        g1 = message.g.add()
        g1.a = 1

        assert self.jsonformat(db, message.SerializeToString(), '.RepeatedFields') == {"g": [{"a":1}]}



    def test_submessage(self, db:  MySQLConnection):
        message = submessage_pb2.ParentMessage()
        message.c.a = 123456

        assert self.jsonformat(db, message.SerializeToString(), '.ParentMessage') == {"c": {"a": 123456}}

    def test_group(self, db:  MySQLConnection):
        message = group_pb2.GroupMessage()
        message.mygroup.a = 'a group'
        message.mygroup.b = 123456

        assert self.jsonformat(db, message.SerializeToString(), '.GroupMessage') == {"mygroup": {"a": "a group", "b": 123456}}

    def test_oneof_submessage(self, db: MySQLConnection):
        message = oneof_pb2.OneOfMessage()
        message.sub_message.a = 123456

        assert self.jsonformat(db, message.SerializeToString(), '.OneOfMessage') == {"subMessage": {"a": 123456}}

    def test_oneof_string(self, db: MySQLConnection):
        message = oneof_pb2.OneOfMessage()
        message.name = 'a string'

        assert self.jsonformat(db, message.SerializeToString(), '.OneOfMessage') == {"name": "a string"}

    def test_packed_repeated_fields(self, db:  MySQLConnection):
        message = packed_pb2.PackedFields()
        message.f.append(1)
        message.f.append(2)
        message.f.append(3)

        assert (self.jsonformat(db, message.SerializeToString(), '.PackedFields') == {"f": [1, 2, 3]})
