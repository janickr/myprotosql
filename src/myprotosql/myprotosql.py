import json
import sys

from google.protobuf.compiler import plugin_pb2 as plugin
from google.protobuf import descriptor_pb2
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


def _build_file_index(proto_file):
    index = {}
    for message_type in proto_file.message_type:
        packed_default = proto_file.syntax == 'proto3'
        if proto_file.package:
            index = index | {f'.{proto_file.package}.{name}': fields for name, fields in _build_message_type_index(message_type, packed_default).items()}
        else:
            index = index | {f'.{name}': fields for name, fields in _build_message_type_index(message_type, packed_default).items()}

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