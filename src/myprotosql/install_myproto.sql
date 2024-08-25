/*
 * Copyright (c) 2024. Janick Reynders
 *
 * This file is part of Myprotosql.
 *
 * Myprotosql is free software: you can redistribute it and/or modify it under the terms of the
 * GNU Lesser General Public License as published by the Free Software Foundation, either
 * version 3 of the License, or (at your option) any later version.
 *
 * Myprotosql is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
 * without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
 * See the GNU Lesser General Public License for more details.
 *
 * You should have received a copy of the GNU Lesser General Public License along with Myprotosql.
 * If not, see <https://www.gnu.org/licenses/>.
 */

DROP FUNCTION IF EXISTS myproto_decode_to_jsonformat;
DROP FUNCTION IF EXISTS myproto_decode_to_textformat;
DROP FUNCTION IF EXISTS _myproto_field_type_to_wiretype;
DROP FUNCTION IF EXISTS _myproto_flatten_message;
DROP FUNCTION IF EXISTS _myproto_format_nanos;
DROP FUNCTION IF EXISTS _myproto_is_frame_field;
DROP FUNCTION IF EXISTS _myproto_is_scalar;
DROP FUNCTION IF EXISTS _myproto_is_start_submessage;
DROP FUNCTION IF EXISTS _myproto_jsonformat;
DROP FUNCTION IF EXISTS _myproto_reinterpret_as_double;
DROP FUNCTION IF EXISTS _myproto_reinterpret_as_float;
DROP FUNCTION IF EXISTS _myproto_snake_case_to_lower_camel_case;
DROP FUNCTION IF EXISTS _myproto_textformat;
DROP FUNCTION IF EXISTS _myproto_textformat_escape;
DROP FUNCTION IF EXISTS _myproto_textformat_escape_binary;
DROP FUNCTION IF EXISTS _myproto_to_utf8_textformat_string;
DROP FUNCTION IF EXISTS _myproto_unquote;
DROP FUNCTION IF EXISTS _myproto_wiretype_egroup;
DROP FUNCTION IF EXISTS _myproto_wiretype_len;
DROP FUNCTION IF EXISTS _myproto_wiretype_sgroup;
DROP PROCEDURE IF EXISTS _myproto_add_path_to_post_process;
DROP PROCEDURE IF EXISTS _myproto_append_end_submessage;
DROP PROCEDURE IF EXISTS _myproto_append_path_value;
DROP PROCEDURE IF EXISTS _myproto_append_start_submessage;
DROP PROCEDURE IF EXISTS _myproto_get_field_and_wiretype;
DROP PROCEDURE IF EXISTS _myproto_get_field_properties;
DROP PROCEDURE IF EXISTS _myproto_get_fixed_number_value;
DROP PROCEDURE IF EXISTS _myproto_get_i32_value;
DROP PROCEDURE IF EXISTS _myproto_get_i64_value;
DROP PROCEDURE IF EXISTS _myproto_get_len_value;
DROP PROCEDURE IF EXISTS _myproto_get_number_field_value;
DROP PROCEDURE IF EXISTS _myproto_interpret_int32_value;
DROP PROCEDURE IF EXISTS _myproto_interpret_int64_value;
DROP PROCEDURE IF EXISTS _myproto_interpret_varint_value;
DROP PROCEDURE IF EXISTS _myproto_json_add_value;
DROP PROCEDURE IF EXISTS _myproto_json_convert_map_entries;
DROP PROCEDURE IF EXISTS _myproto_json_post_process_any;
DROP PROCEDURE IF EXISTS _myproto_json_post_process_duration;
DROP PROCEDURE IF EXISTS _myproto_json_post_process_fieldmask;
DROP PROCEDURE IF EXISTS _myproto_json_post_process_listvalue;
DROP PROCEDURE IF EXISTS _myproto_json_post_process_maps_and_well_known_types;
DROP PROCEDURE IF EXISTS _myproto_json_post_process_nullvalue;
DROP PROCEDURE IF EXISTS _myproto_json_post_process_paths_at_same_depth;
DROP PROCEDURE IF EXISTS _myproto_json_post_process_struct;
DROP PROCEDURE IF EXISTS _myproto_json_post_process_timestamp;
DROP PROCEDURE IF EXISTS _myproto_json_post_process_value;
DROP PROCEDURE IF EXISTS _myproto_json_post_process_wrapper_type;
DROP PROCEDURE IF EXISTS _myproto_len_limit;
DROP PROCEDURE IF EXISTS _myproto_lookup_enum_value_if_enum_type;
DROP PROCEDURE IF EXISTS _myproto_packed_scalar;
DROP PROCEDURE IF EXISTS _myproto_pop_frame;
DROP PROCEDURE IF EXISTS _myproto_pop_frame_and_reset;
DROP PROCEDURE IF EXISTS _myproto_push_frame;
DROP PROCEDURE IF EXISTS _myproto_recover_from_error;
DROP PROCEDURE IF EXISTS _myproto_undo_appended_fields;
DROP PROCEDURE IF EXISTS _myproto_validate_wiretype_and_field_type;
DROP PROCEDURE IF EXISTS _myproto_var_int;

-- from older releases
DROP FUNCTION IF EXISTS _myproto_text_format_escape;
DROP FUNCTION IF EXISTS _myproto_to_utf8_string;
DROP PROCEDURE IF EXISTS _myproto_get_field_value;



delimiter //
create function _myproto_unquote(p_json_string_or_null JSON) returns text deterministic
    BEGIN
        IF JSON_TYPE(p_json_string_or_null) = 'NULL' THEN
            RETURN NULL;
        ELSE
            RETURN JSON_UNQUOTE(p_json_string_or_null);
        END IF;
    END;
//

create function _myproto_is_scalar(p_field_type text) returns boolean deterministic
    BEGIN
        RETURN p_field_type like 'TYPE_INT%'
                OR p_field_type like 'TYPE_UINT%'
                OR p_field_type like 'TYPE_SINT%'
                OR p_field_type like 'TYPE_BOOL'
                OR p_field_type like 'TYPE_ENUM'
                OR p_field_type like 'TYPE_FIXED%'
                OR p_field_type like 'TYPE_FLOAT'
                OR p_field_type like 'TYPE_DOUBLE';
    END;
//

create function _myproto_field_type_to_wiretype(p_field_type text) returns boolean deterministic
    BEGIN
        DECLARE type_not_supported varchar(128) default CONCAT('Field type to wiretype mapping only supported for scalar types, not for ', p_field_type);

        IF p_field_type like 'TYPE_INT%'
                OR p_field_type like 'TYPE_UINT%'
                OR p_field_type like 'TYPE_SINT%'
                OR p_field_type like 'TYPE_BOOL'
                OR p_field_type like 'TYPE_ENUM' THEN
            RETURN 0;
        ELSEIF p_field_type like 'TYPE_FIXED32' OR p_field_type like 'TYPE_FLOAT' THEN
            RETURN 5;
        ELSEIF p_field_type like 'TYPE_FIXED64' OR p_field_type like 'TYPE_DOUBLE' THEN
            RETURN 1;
        ELSE
            SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = type_not_supported;
        END IF;
    END;
//


CREATE PROCEDURE _myproto_var_int(IN p_bytes blob, INOUT p_offset integer, IN p_limit integer, OUT p_result bigint unsigned)
BEGIN
  DECLARE error_text_exceeds_limit varchar(128) default CONCAT('VarInt at offset ', p_offset, ' exceeds limit set by LEN ', p_limit);
  DECLARE error_text_too_many_bytes varchar(128) default CONCAT('VarInt at offset ', p_offset, ' has more than 10 bytes');
  DECLARE next blob;
  DECLARE shift, count integer;
  DECLARE b integer(1);
  SET p_result = 0;
  SET shift = 0;
  SET count = 1;
  SET next = substr(p_bytes, p_offset);
  READ_WHILE_FIRST_BIT_SET: REPEAT
      SET b = ASCII(next);
      SET p_result = p_result + ((b & 0x7f) << shift);
      IF ((b & 0x80) = 0)  THEN
        LEAVE READ_WHILE_FIRST_BIT_SET;
      END IF;
      SET next = substr(next, 2);
      SET shift = shift + 7;
      SET count = count + 1;

      UNTIL count > p_limit-p_offset+1
  END REPEAT;
  IF count > p_limit-p_offset+1 THEN
    SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = error_text_exceeds_limit;
  ELSEIF count > 10 THEN
    SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = error_text_too_many_bytes;
  ELSE
    SET p_offset = p_offset + count;
  END IF;
END;
//

CREATE PROCEDURE _myproto_get_fixed_number_value(IN p_bytes blob, INOUT p_offset integer, IN p_nb_bytes integer, OUT p_value bigint unsigned)
BEGIN
  DECLARE next blob DEFAULT substr(p_bytes, p_offset);
  DECLARE result bigint unsigned default 0;
  DECLARE shift, count integer default 0;
  DECLARE b integer(1);
  WHILE count < p_nb_bytes DO
    SET b = ASCII(next);
    SET result = result + ((b & 0xff) << shift);
    SET shift = shift + 8;
    SET next = substr(next, 2);
    SET count = count + 1;
  END WHILE;
  SET p_value = result;
  SET p_offset = p_offset + p_nb_bytes;
END
//

CREATE PROCEDURE _myproto_get_i32_value(IN p_bytes blob, INOUT p_offset integer, IN p_limit integer, OUT p_value bigint unsigned)
  BEGIN
    DECLARE error_text_exceeds_limit varchar(128) default CONCAT('i32 at offset ', p_offset, ' exceeds limit set by LEN ', p_limit);

    IF p_offset + 4 > p_limit THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = error_text_exceeds_limit;
    ELSE
        CALL _myproto_get_fixed_number_value(p_bytes, p_offset, 4, p_value);
    END IF;
  END;
//

CREATE PROCEDURE _myproto_get_i64_value(IN p_bytes blob, INOUT p_offset integer, IN p_limit integer, OUT p_value bigint unsigned)
  BEGIN
    DECLARE error_text_exceeds_limit varchar(128) default CONCAT('i64 at offset ', p_offset, ' exceeds limit set by LEN ', p_limit);

    IF p_offset + 8 > p_limit THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = error_text_exceeds_limit;
    ELSE
        CALL _myproto_get_fixed_number_value(p_bytes, p_offset, 8, p_value);
    END IF;
  END;
//

CREATE PROCEDURE _myproto_get_len_value(IN p_bytes blob, INOUT p_offset integer, IN p_limit integer, INOUT p_field_type text, OUT p_value JSON)
BEGIN
  DECLARE error_text_exceeds_limit varchar(128) default CONCAT('len at offset ', p_offset, ' exceeds limit set by previous LEN ', p_limit);

  DECLARE length integer;
  DECLARE binary_value blob;
  DECLARE utf8_value text charset utf8mb4;
  CALL _myproto_var_int(p_bytes, p_offset, p_limit, length);
  IF p_offset + length > p_limit THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = error_text_exceeds_limit;
  ELSE
    SET binary_value = substr(p_bytes, p_offset, length);
    SET utf8_value = CONVERT(binary_value USING utf8mb4);
    IF p_field_type = 'TYPE_BYTES' or utf8_value IS NULL THEN
        SET utf8_value = TO_BASE64(binary_value);
        SET p_field_type = 'TYPE_BYTES';
    ELSE
        SET p_field_type = 'TYPE_STRING';
    END IF;
    SET p_value = JSON_QUOTE(utf8_value);
    SET p_offset = p_offset + length;
  END IF;
END;
//

CREATE PROCEDURE _myproto_packed_scalar(
    IN p_bytes blob,
    INOUT p_offset integer,
    IN p_limit integer,
    INOUT p_message JSON,
    IN p_depth integer,
    IN p_parent_path text,
    IN p_field_number integer,
    IN p_field_name text,
    IN p_field_json_name text,
    IN p_field_type text,
    IN p_field_type_name text,
    IN p_protos JSON)
BEGIN
  DECLARE error_text_exceeds_limit varchar(128) default CONCAT('len at offset ', p_offset, ' exceeds limit set by previous LEN ', p_limit);

  DECLARE wiretype integer default _myproto_field_type_to_wiretype(p_field_type);
  DECLARE length integer;
  DECLARE offset integer;
  DECLARE value JSON;
  DECLARE value_list JSON default JSON_ARRAY();
  CALL _myproto_var_int(p_bytes, p_offset, p_limit, length);
  SET offset = p_offset;
  IF p_offset + length > p_limit THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = error_text_exceeds_limit;
  ELSE
    WHILE offset < p_offset + length DO
        CALL _myproto_get_number_field_value(p_bytes, offset, p_offset + length, wiretype, value, p_field_type);
        CALL _myproto_lookup_enum_value_if_enum_type(p_field_type, p_field_type_name, p_protos, value);

        SET value_list = JSON_ARRAY_APPEND(value_list, '$', value);
    END WHILE;
    CALL _myproto_append_path_value(p_message, p_depth, p_parent_path, p_field_number, p_field_name, p_field_json_name, p_field_type, p_field_type_name, True, value_list);

    SET p_offset = offset;
  END IF;
END;
//

CREATE PROCEDURE _myproto_interpret_varint_value(IN p_field_type text, IN p_int bigint unsigned, OUT p_value JSON)
BEGIN
  DECLARE error_text varchar(128) default CONCAT('Illegal type for varint ', p_field_type);

  IF p_field_type IS NULL THEN
      SET p_value = cast(p_int as JSON);
  ELSE
      CASE p_field_type
          WHEN 'TYPE_INT32' THEN
            SET p_value = cast(cast(p_int as signed) as JSON);
          WHEN 'TYPE_INT64' THEN
            SET p_value = cast(cast(p_int as signed) as JSON);
          WHEN 'TYPE_UINT32' THEN
            SET p_value = cast(cast(p_int as unsigned) as JSON);
          WHEN 'TYPE_UINT64' THEN
            SET p_value = cast(cast(p_int as unsigned) as JSON);
          WHEN 'TYPE_SINT32' THEN
            SET p_value = cast(cast(((p_int >> 1) ^ (-(p_int & 1))) as signed) as JSON);
          WHEN 'TYPE_SINT64' THEN
            SET p_value = cast(cast(((p_int >> 1) ^ (-(p_int & 1))) as signed) as JSON);
          WHEN 'TYPE_BOOL' THEN
            SET p_value = cast((p_int & 1)=1 as JSON);
          WHEN 'TYPE_ENUM' THEN
            SET p_value = cast(cast(p_int as signed) as JSON);
          ELSE
            SIGNAL SQLSTATE '45000'
                SET MESSAGE_TEXT = error_text;
      END CASE;
  END IF;
END;
//

CREATE function _myproto_reinterpret_as_float(i bigint unsigned) returns JSON deterministic
BEGIN
    DECLARE mantissa integer default (i & 0x007fffff);
    DECLARE exponent_biased integer default ((i >> 23) & 0xff);
    DECLARE significand integer default mantissa | (1 << 23);
    DECLARE exponent_unbiased integer default (exponent_biased - 127);
    DECLARE sign integer default i >> 31;
    DECLARE result float;
    IF exponent_biased = 255 AND mantissa <> 0 THEN
        RETURN cast('"NaN"' as JSON);
    ELSEIF exponent_biased = 255 and sign = 1 THEN
        RETURN cast('"-Infinity"' as JSON);
    ELSEIF exponent_biased = 255 and sign = 0 THEN
        RETURN cast('"+Infinity"' as JSON);
    ELSEIF exponent_biased = 0 and mantissa = 0 and sign = 1 THEN
        RETURN cast(-0.0 as JSON);
    ELSEIF exponent_biased = 0 and mantissa = 0 and sign = 0 THEN
        RETURN cast(0.0 as JSON);
    ELSEIF exponent_biased = 0 and sign = 1 THEN
        SET result = -mantissa * pow(2, -149);
        RETURN cast(result as JSON);
    ELSEIF exponent_biased = 0 and sign = 0 THEN
        SET result = mantissa * pow(2, -149);
        RETURN cast(result as JSON);
    ELSEIF sign = 1 THEN
        SET result = -significand * pow(2, exponent_unbiased-23);
        RETURN cast(result as JSON);
    ELSEIF sign = 0 THEN
        SET result = significand * pow(2, exponent_unbiased-23);
        RETURN cast(result as JSON);
    END IF;
end;
//

CREATE function _myproto_reinterpret_as_double(i bigint unsigned) returns JSON deterministic
BEGIN
    DECLARE mantissa bigint default (i & 0xfffffffffffff);
    DECLARE exponent_biased bigint default ((i >> 52) & 0x7ff);
    DECLARE significand bigint default mantissa | (1 << 52);
    DECLARE exponent_unbiased bigint default (exponent_biased - 1023);
    DECLARE sign bigint default i >> 63;
    DECLARE result double;
    IF exponent_biased = 2047 AND mantissa <> 0 THEN
        RETURN cast('"NaN"' as JSON);
    ELSEIF exponent_biased = 2047 and sign = 1 THEN
        RETURN cast('"-Infinity"' as JSON);
    ELSEIF exponent_biased = 2047 and sign = 0 THEN
        RETURN cast('"+Infinity"' as JSON);
    ELSEIF exponent_biased = 0 and mantissa = 0 and sign = 1 THEN
        RETURN cast(-0.0 as JSON);
    ELSEIF exponent_biased = 0 and mantissa = 0 and sign = 0 THEN
        RETURN cast(0.0 as JSON);
    ELSEIF exponent_biased = 0 and sign = 1 THEN
        SET result = -mantissa * pow(2, -1074);
        RETURN cast(result as JSON);
    ELSEIF exponent_biased = 0 and sign = 0 THEN
        SET result = mantissa * pow(2, -1074);
        RETURN cast(result as JSON);
    ELSEIF sign = 1 THEN
        SET result = -significand * pow(2, exponent_unbiased-52);
        RETURN cast(result as JSON);
    ELSEIF sign = 0 THEN
        SET result = significand * pow(2, exponent_unbiased-52);
        RETURN cast(result as JSON);
    END IF;
end;
//


CREATE PROCEDURE _myproto_interpret_int64_value(IN p_field_type text, IN p_int bigint unsigned, OUT p_value JSON)
BEGIN
  DECLARE error_text varchar(128) default CONCAT('Illegal type for int64 ', p_field_type);

  IF p_field_type IS NULL THEN
      SET p_value = cast(p_int as JSON);
  ELSE
      CASE p_field_type
          WHEN 'TYPE_FIXED64' THEN
            SET p_value = cast(cast(p_int as unsigned) as JSON);
          WHEN 'TYPE_SFIXED64' THEN
            SET p_value = cast(cast(p_int as signed) as JSON);
          WHEN 'TYPE_DOUBLE' THEN
            SET p_value = _myproto_reinterpret_as_double(p_int);
          ELSE
            SIGNAL SQLSTATE '45000'
                SET MESSAGE_TEXT = error_text;
      END CASE;
  END IF;
END;
//

CREATE PROCEDURE _myproto_interpret_int32_value(IN p_field_type text, IN p_int bigint unsigned, OUT p_value JSON)
BEGIN
  DECLARE error_text varchar(128) default CONCAT('Illegal type for int32 ', p_field_type);

  IF p_field_type IS NULL THEN
      SET p_value = cast(p_int as JSON);
  ELSE
      CASE p_field_type
          WHEN 'TYPE_FIXED32' THEN
            SET p_value = cast(cast(p_int as unsigned) as JSON);
          WHEN 'TYPE_SFIXED32' THEN
            SET p_value = cast(cast(IF((p_int >> 31) > 0, p_int | 0xffffffff00000000, p_int) as signed) as JSON);
          WHEN 'TYPE_FLOAT' THEN
            SET p_value = _myproto_reinterpret_as_float(p_int);
          ELSE
            SIGNAL SQLSTATE '45000'
                SET MESSAGE_TEXT = error_text;
      END CASE;
  END IF;
END;
//

CREATE PROCEDURE _myproto_get_number_field_value(IN p_bytes blob, INOUT p_offset integer, IN p_limit integer, IN p_wiretype integer, OUT p_value JSON, IN p_field_type text)
BEGIN
  DECLARE error_text varchar(128) default CONCAT('Invalid wiretype ', p_wiretype);

  DECLARE int_result bigint unsigned;
  CASE p_wiretype
      WHEN 0 THEN
        CALL _myproto_var_int(p_bytes, p_offset, p_limit, int_result);
        CALL _myproto_interpret_varint_value(p_field_type, int_result, p_value);
      WHEN 1 THEN
        CALL _myproto_get_i64_value(p_bytes, p_offset, p_limit, int_result);
        CALL _myproto_interpret_int64_value(p_field_type, int_result, p_value);
      WHEN 5 THEN
        CALL _myproto_get_i32_value(p_bytes, p_offset, p_limit, int_result);
        CALL _myproto_interpret_int32_value(p_field_type, int_result, p_value);
      ELSE
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = error_text;
    END CASE;
END;
//

CREATE PROCEDURE  _myproto_lookup_enum_value_if_enum_type(IN p_field_type text, IN p_enum_type text, IN p_protos JSON, INOUT p_value json)
BEGIN
    DECLARE enum_value JSON;
    IF p_field_type = 'TYPE_ENUM' THEN
        SET enum_value = JSON_EXTRACT(p_protos, CONCAT('$."', p_enum_type, '".values."', p_value, '"'));
        IF enum_value IS NOT NULL THEN
            SET p_value = enum_value;
        END IF;
    END IF;
END;
//

CREATE PROCEDURE _myproto_push_frame(
    INOUT p_stack JSON,
    IN p_offset integer,
    IN p_limit integer,
    INOUT p_path text,
    IN p_field_number integer,
    IN p_field_name text,
    IN p_field_type text,
    INOUT p_message_type text,
    IN p_field_type_name text)
BEGIN
        SET p_stack = JSON_ARRAY_INSERT(
                p_stack,
                '$[0]',
                JSON_OBJECT(
                  'offset', p_offset,
                  'limit', p_limit,
                  'path', p_path,
                  'field_number', p_field_number,
                  'field_name', p_field_name,
                  'field_type', p_field_type,
                  'message_type', p_message_type,
                  'field_type_name', p_field_type_name
                ));
        SET p_message_type = p_field_type_name;
        IF (p_field_number) THEN
            SET p_path = CONCAT(p_path, '.', p_field_number);
        END IF;
    END;
//

CREATE PROCEDURE _myproto_pop_frame_and_reset(
    INOUT p_stack JSON,
    OUT p_offset integer,
    OUT p_limit integer,
    OUT p_path text,
    OUT p_field_number integer,
    OUT p_field_name text,
    OUT p_field_type text,
    OUT p_message_type text,
    OUT p_field_type_name text)
    BEGIN
        SET p_offset = JSON_EXTRACT(p_stack, '$[0].offset');
        SET p_limit = JSON_EXTRACT(p_stack, '$[0].limit');
        SET p_path = _myproto_unquote(JSON_EXTRACT(p_stack, '$[0].path'));
        SET p_field_number = JSON_EXTRACT(p_stack, '$[0].field_number');
        SET p_stack = JSON_REMOVE(p_stack, '$[0]');
        SET p_field_name = _myproto_unquote(JSON_EXTRACT(p_stack, '$[0].field_name'));
        SET p_field_type = _myproto_unquote(JSON_EXTRACT(p_stack, '$[0].field_type'));
        SET p_message_type = _myproto_unquote(JSON_EXTRACT(p_stack, '$[0].message_type'));
        SET p_field_type_name = _myproto_unquote(JSON_EXTRACT(p_stack, '$[0].field_type_name'));
    END;
//

CREATE PROCEDURE _myproto_pop_frame(
    INOUT p_stack JSON,
    OUT p_limit integer,
    OUT p_path text,
    OUT p_field_number integer,
    OUT p_field_name text,
    OUT p_field_type text,
    OUT p_message_type text,
    OUT p_field_type_name text)
    BEGIN
        SET p_limit = JSON_EXTRACT(p_stack, '$[0].limit');
        SET p_path = _myproto_unquote(JSON_EXTRACT(p_stack, '$[0].path'));
        SET p_field_number = JSON_EXTRACT(p_stack, '$[0].field_number');
        SET p_field_name = _myproto_unquote(JSON_EXTRACT(p_stack, '$[0].field_name'));
        SET p_field_type = _myproto_unquote(JSON_EXTRACT(p_stack, '$[0].field_type'));
        SET p_message_type = _myproto_unquote(JSON_EXTRACT(p_stack, '$[0].message_type'));
        SET p_field_type_name = _myproto_unquote(JSON_EXTRACT(p_stack, '$[0].field_type_name'));
        SET p_stack = JSON_REMOVE(p_stack, '$[0]');
    END;
//

CREATE FUNCTION _myproto_is_frame_field(p_stack JSON, p_field integer) returns boolean deterministic
    RETURN JSON_EXTRACT(p_stack, '$[0].field_number') = p_field;
//

CREATE PROCEDURE _myproto_get_field_and_wiretype(IN p_bytes blob, INOUT p_offset integer, IN p_limit integer, OUT p_field_number integer, OUT p_wiretype integer)
BEGIN
  DECLARE field_wiretype integer;

  CALL _myproto_var_int(p_bytes, p_offset, p_limit, field_wiretype);
  SET p_wiretype = field_wiretype & 0x07;
  SET p_field_number = (field_wiretype >> 3) & 0x1f;
END;
//

CREATE PROCEDURE _myproto_len_limit(IN p_bytes blob, INOUT p_offset integer, INOUT p_limit integer)
BEGIN
  DECLARE error_text_exceeds_limit varchar(128) default CONCAT('len at offset ', p_offset, ' exceeds limit set by previous LEN ', p_limit);

  DECLARE value integer;
  CALL _myproto_var_int(p_bytes, p_offset, p_limit, value);
  IF p_offset + value > p_limit THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = error_text_exceeds_limit;
  ELSE
    SET p_limit = p_offset + value;
  END IF;
END;
//

CREATE FUNCTION _myproto_wiretype_len(p_wiretype integer) returns boolean deterministic
    return p_wiretype = 2;
//

CREATE FUNCTION _myproto_wiretype_sgroup(p_wiretype integer) returns boolean deterministic
    return p_wiretype = 3;
//

CREATE FUNCTION _myproto_wiretype_egroup(p_wiretype integer) returns boolean deterministic
    return p_wiretype = 4;
//

CREATE PROCEDURE _myproto_append_path_value(INOUT p_message JSON, IN p_depth integer, IN p_parent_path text, IN p_field_number integer, IN p_field_name text, IN p_field_json_name text, IN p_field_type text, IN p_field_type_name text, IN p_repeated boolean, IN p_value JSON)
BEGIN
    SET p_message = JSON_ARRAY_APPEND(
            p_message,
            '$',
            JSON_OBJECT(
                'type', 'field',
                'depth', p_depth,
                'path', p_parent_path,
                'field_number', p_field_number,
                'field_name', p_field_name,
                'field_json_name', p_field_json_name,
                'field_type', p_field_type,
                'field_type_name', p_field_type_name,
                'repeated', p_repeated IS NOT NULL and p_repeated,
                'value', p_value
            ));
END;
//

CREATE PROCEDURE _myproto_append_start_submessage(INOUT p_message JSON, IN p_depth integer, IN p_parent_path text, IN p_field_number integer, IN p_field_name text, IN p_field_json_name text, IN p_field_type text, IN p_message_type text, IN p_repeated boolean)
BEGIN
    SET p_message = JSON_ARRAY_APPEND(
            p_message,
            '$',
            JSON_OBJECT(
                'type', 'start message',
                'depth', p_depth,
                'path', p_parent_path,
                'field_number', p_field_number,
                'field_name', p_field_name,
                'field_json_name', p_field_json_name,
                'field_type', p_field_type,
                'message_type', p_message_type,
                'repeated', p_repeated IS NOT NULL and p_repeated
            ));
END;
//

CREATE PROCEDURE _myproto_append_end_submessage(INOUT p_message JSON, IN p_depth integer, IN p_parent_path text, IN p_field_number integer, IN p_field_name text, IN p_field_json_name text, IN p_field_type text, IN p_message_type text, IN p_repeated boolean)
BEGIN
    SET p_message = JSON_ARRAY_APPEND(
            p_message,
            '$',
            JSON_OBJECT(
                'type', 'end message',
                'depth', p_depth,
                'path', p_parent_path,
                'field_number', p_field_number,
                'field_name', p_field_name,
                'field_json_name', p_field_json_name,
                'field_type', p_field_type,
                'message_type', p_message_type,
                'repeated', p_repeated IS NOT NULL and p_repeated
            ));
END;
//

CREATE FUNCTION _myproto_is_start_submessage(p_message JSON, last_element text, p_depth integer, p_parent_path text, p_field_number integer) RETURNS boolean deterministic
BEGIN
    RETURN (cast(JSON_UNQUOTE(JSON_EXTRACT(p_message, CONCAT(last_element, '.type'))) as char) = 'start message'
        AND JSON_EXTRACT(p_message, CONCAT(last_element, '.depth')) = p_depth
        AND cast(JSON_UNQUOTE(JSON_EXTRACT(p_message, CONCAT(last_element, '.path'))) as char) = p_parent_path
        AND JSON_EXTRACT(p_message, CONCAT(last_element, '.field_number')) = p_field_number);
END
//

CREATE PROCEDURE _myproto_undo_appended_fields(INOUT p_message JSON, IN p_depth integer, IN p_parent_path text, IN p_field_number integer)
BEGIN
    DECLARE length integer DEFAULT JSON_LENGTH(p_message)-1;
    DECLARE last_element text DEFAULT CONCAT('$[',length,']');
    WHILE NOT _myproto_is_start_submessage(p_message, last_element, p_depth, p_parent_path, p_field_number) AND length >= 1 DO
        SET p_message = JSON_REMOVE(p_message, last_element);
        SET length = length-1;
        SET last_element = CONCAT('$[',length,']');
    END WHILE;
    SET p_message = JSON_REMOVE(p_message, last_element);
END;
//

CREATE PROCEDURE _myproto_validate_wiretype_and_field_type(
    IN p_message_type text,
    IN p_field_number integer,
    IN p_wiretype integer,
    IN p_field_type text)
BEGIN
  DECLARE error_text varchar(128) default CONCAT('Invalid wiretype ', p_wiretype, ' for ', IFNULL(p_message_type, '<null>'), ' field ', p_field_number, ' ', IFNULL(p_field_type, '<null>'));

  IF NOT(
      (p_wiretype = 0 AND p_field_type IN ('TYPE_INT32', 'TYPE_INT64', 'TYPE_UINT32', 'TYPE_UINT64', 'TYPE_SINT32', 'TYPE_SINT64', 'TYPE_BOOL', 'TYPE_ENUM'))
      OR (p_wiretype = 1 AND p_field_type IN ('TYPE_FIXED64', 'TYPE_SFIXED64', 'TYPE_DOUBLE'))
      OR (p_wiretype = 2) -- AND p_field_type IN ('TYPE_STRING', 'TYPE_BYTES', 'TYPE_MESSAGE')) todo or packed scalar
      OR (p_wiretype = 3 AND p_field_type = 'TYPE_GROUP')
      OR (p_wiretype = 4) -- AND p_field_type = 'TYPE_GROUP') todo figure out a way to validate egroup
      OR (p_wiretype = 5 AND p_field_type IN ('TYPE_FIXED32', 'TYPE_SFIXED32', 'TYPE_FLOAT'))
      ) THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = error_text;
  END IF;
END;
//

CREATE PROCEDURE _myproto_get_field_properties(
    IN p_message_type text,
    IN p_field_number integer,
    IN p_wiretype integer,
    IN p_protos JSON,
    OUT p_field_type text,
    OUT p_field_name text,
    OUT p_field_json_name text,
    OUT p_field_type_name text,
    OUT p_repeated boolean,
    OUT p_packed boolean)
BEGIN
    SET p_field_type = _myproto_unquote(JSON_EXTRACT(p_protos, CONCAT('$."', p_message_type, '".fields."', p_field_number, '".type')));
    SET p_field_name = _myproto_unquote(JSON_EXTRACT(p_protos, CONCAT('$."', p_message_type, '".fields."', p_field_number, '".name')));
    SET p_field_json_name = _myproto_unquote(JSON_EXTRACT(p_protos, CONCAT('$."', p_message_type, '".fields."', p_field_number, '".jsonName')));
    SET p_field_type_name = _myproto_unquote(JSON_EXTRACT(p_protos, CONCAT('$."', p_message_type, '".fields."', p_field_number, '".typeName')));
    SET p_repeated = cast(JSON_EXTRACT(p_protos, CONCAT('$."', p_message_type, '".fields."', p_field_number, '".repeated')) as unsigned) = 1;
    SET p_packed = cast(JSON_EXTRACT(p_protos, CONCAT('$."', p_message_type, '".fields."', p_field_number, '".packed')) as unsigned) = 1;
    CALL _myproto_validate_wiretype_and_field_type(p_message_type, p_field_number, p_wiretype, p_field_type);
END;
//

CREATE PROCEDURE _myproto_recover_from_error(
    IN p_bytes blob,
    INOUT p_stack JSON,
    INOUT p_message JSON,
    OUT p_offset integer,
    OUT p_limit integer,
    OUT p_path text,
    OUT p_field_number integer,
    OUT p_field_name text,
    OUT p_field_json_name text,
    OUT p_message_type text,
    OUT p_field_type_name text
)
BEGIN
    DECLARE in_error_state boolean default true;
    DECLARE value JSON;
    DECLARE field_type text;

    WHILE in_error_state and JSON_LENGTH(p_stack) > 0 DO
        BEGIN
            DECLARE CONTINUE HANDLER FOR SQLSTATE '45000'
            BEGIN
               -- todo resignal if p_stack empty?
               SET in_error_state = true;
            END;
             -- check if stack > 1, if not there is a bug
                -- resignal if not decode raw
            CALL _myproto_pop_frame_and_reset(p_stack, p_offset,p_limit, p_path, p_field_number, p_field_name, field_type, p_message_type, p_field_type_name);
            CALL _myproto_undo_appended_fields(p_message, JSON_LENGTH(p_stack)-1, p_path, p_field_number);
            SET in_error_state = false;
            CALL _myproto_get_len_value(p_bytes, p_offset, p_limit, field_type, value);
            IF not in_error_state THEN
                CALL _myproto_append_path_value(p_message, JSON_LENGTH(p_stack)-1, p_path, p_field_number, p_field_name, p_field_json_name, field_type, p_field_type_name, NULL, value);
            END IF;
        END;
    END WHILE;
END;
//

CREATE FUNCTION _myproto_flatten_message(p_bytes blob, p_message_type text, p_protos JSON) returns JSON deterministic
BEGIN
  DECLARE offset integer default 1;
  DECLARE field_number, wiretype integer;
  DECLARE p_limit, m_limit integer default length(p_bytes)+1;
  DECLARE message, stack, value JSON;
  DECLARE parent_path text default '$';
  DECLARE message_type text default '';
  DECLARE field_type_name text default IF(p_message_type IS NULL, NULL, CONCAT('.', p_message_type));
  DECLARE field_type, field_name, field_json_name text;
  DECLARE decode_raw boolean default p_message_type IS NULL;
  DECLARE packed, repeated boolean default NULL;

  SET stack = JSON_ARRAY();
  CALL _myproto_push_frame(stack, offset, m_limit, parent_path, 0, null, null, message_type, field_type_name);
  SET message = JSON_ARRAY();

  WHILE offset < p_limit DO
      BEGIN
          IF offset = m_limit and JSON_LENGTH(stack) > 1 THEN
                CALL _myproto_pop_frame(stack, m_limit, parent_path, field_number, field_name, field_type, message_type, field_type_name);
                IF JSON_LENGTH(stack) > 0 THEN
                    CALL _myproto_append_end_submessage(message, JSON_LENGTH(stack)-1, parent_path, field_number, field_name, field_json_name, field_type, field_type_name, repeated);
                END IF;
          ELSE
              BEGIN
                DECLARE EXIT HANDLER FOR SQLSTATE '45000'
                BEGIN
                     CALL _myproto_recover_from_error(p_bytes, stack, message, offset, m_limit, parent_path, field_number, field_name, field_json_name, message_type, field_type_name);
                END;

                CALL _myproto_get_field_and_wiretype(p_bytes, offset, m_limit, field_number, wiretype);
                CALL _myproto_get_field_properties(message_type, field_number, wiretype, p_protos, field_type, field_name, field_json_name, field_type_name, repeated, packed);

                IF _myproto_wiretype_len(wiretype) THEN
                    IF field_type = 'TYPE_MESSAGE' OR field_type = 'PROBABLY_MAP' OR decode_raw THEN
                        CALL _myproto_append_start_submessage(message, JSON_LENGTH(stack)-1, parent_path, field_number, field_name, field_json_name, field_type, field_type_name, repeated);
                        CALL _myproto_push_frame(stack, offset, m_limit, parent_path, field_number, field_name, field_type, message_type, field_type_name);
                        CALL _myproto_len_limit(p_bytes, offset, m_limit);
                    ELSEIF repeated AND packed AND _myproto_is_scalar(field_type) THEN
                        CALL _myproto_packed_scalar(p_bytes, offset, m_limit, message, JSON_LENGTH(stack)-1, parent_path, field_number, field_name, field_json_name, field_type, field_type_name, p_protos);
                    ELSE
                        CALL _myproto_get_len_value(p_bytes, offset, m_limit, field_type, value);
                        CALL _myproto_append_path_value(message, JSON_LENGTH(stack)-1, parent_path, field_number, field_name, field_json_name, field_type, field_type_name, repeated, value);
                    END IF;
                ELSEIF _myproto_wiretype_sgroup(wiretype) THEN
                    CALL _myproto_append_start_submessage(message, JSON_LENGTH(stack)-1, parent_path, field_number, field_name, field_json_name, field_type, field_type_name, repeated);
                    CALL _myproto_push_frame(stack, offset, m_limit, parent_path, field_number, field_name, field_type, message_type, field_type_name);
                ELSEIF _myproto_wiretype_egroup(wiretype) THEN
                    IF _myproto_is_frame_field(stack, field_number) THEN
                        CALL _myproto_pop_frame(stack, m_limit, parent_path, field_number, field_name, field_type, message_type, field_type_name);
                        CALL _myproto_append_end_submessage(message, JSON_LENGTH(stack)-1, parent_path, field_number, field_name, field_json_name, field_type, field_type_name, repeated);
                    ELSE
                        SIGNAL SQLSTATE '45000'
                            SET MESSAGE_TEXT = 'Malformed message';
                    END IF;
                ELSE
                    CALL _myproto_get_number_field_value(p_bytes, offset, m_limit, wiretype, value, field_type);
                    CALL _myproto_lookup_enum_value_if_enum_type(field_type, field_type_name, p_protos, value);
                    CALL _myproto_append_path_value(message, JSON_LENGTH(stack)-1, parent_path, field_number, field_name, field_json_name, field_type, field_type_name, repeated, value );
                END IF;
              END;
          END IF;

      END;
  END WHILE;
  WHILE JSON_LENGTH(stack) > 0 DO
      CALL _myproto_pop_frame(stack, m_limit, parent_path, field_number, field_name, field_type, message_type,
                              field_type_name);
      IF JSON_LENGTH(stack) > 0 THEN
        CALL _myproto_append_end_submessage(message, JSON_LENGTH(stack)-1, parent_path, field_number, field_name, field_json_name, field_type,
                                            field_type_name, repeated);
      END IF;
  END WHILE;

  return message;
END;
//

CREATE FUNCTION _myproto_to_utf8_textformat_string(p_string text, p_field_type text) returns text deterministic
BEGIN
 IF p_field_type = 'TYPE_BYTES' THEN
    RETURN _myproto_textformat_escape_binary(FROM_BASE64(p_string));
 ELSE
    RETURN _myproto_textformat_escape(p_string);
 END IF;
END;
//

CREATE FUNCTION _myproto_textformat_escape_binary(p_bytes blob) returns text deterministic
BEGIN
    DECLARE next blob default p_bytes;
    DECLARE b integer(1);
    DECLARE result text charset utf8mb4 default '';
    DECLARE escaped_or_char varchar(4) charset utf8mb4 default '';

    WHILE LENGTH(next) > 0 DO
        SET b = ASCII(next);
        IF (b < 0x20 OR b > 0x7e OR b = 0x22 OR b = 0x5C) THEN
            SET escaped_or_char = CONCAT('\\x', LPAD(hex(b), 2, '0'));
        ELSE
            SET escaped_or_char = SUBSTR(next, 1, 1);
        END IF;
        SET result = CONCAT(result, escaped_or_char);
        SET next = substr(next, 2);
    END WHILE;
    RETURN result;
END;
//

CREATE FUNCTION _myproto_textformat_escape(string blob) returns text deterministic
BEGIN
    RETURN REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(
                   string,
                   '\\', '\\\\'),
                   '"', '\\"'),
                   0x07, '\\a'),
                   0x08, '\\b'),
                   0x09, '\\t'),
                   0x0a, '\\n'),
                   0x0b, '\\v'),
                   0x0c, '\\f'),
                   0x0d, '\\r');
END;


CREATE FUNCTION _myproto_textformat(p_message JSON) returns text deterministic
BEGIN
    DECLARE length integer DEFAULT JSON_LENGTH(p_message);
    DECLARE i, depth, previous_depth integer default 0;
    DECLARE textformat TEXT charset utf8mb4 default '';
    DECLARE next_element TEXT default CONCAT('$[',i,']');
    DECLARE type TEXT;
    DECLARE field_number integer;
    DECLARE value JSON;
    DECLARE field_name, field_type TEXT;
    WHILE i < length DO
        SET type = cast(JSON_UNQUOTE(JSON_EXTRACT(p_message, CONCAT(next_element,'.type'))) as char);
        SET depth = JSON_EXTRACT(p_message, CONCAT(next_element, '.depth'));
        SET field_number = JSON_EXTRACT(p_message, CONCAT(next_element, '.field_number'));
        SET field_type = _myproto_unquote(JSON_EXTRACT(p_message, CONCAT(next_element, '.field_type')));
        SET field_name = _myproto_unquote(JSON_EXTRACT(p_message, CONCAT(next_element, '.field_name')));
        IF type = 'end message' THEN
            SET textformat = CONCAT(textformat, SPACE(depth), '}\n');
        ELSEIF type = 'field' THEN
            SET value = JSON_EXTRACT(p_message, CONCAT(next_element, '.value'));
            IF JSON_TYPE(value) = 'STRING' AND field_type = 'TYPE_ENUM' THEN
                SET textformat = CONCAT(textformat, SPACE(depth), IFNULL(field_name, field_number), ': ', JSON_UNQUOTE(value), '\n');
            ELSEIF JSON_TYPE(value) = 'STRING' THEN
                SET textformat = CONCAT(textformat, SPACE(depth), IFNULL(field_name, field_number), ': "', _myproto_to_utf8_textformat_string(JSON_UNQUOTE(value), field_type), '"\n');
            ELSEIF JSON_TYPE(value) = 'ARRAY' AND ((field_type = 'TYPE_FLOAT') OR (field_type = 'TYPE_DOUBLE')) THEN
                SET textformat = CONCAT(textformat, SPACE(depth), IFNULL(field_name, field_number), ': ', REPLACE(REPLACE(cast(value as char), ']', 'f]'), ', ', 'f, '), '\n');
            ELSEIF JSON_TYPE(value) = 'ARRAY' AND (field_type = 'TYPE_ENUM') THEN
                SET textformat = CONCAT(textformat, SPACE(depth), IFNULL(field_name, field_number), ': ', REPLACE(cast(value as char), '"', ''), '\n');
            ELSEIF JSON_TYPE(value) = 'ARRAY' THEN
                SET textformat = CONCAT(textformat, SPACE(depth), IFNULL(field_name, field_number), ': ', cast(value as char), '\n');
            ELSEIF (field_type = 'TYPE_FLOAT') OR (field_type = 'TYPE_DOUBLE') THEN
                SET textformat = CONCAT(textformat, SPACE(depth), IFNULL(field_name, field_number), ': ', value, 'f\n');
            ELSE
                SET textformat = CONCAT(textformat, SPACE(depth), IFNULL(field_name, field_number), ': ', value, '\n');
            END IF;
        ELSE
            SET textformat = CONCAT(textformat, SPACE(depth), IFNULL(field_name, field_number), ': ', '{\n');
        END IF;

        SET previous_depth = depth;
        SET i = i+1;
        SET next_element = CONCAT('$[',i,']');
    END WHILE;
    WHILE previous_depth > 0 DO
        SET previous_depth = previous_depth - 1;
        SET textformat = CONCAT(textformat, SPACE(previous_depth), '}\n');
    END WHILE;
    RETURN textformat;
END;
//

CREATE PROCEDURE _myproto_json_convert_map_entries(INOUT p_jsonformat JSON, IN p_path text)
BEGIN
    DECLARE map_entries json default JSON_EXTRACT(p_jsonformat, p_path);
    DECLARE converted json default JSON_OBJECT();
    DECLARE i integer default 0;
    DECLARE length integer default JSON_LENGTH(map_entries);
    WHILE i < length DO
        SET converted = JSON_MERGE_PATCH(converted, JSON_OBJECT(JSON_UNQUOTE(JSON_EXTRACT(map_entries, CONCAT('$[',i,'].key'))), JSON_EXTRACT(map_entries, CONCAT('$[',i,'].value'))));
        SET i = i + 1;
    END WHILE;
    SET p_jsonformat = JSON_REPLACE(p_jsonformat, p_path, converted);
END;
//

CREATE FUNCTION _myproto_format_nanos(p_nanos integer) RETURNS text DETERMINISTIC
BEGIN
    DECLARE nanos text default LPAD(p_nanos, 9, '0');
    WHILE SUBSTR(nanos, LENGTH(nanos)) = '0' DO
        SET nanos = SUBSTR(nanos, 1, LENGTH(nanos)-1);
    END WHILE;
    RETURN nanos;
END;
//

CREATE PROCEDURE _myproto_json_post_process_timestamp(INOUT p_jsonformat JSON, IN p_path text)
BEGIN
    DECLARE seconds bigint default JSON_EXTRACT(p_jsonformat, CONCAT(p_path,'.seconds'));
    DECLARE nanos integer default JSON_EXTRACT(p_jsonformat, CONCAT(p_path,'.nanos'));

    IF (nanos is null or nanos = 0) THEN
        SET p_jsonformat = JSON_REPLACE(p_jsonformat, p_path, DATE_FORMAT(FROM_UNIXTIME(seconds), '%Y-%m-%dT%H:%i:%sZ'));
    ELSE
        SET p_jsonformat = JSON_REPLACE(p_jsonformat, p_path, CONCAT(DATE_FORMAT(FROM_UNIXTIME(seconds), '%Y-%m-%dT%H:%i:%s'), '.', _myproto_format_nanos(nanos), 'Z'));
    END IF;
END;
//

CREATE PROCEDURE _myproto_json_post_process_duration(INOUT p_jsonformat JSON, IN p_path text)
BEGIN
    DECLARE seconds bigint default JSON_EXTRACT(p_jsonformat, CONCAT(p_path,'.seconds'));
    DECLARE nanos integer default JSON_EXTRACT(p_jsonformat, CONCAT(p_path,'.nanos'));

    IF (nanos is null or nanos = 0) THEN
        SET p_jsonformat = JSON_REPLACE(p_jsonformat, p_path, CONCAT(seconds, 's'));
    ELSE
        SET p_jsonformat = JSON_REPLACE(p_jsonformat, p_path, CONCAT(seconds, '.', _myproto_format_nanos(nanos), 's'));
    END IF;
END;
//

CREATE PROCEDURE _myproto_json_post_process_any(INOUT p_jsonformat JSON, IN p_path text)
BEGIN
    DECLARE any_type JSON default JSON_EXTRACT(p_jsonformat, CONCAT(p_path,'.typeUrl'));
    DECLARE any_value JSON default JSON_EXTRACT(p_jsonformat, CONCAT(p_path,'.value'));
    SET p_jsonformat = JSON_REPLACE(p_jsonformat, p_path, JSON_OBJECT('@type', any_type, 'value', any_value));
END;
//

CREATE PROCEDURE _myproto_json_post_process_struct(INOUT p_jsonformat JSON, IN p_path text)
BEGIN
    SET p_jsonformat = JSON_REPLACE(p_jsonformat, p_path, JSON_EXTRACT(p_jsonformat, CONCAT(p_path, '.', 'fields')));
END;
//

CREATE PROCEDURE _myproto_json_post_process_value(INOUT p_jsonformat JSON, IN p_path text)
BEGIN
    SET p_jsonformat = JSON_REPLACE(p_jsonformat, p_path,
        COALESCE(
            JSON_EXTRACT(p_jsonformat, CONCAT(p_path,'.numberValue')),
            JSON_EXTRACT(p_jsonformat, CONCAT(p_path,'.stringValue')),
            JSON_EXTRACT(p_jsonformat, CONCAT(p_path,'.boolValue')),
            JSON_EXTRACT(p_jsonformat, CONCAT(p_path,'.structValue')),
            JSON_EXTRACT(p_jsonformat, CONCAT(p_path,'.listValue')),
            JSON_EXTRACT(p_jsonformat, CONCAT(p_path,'.nullValue'))
        ));
END;
//

CREATE PROCEDURE _myproto_json_post_process_listvalue(INOUT p_jsonformat JSON, IN p_path text)
BEGIN
    SET p_jsonformat = JSON_REPLACE(p_jsonformat, p_path, JSON_EXTRACT(p_jsonformat, CONCAT(p_path,'.values')));
END;
//

CREATE PROCEDURE _myproto_json_post_process_nullvalue(INOUT p_jsonformat JSON, IN p_path text)
BEGIN
    SET p_jsonformat = JSON_REPLACE(p_jsonformat, p_path, NULL);
END;
//

CREATE FUNCTION _myproto_snake_case_to_lower_camel_case(p_string text) returns text DETERMINISTIC
BEGIN
    DECLARE pos integer default LOCATE('_', p_string);
    DECLARE previous_pos integer default 1;
    DECLARE camel, lowercase_char text default '';
    WHILE pos > 0 DO
        SET lowercase_char = UPPER(SUBSTR(p_string, pos+1, 1));
        SET camel = CONCAT(camel, SUBSTR(p_string, previous_pos, pos-previous_pos), lowercase_char);
        SET previous_pos = pos+2;
        SET pos = LOCATE('_', p_string, previous_pos);
    END WHILE;
    IF previous_pos < LENGTH(p_string) THEN
        SET camel = CONCAT(camel, SUBSTR(p_string, previous_pos, LENGTH(p_string)));
    END IF;
    RETURN camel;
END;
//

CREATE PROCEDURE _myproto_json_post_process_fieldmask(INOUT p_jsonformat JSON, IN p_path text)
BEGIN
    DECLARE fieldmask text default '';
    DECLARE i integer default 0;
    DECLARE length integer default JSON_LENGTH(p_jsonformat, CONCAT(p_path,'.paths'));
    WHILE i < length DO
        IF fieldmask = '' THEN
            SET fieldmask = _myproto_snake_case_to_lower_camel_case(JSON_UNQUOTE(JSON_EXTRACT(p_jsonformat, CONCAT(p_path,'.paths[', i, ']'))));
        ELSE
            SET fieldmask = CONCAT(fieldmask, ',', _myproto_snake_case_to_lower_camel_case(JSON_UNQUOTE(JSON_EXTRACT(p_jsonformat, CONCAT(p_path,'.paths[', i, ']')))));
        END IF;
        SET i = i + 1;
    END WHILE;
    SET p_jsonformat = JSON_REPLACE(p_jsonformat, p_path, fieldmask);
END;
//

CREATE PROCEDURE _myproto_json_post_process_wrapper_type(INOUT p_jsonformat JSON, IN p_path text)
BEGIN
    SET p_jsonformat = JSON_REPLACE(p_jsonformat, p_path, JSON_EXTRACT(p_jsonformat, CONCAT(p_path,'.value')));
END;
//

CREATE PROCEDURE _myproto_json_add_value(INOUT p_jsonformat JSON, IN p_path text, IN p_field_number integer, IN p_field_name text, IN p_field_json_name text, IN p_repeated boolean, IN p_value JSON, OUT p_new_path text)
BEGIN
    DECLARE name text default IFNULL(p_field_json_name, IFNULL(p_field_name, CONCAT('"',p_field_number, '"')));
    DECLARE path text default CONCAT(REVERSE(p_path), '.', name);
    DECLARE existing_object_or_array JSON default JSON_EXTRACT(p_jsonformat, path);
    IF JSON_TYPE(existing_object_or_array) IS NULL AND p_repeated AND JSON_TYPE(p_value) = 'ARRAY' THEN
        SET p_jsonformat = JSON_SET(p_jsonformat, path, p_value);
        SET p_new_path = REVERSE(CONCAT(path, '[',JSON_LENGTH(p_value)-1,']'));
    ELSEIF JSON_TYPE(existing_object_or_array) IS NULL AND p_repeated THEN
        SET p_jsonformat = JSON_SET(p_jsonformat, path, JSON_ARRAY(p_value));
        SET p_new_path = REVERSE(CONCAT(path, '[0]'));
    ELSEIF JSON_TYPE(existing_object_or_array) IS NULL AND NOT p_repeated THEN
        SET p_jsonformat = JSON_SET(p_jsonformat, path, p_value);
        SET p_new_path = REVERSE(path);
    ELSEIF JSON_TYPE(existing_object_or_array) = 'ARRAY' AND JSON_TYPE(p_value) = 'ARRAY' THEN
        SET p_jsonformat = JSON_SET(p_jsonformat, path, JSON_MERGE_PRESERVE(existing_object_or_array, p_value));
        SET p_new_path = REVERSE(CONCAT(path, '[', JSON_LENGTH(p_jsonformat, path)-1, ']'));
    ELSEIF JSON_TYPE(existing_object_or_array) = 'ARRAY' THEN
        SET p_jsonformat = JSON_ARRAY_APPEND(p_jsonformat, path, p_value);
        SET p_new_path = REVERSE(CONCAT(path, '[', JSON_LENGTH(p_jsonformat, path)-1, ']'));
    ELSEIF JSON_TYPE(p_value) = 'ARRAY' THEN
        SET p_jsonformat = JSON_SET(p_jsonformat, path, JSON_ARRAY_APPEND(p_value, '$', existing_object_or_array));
        SET p_new_path = REVERSE(CONCAT(path, '[', JSON_LENGTH(p_jsonformat, path)-1, ']'));
    ELSE
        SET p_jsonformat = JSON_REPLACE(p_jsonformat, path, JSON_ARRAY(existing_object_or_array, p_value));
        SET p_new_path = REVERSE(CONCAT(path, '[1]'));
    END IF;

END;
//

CREATE PROCEDURE _myproto_add_path_to_post_process(INOUT p_post_process_paths JSON, IN p_path text, IN p_depth integer, IN p_field_type text, IN p_message_type text)
BEGIN
    DECLARE paths JSON;
    WHILE JSON_LENGTH(p_post_process_paths) <= p_depth DO
        SET p_post_process_paths = JSON_ARRAY_APPEND(p_post_process_paths, '$', JSON_OBJECT());
    END WHILE;

    SET paths = JSON_EXTRACT(p_post_process_paths, CONCAT('$[', p_depth, ']'));
    IF p_field_type = 'PROBABLY_MAP' THEN
        SET paths = JSON_MERGE_PATCH(paths, JSON_OBJECT(reverse(SUBSTRING(p_path, LOCATE('[', p_path)+1)), 'PROBABLY_MAP'));
        SET p_post_process_paths = JSON_REPLACE(p_post_process_paths, CONCAT('$[', p_depth, ']'), paths);
    ELSEIF p_message_type IN (
        '.google.protobuf.Timestamp',
        '.google.protobuf.Duration',
        '.google.protobuf.Any',
        '.google.protobuf.Struct',
        '.google.protobuf.Value',
        '.google.protobuf.ListValue',
        '.google.protobuf.NullValue',
        '.google.protobuf.FieldMask',
        '.google.protobuf.DoubleValue',
        '.google.protobuf.FloatValue',
        '.google.protobuf.Int64Value',
        '.google.protobuf.UInt64Value',
        '.google.protobuf.Int32Value',
        '.google.protobuf.UInt32Value',
        '.google.protobuf.BoolValue',
        '.google.protobuf.StringValue',
        '.google.protobuf.BytesValue'
                             ) THEN
        SET paths = JSON_MERGE_PATCH(paths, JSON_OBJECT(reverse(p_path), p_message_type));
        SET p_post_process_paths = JSON_REPLACE(p_post_process_paths, CONCAT('$[', p_depth, ']'), paths);
    END IF;
END;
//

CREATE PROCEDURE _myproto_json_post_process_paths_at_same_depth(INOUT p_jsonformat JSON, IN p_paths_and_types JSON)
BEGIN
    DECLARE paths JSON default JSON_KEYS(p_paths_and_types);
    DECLARE i integer default 0;
    DECLARE length integer default JSON_LENGTH(paths);
    DECLARE path, field_type text;
    WHILE i < length DO
        SET path = JSON_UNQUOTE(JSON_EXTRACT(paths, CONCAT('$[',i,']')));
        SET field_type = JSON_UNQUOTE(JSON_EXTRACT(p_paths_and_types, CONCAT('$."',path,'"')));
        CASE field_type
            WHEN 'PROBABLY_MAP' THEN
                CALL _myproto_json_convert_map_entries(p_jsonformat, path);
            WHEN '.google.protobuf.Timestamp' THEN
                CALL _myproto_json_post_process_timestamp(p_jsonformat, path);
            WHEN '.google.protobuf.Duration' THEN
                CALL _myproto_json_post_process_duration(p_jsonformat, path);
            WHEN '.google.protobuf.Any' THEN
                CALL _myproto_json_post_process_any(p_jsonformat, path);
            WHEN '.google.protobuf.Struct' THEN
                CALL _myproto_json_post_process_struct(p_jsonformat, path);
            WHEN '.google.protobuf.Value' THEN
                CALL _myproto_json_post_process_value(p_jsonformat, path);
            WHEN '.google.protobuf.ListValue' THEN
                CALL _myproto_json_post_process_listvalue(p_jsonformat, path);
            WHEN '.google.protobuf.NullValue' THEN
                CALL _myproto_json_post_process_nullvalue(p_jsonformat, path);
            WHEN '.google.protobuf.FieldMask' THEN
                CALL _myproto_json_post_process_fieldmask(p_jsonformat, path);
            ELSE
                CALL _myproto_json_post_process_wrapper_type(p_jsonformat, path);
        END CASE;
        SET i = i + 1;
    END WHILE;
END;
//

CREATE PROCEDURE _myproto_json_post_process_maps_and_well_known_types(INOUT p_jsonformat JSON, IN p_post_process_paths JSON)
BEGIN
    DECLARE depth integer default JSON_LENGTH(p_post_process_paths);
    DECLARE p_paths_and_types JSON;
    WHILE depth >= 0 DO
        SET p_paths_and_types = JSON_EXTRACT(p_post_process_paths, CONCAT('$[',depth,']'));
        CALL _myproto_json_post_process_paths_at_same_depth(p_jsonformat, p_paths_and_types);
        SET depth = depth - 1;
    END WHILE;
END;
//

CREATE FUNCTION _myproto_jsonformat(p_message JSON) returns JSON deterministic
BEGIN
    DECLARE length integer DEFAULT JSON_LENGTH(p_message);
    DECLARE i, depth, previous_depth integer default 0;
    DECLARE jsonformat JSON default JSON_OBJECT();
    DECLARE path, field_path text default '$';
    DECLARE next_element text default CONCAT('$[',i,']');
    DECLARE type text;
    DECLARE field_number integer;
    DECLARE repeated boolean;
    DECLARE field_name, field_type, field_json_name, field_type_name, message_type text;
    DECLARE value JSON;
    DECLARE post_process_paths JSON default JSON_OBJECT();
    WHILE i < length DO
        SET type = cast(JSON_UNQUOTE(JSON_EXTRACT(p_message, CONCAT(next_element,'.type'))) as char);
        SET depth = JSON_EXTRACT(p_message, CONCAT(next_element, '.depth'));
        SET field_number = JSON_EXTRACT(p_message, CONCAT(next_element, '.field_number'));
        SET repeated = cast(JSON_EXTRACT(p_message, CONCAT(next_element, '.repeated')) as unsigned) = 1;
        SET field_name = _myproto_unquote(JSON_EXTRACT(p_message, CONCAT(next_element, '.field_name')));
        SET field_type = _myproto_unquote(JSON_EXTRACT(p_message, CONCAT(next_element, '.field_type')));
        SET field_type_name = _myproto_unquote(JSON_EXTRACT(p_message, CONCAT(next_element, '.field_type_name')));
        SET field_json_name = _myproto_unquote(JSON_EXTRACT(p_message, CONCAT(next_element, '.field_json_name')));
        IF type = 'end message' THEN
            SET message_type = _myproto_unquote(JSON_EXTRACT(p_message, CONCAT(next_element, '.message_type')));
            CALL _myproto_add_path_to_post_process(post_process_paths, path, depth, field_type, message_type);
            SET path = SUBSTRING(path, LOCATE('.', path)+1);
        ELSEIF type = 'field' THEN
            SET value = JSON_EXTRACT(p_message, CONCAT(next_element, '.value'));
            CALL _myproto_json_add_value(jsonformat, path, field_number, field_name, field_json_name, repeated, value, field_path);
            CALL _myproto_add_path_to_post_process(post_process_paths, field_path, depth, field_type, field_type_name);
        ELSE
            CALL _myproto_json_add_value(jsonformat, path, field_number, field_name, field_json_name, repeated, JSON_OBJECT(), path);
        END IF;

        SET previous_depth = depth;
        SET i = i+1;
        SET next_element = CONCAT('$[',i,']');
    END WHILE;
    CALL _myproto_json_post_process_maps_and_well_known_types(jsonformat, post_process_paths);

    RETURN jsonformat;
END;
//

CREATE FUNCTION myproto_decode_to_textformat(p_bytes blob, p_message_type text, p_protos JSON) returns text deterministic
BEGIN
    RETURN _myproto_textformat(_myproto_flatten_message(p_bytes, p_message_type, p_protos));
END;
//

CREATE FUNCTION myproto_decode_to_jsonformat(p_bytes blob, p_message_type text, p_protos JSON) returns JSON deterministic
BEGIN
    RETURN _myproto_jsonformat(_myproto_flatten_message(p_bytes, p_message_type, p_protos));
END;
//