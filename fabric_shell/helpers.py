from typing import Literal


def anchor(*args: Literal["top", "bottom", "left", "right"]):
    return " ".join(args)
