import json
import sys

from google.protobuf.compiler import plugin_pb2 as plugin
from google.protobuf import descriptor_pb2
from google.protobuf.json_format import MessageToJson


def fqn(proto_file:  descriptor_pb2.FileDescriptorProto, message_type):
    if proto_file.package:
        return '.' + proto_file.package + '.' + message_type.name
    else:
        return '.' + message_type.name


def field_descriptor(field):
    return json.loads(MessageToJson(field))


def descriptor(proto_file:  descriptor_pb2.FileDescriptorProto, message_type):
    return {
        'package': proto_file.package,
        'name': message_type.name,
        'fields': {field.number: field_descriptor(field) for field in message_type.field}
    }


def run_plugin():
    request = plugin.CodeGeneratorRequest.FromString(sys.stdin.buffer.read())
    response = plugin.CodeGeneratorResponse()

    generated_file = response.file.add()

    descriptors = {
        fqn(proto_file, message_type): descriptor(proto_file, message_type)
        for proto_file in request.proto_file
        for message_type in proto_file.message_type}

    generated_file.name = "myproto_descriptors.sql"

    generated_file.content = f'''
delimiter //
CREATE FUNCTION myproto_descriptors() RETURNS JSON deterministic 
    RETURN '{json.dumps(descriptors, indent=2)}';
//
    '''

if __name__ == "__main__":
    run_plugin()