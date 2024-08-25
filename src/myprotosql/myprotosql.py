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
import pkgutil

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


def _mark_possible_maps(message_types: dict):
    for message_type_name, message_type in message_types.items():
        for field_descriptor in message_type.get('fields', {}).values():
            if is_probably_a_map(field_descriptor, message_type_name, message_types):
                field_descriptor['type'] = 'PROBABLY_MAP'

    return message_types


def to_camel_case(snake_case: str):
    return ''.join(word.title() for word in snake_case.split('_'))


def to_map_type_name(message_type_name: str, field_name: str):
    return message_type_name + '.' + to_camel_case(field_name) + 'Entry'


def looks_like_a_map_type(map_type_name, message_types):
    return {
        field_descriptor['name']
        for field_descriptor in message_types.get(map_type_name, {}).get('fields', {}).values()
    } == {'key', 'value'}


def is_probably_a_map(field_descriptor, message_type_name, message_types):
    map_type_name = to_map_type_name(message_type_name, field_descriptor['name'])
    return (field_descriptor['type'] == 'TYPE_MESSAGE'
            and field_descriptor['repeated']
            and field_descriptor['typeName'] == map_type_name
            and looks_like_a_map_type(map_type_name, message_types))


def get_myprotosql_install_script():
    return pkgutil.get_data(__name__, "install_myproto.sql").decode("utf-8")


def get_myprotosql_uninstall_script():
    return pkgutil.get_data(__name__, "uninstall_myproto.sql").decode("utf-8")


def run_plugin():
    request = plugin.CodeGeneratorRequest.FromString(sys.stdin.buffer.read())
    response = plugin.CodeGeneratorResponse()

    descriptors_file = response.file.add()

    descriptors_file.name = "myproto_descriptors.sql"
    descriptors = _mark_possible_maps(_build_index(request))

    descriptors_file.content = f'''
DROP FUNCTION IF EXISTS myproto_descriptors;
delimiter //
CREATE FUNCTION myproto_descriptors() RETURNS JSON deterministic 
    RETURN '{json.dumps(descriptors, indent=2)}';
//
    '''

    install_file = response.file.add()
    install_file.name = "install_myproto.sql"
    install_file.content = get_myprotosql_install_script()

    install_file = response.file.add()
    install_file.name = "uninstall_myproto.sql"
    install_file.content = get_myprotosql_uninstall_script()

    sys.stdout.buffer.write(response.SerializeToString())


def dump_request():
    request = plugin.CodeGeneratorRequest.FromString(sys.stdin.buffer.read())
    response = plugin.CodeGeneratorResponse()

    generated_file = response.file.add()
    generated_file.name = "code_generator_request_dump.json"
    generated_file.content = MessageToJson(request)

    sys.stdout.buffer.write(response.SerializeToString())


def print_install_script():
    print(get_myprotosql_install_script())


def print_uninstall_script():
    print(get_myprotosql_uninstall_script())


if __name__ == "__main__":
    run_plugin()
