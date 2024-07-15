from dataclasses import dataclass

WIRETYPE_VARINT: int = 0
WIRETYPE_I64 = 1
WIRETYPE_LEN = 2
WIRETYPE_SGROUP = 3
WIRETYPE_EGROUP = 4
WIRETYPE_I32 = 5

@dataclass
class BinaryInput:
    bytes: bytes
    index: int = 0

    @staticmethod
    def fromhex(s:str):
        return BinaryInput(bytes.fromhex(s))


test = BinaryInput.fromhex('08 96 01')
print(test)


def var_int(bytes: BinaryInput):
    print(bytes)
    result = 0
    shift = 0
    count = 1
    for b in bytes.bytes[bytes.index:]:
        result += ((b & 0x7f) << shift)
        if b & 0x80:
            shift += 7
            count += 1
        else:
            break

    bytes.index += count
    return result


print(var_int(BinaryInput.fromhex('9601')))


def get_value(wiretype: int, bytes: BinaryInput):
    print(bytes)
    if wiretype == WIRETYPE_VARINT:
        return var_int(bytes)
    elif wiretype == WIRETYPE_LEN:
        return 'len'
    else:
        return wiretype


def get_data(bytes: BinaryInput):
    field_wiretype = var_int(bytes)
    wiretype = field_wiretype & 0x07
    field_number = (field_wiretype >> 3) & 0x1f
    print(wiretype)
    print(field_number)
    value = get_value(wiretype, bytes)

    return {field_number: value}


print(get_data(test))

print( int.to_bytes(1234567890, 4, byteorder='little').hex())
print( int.to_bytes(1234567890987654321, 8, byteorder='little').hex())