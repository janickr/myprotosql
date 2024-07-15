from dataclasses import dataclass

import pytest
from mysql.connector import MySQLConnection


class TestI64:
    @dataclass
    class I64Result:
        offset: int
        value: int

    def get_I64_value(self, connection, p_bytes, p_offset, p_limit):
        with connection.cursor() as cursor:
            result = cursor.callproc('get_I64_value', (p_bytes, p_offset, p_limit, 0))
            return TestI64.I64Result(result[1], result[3])

    def test_zero(self, db:  MySQLConnection):
        assert self.get_I64_value(db, (0).to_bytes(byteorder="little", length=8), 1, 9) == TestI64.I64Result(9, 0)

    def test_max_value(self, db:  MySQLConnection):
        assert self.get_I64_value(db, (0xffffffffffffffff).to_bytes(byteorder="little", length=8), 1, 9) == TestI64.I64Result(9, 0xffffffffffffffff)

    def test_another_value(self, db:  MySQLConnection):
        assert self.get_I64_value(db, (1234567890123456789).to_bytes(byteorder="little", length=8), 1, 9) == TestI64.I64Result(9, 1234567890123456789)

    def test_error_value_exceeds_limit(self, db: MySQLConnection):
        with pytest.raises(Exception) as expected_error:
            self.get_I64_value(db, (0).to_bytes(byteorder="little", length=8), 1, 2)

        assert expected_error.value.args[1] == '1644 (45000): i64 at offset 1 exceeds limit set by LEN 2'
