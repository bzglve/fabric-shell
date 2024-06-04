from pathlib import Path
from typing import Any, Callable, Optional, override

import fabric.utils as utils
from fabric.service import (
    Property,
    Service,
    Signal,
    SignalConnection,
    SignalContainer,
)
from gi.repository.Gio import FileMonitorEvent  # type: ignore
from gi.repository.GObject import Binding, BindingFlags, Object  # type: ignore


class Backlight(Service):
    __gsignals__ = SignalContainer(
        Signal("changed", "run-first", None, (float,)),
    )

    def __init__(self, interface: Optional[str] = None, **kwargs):
        super().__init__(**kwargs)

        self.__interface = interface or self.__detect_interface()
        self.__monitor = self.__setup_monitor()
        self.__max = self.__get_max_brightness()
        self.__value = 0.0
        self.__update()

    def __detect_interface(self) -> str:
        return list(Path("/sys/class/backlight").iterdir())[0].name

    def __setup_monitor(self) -> Any:
        monitor = utils.monitor_file(f"/sys/class/backlight/{self.__interface}/brightness")
        monitor.connect("changed", self.__on_file_change)
        return monitor

    def __get_max_brightness(self) -> int:
        return int(utils.exec_shell_command("brightnessctl max"))

    def __get_current_brightness(self) -> int:
        return int(utils.exec_shell_command("brightnessctl get"))

    def __set_brightness(self, value: float):
        clamped_value = max(0.0, min(value, 1.0))
        utils.exec_shell_command_async(
            [
                "brightnessctl",
                "-s",
                "set",
                f"{int(clamped_value * 100)}%",
                "-q",
            ],
            lambda *args: None,
        )

    def __on_file_change(self, *args):
        if args[3] == FileMonitorEvent.CHANGES_DONE_HINT:
            self.__update()

    def __update(self):
        self.__value = self.__get_current_brightness() / self.__max
        self.notify("value")
        self.emit("changed", self.__value)

    @Property(value_type=float, flags="read-write")
    def value(self) -> float:  # type: ignore
        return self.__value

    @value.setter
    def value(self, value: float):
        self.__set_brightness(value)

    @override
    def connect(self, signal_spec: str, callback: Callable) -> SignalConnection:
        signal_connection = super().connect(signal_spec, callback)
        if signal_spec == "changed":
            callback(self, self.__value)
        return signal_connection

    @override
    def bind_property(
        self,
        source_property: str,
        target: Object,
        target_property: str,
        flags: BindingFlags = BindingFlags.DEFAULT,
        transform_to: Optional[Callable[..., Any]] = None,
        transform_from: Optional[Callable[..., Any]] = None,
        user_data: Optional[Any] = None,
    ) -> Binding:
        binding = super().bind_property(
            source_property,
            target,
            target_property,
            flags,
            transform_to,
            transform_from,
            user_data,
        )
        self.notify(source_property)
        return binding


backlight = Backlight()
