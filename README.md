# Myprotosql

A set of mysql stored functions/procedures to read protobuf binary data  

[![Tests](https://github.com/janickr/myprotosql/actions/workflows/tests-mysql5_7.yml/badge.svg)](https://github.com/janickr/myprotosql/actions/workflows/tests-mysql5_7.yml)
[![Tests](https://github.com/janickr/myprotosql/actions/workflows/tests-mysql8.yml/badge.svg)](https://github.com/janickr/myprotosql/actions/workflows/tests-mysql8.yml)
[![PyPi](https://img.shields.io/pypi/v/myprotosql)](https://pypi.org/project/myprotosql/)

## Getting started

### Without `*.proto` files
This is similar to `protoc --decode_raw`.  

Run the `myproto.sql` script on your MySQL DB. This script creates the stored functions and procedures necessary to decode protobuf.

#### Decode to textformat
For example to decode_raw the `0x1a03089601` binary data to textformat:
```mysql
select myproto_decode_to_textformat(0x1a03089601, null, null);
```
Returns:
```prototext
3: {
 1: 150
}
```
#### Decode to JSON
```mysql
select myproto_decode_to_jsonformat(0x1a03089601, null, null);
```
Returns:
```json
{"3": {"1": 150}}
```

#### Limitations of decode_raw
Decode raw has limitations because protobuf binary data does not contain all info to properly decode the data.
- output will not contain field names, only field numbers
- packed repeated scalar values will be decoded as one binary string
- numbers will be decoded as unsigned integers

If you need proper decoding, then read on and learn how to use information in your `*.proto` files

### Using .proto files
The functions and stored procedures in `myproto.sql` are still needed: run the `myproto.sql` script in MySQL.

Let's say we have a `.proto` file like this:
```protobuf
package foo.bar;

message SubMessage {
  optional int32 a = 1;
}

message ParentMessage {
  optional SubMessage c = 3;
}
```
We need to compile these `*.proto` files in something MySQL can understand. 

1) [Download and install](https://github.com/protocolbuffers/protobuf?tab=readme-ov-file#protobuf-compiler-installation) protoc
2) Install the myprotosql protoc plugin (you need python for this): 
    ```bash
    pip install myprotosql
    ```
3) Run the plugin using protoc:  
    `protoc  --proto_path=<the-path-to-your-proto-files> --myprotosql_out=<the-output-path> --plugin=protoc-gen-myprotosql=<the-path-to-the-myprotosql-plugin> <the-path-to-your-proto-files>\*`   
    This will generate a `myproto_descriptors.sql` file.  
    For example:
    - on Windows if you used Virtualenv, with your proto files located in `.\proto` and your virtual env path is `.\venv`:
        ```bash
        protoc.exe  --proto_path=proto --myprotosql_out=build --plugin=protoc-gen-myprotosql=.\venv\Scripts\protoc-gen-myprotosql.exe .\proto\*
        ```
    - on Ubuntu without virtualenv with your proto files located in `./proto`:
        ```bash
        protoc  --proto_path=proto --myprotosql_out=build ./proto/*
        ```
    
4) Run the `myproto_descriptors.sql` script in MySQL, this will create a `myproto_descriptors` 
function which returns the necessary information to decode protobuf data that conforms to the `.proto` files.


#### Decode to textformat

For example to decode_raw the `0x1a03089601` binary data to textformat:
```mysql
select myproto_decode_to_textformat(0x1a03089601, 'foo.bar.ParentMessage', myproto_descriptors());
```
Returns:
```prototext
c: {
 a: 150
}
```
#### Decode to JSON
```mysql
select myproto_decode_to_jsonformat(0x1a03089601, 'foo.bar.ParentMessage', myproto_descriptors());
```
Returns:
```json
{"c": {"a": 150}}
```


## Todo
- todos in code
- maps
- mysql 5.7 and integer float doc