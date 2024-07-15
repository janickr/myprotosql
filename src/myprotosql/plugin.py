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
        # 'fqn': fqn(proto_file, message_type),
        'package': proto_file.package,
        'name': message_type.name,
        'fields': {field.number: field_descriptor(field) for field in message_type.field}
    }


if __name__ == "__main__":
    request = plugin.CodeGeneratorRequest.FromString(sys.stdin.buffer.read())
    response = plugin.CodeGeneratorResponse()
    # print(request.ToJSONString())

    generated_file = response.file.add()
    generated_file.name = "hello_world.json"
    generated_file.content = MessageToJson(request)
    # for proto_file in request.proto_file:                         # 1
    #     if proto_file.name in request.file_to_generate:           # 2
    #         f = generate_for_proto(proto_file)                    # 3
    #         response.file.append(f)                               # 4

    descriptors = {
        fqn(proto_file, message_type): descriptor(proto_file, message_type)
        for proto_file in request.proto_file
        for message_type in proto_file.message_type}
    other = response.file.add()

    generated_file.name = "myproto_descriptors.sql"

    generated_file.content = f'''
delimiter //
CREATE FUNCTION myproto_descriptors() RETURNS JSON deterministic 
    RETURN '{json.dumps(descriptors, indent=2)}';
//
    '''

    sys.stdout.buffer.write(response.SerializeToString())