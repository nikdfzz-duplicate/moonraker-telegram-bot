import configparser
import re
from typing import Any, Callable, List, Optional, Union


class ConfigHelper:
    _SECTION: str
    _KNOWN_ITEMS: List[str]

    def __init__(self, config: configparser.ConfigParser):
        self._config = config
        self._parsing_errors: List[str] = []

    @property
    def unknown_fields(self) -> str:
        return self._check_config()

    @property
    def parsing_errors(self) -> str:
        if self._parsing_errors:
            return f"Config errors in section [{self._SECTION}]:\n  " + "\n  ".join(self._parsing_errors) + "\n"
        else:
            return ""

    def _check_config(self) -> str:
        if not self._config.has_section(self._SECTION):
            return ""
        unknwn = list(
            map(
                lambda fil: f"  {fil[0]}: {fil[1]}\n",
                filter(lambda el: el[0] not in self._KNOWN_ITEMS, self._config.items(self._SECTION)),
            )
        )
        if unknwn:
            return f"Unknown/bad items in section [{self._SECTION}]:\n{''.join(unknwn)}\n"
        else:
            return ""

    def _check_numerical_value(
        self,
        option: str,
        value: Union[int, float],
        above: Optional[Union[int, float]] = None,
        below: Optional[Union[int, float]] = None,
        min_value: Optional[Union[int, float]] = None,
        max_value: Optional[Union[int, float]] = None,
    ) -> None:
        if above is not None and value <= above:
            self._parsing_errors.append(f"Option '{option}: {value}': value is not above {above}")
        if below is not None and value >= below:
            self._parsing_errors.append(f"Option '{option}: {value}': value is not below {below}")
        if min_value is not None and value < min_value:
            self._parsing_errors.append(f"Option '{option}: {value}': value is below minimum value {min_value}")
        if max_value is not None and value > max_value:
            self._parsing_errors.append(f"Option '{option}: {value}': value is above maximum value {max_value}")

    def _get_option_value(self, func: Callable, option: str, default: Optional[Any] = None) -> Any:
        try:
            val = func(self._SECTION, option, fallback=default) if default is not None else func(self._SECTION, option)
        except Exception as ex:
            if default is not None:
                self._parsing_errors.append(f"Error parsing option ({option}) \n {ex}")
                val = default
            else:
                raise ex
        return val

    def _getint(
        self,
        option: str,
        default: Optional[int] = None,
        above: Optional[Union[int, float]] = None,
        below: Optional[Union[int, float]] = None,
        min_value: Optional[Union[int, float]] = None,
        max_value: Optional[Union[int, float]] = None,
    ) -> int:
        val = self._get_option_value(self._config.getint, option, default)
        self._check_numerical_value(option, val, above, below, min_value, max_value)
        return val

    def _getfloat(
        self,
        option: str,
        default: Optional[float] = None,
        above: Optional[Union[int, float]] = None,
        below: Optional[Union[int, float]] = None,
        min_value: Optional[Union[int, float]] = None,
        max_value: Optional[Union[int, float]] = None,
    ) -> float:
        val = self._get_option_value(self._config.getfloat, option, default)
        self._check_numerical_value(option, val, above, below, min_value, max_value)
        return val

    def _getstring(self, option: str, default: Optional[str] = None) -> str:
        val = self._get_option_value(self._config.get, option, default)
        return val

    def _getboolean(self, option: str, default: Optional[bool] = None) -> bool:
        val = self._get_option_value(self._config.getboolean, option, default)
        return val

    def _getlist(self, option: str, default: Optional[List] = None, el_type: Any = str) -> List:
        if self._config.has_option(self._SECTION, option):
            try:
                val = [el_type(el.strip()) for el in self._getstring(option).split(",")]
            except Exception as ex:
                if default is not None:
                    self._parsing_errors.append(f"Error parsing option ({option}) \n {ex}")
                    val = default
                else:
                    # Todo: reaise some parsing exception
                    pass
        elif default is not None:
            val = default
        else:
            # Todo: reaise some parsing exception
            pass

        return val


class BotConfig(ConfigHelper):
    _SECTION = "bot"
    _KNOWN_ITEMS = [
        "server",
        "socks_proxy",
        "bot_token",
        "chat_id",
        "debug",
        "log_parser",
        "log_path",
        "power_device",
        "light_device",
        "user",
        "password",
        "api_token",
    ]

    def __init__(self, config: configparser.ConfigParser):
        super().__init__(config)

        self.host: str = self._getstring("server", default="localhost")
        self.socks_proxy: str = self._getstring("socks_proxy", default="")
        self.token: str = self._getstring("bot_token")
        self.api_url: str = self._getstring("api_url", default="https://api.telegram.org/bot")
        self.chat_id: int = self._getint("chat_id", default=0)
        self.debug: bool = self._getboolean("debug", default=False)
        self.log_parser: bool = self._getboolean("log_parser", default=False)
        self.log_path: str = self._getstring("log_path", default="/tmp")
        self.poweroff_device_name: str = self._getstring("power_device", default="")
        self.light_device_name: str = self._getstring("light_device", default="")
        self.user: str = self._getstring("user", default="")
        self.passwd: str = self._getstring("password", default="")
        self.api_token: str = self._getstring("api_token", default="")


class CameraConfig(ConfigHelper):
    _SECTION = "camera"
    _KNOWN_ITEMS = [
        "host",
        "threads",
        "flip_vertically",
        "flip_horizontally",
        "rotate",
        "fourcc",
        "video_duration",
        "video_buffer_size",
        "fps",
        "light_control_timeout",
        "picture_quality",
    ]

    def __init__(self, config: configparser.ConfigParser):
        super().__init__(config)
        self.enabled: bool = config.has_section(self._SECTION)
        self.host: str = self._getstring("host", default="")
        # self.threads: int = self._getint( "threads", fallback=int(len(os.sched_getaffinity(0)) / 2))
        self.threads: int = self._getint("threads", default=2, min_value=0)
        self.flip_vertically: bool = self._getboolean("flip_vertically", default=False)
        self.flip_horizontally: bool = self._getboolean("flip_horizontally", default=False)
        self.rotate: str = self._getstring("rotate", default="")
        self.fourcc: str = self._getstring("fourcc", default="x264")
        self.video_duration: int = self._getint("video_duration", default=5)
        self.video_buffer_size: int = self._getint("video_buffer_size", default=2)
        self.stream_fps: int = self._getint("fps", default=0)
        self.light_timeout: int = self._getint("light_control_timeout", default=0)
        self.picture_quality: str = self._getstring("picture_quality", default="high")


class NotifierConfig(ConfigHelper):
    _SECTION = "progress_notification"
    _KNOWN_ITEMS = ["percent", "height", "time", "groups", "group_only"]

    def __init__(self, config: configparser.ConfigParser):
        super().__init__(config)
        self.enabled: bool = config.has_section(self._SECTION)
        self.percent: int = self._getint("percent", default=0)
        self.height: float = self._getfloat("height", default=0)
        self.interval: int = self._getint("time", default=0)
        self.notify_groups: List[int] = self._getlist("groups", default=[], el_type=int)
        self.group_only: bool = self._getboolean("group_only", default=False)


class TimelapseConfig(ConfigHelper):
    _SECTION = "timelapse"
    _KNOWN_ITEMS = [
        "basedir",
        "copy_finished_timelapse_dir",
        "cleanup",
        "manual_mode",
        "height",
        "time",
        "target_fps",
        "min_lapse_duration",
        "max_lapse_duration",
        "last_frame_duration",
        "after_lapse_gcode",
        "send_finished_lapse",
        "after_photo_gcode",
    ]

    def __init__(self, config: configparser.ConfigParser):
        super().__init__(config)
        self.enabled: bool = config.has_section(self._SECTION)
        self.base_dir: str = self._getstring("basedir", default="/tmp/timelapse")  # Fixme: relative path failed! ~/timelapse
        self.ready_dir: str = self._getstring("copy_finished_timelapse_dir", default="")  # Fixme: relative path failed! ~/timelapse
        self.cleanup: bool = self._getboolean("cleanup", default=True)
        self.mode_manual: bool = self._getboolean("manual_mode", default=False)
        self.height: float = self._getfloat("height", default=0.0)
        self.interval: int = self._getint("time", default=0)
        self.target_fps: int = self._getint("target_fps", default=15)
        self.min_lapse_duration: int = self._getint("min_lapse_duration", default=0)
        self.max_lapse_duration: int = self._getint("max_lapse_duration", default=0)
        self.last_frame_duration: int = self._getint("last_frame_duration", default=5)

        # Todo: add to runtime params section!
        self.after_lapse_gcode: str = self._getstring("after_lapse_gcode", default="")
        self.send_finished_lapse: bool = self._getboolean("send_finished_lapse", default=True)
        self.after_photo_gcode: str = self._getstring("after_photo_gcode", default="")


class TelegramUIConfig(ConfigHelper):
    _SECTION = "telegram_ui"
    _KNOWN_ITEMS = [
        "silent_progress",
        "silent_commands",
        "silent_status",
        "pin_status_single_message",
        "status_message_content",
        "buttons",
        "require_confirmation_macro",
        "include_macros_in_command_list",
        "disabled_macros",
        "show_hidden_macros",
        "eta_source",
        "status_message_sensors",
        "status_message_heaters",
        "status_message_devices",
        "status_message_temperature_fans",
        "status_message_m117_update",
    ]
    _MESSAGE_CONTENT = [
        "progress",
        "height",
        "filament_length",
        "filament_weight",
        "print_duration",
        "eta",
        "finish_time",
        "m117_status",
        "tgnotify_status",
        "last_update_time",
    ]

    def __init__(self, config: configparser.ConfigParser):
        super().__init__(config)
        self.silent_progress: bool = self._getboolean("silent_progress", default=False)
        self.silent_commands: bool = self._getboolean("silent_commands", default=False)
        self.silent_status: bool = self._getboolean("silent_status", default=False)
        self.pin_status_single_message: bool = self._getboolean("pin_status_single_message", default=False)  # Todo: implement
        self.status_message_content: List[str] = self._getlist("status_message_content", default=self._MESSAGE_CONTENT)

        self.buttons: List[List[str]] = list(
            map(
                lambda el: list(
                    map(
                        lambda iel: f"/{iel.strip()}",
                        el.replace("[", "").replace("]", "").split(","),
                    )
                ),
                re.findall(r"\[.[^\]]*\]", self._getstring("buttons", default="[status,pause,cancel,resume],[files,emergency,macros,shutdown]")),
            )
        )
        self.buttons_default: bool = bool(not config.has_option(self._SECTION, "buttons"))
        self.require_confirmation_macro: bool = self._getboolean("require_confirmation_macro", default=True)
        self.include_macros_in_command_list: bool = self._getboolean("include_macros_in_command_list", default=True)
        self.disabled_macros: List[str] = self._getlist("disabled_macros", default=[])
        self.show_hidden_macros: bool = self._getboolean("show_hidden_macros", default=False)
        self.eta_source: str = self._getstring("eta_source", default="slicer")
        self.status_message_sensors: List[str] = self._getlist("status_message_sensors", default=[])
        self.status_message_heaters: List[str] = self._getlist("status_message_heaters", default=[])
        self.status_message_temp_fans: List[str] = self._getlist("status_message_temperature_fans", default=[])
        self.status_message_devices: List[str] = self._getlist("status_message_devices", default=[])
        self.status_message_m117_update: bool = self._getboolean("status_message_m117_update", default=False)


class ConfigWrapper:
    def __init__(self, config: configparser.ConfigParser):
        self.bot = BotConfig(config)
        self.camera = CameraConfig(config)
        self.notifications = NotifierConfig(config)
        self.timelapse = TimelapseConfig(config)
        self.telegram_ui = TelegramUIConfig(config)
        self.unknown_fields = self.bot.unknown_fields + self.camera.unknown_fields + self.notifications.unknown_fields + self.timelapse.unknown_fields + self.telegram_ui.unknown_fields
        self.parsing_errors = self.bot.parsing_errors + self.camera.parsing_errors + self.notifications.parsing_errors + self.timelapse.parsing_errors + self.telegram_ui.parsing_errors
