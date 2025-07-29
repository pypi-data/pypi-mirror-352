import enum
from dataclasses import dataclass


class ThresholdType(enum.Enum):
    absolute = "absolute"
    offset = "offset"

@dataclass
class Threshold:
    type: ThresholdType = None
    base: int = None
    absolute: int = None
    offset: int = 0

    def value(self):

        if self.type is None:
            RuntimeError("Threshold type not set!")
        if self.type == ThresholdType.offset and self.base is None:
            RuntimeError("Threshold base not set for offset usage!")
        if self.type == ThresholdType.absolute and self.absolute is None:
            RuntimeError("Threshold absolute not set for absolute usage!")

        return self.base + self.offset if type == ThresholdType.offset else self.absolute
