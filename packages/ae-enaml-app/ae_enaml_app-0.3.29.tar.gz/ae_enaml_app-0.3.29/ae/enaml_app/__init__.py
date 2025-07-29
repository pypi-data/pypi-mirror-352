"""
enaml application widgets, helper functions and classes
=======================================================

the enaml module `widgets` is providing widgets to write themed applications which can switch their font colors and
backgrounds at run-time between dark and light.

another set of widgets provided by this namespace portion allows the automatic change of the application flow with
only few lines of code.

to convert colors between the enaml and other formats the functions declared in the :mod:`functions` of this package
can be used.


main application class for GUIApp-conform Enaml app
---------------------------------------------------

the classes :class:`FrameworkApp` and :class:`EnamlMainApp` of this ae portion are bundling and adding useful
attributes and methods for your application and are extendable by creating a subclass.

the class :class:`EnamlMainApp` is implementing a main app class that is reducing the amount of code needed to create a
Python application based on the `enaml framework <https://enaml.readthedocs.io/en/latest/>`_.

:class:`EnamlMainApp` is based on the following classes:

* the abstract base class :class:`~ae.gui.app.MainAppBase`
  which is providing :ref:`application status`
  (including :ref:`app-state-variables` and :ref:`app-state-constants`),
  :ref:`application flow` and :ref:`application events`.
* the class :class:`~ae.console.ConsoleApp` is adding
  :ref:`config-files`, :ref:`config-variables`
  and :ref:`config-options`.
* the class :class:`~ae.core.AppBase` is adding
  :ref:`application logging` and :ref:`application debugging`.


the main app class :class:`EnamlMainApp` is also encapsulating the enaml app class for the Qt widget set
(<enaml.QtApplication>) within the :class:`FrameworkApp` class.

an instance of the Enaml app class can be directly accessed from the main app class instance via the
:attr:`~ae.gui.app.MainAppBase.framework_app` attribute.


enaml application events
^^^^^^^^^^^^^^^^^^^^^^^^

this portion is firing :ref:`application events` additional to the ones provided by :class:`~ae.gui.app.MainAppBase`.
these framework app events get fired after :meth:`~ae.gui.app.MainAppBase.on_app_run` in the following order:

* on_app_build (fired on start of the application event loop).
* on_app_stopped (fired after the main application window got closed)

"""
from typing import Any, Callable, Dict, Optional, Tuple, Type, Union

import atom.api

import enaml                                                                                # type: ignore
# from enaml.application import Application

from enaml.qt import QtCore                                                                 # type: ignore
from enaml.qt.qt_application import QtApplication                                           # type: ignore

from enaml.icon import IconImage, Icon                                                      # type: ignore
from enaml.image import Image                                                               # type: ignore
from enaml.widgets.widget import Widget                                                     # type: ignore
# from enaml.widgets.popup_view import PopupView as PopupsRegister

from ae.base import read_file                                                               # type: ignore
from ae.files import CachedFile                                                             # type: ignore

from ae.gui.utils import (                                                                  # type: ignore
    MAX_FONT_SIZE, MIN_FONT_SIZE,
    register_package_images)
from ae.gui.app import MainAppBase                                                          # type: ignore

from .functions import ae_rgba                                                              # noqa: F401

# import `from [ae.enaml_app].widgets import...` fails with: ModuleNotFoundError: No module named 'ae.enaml_app.widgets'
# .. therefore moved these imports directly to enaml_lisz.main_view.enaml
# with enaml.imports():
#     # noinspection PyUnresolvedReferences
#     # pylint:disable=import-error
#     from ae.enaml_app.widgets import (                                                    # type: ignore # noqa: F401
#         FlowButton, FlowPopup, FontSizeEditPopup,
#         ThemeButton, ThemeContainer, ThemeField, ThemeMainWindow,
#         UserPreferencesPopup)


__version__ = '0.3.29'


register_package_images()   # register base image files of this portion

COMMAND_KEYS = {
    QtCore.Qt.Key_Escape:       'escape',
    QtCore.Qt.Key_Tab:          'tab',
    QtCore.Qt.Key_Backspace:    'backspace',
    QtCore.Qt.Key_Delete:       'del',
    QtCore.Qt.Key_Enter:        'enter',
    QtCore.Qt.Key_Return:       'enter',
    QtCore.Qt.Key_Up:           'up',
    QtCore.Qt.Key_Down:         'down',
    QtCore.Qt.Key_Right:        'right',
    QtCore.Qt.Key_Left:         'left',
    QtCore.Qt.Key_Home:         'home',
    QtCore.Qt.Key_End:          'end',
    QtCore.Qt.Key_PageUp:       'pgup',
    QtCore.Qt.Key_PageDown:     'pgdown',
}


def convert_key_event_to_code(event) -> Tuple[str, str]:
    """ converts the Qt key-press/-release event into a modifiers and key code string. """
    mod_flag = int(event.modifiers())
    mod_parts = []
    if mod_flag & QtCore.Qt.AltModifier:
        mod_parts.append('Alt')
    if mod_flag & QtCore.Qt.ControlModifier:
        mod_parts.append('Ctrl')
    if mod_flag & QtCore.Qt.MetaModifier:
        mod_parts.append('Meta')
    if mod_flag & QtCore.Qt.ShiftModifier:
        mod_parts.append('Shift')
    modifiers = "".join(mod_parts)

    key_code = event.key()
    return modifiers, COMMAND_KEYS.get(key_code) or event.text() or str(key_code)


class FrameworkApp(QtApplication):
    """ enaml framework application class with atom member/attribute support. """
    app_state_flow_id = atom.api.Str()
    app_state_flow_path = atom.api.ContainerList()
    app_state_font_size = atom.api.Float()
    app_state_light_theme = atom.api.Bool()
    app_state_sound_volume = atom.api.Float()
    app_state_win_rectangle = atom.api.Tuple()

    app_state_cancel_ink = atom.api.List()
    app_state_confirm_ink = atom.api.List()
    app_state_create_ink = atom.api.List()
    app_state_delete_ink = atom.api.List()
    app_state_error_ink = atom.api.List()
    app_state_flow_id_ink = atom.api.List()
    app_state_flow_path_ink = atom.api.List()
    app_state_help_ink = atom.api.List()
    app_state_info_ink = atom.api.List()
    app_state_read_ink = atom.api.List()
    app_state_selected_ink = atom.api.List()
    app_state_unselected_ink = atom.api.List()
    app_state_update_ink = atom.api.List()
    app_state_warn_ink = atom.api.List()

    app_state_theme_names = atom.api.List()

    # shortcut attributes (indirectly saved as app states)
    landscape = atom.api.Bool()                             #: saved via win_rectangle app state
    max_font_size = atom.api.Float(default=MAX_FONT_SIZE)   #: maximum font size in pixels bound to window size
    min_font_size = atom.api.Float(default=MIN_FONT_SIZE)   #: minimum - " -
    mixed_back_ink = atom.api.List()                        #: mixed color - used for user pref dropdown opening button


class EnamlMainApp(MainAppBase):
    """ enaml application main base class """
    _original_key_press_handler: Optional[Callable] = None
    _original_key_release_handler: Optional[Callable] = None
    _original_win_resize_handler: Optional[Callable] = None

    # implementation of abstract method

    def init_app(self, framework_app_class: Type[FrameworkApp] = FrameworkApp
                 ) -> Tuple[Optional[Callable], Optional[Callable]]:
        """ initialize framework app instance and root window/layout, return GUI event loop start/stop methods. """

        # tried to fix pytest problem: re-use Application._instance instead of resetting it:
        # try:
        #     self.framework_app = framework_app_class()
        # except RuntimeError:
        #     self.framework_app = Application.instance()
        #     print(f"EnamlMainApp.init_app: re-using app instance {self.framework_app}")
        self.framework_app = framework_app_class()

        with enaml.imports():
            # pylint:disable=import-error,import-outside-toplevel
            # noinspection PyUnresolvedReferences
            from main_view import Main              # type: ignore

        self.framework_win = Main(app=self.framework_app, main_app=self)
        self.framework_win.title = self.app_title

        self.framework_win.observe('closed', self.win_closed)

        def _event_loop_start():
            """ start event loop and ensure on_app_build application event is firing when event loop is started.

            `on_app_build` is used e.g. to load the application resources and to set the initial focus.
            """
            # QtCore.QTimer().singleShot(0, partial(self.call_method, 'on_app_build'))  # pylint:disable=no-member
            self.call_method('on_app_build')
            self.framework_app.start()

        return _event_loop_start, self.framework_app.stop    # enaml event loop start and stop methods

    # overwritten and helper methods

    def cached_icon(self, icon_name: str, size: float, light: bool) -> Optional[Icon]:
        """ get cached image/icon object. """
        cached: Optional[CachedFile] = self.find_image(icon_name, height=size, light_theme=light)
        if cached:
            return cached.loaded_object
        return None

    def call_method_delayed(self, _delay: float, callback: Union[Callable, str], *args, **kwargs) -> Any:
        """ delay not implemented - for now redirect to direct call. """
        return self.call_method(callback, *args, **kwargs)

    def focus_widget(self, widget: Widget):
        """ set input/keyboard focus to the passed widget.

        :param widget:      widget/window that will receive the focus.
        """
        self.dpo(f"EnamlMainApp.focus_widget change focus from {self.focused_widget()} to {widget}")
        widget.set_focus()

    def focused_widget(self) -> str:
        """ enaml/qt focus debug helper method determining tool tip of the current qt widget with focus

        :return: tool tip string of current focus or app window status.
        """
        window = self.framework_win
        if not window:
            return "focused_widget:no framework_win"
        proxy = window.proxy
        if not proxy:
            return f"focused_widget:no proxy; framework_win={window}"
        widget = proxy.widget.focusWidget()
        if not widget:
            return f"focused_widget:no focus widget; {proxy=}"
        tip = widget.toolTip()
        if not tip:
            return f"focused_widget:empty toolTip; {widget=}"
        return tip

    def key_press_from_enaml(self, event):
        """ convert/normalize enaml/Qt key press/down event and pass it to MainAppBase key press dispatcher. """
        modifiers, key = convert_key_event_to_code(event)
        self.dpo(f"EnamlMainApp.key_press_from_enaml '{modifiers}_{key}'")
        if not self.key_press_from_framework(modifiers, key):
            self._original_key_press_handler(event)

    def key_release_from_enaml(self, event):
        """ convert/normalize enaml/Qt key release/up event and pass it to MainAppBase key release dispatcher. """
        modifiers, key = convert_key_event_to_code(event)
        self.dpo(f"EnamlMainApp.key_release_from_enaml '{modifiers}_{key}'")
        self.call_method('on_key_release', key)

    def load_images(self):
        """ overwrite un-cached image file register to use cached image files instead. """
        def load_icon(icon_file: CachedFile) -> Icon:
            """ load image file as icon object into file cache object. """
            data = read_file(icon_file.path, extra_mode='b')
            img = Image(data=data)
            ico = IconImage(image=img)
            return Icon(images=[ico])

        super().load_images()   # load from img file paths all files into :class:`~ae.files.RegisteredFile` instances
        self.image_files.reclassify(object_loader=load_icon)    # remap into :class:`~ae.files.CachedFile` instances

    def on_app_run(self):
        """ run/start app event handler. """
        super().on_app_run()
        self.framework_win.initial_position = self.win_rectangle[:2]
        self.framework_win.initial_size = self.win_rectangle[2:]
        self.framework_win.show()

    def on_flow_widget_focused(self):
        """ set focus to the widget referenced by the current flow id. """
        liw = self.widget_by_flow_id(self.flow_id)
        self.dpo(f"EnamlMainApp.on_flow_widget_focused() '{self.flow_id}'"
                 f" {liw} hasFocus={liw.has_focus() if hasattr(liw, 'has_focus') else ''}")
        if liw and not liw.has_focus():
            self.focus_widget(liw)

    def on_font_size_change(self, _flow_key: str, event_kwargs: Dict[str, Any]) -> bool:
        """ font size app state flow change confirmation event handler.

        :param _flow_key:       flow key.
        :param event_kwargs:    event kwargs with key `'font_size'` containing the font_size in pixels.
        :return:                True to confirm change of flow id.
        """
        font_size: float = event_kwargs['font_size']
        self.vpo(f"EnamlMainApp.on_font_size_change to {font_size}")
        self.change_app_state('font_size', font_size)
        return True

    def open_popup(self, popup_class: Type, **popup_kwargs) -> Widget:
        """ open Popup and set focus to the first widget.

        :param popup_class:     class of the Popup widget/window.
        :param popup_kwargs:    args to instantiate and show/open the popup.
        :return:                instance of the popup widget.
        """
        if 'opener' not in popup_kwargs:
            popup_kwargs['opener'] = self.framework_win

        popup_instance = super().open_popup(popup_class, **popup_kwargs)

        self.dpo(f"EnamlMainApp.open_popup instance={popup_instance} win_type={popup_instance.window_type}")
        self.focus_widget(popup_instance.children[0].children[0])    # first children[0] is the container
        return popup_instance

    def play_sound(self, sound_name: str):
        """ play audio/sound file. """
        self.dpo(f"EnamlMainApp.play_sound {sound_name}")
        file = self.find_sound(sound_name)
        if file:
            try:
                # pylint:disable=no-name-in-module,import-outside-toplevel
                from PyQt5.QtMultimedia import QSoundEffect
                from PyQt5.QtCore import QUrl
                # pylint:enable=no-name-in-module,import-outside-toplevel

                sound_obj = QSoundEffect()
                sound_obj.setSource(QUrl.fromLocalFile(file.path))
                sound_obj.setVolume(
                    file.properties.get('volume', 1.0) * self.framework_app.app_state_sound_volume)
                sound_obj.play()
            except Exception as ex:     # pylint:disable=broad-except
                self.po(f"   *  EnamlMainApp.play_sound({sound_name}) exception {ex}")
        else:
            self.dpo(f"EnamlMainApp.play_sound({sound_name}) not found")

    def user_preference_color_selected(self, color_name: str, dialog):
        """ ColorDialog callback. """
        self.dpo(F"EnamlMainApp.user_preference_color_selected {color_name} {dialog.selected_color}")
        if dialog.selected_color:
            self.change_app_state(color_name, ae_rgba(dialog.selected_color))

    def win_activated(self, main_window: Any):
        """ main window activated event handler, called only once on app startup via widgets.enaml/ThemeMainWindow.

        :param main_window:
        :return:
        """
        qt_window = main_window.proxy.widget
        assert main_window == self.framework_win, f"win_activated {main_window} != {self.framework_win}"

        assert not self._original_key_press_handler, "win_activated has to be called only once at window open"
        self._original_key_press_handler = qt_window.keyPressEvent
        qt_window.keyPressEvent = self.key_press_from_enaml

        assert not self._original_key_release_handler, "win_activated has to be called only once at window open"
        self._original_key_release_handler = qt_window.keyReleaseEvent
        qt_window.keyReleaseEvent = self.key_release_from_enaml

        assert not self._original_win_resize_handler, "win_activated has to be called only once at window open"
        self._original_win_resize_handler = qt_window.resizeEvent
        qt_window.resizeEvent = self.win_resize_from_enaml

    def win_closed(self, changed: dict):
        """ callback fired on close of Main window to save/restore framework_win.geometry on app exit/start.

        :param changed:    qt/enaml changed event dict.

        .. note::
            neither self.framework_app.stop() nor self.framework_app._ qapp.exit(exit_code) trigger window closed event.

        """
        self.dpo(f"EnamlMainApp.win_closed({changed}) called")

        qt_window = self.framework_win.proxy.widget
        qt_window.resizeEvent = self._original_win_resize_handler
        qt_window.keyPressEvent = self._original_key_press_handler
        qt_window.keyReleaseEvent = self._original_key_release_handler

        geo = self.framework_win.geometry()
        self.win_pos_size_change(geo.x, geo.y, geo.width, geo.height)

        self.save_app_states()
        self.call_method('on_app_stopped')

    def win_resize_from_enaml(self, event):
        """ convert/normalize enaml/Qt key press/down event and pass it to MainAppBase key press dispatcher. """
        win_size = event.size()
        self.dpo(f"EnamlMainApp.win_resize_from_enaml {self.framework_app.landscape} {event.oldSize()}=>{win_size}")
        self.win_pos_size_change(*self.win_rectangle[:2], win_size.width(), win_size.height())
        self._original_win_resize_handler(event)
