import json
from dataclasses import dataclass, field, asdict


@dataclass
class RawAddress:
    address_line_1: str | None = field(default=None)
    address_line_2: str | None = field(default=None)
    address_line_3: str | None = field(default=None)
    address_line_4: str | None = field(default=None)
    postal_code: str | None = field(default=None)
    province_code: str | None = field(default=None)

    def __str__(self):
        return json.dumps(asdict(self))