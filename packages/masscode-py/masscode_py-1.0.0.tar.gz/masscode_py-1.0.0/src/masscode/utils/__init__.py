import base64
import uuid


try:
    import orjson

    json = None
except ImportError:
    import json

    orjson = None


def load_json(path: str) -> dict:
    if orjson is not None:
        with open(path, "rb") as f:
            return orjson.loads(f.read())
    else:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)


def dump_json(data: dict, path: str):
    if orjson is not None:
        with open(path, "wb") as f:
            f.write(orjson.dumps(data, option=orjson.OPT_INDENT_2))
    else:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent="\t", ensure_ascii=False)


def generate_id(length=8):
    uuido = uuid.uuid4()
    encoded = base64.b64encode(uuido.bytes).decode()
    return encoded[:length]


__all__ = ["load_json", "dump_json", "generate_id"]
