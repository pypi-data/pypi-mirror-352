import json
from dataclasses import dataclass, field, asdict

from .. import literals


@dataclass(repr=True)
class CleanAddress:
    address_line: str = field(default=None)
    city: str = field(default=None)
    province_code: literals.ProvinceCode = field(default=None)
    postal_code: str | None = field(default=None)

    def __str__(self):
        return json.dumps(asdict(self))