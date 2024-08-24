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

import packages_submessage_pb2
import imports_parentmessage_pb2
import packages_imports_parentmessage_pb2

from conftest import MyProtoSql


class TestPackagesAndImports:

    def test_decode_packages_submessage(self, myprotosql: MyProtoSql):
        message = packages_submessage_pb2.ParentMessagePackage()
        message.c.a = 123456

        assert (myprotosql.decode(message.SerializeToString(), 'foo.bar.ParentMessagePackage') ==
                [{'depth': 0,
                  'field_json_name': 'c',
                  'field_name': 'c',
                  'field_number': 3,
                  'field_type': 'TYPE_MESSAGE',
                  'message_type': '.foo.bar.SubMessagePackage',
                  'path': '$',
                  'repeated': False,
                  'type': 'start message'},
                 {'depth': 1,
                  'field_json_name': 'a',
                  'field_name': 'a',
                  'field_number': 1,
                  'field_type': 'TYPE_INT32',
                  'field_type_name': None,
                  'path': '$.3',
                  'repeated': False,
                  'type': 'field',
                  'value': 123456},
                 {'depth': 0,
                  'field_json_name': 'a',
                  'field_name': 'c',
                  'field_number': 3,
                  'field_type': 'TYPE_MESSAGE',
                  'message_type': '.foo.bar.SubMessagePackage',
                  'path': '$',
                  'repeated': False,
                  'type': 'end message'}])

    def test_decode_imports_submessage(self, myprotosql: MyProtoSql):
        message = imports_parentmessage_pb2.ParentMessageImports()
        message.c.a = 123456

        assert (myprotosql.decode(message.SerializeToString(), 'ParentMessageImports') ==
                [{'depth': 0,
                  'field_json_name': 'c',
                  'field_name': 'c',
                  'field_number': 3,
                  'field_type': 'TYPE_MESSAGE',
                  'message_type': '.SubMessageImports',
                  'path': '$',
                  'repeated': False,
                  'type': 'start message'},
                 {'depth': 1,
                  'field_json_name': 'a',
                  'field_name': 'a',
                  'field_number': 1,
                  'field_type': 'TYPE_INT32',
                  'field_type_name': None,
                  'path': '$.3',
                  'repeated': False,
                  'type': 'field',
                  'value': 123456},
                 {'depth': 0,
                  'field_json_name': 'a',
                  'field_name': 'c',
                  'field_number': 3,
                  'field_type': 'TYPE_MESSAGE',
                  'message_type': '.SubMessageImports',
                  'path': '$',
                  'repeated': False,
                  'type': 'end message'}])

    def test_decode_package_imports_submessage(self, myprotosql: MyProtoSql):
        message = packages_imports_parentmessage_pb2.ParentMessagePackageImports()
        message.c.a = 123456

        assert (myprotosql.decode(message.SerializeToString(), 'foo.bar.imports.parent.ParentMessagePackageImports') ==
                [{'depth': 0,
                  'field_json_name': 'c',
                  'field_name': 'c',
                  'field_number': 3,
                  'field_type': 'TYPE_MESSAGE',
                  'message_type': '.foo.bar.imports.sub.SubMessagePackageImports',
                  'path': '$',
                  'repeated': False,
                  'type': 'start message'},
                 {'depth': 1,
                  'field_json_name': 'a',
                  'field_name': 'a',
                  'field_number': 1,
                  'field_type': 'TYPE_INT32',
                  'field_type_name': None,
                  'path': '$.3',
                  'repeated': False,
                  'type': 'field',
                  'value': 123456},
                 {'depth': 0,
                  'field_json_name': 'a',
                  'field_name': 'c',
                  'field_number': 3,
                  'field_type': 'TYPE_MESSAGE',
                  'message_type': '.foo.bar.imports.sub.SubMessagePackageImports',
                  'path': '$',
                  'repeated': False,
                  'type': 'end message'}])
