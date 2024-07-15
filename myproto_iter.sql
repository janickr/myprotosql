DROP PROCEDURE IF EXISTS var_int;
DROP PROCEDURE IF EXISTS get_fixed_number_value;
DROP PROCEDURE IF EXISTS get_i32_value;
DROP PROCEDURE IF EXISTS get_i64_value;
DROP PROCEDURE IF EXISTS get_len_value;
DROP PROCEDURE IF EXISTS _myproto_get_field_value;
DROP PROCEDURE IF EXISTS _myproto_push_frame;
DROP PROCEDURE IF EXISTS _myproto_pop_frame_and_reset;
DROP PROCEDURE IF EXISTS _myproto_pop_frame;
DROP PROCEDURE IF EXISTS _myproto_get_field_and_wiretype;
DROP PROCEDURE IF EXISTS _myproto_len_limit;
DROP FUNCTION IF EXISTS _myproto_wiretype_len;
DROP FUNCTION IF EXISTS _myproto_wiretype_sgroup;
DROP FUNCTION IF EXISTS _myproto_wiretype_egroup;
DROP PROCEDURE IF EXISTS _myproto_append_path_value;
DROP FUNCTION IF EXISTS _myproto_flatten_message;
DROP PROCEDURE IF EXISTS _p_myproto_flatten_message;

delimiter //

CREATE PROCEDURE var_int(IN p_bytes varbinary(10000), INOUT p_offset integer, IN p_limit integer, OUT p_result integer, OUT p_error varchar(512))
BEGIN
  DECLARE next varbinary(10000);
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
    SET p_error = 'VarInt exceeds LEN '+ p_limit;
  ELSE
    SET p_offset = p_offset + count;
  END IF;
END;
//

CREATE PROCEDURE get_fixed_number_value(IN p_bytes varbinary(10000), INOUT p_offset integer, IN p_nb_bytes integer, OUT p_value JSON)
BEGIN
  DECLARE next varbinary(10000) DEFAULT substr(p_bytes, p_offset);
  DECLARE result long default 0;
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
  SET p_offset = p_offset + p_bytes;
END
//

CREATE PROCEDURE get_i32_value(IN p_bytes varbinary(10000), INOUT p_offset integer, IN p_limit integer, OUT p_value JSON, OUT p_error varchar(512))
  IF p_offset + 4 > p_limit THEN
    SET p_error = 'i32 exceeds LEN '+ p_limit;
  ELSE
    CALL get_fixed_number_value(p_bytes, p_offset, 4, p_value);
  END IF;
//

CREATE PROCEDURE get_i64_value(IN p_bytes varbinary(10000), INOUT p_offset integer, IN p_limit integer, OUT p_value JSON, OUT p_error varchar(512))
  IF p_offset + 8 > p_limit THEN
    SET p_error = 'i64 exceeds LEN '+ p_limit;
  ELSE
    CALL get_fixed_number_value(p_bytes, p_offset, 8, p_value);
  END IF;
//

CREATE PROCEDURE get_len_value(p_bytes varbinary(10000), p_offset integer, p_limit integer, OUT p_value JSON, OUT p_error varchar(512))
BEGIN
  DECLARE length integer;

  CALL var_int(p_bytes, p_offset, p_limit, length, p_error);
  SET p_value = substr(p_bytes, p_offset, length);
  SET p_offset = p_offset + length;
END;
//

CREATE PROCEDURE _myproto_get_field_value(IN p_bytes varbinary(10000), INOUT p_offset integer, IN p_limit integer, IN p_wiretype integer, OUT p_value JSON, OUT p_error varchar(512))
BEGIN
    DECLARE varint integer;
  CASE p_wiretype
      WHEN 0 THEN
        CALL var_int(p_bytes, p_offset, p_limit, varint, p_error);
        SET p_value = cast(varint as JSON);
      WHEN 1 THEN
        CALL get_i64_value(p_bytes, p_offset, p_limit, p_value, p_error);
      WHEN 5 THEN
        CALL get_i32_value(p_bytes, p_offset, p_limit, p_value, p_error);
      WHEN 2 THEN
        CALL get_len_value(p_bytes, p_offset, p_limit, p_value, p_error);
      ELSE
        SET p_error = 'Invalid wiretype: '+p_wiretype;
    END CASE;
END;
//


CREATE PROCEDURE _myproto_push_frame(INOUT p_stack JSON, IN p_offset integer, IN p_limit integer, IN p_path varchar(1000))
    BEGIN
        SET p_stack = JSON_ARRAY_INSERT(
                p_stack,
                '$[0]',
                JSON_OBJECT(
                  'offset', p_offset,
                  'limit', p_limit,
                  'path', p_path
                ));
    END;
//

CREATE PROCEDURE _myproto_pop_frame_and_reset(INOUT p_stack JSON, OUT p_offset integer, OUT p_limit integer, OUT p_path varchar(1000))
    BEGIN
        SET p_offset = JSON_EXTRACT(p_stack, '$[0].offset');
        SET p_limit = JSON_EXTRACT(p_stack, '$[0].limit');
        SET p_path = JSON_EXTRACT(p_stack, '$[0].path');
        SET p_stack = JSON_REMOVE(p_stack, '$[0]');
    END;
//

CREATE PROCEDURE _myproto_pop_frame(INOUT p_stack JSON, OUT p_limit integer, OUT p_path varchar(1000))
    BEGIN
        SET p_limit = JSON_EXTRACT(p_stack, '$[0].limit');
        SET p_path = JSON_EXTRACT(p_stack, '$[0].path');
        SET p_stack = JSON_REMOVE(p_stack, '$[0]');
    END;
//

CREATE PROCEDURE _myproto_get_field_and_wiretype(IN p_bytes varbinary(10000), INOUT p_offset integer, IN p_limit integer, OUT p_field_number integer, OUT p_wiretype integer, OUT p_error VARCHAR(512))
BEGIN
  DECLARE field_wiretype integer;

  CALL var_int(p_bytes, p_offset, p_limit, field_wiretype, p_error);
  SET p_wiretype = field_wiretype & 0x07;
  SET p_field_number = (field_wiretype >> 3) & 0x1f;
END;
//

CREATE PROCEDURE _myproto_len_limit(IN p_bytes varbinary(10000), INOUT p_offset integer, INOUT p_limit integer, OUT p_error VARCHAR(512))
BEGIN
  DECLARE value integer;
  CALL var_int(p_bytes, p_offset, p_limit, value, p_error);
  SET p_limit = p_offset + value + 1;
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

CREATE PROCEDURE _myproto_append_path_value(INOUT p_message JSON, IN p_depth integer, IN p_parent_path varchar(1000), IN p_field_number integer, IN p_value JSON)
BEGIN
    SET p_message = JSON_ARRAY_APPEND(
            p_message,
            '$',
            JSON_OBJECT(
                'depth', p_depth,
                'parent_path', p_parent_path,
                'field_number', p_field_number,
                'value', p_value
            ));
END;
//

CREATE FUNCTION _myproto_flatten_message(p_bytes varbinary(10000)) returns JSON deterministic
BEGIN
  DECLARE offset integer default 1;
  DECLARE depth integer default 0;
  DECLARE field_number, wiretype integer;
  DECLARE p_limit, m_limit integer default length(p_bytes)+1;
  DECLARE message, stack, value JSON;
  DECLARE parent_path varchar(1000) default '';
  DECLARE error varchar(512);

  SET stack = JSON_ARRAY();
  CALL _myproto_push_frame(stack, offset, m_limit, parent_path);
  SET message = JSON_ARRAY();

  WHILE offset < p_limit DO

    CALL _myproto_get_field_and_wiretype(p_bytes, offset, m_limit, field_number, wiretype, error);

    IF error IS NOT NULL THEN
        CALL _myproto_pop_frame_and_reset(stack, offset,m_limit, parent_path);
        SET depth = depth - 1;
        CALL get_len_value(p_bytes, offset, m_limit, value, error);
        CALL _myproto_append_path_value(message, depth, parent_path, field_number, value);
    ELSEIF _myproto_wiretype_len(wiretype) OR _myproto_wiretype_sgroup(wiretype) THEN
        CALL _myproto_push_frame(stack, offset, m_limit, parent_path);
        CALL _myproto_len_limit(p_bytes, offset, m_limit, error);
        SET depth = depth + 1;
        SET parent_path = CONCAT(parent_path, '.', field_number);
    ELSEIF _myproto_wiretype_egroup(wiretype) THEN
        CALL _myproto_pop_frame(stack, m_limit, parent_path);
        SET depth = depth - 1;
    ELSE
        CALL _myproto_get_field_value(p_bytes, offset, m_limit, wiretype, value, error);
        CALL _myproto_append_path_value(message, depth, parent_path, field_number, value);
    END IF;
  END WHILE;

  return message;
END;
//


CREATE procedure _p_myproto_flatten_message(p_bytes varbinary(10000))
BEGIN
  DECLARE offset integer default 1;
  DECLARE depth integer default 0;
  DECLARE field_number, wiretype integer;
  DECLARE p_limit, m_limit integer default length(p_bytes)+1;
  DECLARE message, stack, value JSON;
  DECLARE parent_path varchar(1000) default '';
  DECLARE error varchar(512);

  SET stack = JSON_ARRAY();
  CALL _myproto_push_frame(stack, offset, m_limit, parent_path);
  SET message = JSON_ARRAY();

  WHILE offset < p_limit DO

    CALL _myproto_get_field_and_wiretype(p_bytes, offset, m_limit, field_number, wiretype, error);
    SELECT 'field and wiretype', field_number, wiretype, offset, error;
    IF error IS NOT NULL THEN
        select error;
        CALL _myproto_pop_frame_and_reset(stack, offset,m_limit, parent_path);
        SET depth = depth - 1;
        CALL get_len_value(p_bytes, offset, m_limit, value, error);
        CALL _myproto_append_path_value(message, depth, parent_path, field_number, value);
    ELSEIF _myproto_wiretype_len(wiretype) OR _myproto_wiretype_sgroup(wiretype) THEN
        select 'len', field_number;

        CALL _myproto_push_frame(stack, offset, m_limit, parent_path);
        CALL _myproto_len_limit(p_bytes, offset, m_limit, error);
        SET depth = depth + 1;
        SET parent_path = CONCAT(parent_path, '.', field_number);
    ELSEIF _myproto_wiretype_egroup(wiretype) THEN
        select 'meh', stack;
        CALL _myproto_pop_frame(stack, m_limit, parent_path);
        SET depth = depth - 1;
    ELSE
        select 'get value';
        CALL _myproto_get_field_value(p_bytes, offset, m_limit, wiretype, value, error);
        CALL _myproto_append_path_value(message, depth, parent_path, field_number, value);
        select 'message', message;
    END IF;
    select stack;
  END WHILE;

  select message;
END;
//
