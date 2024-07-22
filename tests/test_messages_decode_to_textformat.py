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

import simple_message_pb2
import string_message_pb2
import repeated_fields_pb2
import submessage_pb2
import group_pb2
import oneof_pb2
import packed_pb2
import repeatedv3_pb2
from mysql.connector import MySQLConnection


class TestDecodeTextFormat:

    def textformat(self, connection, p_bytes, p_message_type):
        with connection.cursor() as cursor:
            cursor.execute("select myproto_decode_to_textformat(%s, %s, myproto_descriptors())", (p_bytes, p_message_type))
            return cursor.fetchone()[0]

    def test_simple_message(self, db:  MySQLConnection):
        message = simple_message_pb2.SimpleMessage()
        message.a = 123456
        assert self.textformat(db, message.SerializeToString(), 'SimpleMessage') == 'a: 123456\n'

    def test_string_message(self, db:  MySQLConnection):
        message = string_message_pb2.StringMessage()
        message.b = 'Hello World!'
        assert self.textformat(db, message.SerializeToString(), 'StringMessage') == 'b: "Hello World!"\n'

    def test_repeated_fields_message(self, db:  MySQLConnection):
        message = repeated_fields_pb2.RepeatedFields()
        message.d = '123'
        message.e.append(1)
        message.e.append(2)
        message.e.append(3)

        assert self.textformat(db, message.SerializeToString(), 'RepeatedFields') == 'd: "123"\ne: 1\ne: 2\ne: 3\n'


    def test_submessage(self, db:  MySQLConnection):
        message = submessage_pb2.ParentMessage()
        message.c.a = 123456

        assert self.textformat(db, message.SerializeToString(), 'ParentMessage') == 'c: {\n a: 123456\n}\n'

    def test_group(self, db:  MySQLConnection):
        message = group_pb2.GroupMessage()
        message.mygroup.a = 'a group'
        message.mygroup.b = 123456

        assert self.textformat(db, message.SerializeToString(), 'GroupMessage') == 'mygroup: {\n a: "a group"\n b: 123456\n}\n'


    def test_oneof_submessage(self, db: MySQLConnection):
        message = oneof_pb2.OneOfMessage()
        message.sub_message.a = 123456

        assert self.textformat(db, message.SerializeToString(), 'OneOfMessage') == 'sub_message: {\n a: 123456\n}\n'

    def test_oneof_string(self, db: MySQLConnection):
        message = oneof_pb2.OneOfMessage()
        message.name = 'a string'

        assert self.textformat(db, message.SerializeToString(), 'OneOfMessage') == 'name: "a string"\n'


    def test_packed_repeated_fields(self, db:  MySQLConnection):
        message = packed_pb2.PackedFields()
        message.f.append(1)
        message.f.append(2)
        message.f.append(3)

        assert self.textformat(db, message.SerializeToString(), 'PackedFields') == 'f: {1 2 3}\n'


    def test_packed_repeatedv3_fields(self, db:  MySQLConnection):
        message = repeatedv3_pb2.RepeatedV3()
        message.f.append(1)
        message.f.append(2)
        message.f.append(3)

        assert self.textformat(db, message.SerializeToString(), 'RepeatedV3') == 'f: {1 2 3}\n'
