# Myprotosql

A set of mysql stored functions/procedures to read protobuf binary data

```
.\bin\protoc-27.2-win64\bin\protoc.exe  --proto_path=proto --python_out=build --myprotosql_out=build --plugin=protoc-gen-myprotosql=.\venv\Scripts\protoc-gen-myprotosql.exe .\proto\*
```

## todo
- packed repeated fields
- enums
- todos in code
- maps?
- bytes
- proto v3 default packed