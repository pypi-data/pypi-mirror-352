def nullable_type(t, nullable):
    assert isinstance(t, str)
    assert isinstance(nullable, bool)

    if not nullable:
        return t
    return [t, "null"]


primitives = ["string", "number", "boolean"]


def make_union(items, nullable):
    assert isinstance(items, list)
    assert len(items) > 1
    assert isinstance(nullable, bool)

    if all(item in primitives for item in items):
        union = items
        if nullable:
            union += ["null"]
        return {"type": union}

    union = [make_type(item, False) for item in items]
    if nullable:
        union.append({"type": "null"})
    return {"anyOf": union}


def make_array(items, nullable):
    assert isinstance(items, list)
    assert len(items) == 1

    return {
        "type": nullable_type("array", nullable),
        "items": make_type(items[0], False),
    }


def make_type(value, nullable):
    match value:
        case list(arr) if len(arr) == 1:
            return make_array(arr, nullable)
        case list(arr) if len(arr) > 1:
            return make_union(arr, nullable)
        case dict(obj):
            return make_object(obj, nullable)
        case str(t) if t in primitives:
            return make_primitive(t, nullable)
        case _:
            raise ValueError(f"Unsupported value type: {value}")


def make_primitive(t, nullable):
    assert t in primitives

    return {"type": nullable_type(t, nullable)}


def make_object(obj, nullable):
    assert isinstance(obj, dict)
    assert all(isinstance(key, str) for key in obj.keys())
    assert isinstance(nullable, bool)

    props = {
        key.removesuffix("?"): make_type(val, key.endswith("?"))
        for key, val in obj.items()
    }
    return {
        "type": nullable_type("object", nullable),
        "properties": props,
        "required": list(props.keys()),
        "additionalProperties": False,
    }


def object_schema(obj):
    return make_object(obj, False)
