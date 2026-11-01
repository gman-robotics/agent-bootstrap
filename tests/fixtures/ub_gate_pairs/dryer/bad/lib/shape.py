def shape_left(parts):
    first = parts[0]
    second = parts[1]
    third = parts[2]
    fourth = parts[3]
    fifth = parts[4]
    head = first + second
    head = head + third
    head = head + fourth
    head = head + fifth
    body = head + first
    body = body + second
    body = body + third
    tail = body + "end"
    tail = tail + fourth
    tail = tail + fifth
    return tail


def shape_right(parts):
    first = parts[0]
    second = parts[1]
    third = parts[2]
    fourth = parts[3]
    fifth = parts[4]
    head = first + second
    head = head + third
    head = head + fourth
    head = head + fifth
    body = head + first
    body = body + second
    body = body + third
    tail = body + "end"
    tail = tail + fourth
    tail = tail + fifth
    return tail
