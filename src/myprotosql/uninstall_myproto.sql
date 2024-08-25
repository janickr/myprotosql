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