def get_segments(objects, obj_id):

    if obj_id not in objects:
        return None

    return objects[obj_id]["segments"]


def find_segment(objects, obj_id, frame):

    segments = get_segments(objects, obj_id)

    if segments is None:
        return None

    for seg in segments:
        if seg["start_frame"] <= frame <= seg["end_frame"]:
            return seg

    return None