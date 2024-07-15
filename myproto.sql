drop function if exists var_int;
drop function if exists get_value;
drop function if exists get_data;
drop function if exists get_message;
drop function if exists _myproto_get_value;
drop function if exists _myproto_get_offset;
drop function if exists _myproto_get_bytes_read;
drop function if exists _myproto_get_error;
drop function if exists _myproto_error;
drop function if exists _myproto_result;
drop function if exists get_i32_value;
drop function if exists get_i64_value;
drop function if exists get_len_value;
drop function if exists get_fixed_number_value;

delimiter //


CREATE FUNCTION _myproto_result(p_value JSON, p_offset integer, p_bytes_read integer) returns JSON deterministic
    return JSON_OBJECT(
          'value', p_value,
          'offset', p_offset,
          'bytes_read', p_bytes_read
         )
//

CREATE FUNCTION _myproto_error(p_value JSON, p_offset integer, p_bytes_read integer, p_error varchar(512)) returns JSON deterministic
    return JSON_OBJECT(
          'value', p_value,
          'offset', p_offset,
          'bytes_read', p_bytes_read,
          'error', p_error
         )
//

CREATE FUNCTION _myproto_get_value(p_result JSON) returns JSON deterministic
    return JSON_EXTRACT(p_result, '$.value');
//
CREATE FUNCTION _myproto_get_offset(p_result JSON) returns integer deterministic
    return JSON_EXTRACT(p_result, '$.offset');
//
CREATE FUNCTION _myproto_get_bytes_read(p_result JSON) returns integer deterministic
    return JSON_EXTRACT(p_result, '$.bytes_read');
//
CREATE FUNCTION _myproto_get_error(p_result JSON) returns integer deterministic
    return JSON_EXTRACT(p_result, '$.error');
//

CREATE FUNCTION var_int(p_bytes varbinary(10000), p_offset integer, p_limit integer) returns JSON deterministic
BEGIN
  DECLARE next varbinary(10000);
  DECLARE result, shift, count integer;
  DECLARE b integer(1);
    
  SET result = 0;
  SET shift = 0;
  SET count = 1;
  SET next = substr(p_bytes, p_offset);
  READ_WHILE_FIRST_BIT_SET: REPEAT
      SET b = ASCII(next);
      SET result = result + ((b & 0x7f) << shift);
      IF ((b & 0x80) = 0)  THEN
        LEAVE READ_WHILE_FIRST_BIT_SET;
      END IF;
      SET next = substr(next, 2);
      SET shift = shift + 7;
      SET count = count + 1;

      UNTIL count > p_limit-p_offset+1
  END REPEAT;
  IF count > p_limit-p_offset+1 THEN
    return _myproto_error(cast(result as json), p_offset, p_limit, 'VarInt exceeds LEN '+ p_limit);
  ELSE
    return _myproto_result(cast(result as json), p_offset+count, count);
  END IF;
END;
//

CREATE FUNCTION get_fixed_number_value(p_bytes varbinary(10000), p_offset integer, p_limit integer, p_nb_bytes integer) returns JSON deterministic
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
  return _myproto_result(cast(result as json), p_offset+count, count);
END
//

CREATE FUNCTION get_i32_value(p_bytes varbinary(10000), p_offset integer, p_limit integer) returns JSON deterministic
  IF p_offset + 4 > p_limit THEN
    return _myproto_error(null, p_offset, p_limit, 'i32 exceeds LEN '+ p_limit);
  ELSE
    return get_fixed_number_value(p_bytes, p_offset, p_limit, 4);
  END IF;
//

CREATE FUNCTION get_i64_value(p_bytes varbinary(10000), p_offset integer, p_limit integer) returns JSON deterministic
  IF p_offset + 8 > p_limit THEN
    return _myproto_error(null, p_offset, p_limit, 'i64 exceeds LEN '+ p_limit);
  ELSE
    return get_fixed_number_value(p_bytes, p_offset, p_limit, 8);
  END IF;
//

CREATE FUNCTION get_len_value(p_bytes varbinary(10000), p_offset integer, p_limit integer) returns JSON deterministic
BEGIN
  DECLARE length_result, message JSON;
  DECLARE length, offset integer;

  SET length_result = var_int(p_bytes, p_offset, p_limit);
  SET length = _myproto_get_value(length_result);
  SET offset = _myproto_get_offset(length_result);
  SET message = get_message(p_bytes, offset, offset+length);

  return message;
END
//

CREATE FUNCTION get_value(p_wiretype integer, p_bytes varbinary(10000), p_offset integer, p_limit integer) returns JSON deterministic
BEGIN
  CASE p_wiretype
      WHEN 0 THEN
        return var_int(p_bytes, p_offset, p_limit);
      WHEN 1 THEN
        return get_i64_value(p_bytes, p_offset, p_limit);
      WHEN 5 THEN
        return get_i32_value(p_bytes, p_offset, p_limit);
      WHEN 2 THEN
        return get_len_value(p_bytes, p_offset, p_limit);
      ELSE
        return _myproto_error(null, p_offset, p_limit, 'Invalid wiretype: '+p_wiretype);
    END CASE;
END;
//

CREATE FUNCTION get_data(p_bytes varbinary(10000), p_offset integer, p_limit integer) returns JSON deterministic
BEGIN
  DECLARE field_wiretype_result, value JSON;
  DECLARE field_wiretype, field_number, wiretype, offset integer;
  
  SET field_wiretype_result = var_int(p_bytes, p_offset, p_limit);
  SET field_wiretype = _myproto_get_value(field_wiretype_result);
  SET wiretype = field_wiretype & 0x07;
  SET field_number = (field_wiretype >> 3) & 0x1f;
  set offset = _myproto_get_offset(field_wiretype_result);

  SET value = get_value(wiretype, p_bytes, offset, p_limit);
  return _myproto_result(
           JSON_OBJECT( field_number, _myproto_get_value(value) ),
           _myproto_get_offset(value),
           _myproto_get_bytes_read(field_wiretype_result) + _myproto_get_bytes_read(value)
         );
END;
//

CREATE FUNCTION get_message(p_bytes varbinary(10000), p_offset integer, p_limit integer) returns JSON deterministic
BEGIN
  DECLARE offset, count integer;
  DECLARE message, field, value JSON;

  SET message = JSON_OBJECT();
  SET offset = p_offset;
  SET count = 0;
  WHILE offset < p_limit DO
      SET field = get_data(p_bytes, offset, p_limit);
      SET value = _myproto_get_value(field);
      SET count = count + _myproto_get_bytes_read(field);
      SET offset = _myproto_get_offset(field);
      SET message = JSON_MERGE_PRESERVE(message, value);
  END WHILE;

  return _myproto_result(message, offset, count);
END;
//
