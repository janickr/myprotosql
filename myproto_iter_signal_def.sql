

delimiter //
create function _myproto_unquote(p_json_string_or_null JSON) returns varchar(1000) deterministic
    BEGIN
        IF JSON_TYPE(p_json_string_or_null) = 'NULL' THEN
            RETURN NULL;
        ELSE
            RETURN JSON_UNQUOTE(p_json_string_or_null);
        END IF;
    END;
//


CREATE PROCEDURE var_int(IN p_bytes varbinary(10000), INOUT p_offset integer, IN p_limit integer, OUT p_result bigint unsigned)
BEGIN
  DECLARE error_text varchar(128) default CONCAT('VarInt at offset ', p_offset, ' exceeds limit set by LEN ', p_limit);
  DECLARE next varbinary(10000);
  DECLARE shift, count integer;
  DECLARE b integer(1);
    -- todo janick max varint bytes check
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
        SET MESSAGE_TEXT = error_text;
  ELSE
    SET p_offset = p_offset + count;
  END IF;
END;
//

CREATE PROCEDURE get_fixed_number_value(IN p_bytes varbinary(10000), INOUT p_offset integer, IN p_nb_bytes integer, OUT p_value bigint unsigned)
BEGIN
  DECLARE next varbinary(10000) DEFAULT substr(p_bytes, p_offset);
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

CREATE PROCEDURE get_i32_value(IN p_bytes varbinary(10000), INOUT p_offset integer, IN p_limit integer, OUT p_value bigint unsigned)
  BEGIN
    DECLARE error_text varchar(128) default CONCAT('i32 at offset ', p_offset, ' exceeds limit set by LEN ', p_limit);

    IF p_offset + 4 > p_limit THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = error_text;
    ELSE
        CALL get_fixed_number_value(p_bytes, p_offset, 4, p_value);
    END IF;
  END;
//

CREATE PROCEDURE get_i64_value(IN p_bytes varbinary(10000), INOUT p_offset integer, IN p_limit integer, OUT p_value bigint unsigned)
  BEGIN
    DECLARE error_text varchar(128) default CONCAT('i64 at offset ', p_offset, ' exceeds limit set by LEN ', p_limit);

    IF p_offset + 8 > p_limit THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = error_text;
    ELSE
        CALL get_fixed_number_value(p_bytes, p_offset, 8, p_value);
    END IF;
  END;
//

CREATE PROCEDURE get_len_value(IN p_bytes varbinary(10000), INOUT p_offset integer, IN p_limit integer, OUT p_value JSON)
BEGIN
  DECLARE length integer;
  CALL var_int(p_bytes, p_offset, p_limit, length);
  -- todo length should be within the limit
  SET p_value = JSON_QUOTE(cast(substr(p_bytes, p_offset, length) as char));
  SET p_offset = p_offset + length;
END;
//

CREATE PROCEDURE _myproto_get_field_value(IN p_bytes varbinary(10000), INOUT p_offset integer, IN p_limit integer, IN p_wiretype integer, OUT p_value JSON)
BEGIN
  DECLARE error_text varchar(128) default CONCAT('Invalid wiretype ', p_wiretype);

  DECLARE varint integer;
  CASE p_wiretype
      WHEN 0 THEN
        CALL var_int(p_bytes, p_offset, p_limit, varint);
        SET p_value = cast(varint as JSON);
      WHEN 1 THEN
        CALL get_i64_value(p_bytes, p_offset, p_limit, p_value);
      WHEN 5 THEN
        CALL get_i32_value(p_bytes, p_offset, p_limit, p_value);
      WHEN 2 THEN
        CALL get_len_value(p_bytes, p_offset, p_limit, p_value);
      ELSE
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = error_text;
    END CASE;
END;
//

CREATE PROCEDURE _myproto_interpret_varint_value(IN p_field_type varchar(1000), IN p_int bigint unsigned, OUT p_value JSON)
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
            SET p_value = cast(cast((p_int >> 1 ^ (-(p_int & 1))) as signed) as JSON);
          WHEN 'TYPE_SINT64' THEN
            SET p_value = cast(cast((p_int >> 1 ^ (-(p_int & 1))) as signed) as JSON);
          WHEN 'TYPE_BOOL' THEN
            SET p_value = cast((p_int & 1)=1 as JSON);
          ELSE
            SIGNAL SQLSTATE '45000'
                SET MESSAGE_TEXT = error_text;
      END CASE;
  END IF;
END;
//

CREATE function _myproto_reinterpret_as_float(i integer unsigned) returns JSON deterministic
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
        SET result = -0.0;
        RETURN cast(result as JSON );
    ELSEIF exponent_biased = 0 and mantissa = 0 and sign = 0 THEN
        SET result = 0.0;
        RETURN cast(result as JSON );
    ELSEIF exponent_biased = 0 and sign = 1 THEN
        SET result = -mantissa * pow(2, -149);
        RETURN cast(result as JSON );
    ELSEIF exponent_biased = 0 and sign = 0 THEN
        SET result = mantissa * pow(2, -149);
        RETURN cast(result as JSON );
    ELSEIF sign = 1 THEN
        SET result = -significand * pow(2, exponent_unbiased-23);
        RETURN cast(result as JSON );
    ELSEIF sign = 0 THEN
        SET result = significand * pow(2, exponent_unbiased-23);
        RETURN cast(result as JSON );
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
        SET result = -0.0;
        RETURN cast(result as JSON );
    ELSEIF exponent_biased = 0 and mantissa = 0 and sign = 0 THEN
        SET result = 0.0;
        RETURN cast(result as JSON );
    ELSEIF exponent_biased = 0 and sign = 1 THEN
        SET result = -mantissa * pow(2, -1074);
        RETURN cast(result as JSON );
    ELSEIF exponent_biased = 0 and sign = 0 THEN
        SET result = mantissa * pow(2, -1074);
        RETURN cast(result as JSON );
    ELSEIF sign = 1 THEN
        SET result = -significand * pow(2, exponent_unbiased-52);
        RETURN cast(result as JSON );
    ELSEIF sign = 0 THEN
        SET result = significand * pow(2, exponent_unbiased-52);
        RETURN cast(result as JSON );
    END IF;
end;
//


CREATE PROCEDURE _myproto_interpret_int64_value(IN p_field_type varchar(1000), IN p_int bigint unsigned, OUT p_value JSON)
BEGIN
  DECLARE error_text varchar(128) default CONCAT('Illegal type for int64 ', p_field_type);

  IF p_field_type IS NULL THEN
      SET p_value = cast(p_int as JSON);
  ELSE
      CASE p_field_type
          WHEN 'TYPE_FIXED64' THEN
            SET p_value = cast(cast(p_int as unsigned) as JSON);
          WHEN 'TYPE_SFIXED64' THEN
            SET p_value = cast(cast(((p_int >> 1) ^ (-(p_int & 1))) as signed) as JSON);
          WHEN 'TYPE_DOUBLE' THEN
            SET p_value = _myproto_reinterpret_as_double(p_int);
          ELSE
            SIGNAL SQLSTATE '45000'
                SET MESSAGE_TEXT = error_text;
      END CASE;
  END IF;
END;
//

CREATE PROCEDURE _myproto_interpret_int32_value(IN p_field_type varchar(1000), IN p_int integer unsigned, OUT p_value JSON)
BEGIN
  DECLARE error_text varchar(128) default CONCAT('Illegal type for int32 ', p_field_type);

  IF p_field_type IS NULL THEN
      SET p_value = cast(p_int as JSON);
  ELSE
      CASE p_field_type
          WHEN 'TYPE_FIXED32' THEN
            SET p_value = cast(cast(p_int as unsigned) as JSON);
          WHEN 'TYPE_SFIXED32' THEN
            SET p_value = cast(cast(((p_int >> 1) ^ (-(p_int & 1))) as signed) as JSON);
          WHEN 'TYPE_FLOAT' THEN
            SET p_value = _myproto_reinterpret_as_float(p_int);
          ELSE
            SIGNAL SQLSTATE '45000'
                SET MESSAGE_TEXT = error_text;
      END CASE;
  END IF;
END;
//

CREATE PROCEDURE _myproto_get_number_field_value(IN p_bytes varbinary(10000), INOUT p_offset integer, IN p_limit integer, IN p_wiretype integer, OUT p_value JSON, IN p_field_type varchar(1000))
BEGIN
  DECLARE error_text varchar(128) default CONCAT('Invalid wiretype ', p_wiretype);

  DECLARE int_result bigint unsigned;
  CASE p_wiretype
      WHEN 0 THEN
        CALL var_int(p_bytes, p_offset, p_limit, int_result);
        CALL _myproto_interpret_varint_value(p_field_type, int_result, p_value);
      WHEN 1 THEN
        CALL get_i64_value(p_bytes, p_offset, p_limit, int_result);
        CALL _myproto_interpret_int64_value(p_field_type, int_result, p_value);
      WHEN 5 THEN
        CALL get_i32_value(p_bytes, p_offset, p_limit, int_result);
        CALL _myproto_interpret_int32_value(p_field_type, int_result, p_value);
      ELSE
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = error_text;
    END CASE;
END;
//


CREATE PROCEDURE _myproto_push_frame(
    INOUT p_stack JSON,
    IN p_offset integer,
    IN p_limit integer,
    INOUT p_path varchar(1000),
    IN p_field_number integer,
    IN p_field_name varchar(1000),
    INOUT p_message_type varchar(1000),
    IN p_sub_message_type varchar(1000))
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
                  'message_type', p_message_type
                ));
        SET p_message_type = p_sub_message_type;
        IF (p_field_number) THEN
            SET p_path = CONCAT(p_path, '.', p_field_number);
        END IF;
    END;
//

CREATE PROCEDURE _myproto_pop_frame_and_reset(
    INOUT p_stack JSON,
    OUT p_offset integer,
    OUT p_limit integer,
    OUT p_path varchar(1000),
    OUT p_field_number integer,
    OUT p_field_name varchar(1000),
    OUT p_message_type varchar(1000))
    BEGIN
        SET p_offset = JSON_EXTRACT(p_stack, '$[0].offset');
        SET p_limit = JSON_EXTRACT(p_stack, '$[0].limit');
        SET p_path = _myproto_unquote(JSON_EXTRACT(p_stack, '$[0].path'));
        SET p_field_number = JSON_EXTRACT(p_stack, '$[0].field_number');
        SET p_stack = JSON_REMOVE(p_stack, '$[0]');
        SET p_field_name = _myproto_unquote(JSON_EXTRACT(p_stack, '$[0].field_name'));
        SET p_message_type = _myproto_unquote(JSON_EXTRACT(p_stack, '$[0].message_type'));
    END;
//

CREATE PROCEDURE _myproto_pop_frame(
    INOUT p_stack JSON,
    OUT p_limit integer,
    OUT p_path varchar(1000),
    OUT p_field_number integer,
    OUT p_field_name varchar(1000),
    OUT p_message_type varchar(1000))
    BEGIN
        SET p_limit = JSON_EXTRACT(p_stack, '$[0].limit');
        SET p_path = _myproto_unquote(JSON_EXTRACT(p_stack, '$[0].path'));
        SET p_field_number = JSON_EXTRACT(p_stack, '$[0].field_number');
        SET p_stack = JSON_REMOVE(p_stack, '$[0]');
        SET p_field_name = _myproto_unquote(JSON_EXTRACT(p_stack, '$[0].field_name'));
        SET p_message_type = _myproto_unquote(JSON_EXTRACT(p_stack, '$[0].message_type'));
    END;
//

CREATE FUNCTION _myproto_is_frame_field(p_stack JSON, p_field integer) returns boolean deterministic
    RETURN JSON_EXTRACT(p_stack, '$[0].field') = p_field;
//

CREATE PROCEDURE _myproto_get_field_and_wiretype(IN p_bytes varbinary(10000), INOUT p_offset integer, IN p_limit integer, OUT p_field_number integer, OUT p_wiretype integer)
BEGIN
  DECLARE field_wiretype integer;

  CALL var_int(p_bytes, p_offset, p_limit, field_wiretype);
  SET p_wiretype = field_wiretype & 0x07;
  SET p_field_number = (field_wiretype >> 3) & 0x1f;
END;
//

CREATE PROCEDURE _myproto_len_limit(IN p_bytes varbinary(10000), INOUT p_offset integer, INOUT p_limit integer)
BEGIN
  DECLARE value integer;
  CALL var_int(p_bytes, p_offset, p_limit, value);
  -- todo raise when new limit > old limit
  SET p_limit = p_offset + value;
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

CREATE PROCEDURE _myproto_append_path_value(INOUT p_message JSON, IN p_depth integer, IN p_parent_path varchar(1000), IN p_field_number integer, IN p_field_name varchar(1000), IN p_field_type varchar(1000), IN p_value JSON)
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
                'field_type', p_field_type,
                'value', p_value
            ));
END;
//

CREATE PROCEDURE _myproto_append_start_submessage(INOUT p_message JSON, IN p_depth integer, IN p_parent_path varchar(1000), IN p_field_number integer, IN p_field_name varchar(1000), IN p_message_type varchar(1000))
BEGIN
    SET p_message = JSON_ARRAY_APPEND(
            p_message,
            '$',
            JSON_OBJECT(
                'type', 'message',
                'depth', p_depth,
                'path', p_parent_path,
                'field_number', p_field_number,
                'field_name', p_field_name,
                'message_type', p_message_type
            ));
END;
//

CREATE FUNCTION _myproto_is_start_submessage(p_message JSON, last_element varchar(50), p_depth integer, p_parent_path varchar(1000), p_field_number integer) RETURNS boolean deterministic
BEGIN
    RETURN (cast(JSON_UNQUOTE(JSON_EXTRACT(p_message, CONCAT(last_element, '.type'))) as char) = 'object'
        AND JSON_EXTRACT(p_message, CONCAT(last_element, '.depth')) = p_depth
        AND cast(JSON_UNQUOTE(JSON_EXTRACT(p_message, CONCAT(last_element, '.path'))) as char) = p_parent_path
        AND JSON_EXTRACT(p_message, CONCAT(last_element, '.field')) = p_field_number);
END
//

CREATE PROCEDURE _myproto_undo_appended_fields(INOUT p_message JSON, IN p_depth integer, IN p_parent_path varchar(1000), IN p_field_number integer)
BEGIN
    DECLARE length integer DEFAULT JSON_LENGTH(p_message)-1;
    DECLARE last_element varchar(50) DEFAULT CONCAT('$[',length,']');
    WHILE NOT _myproto_is_start_submessage(p_message, last_element, p_depth, p_parent_path, p_field_number) AND length > 1 DO
        SET p_message = JSON_REMOVE(p_message, last_element);
        SET length = length-1;
    END WHILE;
    SET p_message = JSON_REMOVE(p_message, CONCAT('$[',length,']'));
END;
//

CREATE PROCEDURE _myproto_validate_wiretype_and_field_type(
    IN p_message_type varchar(1000),
    IN p_field_number integer,
    IN p_wiretype integer,
    IN p_field_type varchar(1000))
BEGIN
  DECLARE error_text varchar(128) default CONCAT('Invalid wiretype ', p_wiretype, ' for ', p_message_type, ' field ', p_field_number, ' ', p_field_type);

  IF NOT(
      (p_wiretype = 0 AND p_field_type IN ('TYPE_INT32', 'TYPE_INT64', 'TYPE_UINT32', 'TYPE_UINT64', 'TYPE_SINT32', 'TYPE_SINT64', 'TYPE_BOOL', 'TYPE_ENUM'))
      OR (p_wiretype = 1 AND p_field_type IN ('TYPE_FIXED64', 'TYPE_SFIXED64', 'TYPE_DOUBLE'))
      OR (p_wiretype = 2 AND p_field_type IN ('TYPE_STRING', 'TYPE_BYTES', 'TYPE_MESSAGE'))
      OR (p_wiretype = 3 AND p_field_type = 'TYPE_GROUP')
      OR (p_wiretype = 4 AND p_field_type = 'TYPE_GROUP')
      OR (p_wiretype = 5 AND p_field_type IN ('TYPE_FIXED32', 'TYPE_SFIXED32', 'TYPE_FLOAT'))
      ) THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = error_text;
  END IF;
END;
//

CREATE PROCEDURE _myproto_get_field_properties(
    IN p_message_type varchar(1000),
    IN p_field_number integer,
    IN p_wiretype integer,
    IN p_protos JSON,
    OUT p_field_type varchar(1000),
    OUT p_field_name varchar(1000),
    OUT p_sub_message_type varchar(1000))
BEGIN
    SET p_field_type = JSON_UNQUOTE(JSON_EXTRACT(p_protos, CONCAT('$."', p_message_type, '".fields."', p_field_number, '".type')));
    SET p_field_name = JSON_UNQUOTE(JSON_EXTRACT(p_protos, CONCAT('$."', p_message_type, '".fields."', p_field_number, '".name')));
    SET p_sub_message_type = JSON_UNQUOTE(JSON_EXTRACT(p_protos, CONCAT('$."', p_message_type, '".fields."', p_field_number, '".typeName')));
    CALL _myproto_validate_wiretype_and_field_type(p_message_type, p_field_number, p_wiretype, p_field_type);
END;
//

CREATE FUNCTION _myproto_flatten_message(p_bytes varbinary(10000), p_message_type varchar(1000), p_protos JSON) returns JSON deterministic
BEGIN
  DECLARE offset integer default 1;
  DECLARE field_number, wiretype integer;
  DECLARE p_limit, m_limit integer default length(p_bytes)+1;
  DECLARE message, stack, value JSON;
  DECLARE parent_path varchar(1000) default '$';
  DECLARE message_type varchar(1000) default '';
  DECLARE sub_message_type, field_type, field_name varchar(1000) default p_message_type;
  DECLARE decode_raw boolean default p_message_type IS NULL;

  SET stack = JSON_ARRAY();
  CALL _myproto_push_frame(stack, offset, m_limit, parent_path, 0, null, message_type, sub_message_type);
  SET message = JSON_ARRAY();

   WHILE offset < p_limit DO
      BEGIN
        DECLARE CONTINUE HANDLER FOR SQLSTATE '45000'
        BEGIN
            -- check if stack > 1, if not there is a bug
            -- resignal if not decode raw
            CALL _myproto_pop_frame_and_reset(stack, offset,m_limit, parent_path, field_number, field_name, message_type);
            CALL _myproto_undo_appended_fields(message, JSON_LENGTH(stack)-1, parent_path, field_number);
            CALL get_len_value(p_bytes, offset, m_limit, value);
            CALL _myproto_append_path_value(message, JSON_LENGTH(stack)-1, parent_path, field_number, field_name, field_type, value);
        END;

        CALL _myproto_get_field_and_wiretype(p_bytes, offset, m_limit, field_number, wiretype);
        CALL _myproto_get_field_properties(message_type, field_number, wiretype, p_protos, field_type, field_name, sub_message_type);

        IF _myproto_wiretype_len(wiretype) THEN
            IF field_type = 'TYPE_MESSAGE' OR decode_raw THEN
                CALL _myproto_append_start_submessage(message, JSON_LENGTH(stack)-1, parent_path, field_number, field_name, message_type);
                CALL _myproto_push_frame(stack, offset, m_limit, parent_path, field_number, field_name, message_type, sub_message_type);
                CALL _myproto_len_limit(p_bytes, offset, m_limit);
            ELSE
                CALL get_len_value(p_bytes, offset, m_limit, value);
                CALL _myproto_append_path_value(message, JSON_LENGTH(stack)-1, parent_path, field_number, field_name, field_type, value);
            END IF;
        ELSEIF _myproto_wiretype_sgroup(wiretype) THEN
            CALL _myproto_append_start_submessage(message, JSON_LENGTH(stack)-1, parent_path, field_number, field_name, message_type);
            CALL _myproto_push_frame(stack, offset, m_limit, parent_path, field_number, field_name, message_type, sub_message_type);
            CALL _myproto_len_limit(p_bytes, offset, m_limit);
        ELSEIF _myproto_wiretype_egroup(wiretype) THEN
            IF _myproto_is_frame_field(stack, field_number) THEN
                CALL _myproto_pop_frame(stack, m_limit, parent_path, field_number, field_name, message_type);
            ELSE
                SIGNAL SQLSTATE '45000'
                    SET MESSAGE_TEXT = 'Malformed message';
            END IF;
        ELSE
            CALL _myproto_get_number_field_value(p_bytes, offset, m_limit, wiretype, value, field_type);
            CALL _myproto_append_path_value(message, JSON_LENGTH(stack)-1, parent_path, field_number, field_name, field_type,value );
        END IF;

        IF offset = m_limit THEN
            CALL _myproto_pop_frame(stack, m_limit, parent_path, field_number, field_name, message_type);
        END IF;
    END;
  END WHILE;

  return message;
END;
//


CREATE procedure _p_myproto_flatten_message(p_bytes varbinary(10000))
BEGIN
  DECLARE offset integer default 1;
  DECLARE field_number, wiretype, egroup_field_number integer;
  DECLARE p_limit, m_limit integer default length(p_bytes)+1;
  DECLARE message, stack, value JSON;
  DECLARE parent_path varchar(1000) default '';

  SET stack = JSON_ARRAY();
  CALL _myproto_push_frame(stack, offset, m_limit, parent_path, NULL);
  SET message = JSON_ARRAY();

  WHILE offset < p_limit DO
      BEGIN
        DECLARE CONTINUE HANDLER FOR SQLSTATE '45000'
        BEGIN
            select 'error', stack, offset,m_limit, parent_path, field_number;
            CALL _myproto_pop_frame_and_reset(stack, offset,m_limit, parent_path, field_number);
            CALL _myproto_undo_appended_fields(message, JSON_LENGTH(stack)-1, parent_path, field_number);
            select 'popped', message, stack;
            CALL get_len_value(p_bytes, offset, m_limit, value);
            CALL _myproto_append_path_value(message, JSON_LENGTH(stack)-1, parent_path, field_number, value);
            select 'appended', message;
        END;

        CALL _myproto_get_field_and_wiretype(p_bytes, offset, m_limit, field_number, wiretype);

        IF _myproto_wiretype_len(wiretype) OR _myproto_wiretype_sgroup(wiretype) THEN
            CALL _myproto_append_start_submessage(message, JSON_LENGTH(stack)-1, parent_path, field_number);
            CALL _myproto_push_frame(stack, offset, m_limit, parent_path, field_number);
            CALL _myproto_len_limit(p_bytes, offset, m_limit);
            select 'sub', message, stack;
        ELSEIF _myproto_wiretype_egroup(wiretype) THEN
            IF _myproto_is_frame_field(stack, field_number) THEN
                CALL _myproto_pop_frame(stack, m_limit, parent_path, field_number);
            ELSE
                SIGNAL SQLSTATE '45000'
                    SET MESSAGE_TEXT = 'Malformed message';
            END IF;
            select 'egroup', message, stack;
        ELSE
            CALL _myproto_get_field_value(p_bytes, offset, m_limit, wiretype, value);
            CALL _myproto_append_path_value(message, JSON_LENGTH(stack)-1, parent_path, field_number, value);
        END IF;
    END;
  END WHILE;

  select message;
END;
//
