import simple_message_pb2
import string_message_pb2
import repeated_fields_pb2
import submessage_pb2
import group_pb2
import oneof_pb2
from mysql.connector import MySQLConnection


class TestDecodeRawTextFormat:

    def textformat(self, connection, p_bytes):
        with connection.cursor() as cursor:
            cursor.execute("select myproto_decode_to_textformat(%s, NULL, NULL)", (p_bytes, ))
            return cursor.fetchone()[0]

    def test_simple_message(self, db:  MySQLConnection):
        message = simple_message_pb2.SimpleMessage()
        message.a = 123456
        assert self.textformat(db, message.SerializeToString()) == '1: 123456\n'

    def test_string_message(self, db:  MySQLConnection):
        message = string_message_pb2.StringMessage()
        message.b = 'Hello World!'
        assert self.textformat(db, message.SerializeToString()) == '2: "Hello World!"\n'

    def test_repeated_fields_message(self, db:  MySQLConnection):
        message = repeated_fields_pb2.RepeatedFields()
        message.d = '123'
        message.e.append(1)
        message.e.append(2)
        message.e.append(3)

        assert self.textformat(db, message.SerializeToString()) == '4: "123"\n5: 1\n5: 2\n5: 3\n'


    def test_submessage(self, db:  MySQLConnection):
        message = submessage_pb2.ParentMessage()
        message.c.a = 123456

        assert self.textformat(db, message.SerializeToString()) == '3: {\n 1: 123456\n}\n'

    def test_group(self, db:  MySQLConnection):
        message = group_pb2.GroupMessage()
        message.mygroup.a = 'a group'
        message.mygroup.b = 123456

        assert self.textformat(db, message.SerializeToString()) == '1: {\n 1: "a group"\n 2: 123456\n}\n'

    def test_oneof_submessage(self, db: MySQLConnection):
        message = oneof_pb2.OneOfMessage()
        message.sub_message.a = 123456

        assert self.textformat(db, message.SerializeToString()) == '9: {\n 1: 123456\n}\n'

    def test_oneof_string(self, db: MySQLConnection):
        message = oneof_pb2.OneOfMessage()
        message.name = 'a string'

        assert self.textformat(db, message.SerializeToString()) == '4: "a string"\n'

