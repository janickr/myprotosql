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
DROP PROCEDURE IF EXISTS _myproto_append_start_submessage;
DROP PROCEDURE IF EXISTS _myproto_undo_appended_fields;
DROP FUNCTION IF EXISTS _myproto_is_start_submessage;
DROP FUNCTION IF EXISTS _myproto_is_frame_field;

delimiter //

CREATE PROCEDURE var_int(IN p_bytes varbinary(10000), INOUT p_offset integer, IN p_limit integer, OUT p_result integer)
BEGIN
  DECLARE error_text varchar(128) default CONCAT('VarInt at offset ', p_offset, ' exceeds limit set by LEN ', p_limit);
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
    SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = error_text;
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
  SET p_offset = p_offset + p_nb_bytes;
END
//

CREATE PROCEDURE get_i32_value(IN p_bytes varbinary(10000), INOUT p_offset integer, IN p_limit integer, OUT p_value JSON)
  BEGIN
    DECLARE error_text varchar(128) default CONCAT('i32 at offset ', p_offset, ' exceeds limit set by LEN ', p_limit);

    IF p_offset + 4 > p_limit THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = error_text;
    ELSE
        CALL get_fixed_number_value(p_bytes, p_offset, 4, p_value);
    END IF;
  END;
//

CREATE PROCEDURE get_i64_value(IN p_bytes varbinary(10000), INOUT p_offset integer, IN p_limit integer, OUT p_value JSON)
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


CREATE PROCEDURE _myproto_push_frame(INOUT p_stack JSON, IN p_offset integer, IN p_limit integer, INOUT p_path varchar(1000), IN p_field integer)
    BEGIN
        SET p_stack = JSON_ARRAY_INSERT(
                p_stack,
                '$[0]',
                JSON_OBJECT(
                  'offset', p_offset,
                  'limit', p_limit,
                  'path', p_path,
                  'field', p_field
                ));
        IF (p_field) THEN
            SET p_path = CONCAT(p_path, '.', p_field);
        END IF;
    END;
//

CREATE PROCEDURE _myproto_pop_frame_and_reset(INOUT p_stack JSON, OUT p_offset integer, OUT p_limit integer, OUT p_path varchar(1000), OUT p_field integer)
    BEGIN
        SET p_offset = JSON_EXTRACT(p_stack, '$[0].offset');
        SET p_limit = JSON_EXTRACT(p_stack, '$[0].limit');
        SET p_path = JSON_UNQUOTE(JSON_EXTRACT(p_stack, '$[0].path'));
        SET p_field = JSON_EXTRACT(p_stack, '$[0].field');
        SET p_stack = JSON_REMOVE(p_stack, '$[0]');
    END;
//

CREATE PROCEDURE _myproto_pop_frame(INOUT p_stack JSON, OUT p_limit integer, OUT p_path varchar(1000), OUT p_field integer)
    BEGIN
        SET p_limit = JSON_EXTRACT(p_stack, '$[0].limit');
        SET p_path = JSON_UNQUOTE(JSON_EXTRACT(p_stack, '$[0].path'));
        SET p_field = JSON_EXTRACT(p_stack, '$[0].field');
        SET p_stack = JSON_REMOVE(p_stack, '$[0]');
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

CREATE PROCEDURE _myproto_append_path_value(INOUT p_message JSON, IN p_depth integer, IN p_parent_path varchar(1000), IN p_field_number integer, IN p_value JSON)
BEGIN
    SET p_message = JSON_ARRAY_APPEND(
            p_message,
            '$',
            JSON_OBJECT(
                'type', 'field',
                'depth', p_depth,
                'path', p_parent_path,
                'field', p_field_number,
                'value', p_value
            ));
END;
//

CREATE PROCEDURE _myproto_append_start_submessage(INOUT p_message JSON, IN p_depth integer, IN p_parent_path varchar(1000), IN p_field_number integer)
BEGIN
    SET p_message = JSON_ARRAY_APPEND(
            p_message,
            '$',
            JSON_OBJECT(
                'type', 'object',
                'depth', p_depth,
                'path', p_parent_path,
                'field', p_field_number
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


CREATE FUNCTION _myproto_flatten_message(p_bytes varbinary(10000)) returns JSON deterministic
BEGIN
  DECLARE offset integer default 1;
  DECLARE field_number, wiretype integer;
  DECLARE p_limit, m_limit integer default length(p_bytes)+1;
  DECLARE message, stack, value JSON;
  DECLARE parent_path varchar(1000) default '$';

  SET stack = JSON_ARRAY();
  CALL _myproto_push_frame(stack, offset, m_limit, parent_path, 0);
  SET message = JSON_ARRAY();

   WHILE offset < p_limit DO
      BEGIN
        DECLARE CONTINUE HANDLER FOR SQLSTATE '45000'
        BEGIN
            -- check if stack > 1, if not there is a bug
            CALL _myproto_pop_frame_and_reset(stack, offset,m_limit, parent_path, field_number);
            CALL _myproto_undo_appended_fields(message, JSON_LENGTH(stack)-1, parent_path, field_number);
            CALL get_len_value(p_bytes, offset, m_limit, value);
            CALL _myproto_append_path_value(message, JSON_LENGTH(stack)-1, parent_path, field_number, value);
        END;

        CALL _myproto_get_field_and_wiretype(p_bytes, offset, m_limit, field_number, wiretype);

        IF _myproto_wiretype_len(wiretype) OR _myproto_wiretype_sgroup(wiretype) THEN
            CALL _myproto_append_start_submessage(message, JSON_LENGTH(stack)-1, parent_path, field_number);
            CALL _myproto_push_frame(stack, offset, m_limit, parent_path, field_number);
            CALL _myproto_len_limit(p_bytes, offset, m_limit);
        ELSEIF _myproto_wiretype_egroup(wiretype) THEN
            IF _myproto_is_frame_field(stack, field_number) THEN
                CALL _myproto_pop_frame(stack, m_limit, parent_path, field_number);
            ELSE
                SIGNAL SQLSTATE '45000'
                    SET MESSAGE_TEXT = 'Malformed message';
            END IF;
        ELSE
            CALL _myproto_get_field_value(p_bytes, offset, m_limit, wiretype, value);
            CALL _myproto_append_path_value(message, JSON_LENGTH(stack)-1, parent_path, field_number, value);
        END IF;

        IF offset = m_limit THEN
            CALL _myproto_pop_frame(stack, m_limit, parent_path, field_number);
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
