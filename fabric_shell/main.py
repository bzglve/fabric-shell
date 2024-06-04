import fabric
from fabric.utils.fabricator import Fabricator
from fabric.widgets.box import Box
from fabric.widgets.centerbox import CenterBox
from fabric.widgets.eventbox import EventBox
from fabric.widgets.label import Label
from fabric.widgets.wayland import Window
from gi.repository import GLib  # type: ignore
from gi.repository.GObject import BindingFlags  # type: ignore

from .config import config
from .helpers import anchor
from .logger import logger  # noqa: F401
from .services.backlight import backlight


class Date(EventBox):
    def __init__(self):
        super().__init__(children=self.__create_children())
        self.__label_poll = self.__setup_label_poll()

    def __create_children(self) -> Box:
        self.__label = Label()
        return Box(children=[self.__label])

    def __setup_label_poll(self) -> Fabricator:
        label_poll = Fabricator(
            poll_from=lambda: GLib.DateTime.new_now_local().format(  # type: ignore
                config.clock.time
            ),
            interval=1000,
        )
        label_poll.bind_property("value-str", self.__label, "label")
        return label_poll


class Brightness(EventBox):
    def __init__(self):
        super().__init__(children=self.__create_children())
        backlight.bind_property(
            "value",
            self.__label,
            "label",
            BindingFlags.DEFAULT,
            self.__label_transform_to,
        )

    def __create_children(self) -> Box:
        self.__label = Label(label="N/A")
        return Box(children=[self.__label])

    @staticmethod
    def __label_transform_to(_, value: float) -> str:
        return str(int(value * 100))


class StatusBar(Window):
    def __init__(self):
        super().__init__(
            layer="overlay",
            anchor=anchor("top", "left", "right"),
            children=self.__create_children(),
        )

    def __create_children(self) -> CenterBox:
        return CenterBox(
            start_children=Box(children=[]),
            center_children=Box(children=[Date()]),
            end_children=Box(children=[Brightness()]),
        )


def start():
    window = StatusBar()
    window.show_all()

    fabric.start()


if __name__ == "__main__":
    start()
