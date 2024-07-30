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

import json
import sys

from google.protobuf.compiler import plugin_pb2 as plugin
from google.protobuf.json_format import MessageToJson


def field_descriptor(field, packed_default):
    file_properties = json.loads(MessageToJson(field))
    return {
              "name": file_properties['name'],
              "number": file_properties['number'],
              "repeated": file_properties['label'] == "LABEL_REPEATED",
              "packed": file_properties.get('options', {}).get('packed', packed_default),
              "type": file_properties['type'],
              "typeName": file_properties.get('typeName', None),
              "jsonName": file_properties['jsonName']
            }


def _build_message_type_index(message_type, packed_default):
    index = {message_type.name: {'fields': {field.number: field_descriptor(field, packed_default) for field in message_type.field}}}
    for nested_type in message_type.nested_type:
        index = index | {f'{message_type.name}.{name}': fields for name, fields in _build_message_type_index(nested_type, packed_default).items()}

    return index

def _build_enum_type_index(enum_type):
    return {enum_type.name: {'values': {value.number: value.name for value in enum_type.value}}}


def _build_file_index(proto_file):
    index = {}
    for message_type in proto_file.message_type:
        packed_default = proto_file.syntax == 'proto3'
        if proto_file.package:
            index = index | {f'.{proto_file.package}.{name}': fields for name, fields in _build_message_type_index(message_type, packed_default).items()}
        else:
            index = index | {f'.{name}': fields for name, fields in _build_message_type_index(message_type, packed_default).items()}
    for enum_type in proto_file.enum_type:
        if proto_file.package:
            index = index | {f'.{proto_file.package}.{name}': values for name, values in _build_enum_type_index(enum_type).items()}
        else:
            index = index | {f'.{name}': values for name, values in _build_enum_type_index(enum_type).items()}
    return index


def _build_index(request):
    index = {}
    for proto_file in request.proto_file:
        index = index | _build_file_index(proto_file)

    return index


def run_plugin():
    request = plugin.CodeGeneratorRequest.FromString(sys.stdin.buffer.read())
    response = plugin.CodeGeneratorResponse()

    generated_file = response.file.add()

    generated_file.name = "myproto_descriptors.sql"
    descriptors = _build_index(request)

    generated_file.content = f'''
DROP FUNCTION IF EXISTS myproto_descriptors;
delimiter //
CREATE FUNCTION myproto_descriptors() RETURNS JSON deterministic 
    RETURN '{json.dumps(descriptors, indent=2)}';
//
    '''
    sys.stdout.buffer.write(response.SerializeToString())


def dump_request():
    request = plugin.CodeGeneratorRequest.FromString(sys.stdin.buffer.read())
    response = plugin.CodeGeneratorResponse()

    generated_file = response.file.add()
    generated_file.name = "code_generator_request_dump.json"
    generated_file.content = MessageToJson(request)

    sys.stdout.buffer.write(response.SerializeToString())


if __name__ == "__main__":
    run_plugin()
