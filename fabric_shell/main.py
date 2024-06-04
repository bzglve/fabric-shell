import fabric
from fabric.widgets.label import Label
from fabric.widgets.centerbox import CenterBox
from fabric.widgets.wayland import Window


class StatusBar(Window):
    def __init__(self):
        super().__init__(
            layer="overlay",
            anchor="top left right",
            children=CenterBox(center_children=Label("TEST")),
        )


window = StatusBar()
window.show()
fabric.start()
