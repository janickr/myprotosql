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

from dataclasses import dataclass

import pytest
from mysql.connector import MySQLConnection


class TestVarInt:
    @dataclass
    class VarIntResult:
        offset: int
        value: int

    def varint(self, connection, p_bytes, p_offset, p_limit):
        with connection.cursor() as cursor:
            result = cursor.callproc('_myproto_var_int', (p_bytes, p_offset, p_limit, 0))
            return TestVarInt.VarIntResult(result[1], result[3])

    def test_one(self, db:  MySQLConnection):
        assert self.varint(db, bytes.fromhex('01'), 1, 5) == TestVarInt.VarIntResult(2, 1)

    def test_150(self, db:  MySQLConnection):
        assert self.varint(db, bytes.fromhex('9601'), 1, 5) == TestVarInt.VarIntResult(3, 150)

    def test_zero(self, db:  MySQLConnection):
        assert self.varint(db, bytes.fromhex('00'), 1, 5) == TestVarInt.VarIntResult(2, 0)

    def test_max(self, db:  MySQLConnection):
        assert self.varint(db, bytes.fromhex('ffffffffffffffffff7f'), 1, 10) == TestVarInt.VarIntResult(11, 0xffffffffffffffff)

    def test_error_value_exceeds_limit(self, db:  MySQLConnection):
        with pytest.raises(Exception) as expected_error:
            self.varint(db, bytes.fromhex('ffffffffffffffffff7f'), 1, 2)

        assert expected_error.value.args[1] == '1644 (45000): VarInt at offset 1 exceeds limit set by LEN 2'
