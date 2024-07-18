import json
import simple_message_pb2 as simple_message_pb2
import string_message_pb2 as string_message_pb2
import repeated_fields_pb2 as repeated_fields_pb2
import submessage_pb2 as submessage_pb2
import packages_submessage_pb2 as packages_submessage_pb2
import imports_parentmessage_pb2 as imports_parentmessage_pb2
import packages_imports_parentmessage_pb2 as packages_imports_parentmessage_pb2
import group_pb2 as group_pb2
from mysql.connector import MySQLConnection


class TestDecodeTextFormat:

    def textformat(self, connection, p_bytes, p_message_type):
        with connection.cursor() as cursor:
            cursor.execute("select myproto_decode_to_textformat(%s, %s, myproto_descriptors())", (p_bytes, p_message_type))
            return cursor.fetchone()[0]

    def test_simple_message(self, db:  MySQLConnection):
        message = simple_message_pb2.SimpleMessage()
        message.a = 123456
        assert self.textformat(db, message.SerializeToString(), '.SimpleMessage') == 'a: 123456\n'

    def test_string_message(self, db:  MySQLConnection):
        message = string_message_pb2.StringMessage()
        message.b = 'Hello World!'
        assert self.textformat(db, message.SerializeToString(), '.StringMessage') == 'b: "Hello World!"\n'

    def test_repeated_fields_message(self, db:  MySQLConnection):
        message = repeated_fields_pb2.RepeatedFields()
        message.d = '123'
        message.e.append(1)
        message.e.append(2)
        message.e.append(3)

        assert self.textformat(db, message.SerializeToString(), '.RepeatedFields') == 'd: "123"\ne: 1\ne: 2\ne: 3\n'


    def test_submessage(self, db:  MySQLConnection):
        message = submessage_pb2.ParentMessage()
        message.c.a = 123456

        assert self.textformat(db, message.SerializeToString(), '.ParentMessage') == 'c: {\n a: 123456\n}\n'

    def test_group(self, db:  MySQLConnection):
        message = group_pb2.GroupMessage()
        message.mygroup.a = 'a group'
        message.mygroup.b = 123456

        assert self.textformat(db, message.SerializeToString(), '.GroupMessage') == 'mygroup: {\n a: "a group"\n b: 123456\n}\n'
