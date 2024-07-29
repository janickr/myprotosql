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

import pytest
from mysql.connector import MySQLConnection


class TestInterpretI64:

    def interpret_int64(self, connection, p_field_type, p_int):
        with connection.cursor() as cursor:
            return cursor.callproc('_myproto_interpret_int64_value', (p_field_type, p_int, None))[2]

    def test_fixed_1(self, db:  MySQLConnection):
        assert self.interpret_int64(db, 'TYPE_FIXED64', 1) == '1'

    def test_fixed_2(self, db:  MySQLConnection):
        assert self.interpret_int64(db, 'TYPE_FIXED64', 2) == '2'

    def test_fixed_max(self, db:  MySQLConnection):
        assert self.interpret_int64(db, 'TYPE_FIXED64', 0xffffffffffffffff) == '18446744073709551615'

    def test_sfixed_zero(self, db:  MySQLConnection):
        assert self.interpret_int64(db, 'TYPE_SFIXED64', 0) == '0'

    def test_sfixed_neg1(self, db:  MySQLConnection):
        assert self.interpret_int64(db, 'TYPE_SFIXED64', 0xffffffffffffffff) == '-1'

    def test_sfixed_neg2(self, db:  MySQLConnection):
        assert self.interpret_int64(db, 'TYPE_SFIXED64', 0xfffffffffffffffe) == '-2'

    def test_sfixed_1(self, db:  MySQLConnection):
        assert self.interpret_int64(db, 'TYPE_SFIXED64', 1) == '1'

    def test_sfixed_2(self, db:  MySQLConnection):
        assert self.interpret_int64(db, 'TYPE_SFIXED64', 2) == '2'

    def test_sfixed_min(self, db:  MySQLConnection):
        assert self.interpret_int64(db, 'TYPE_SFIXED64', 0x8000000000000000) == '-9223372036854775808'

    def test_sfixed_max(self, db:  MySQLConnection):
        assert self.interpret_int64(db, 'TYPE_SFIXED64', 0x7fffffffffffffff) == '9223372036854775807'


    def test_double_smallest_denormalized(self, db:  MySQLConnection):
        # this should be more precise 4.9406564584124654e-324
        assert self.interpret_int64(db, 'TYPE_DOUBLE', 0x0000000000000001) == '5e-324'
        assert self.interpret_int64(db, 'TYPE_DOUBLE', 0x8000000000000001) == '-5e-324'

    def test_double_largest_denormalized(self, db:  MySQLConnection):
        assert self.interpret_int64(db, 'TYPE_DOUBLE', 0x000fffffffffffff) == '2.225073858507201e-308'
        assert self.interpret_int64(db, 'TYPE_DOUBLE', 0x800fffffffffffff) == '-2.225073858507201e-308'

    def test_double_largest_normalized(self, db:  MySQLConnection):
        assert self.interpret_int64(db, 'TYPE_DOUBLE', 0x7fefffffffffffff) == '1.7976931348623157e308'
        assert self.interpret_int64(db, 'TYPE_DOUBLE', 0xffefffffffffffff) == '-1.7976931348623157e308'

    def test_double_smallest_normalized(self, db:  MySQLConnection):
        assert self.interpret_int64(db, 'TYPE_DOUBLE', 0x0010000000000000) == '2.2250738585072014e-308'
        assert self.interpret_int64(db, 'TYPE_DOUBLE', 0x8010000000000000) == '-2.2250738585072014e-308'

    @pytest.mark.mysql8
    def test_double_1(self, db:  MySQLConnection):
        assert self.interpret_int64(db, 'TYPE_DOUBLE', 0x3ff0000000000000) == '1.0'

    @pytest.mark.mysql8
    def test_double_neg1(self, db:  MySQLConnection):
        assert self.interpret_int64(db, 'TYPE_DOUBLE', 0xbff0000000000000) == '-1.0'

    @pytest.mark.mysql8
    def test_double_neg2(self, db:  MySQLConnection):
        assert self.interpret_int64(db, 'TYPE_DOUBLE', 0xc000000000000000) == '-2.0'

    @pytest.mark.mysql5_7
    def test_double_1_mysql5_7_cannot_cast_int_double(self, db:  MySQLConnection):
        assert self.interpret_int64(db, 'TYPE_DOUBLE', 0x3ff0000000000000) == '1'

    @pytest.mark.mysql5_7
    def test_double_neg1_mysql5_7_cannot_cast_int_double(self, db:  MySQLConnection):
        assert self.interpret_int64(db, 'TYPE_DOUBLE', 0xbff0000000000000) == '-1'

    @pytest.mark.mysql5_7
    def test_double_neg2_mysql5_7_cannot_cast_int_double(self, db:  MySQLConnection):
        assert self.interpret_int64(db, 'TYPE_DOUBLE', 0xc000000000000000) == '-2'

    def test_double_neg0(self, db:  MySQLConnection):
        assert self.interpret_int64(db, 'TYPE_DOUBLE', 0x8000000000000000) == '0.0'

    def test_double_pos0(self, db:  MySQLConnection):
        assert self.interpret_int64(db, 'TYPE_DOUBLE', 0x0000000000000000) == '0.0'

    def test_double_pos_infinity(self, db:  MySQLConnection):
        assert self.interpret_int64(db, 'TYPE_DOUBLE', 0x7ff0000000000000) == '"+Infinity"'

    def test_double_neg_infinity(self, db:  MySQLConnection):
        assert self.interpret_int64(db, 'TYPE_DOUBLE', 0xfff0000000000000) == '"-Infinity"'

    def test_double_NaN(self, db:  MySQLConnection):
        assert self.interpret_int64(db, 'TYPE_DOUBLE', 0x7ff0000000000001) == '"NaN"'
        assert self.interpret_int64(db, 'TYPE_DOUBLE', 0xfff0000000000001) == '"NaN"'
        assert self.interpret_int64(db, 'TYPE_DOUBLE', 0x7ff8000000000001) == '"NaN"'
        assert self.interpret_int64(db, 'TYPE_DOUBLE', 0xfff8000000000001) == '"NaN"'

