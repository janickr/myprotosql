from dataclasses import dataclass

import pytest
from mysql.connector import MySQLConnection


class TestI32:
    @dataclass
    class I32Result:
        offset: int
        value: int

    def get_i32_value(self, connection, p_bytes, p_offset, p_limit):
        with connection.cursor() as cursor:
            result = cursor.callproc('_myproto_get_i32_value', (p_bytes, p_offset, p_limit, 0))
            return TestI32.I32Result(result[1], result[3])

    def test_zero(self, db:  MySQLConnection):
        assert self.get_i32_value(db, (0).to_bytes(byteorder="little", length=4), 1, 5) == TestI32.I32Result(5, 0)

    def test_max_value(self, db:  MySQLConnection):
        assert self.get_i32_value(db, (0xffffffff).to_bytes(byteorder="little", length=4), 1, 5) == TestI32.I32Result(5, 0xffffffff)

    def test_another_value(self, db:  MySQLConnection):
        assert self.get_i32_value(db, (1234567890).to_bytes(byteorder="little", length=4), 1, 5) == TestI32.I32Result(5, 1234567890)

    def test_error_value_exceeds_limit(self, db: MySQLConnection):
        with pytest.raises(Exception) as expected_error:
            self.get_i32_value(db, (0).to_bytes(byteorder="little", length=4), 1, 2)

        assert expected_error.value.args[1] == '1644 (45000): i32 at offset 1 exceeds limit set by LEN 2'
