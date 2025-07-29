import json
from json import JSONEncoder
from typing import Any

from cyberfusion.SystemdSupport import Unit


class CustomEncoder(JSONEncoder):
    def default(self, o: Any) -> Any:
        if isinstance(o, Unit):
            return {"name": o.name}

        return super().default(o)


def json_serialize(obj: Any) -> str:
    return json.dumps(obj, cls=CustomEncoder)
