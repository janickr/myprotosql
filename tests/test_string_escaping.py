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

import string_message_pb2

from conftest import MyProtoSql


class TestStringMessage:

    def test_decode_raw_textformat_quoted(self, myprotosql: MyProtoSql):
        message = string_message_pb2.StringMessage()
        message.b = 'this is "quoted"\n'
        assert myprotosql.decode_raw_textformat(message.SerializeToString()) == '2: "this is \\"quoted\\"\\n"\n'

    def test_decode_raw_jsonformat_quoted(self, myprotosql: MyProtoSql):
        message = string_message_pb2.StringMessage()
        message.b = 'this is "quoted"'
        assert myprotosql.decode_raw_jsonformat(message.SerializeToString()) == {"2": 'this is "quoted"'}

    def test_decode_raw_textformat_escaped_characters(self, myprotosql: MyProtoSql):
        message = string_message_pb2.StringMessage()
        message.b = '\x07\x08\x09\x0a\x0b\x0c\x0d\\'
        assert myprotosql.decode_raw_textformat(message.SerializeToString()) == '2: "\\a\\b\\t\\n\\v\\f\\r\\\\"\n'

