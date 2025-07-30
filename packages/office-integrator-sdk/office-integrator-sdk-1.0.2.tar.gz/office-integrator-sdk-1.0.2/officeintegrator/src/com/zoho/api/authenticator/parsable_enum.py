from enum import Enum

class ParsableEnum(Enum):

    def get_transform_value(self) -> str:
        return self.name.lower()

    @classmethod
    def parse(cls, value):

        for item in cls:
            if item.get_transform_value() == value.lower():
                return item
        raise ValueError(f"Given value '{value}' is not a valid '{cls.__name__}'")
