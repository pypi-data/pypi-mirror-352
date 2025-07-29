from dataclasses import dataclass, field


@dataclass(frozen=True)
class CommandArgs:
    model_path: str = field()
    device: str = field()
    samples_path: str = field()