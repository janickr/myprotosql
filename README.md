# Myprotosql

A set of mysql stored functions/procedures to read protobuf binary data  

[![Tests](https://github.com/janickr/myprotosql/actions/workflows/tests-mysql5_7.yml/badge.svg)](https://github.com/janickr/myprotosql/actions/workflows/tests-mysql5_7.yml)
[![Tests](https://github.com/janickr/myprotosql/actions/workflows/tests-mysql8.yml/badge.svg)](https://github.com/janickr/myprotosql/actions/workflows/tests-mysql8.yml)
[![PyPi](https://img.shields.io/pypi/v/myprotosql)](https://pypi.org/project/myprotosql/)

## Getting started (with *.proto files)
See [decode using .proto files](#decode-using-proto-files) for an example.   

- [Download and install](https://github.com/protocolbuffers/protobuf?tab=readme-ov-file#protobuf-compiler-installation) protoc  
  
- Install myprotosql (requires python):  

    ```bash
    pip install myprotosql
    ```   
  
- Run protoc with the myprotosql plugin (your `*.proto` files located in `./proto`, output in `./build`):  
  
    ```bash
    protoc  --proto_path=proto --myprotosql_out=build ./proto/*
    ```  
  
- Run the generated `install_myprotosql.sql` and `myproto_descriptors.sql` scripts in MySQL  
  If you used this proto file, you can now decode your first protobuf message  
  
    ```mysql
    select myproto_decode_to_textformat(
        0x1a03089601, 'foo.bar.ParentMessage', myproto_descriptors());
    ```

## Getting started (without *.proto files)
This is similar to `protoc --decode_raw`. See [decode raw](#decode-raw) for an example.

- Install myprotosql (requires python): 
  
    ```bash
    pip install myprotosql
    ```
- Generate the install script  
  
    ```bash
    myprotosql-install-script > install_myprotosql.sql
    ```  
- Run the generated `install_myprotosql.sql` script in MySQL  
  Decode your first protobuf message:
  
    ```mysql
    select myproto_decode_to_textformat(0x1a03089601, null, null);
    ```
#### Alternative
Instead of using pip and python to install myprotosql, you can also just download the `install_myprotosql.sql` from the github repository and run that in MySQL.

## Decoding
Running `install_myprotosql.sql` installs two functions that can be used to decode protobuf binary messages:
- myproto_decode_to_textformat(binary_message, message_type, type_descriptors)
- myproto_decode_to_jsonformat(binary_message, message_type, type_descriptors)

### Decode raw
Decoding without the `*.proto` files

#### Textformat
decode_raw the `0x1a03089601` binary data to textformat:
```mysql
select myproto_decode_to_textformat(0x1a03089601, null, null);
```
Returns:
```prototext
3: {
 1: 150
}
```
#### JSON
```mysql
select myproto_decode_to_jsonformat(0x1a03089601, null, null);
```
Returns:
```json
{"3": {"1": 150}}
```

### Decode using .proto files

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
Check out [Getting started (with *.proto files)](#getting-started-with-proto-files) to compile these `*.proto` files in something MySQL can understand. 

#### Textformat

For example to decode the `0x1a03089601` binary data to textformat:
```mysql
select myproto_decode_to_textformat(0x1a03089601, 'foo.bar.ParentMessage', myproto_descriptors());
```
Returns:
```prototext
c: {
 a: 150
}
```
#### JSON
```mysql
select myproto_decode_to_jsonformat(0x1a03089601, 'foo.bar.ParentMessage', myproto_descriptors());
```
Returns:
```json
{"c": {"a": 150}}
```

## Troubleshooting
### on Windows if you used Virtualenv
you need to specify the full path to the myprotosql plugin, like this:
```bash
protoc.exe  --proto_path=proto --myprotosql_out=build --plugin=protoc-gen-myprotosql=.\venv\Scripts\protoc-gen-myprotosql.exe .\proto\* 
```
This assumed your proto files are located in `.\proto` and your virtual env path is `.\venv`. In general the command is of the form:
```bash
protoc  --proto_path=<the-path-to-your-proto-files> --myprotosql_out=<the-output-path> --plugin=protoc-gen-myprotosql=<the-path-to-the-myprotosql-plugin> <the-path-to-your-proto-files>\*
```

### Limitations of decode_raw
Decode raw has limitations because protobuf binary data does not contain all info to properly decode the data.
- output will not contain field names, only field numbers
- packed repeated scalar values will be decoded as one binary string
- numbers will be decoded as unsigned integers

If you need proper decoding, then read on and learn how to use information in your `*.proto` files

### Protobuf extensions
Not implemented yet

## Todo
- todos in code
- Extensions