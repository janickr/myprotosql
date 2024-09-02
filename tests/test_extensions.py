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

import extendable_message_pb2 as extendable
import extension_message_pb2 as extension

from conftest import MyProtoSql


class TestExtensions:

    def test_decode_raw_textformat(self, myprotosql: MyProtoSql):
        message = extendable.ExtendableMessageVerified()
        message.Extensions[extension.an_extension_field_verified] = 123
        message.Extensions[extension.NestedExtensionNotRecommended.nested_field_2_verified] = 'a text'
        message.Extensions[extension.NestedExtensionNotRecommended.AnotherNestedLevel.nested_field_4_verified] = 'another text'
        message.Extensions[extension.AnExtensionFieldType.nested_field_3_verified].extension_message_field = 654
        assert (myprotosql.decode_raw_textformat(message.SerializeToString()) ==
                '2001: 123\n'
                '2002: "a text"\n'
                '2004: "another text"\n'
                '2003: {\n'
                ' 1: 654\n'
                '}\n'
                )

    def test_decode_textformat(self, myprotosql: MyProtoSql):
        message = extendable.ExtendableMessageVerified()
        message.Extensions[extension.an_extension_field_verified] = 123
        message.Extensions[extension.NestedExtensionNotRecommended.nested_field_2_verified] = 'a text'
        message.Extensions[extension.NestedExtensionNotRecommended.AnotherNestedLevel.nested_field_4_verified] = 'another text'
        message.Extensions[extension.AnExtensionFieldType.nested_field_3_verified].extension_message_field = 654
        assert (myprotosql.decode_textformat(message.SerializeToString(), 'foo.bar.extendable.ExtendableMessageVerified') ==
                'an_extension_field_verified: 123\n'
                'nested_field_2_verified: "a text"\n'
                'nested_field_4_verified: "another text"\n'
                'nested_field_3_verified: {\n'
                ' extension_message_field: 654\n'
                '}\n'
                )

    def test_decode_raw_jsonformat(self, myprotosql: MyProtoSql):
        message = extendable.ExtendableMessageVerified()
        message.Extensions[extension.an_extension_field_verified] = 123
        message.Extensions[extension.NestedExtensionNotRecommended.nested_field_2_verified] = 'a text'
        message.Extensions[extension.NestedExtensionNotRecommended.AnotherNestedLevel.nested_field_4_verified] = 'another text'
        message.Extensions[extension.AnExtensionFieldType.nested_field_3_verified].extension_message_field = 654
        assert (myprotosql.decode_raw_jsonformat(message.SerializeToString()) ==
                {
                    '2001': 123,
                    '2002': 'a text',
                    '2004': 'another text',
                    '2003': {'1': 654}
                })

    def test_decode_jsonformat(self, myprotosql: MyProtoSql):
        message = extendable.ExtendableMessageVerified()
        message.Extensions[extension.an_extension_field_verified] = 123
        message.Extensions[extension.NestedExtensionNotRecommended.nested_field_2_verified] = 'a text'
        message.Extensions[extension.NestedExtensionNotRecommended.AnotherNestedLevel.nested_field_4_verified] = 'another text'
        message.Extensions[extension.AnExtensionFieldType.nested_field_3_verified].extension_message_field = 654
        assert (myprotosql.decode_jsonformat(message.SerializeToString(), 'foo.bar.extendable.ExtendableMessageVerified') ==
                {
                    'anExtensionFieldVerified': 123,
                    'nestedField2Verified': 'a text',
                    'nestedField4Verified': 'another text',
                    'nestedField3Verified': {'extensionMessageField': 654}
                })

