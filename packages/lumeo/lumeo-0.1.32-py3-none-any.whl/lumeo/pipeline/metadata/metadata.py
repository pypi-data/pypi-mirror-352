import re

from ..utils import install_import

def num_milliseconds_seen(last_seen_frame, first_seen_frame, video_info):
    """
    Returns the total of milliseconds passed between two frame counts.

    Args:
        last_seen_frame (int): The last seen frame count.
        first_seen_frame (int): The first seen frame count.
        video_info (object): An object containing video information, including fps_d and fps_n.

    Returns:
        int: The total number of milliseconds passed between the two frame counts.
    """
    num_frames_seen = last_seen_frame - first_seen_frame
    num_seconds_seen = num_frames_seen * video_info.fps_d / video_info.fps_n if video_info.fps_n != 0 else num_frames_seen
    return round(num_seconds_seen * 1000)

def get_timestamp(frame, frame_count):
    """
    Return the timestamp of a certain frame, based on the current frame_count and video FPS.

    Args:
        frame (object): An object containing video frame information.
        frame_count (int): The current frame count.

    Returns:
        float: The timestamp of the frame.
    """
    timestamp = frame_count / 15  # assumes 15fps if fps info not provided

    try:
        timestamp = frame_count * frame.video_info().fps_d / frame.video_info().fps_n
    except:
        pass

    return timestamp


def eval_trigger_condition(meta, condition_string):
    """
    Evaluates if the current metadata matches a trigger condition.

    Args:
        meta (dict): The metadata to evaluate.
        condition_string (str): A condition string to compile and evaluate.

    Returns:
        bool: True if the trigger condition is met, False otherwise.
    """

    def __split(string, separators):
        result = [string]
        for sep in separators:
            temp = []
            for substr in result:
                temp += substr.split(sep)
            result = temp
        return [r.strip() for r in result]

    # Note: python-box is not available as apt package on the distros we use, so will use
    # install_import. It's installed/imported inside the function to avoid install it when
    # users don't need it. There's no impact on performance: this just imports the module
    # once in the 1st function call, then its cached
    box = install_import('python-box', module_name='box')
    dpath = install_import('dpath')
    from box import Box

    trigger_result = False

    compiled_condition = None
    if condition_string:
        try:
            expression = condition_string
            # Treat a '*' as a wildcard to sum all leaf values in the expression
            if '*' in expression:
                e_parts = __split(expression, ['==', '!=', '>=', '>', '<=', '<', ' and ', ' or '])
                for e_part in e_parts:
                    if '*' in e_part:
                        v = sum(dpath.values(meta, e_part, separator='.'))
                        expression = expression.replace(e_part, str(v))
            compiled_condition = compile(expression, "<string>", "eval")
        except:
            trigger_result = False

    if compiled_condition is not None:
        try:
            # Create trigger_condition_objects so the trigger can't operate/reference on
            # anything else. Convert meta to Box format which allows you to access it using
            # dot notation like : node.annotate_presence1.rois.roi1.objects_entered_count
            # instead of meta['nodes']['annotate_presence1']['rois']['roi1'][
            # 'objects_entered_count']
            trigger_condition_objects = Box(meta)

            # Evalate the trigger condition.
            trigger_result = eval(compiled_condition, {}, trigger_condition_objects)
        except Exception:
            trigger_result = False

    return trigger_result > 0


def merge_dicts(a, b, path=[]):
    """
    Merges two dictionaries and preserves elements on repeated keys.

    Args:
        a (dict): The first dictionary.
        b (dict): The second dictionary.
        path (list, optional): The current path of keys. Default is an empty list.

    Returns:
        dict: The merged dictionary.
    """
    for key in b:
        if key in a:
            if isinstance(a[key], dict) and isinstance(b[key], dict):
                merge_dicts(a[key], b[key], path + [str(key)])
            elif a[key] == b[key]:
                pass
            else:
                raise Exception('Conflict at %s' % '.'.join(path + [str(key)]))
        else:
            a[key] = b[key]
    return a

def flatten_dict(pyobj, keystring=''):
    """
    Flattens a nested dictionary or list into a flat dictionary.

    Args:
        pyobj (dict or list): The nested dictionary or list to flatten.
        keystring (str, optional): The current key string. Default is an empty string.

    Yields:
        tuple: A tuple containing the key string and the value.
    """
    if isinstance(pyobj, dict):
        keystring = keystring + '.' if keystring else keystring
        for key, value in pyobj.items():
            yield from flatten_dict(value, keystring + str(key))
    elif isinstance(pyobj, list):
        keystring = keystring + '.' if keystring else keystring
        for i, value in enumerate(pyobj):
            yield from flatten_dict(value, keystring + str(i))
    else:
        yield keystring, pyobj


def filter_dict(key_patterns, meta_dict):
    """
    Filters a dictionary based on a list of key patterns.

    Args:
        key_patterns (list): A list of key patterns to filter the dictionary by.
        meta_dict (dict): The dictionary to filter.

    Returns:
        dict: The filtered dictionary.
    """
    filtered_dict = {}

    if key_patterns is not None:
        key_list = meta_dict.keys()
        for key_pattern in key_patterns:
            r = re.compile(key_pattern)
            # We sort the keys because on different pipeline runs the default order can change
            filtered_keys = sorted(filter(r.match, key_list))
            for k in filtered_keys:
                filtered_dict[k] = meta_dict[k]
    else:
        for k in sorted(meta_dict):
            filtered_dict[k] = meta_dict[k]

    return filtered_dict


def object_has_attributes(obj, attribute_labels) -> bool:
    """
    Checks if an object has the specified attributes.

    Args:
        obj (dict): The object to check.
        attribute_labels (list): A list of attribute labels to check for.

    Returns:
        bool: True if the object matches all specified attribute conditions, False otherwise.
    """
    obj_attributes_set = {attribute.get('label','').lower() for attribute in obj['attributes']}
    for label in attribute_labels:
        if label == '*':
            if len(obj_attributes_set) == 0:
                return False
        elif label == '-*':
            if len(obj_attributes_set) > 0:
                return False
        elif label.startswith('-'):
            # Check if the attribute is not present
            if label[1:].lower() in obj_attributes_set:
                return False
        else:
            # Check if the attribute is present
            if label.lower() not in obj_attributes_set:
                return False
    return True


def object_matches_type(obj, object_type) -> bool:
    """
    Checks if an object matches a specified type.

    Args:
        obj (dict): The object to check.
        object_type (tuple): A tuple containing the object type and optional attributes.

    Returns:
        bool: True if the object matches the specified type, False otherwise.
    """
    obj_label_match = (object_type[0] == obj.get('label','').lower())
    if obj_label_match: 
        if len(object_type) > 1:
            return object_has_attributes(obj, object_type[1:])
        else:
            return True
    return False

def object_matches_types(obj, object_types) -> bool:
    """
    Checks if an object matches any of the specified types.

    Args:
        obj (dict): The object to check.
        object_types (list): A list of object types to check against.

    Returns:
        bool: True if the object matches any of the specified types, False otherwise.
    """
    for object_type in object_types:
        if object_matches_type(obj, object_type):
            return True
    return False


def object_matches_all_types(obj, object_types) -> bool:
    """
    Checks if an object matches all of the specified types.

    Args:
        obj (dict): The object to check.
        object_types (list): A list of object types to check against.

    Returns:
        bool: True if the object matches all of the specified types, False otherwise.
    """    
    return all(object_matches_type(obj, object_type) for object_type in object_types)
