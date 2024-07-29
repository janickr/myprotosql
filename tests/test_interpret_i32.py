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


class TestInterpretI32:

    def interpret_int32(self, connection, p_field_type, p_int):
        with connection.cursor() as cursor:
            return cursor.callproc('_myproto_interpret_int32_value', (p_field_type, p_int, None))[2]

    def test_fixed_1(self, db:  MySQLConnection):
        assert self.interpret_int32(db, 'TYPE_FIXED32', 1) == '1'

    def test_fixed_2(self, db:  MySQLConnection):
        assert self.interpret_int32(db, 'TYPE_FIXED32', 2) == '2'

    def test_fixed_max(self, db:  MySQLConnection):
        assert self.interpret_int32(db, 'TYPE_FIXED32', 0xffffffff) == '4294967295'

    def test_sfixed_zero(self, db:  MySQLConnection):
        assert self.interpret_int32(db, 'TYPE_SFIXED32', 0) == '0'

    def test_sfixed_neg1(self, db:  MySQLConnection):
        assert self.interpret_int32(db, 'TYPE_SFIXED32', 0xffffffff) == '-1'

    def test_sfixed_neg2(self, db:  MySQLConnection):
        assert self.interpret_int32(db, 'TYPE_SFIXED32', 0xfffffffe) == '-2'

    def test_sfixed_1(self, db:  MySQLConnection):
        assert self.interpret_int32(db, 'TYPE_SFIXED32', 1) == '1'

    def test_sfixed_2(self, db:  MySQLConnection):
        assert self.interpret_int32(db, 'TYPE_SFIXED32', 2) == '2'

    def test_sfixed_min(self, db:  MySQLConnection):
        assert self.interpret_int32(db, 'TYPE_SFIXED32', 0x80000000) == '-2147483648'

    def test_sfixed_max(self, db:  MySQLConnection):
        assert self.interpret_int32(db, 'TYPE_SFIXED32', 0x7fffffff) == '2147483647'


    def test_float_smallest_denormalized(self, db:  MySQLConnection):
        assert self.interpret_int32(db, 'TYPE_FLOAT', 0x00000001) == '1.401298464324817e-45'
        assert self.interpret_int32(db, 'TYPE_FLOAT', 0x80000001) == '-1.401298464324817e-45'

    def test_float_largest_denormalized(self, db:  MySQLConnection):
        assert self.interpret_int32(db, 'TYPE_FLOAT', 0x007fffff) == '1.1754942106924411e-38'
        assert self.interpret_int32(db, 'TYPE_FLOAT', 0x807fffff) == '-1.1754942106924411e-38'

    def test_float_largest_normalized(self, db:  MySQLConnection):
        assert self.interpret_int32(db, 'TYPE_FLOAT', 0x7f7fffff) == '3.4028234663852886e38'
        assert self.interpret_int32(db, 'TYPE_FLOAT', 0xff7fffff) == '-3.4028234663852886e38'

    def test_float_smallest_normalized(self, db:  MySQLConnection):
        assert self.interpret_int32(db, 'TYPE_FLOAT', 0x00800000) == '1.1754943508222875e-38'
        assert self.interpret_int32(db, 'TYPE_FLOAT', 0x80800000) == '-1.1754943508222875e-38'

    @pytest.mark.mysql8
    def test_float_1(self, db:  MySQLConnection):
        assert self.interpret_int32(db, 'TYPE_FLOAT', 0x3f800000) == '1.0'

    @pytest.mark.mysql8
    def test_float_neg1(self, db:  MySQLConnection):
        assert self.interpret_int32(db, 'TYPE_FLOAT', 0xbf800000) == '-1.0'

    @pytest.mark.mysql8
    def test_float_neg2(self, db:  MySQLConnection):
        assert self.interpret_int32(db, 'TYPE_FLOAT', 0xc0000000) == '-2.0'

    @pytest.mark.mysql5_7
    def test_float_1_mysql5_7_cannot_cast_int_float(self, db:  MySQLConnection):
        assert self.interpret_int32(db, 'TYPE_FLOAT', 0x3f800000) == '1'

    @pytest.mark.mysql5_7
    def test_float_neg1_mysql5_7_cannot_cast_int_float(self, db:  MySQLConnection):
        assert self.interpret_int32(db, 'TYPE_FLOAT', 0xbf800000) == '-1'

    @pytest.mark.mysql5_7
    def test_float_neg2_mysql5_7_cannot_cast_int_float(self, db:  MySQLConnection):
        assert self.interpret_int32(db, 'TYPE_FLOAT', 0xc0000000) == '-2'

    def test_float_neg0(self, db:  MySQLConnection):
        assert self.interpret_int32(db, 'TYPE_FLOAT', 0x80000000) == '0.0'

    def test_float_pos0(self, db:  MySQLConnection):
        assert self.interpret_int32(db, 'TYPE_FLOAT', 0x00000000) == '0.0'

    def test_float_pos_infinity(self, db:  MySQLConnection):
        assert self.interpret_int32(db, 'TYPE_FLOAT', 0x7f800000) == '"+Infinity"'

    def test_float_neg_infinity(self, db:  MySQLConnection):
        assert self.interpret_int32(db, 'TYPE_FLOAT', 0xff800000) == '"-Infinity"'

    def test_float_NaN(self, db:  MySQLConnection):
        assert self.interpret_int32(db, 'TYPE_FLOAT', 0x7f800001) == '"NaN"'
        assert self.interpret_int32(db, 'TYPE_FLOAT', 0xff800001) == '"NaN"'
        assert self.interpret_int32(db, 'TYPE_FLOAT', 0x7fc00001) == '"NaN"'
        assert self.interpret_int32(db, 'TYPE_FLOAT', 0xffc00001) == '"NaN"'

