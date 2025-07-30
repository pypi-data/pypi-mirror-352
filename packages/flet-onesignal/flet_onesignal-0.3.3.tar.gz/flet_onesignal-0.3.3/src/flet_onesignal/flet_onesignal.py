import json
from flet.core.ref import Ref
from typing import Any, Optional
from dataclasses import dataclass
from flet.core.control import Control
from flet_onesignal.languages import Language
from flet.core.event_handler import EventHandler
from flet.core.control_event import ControlEvent
from flet.core.types import OptionalEventCallable, OptionalControlEventCallable


@dataclass
class OneSignalSettings:
    app_id: str


@dataclass
class OneSignalChangeEvent(ControlEvent):
    def __init__(self, e: ControlEvent):
        super().__init__(e.target, e.name, e.data, e.control, e.page)
        data = json.loads(e.data)
        self.notification_received: dict = data.get("json_data")
        self.notification_opened: dict = data.get("json_data")
        self.click_in_app_messages : dict = data.get("json_data")
        self.will_display_in_app_messages: dict = data.get("json_data")
        self.did_display_in_app_messages: dict = data.get("json_data")
        self.will_dismiss_in_app_messages: dict = data.get("json_data")
        self.did_dismiss_in_app_messages: dict = data.get("json_data")


class OneSignal(Control):
    """
    A control that allows you to send push notifications and messages to mobile applications. This control makes it easy
    to integrate your iOS and/or Android applications with OneSignal.

    This control is not visual and should be added to the `page.overlay` list.
    """

    def __init__(
        self,
        # Control
        #
        ref: Optional[Ref] = None,
        data: Any = None,
        settings: OneSignalSettings = None,
        on_notification_opened: OptionalEventCallable[OneSignalChangeEvent] = None,
        on_notification_received: OptionalEventCallable[OneSignalChangeEvent] = None,
        on_click_in_app_messages: OptionalEventCallable[OneSignalChangeEvent] = None,
        on_will_display_in_app_messages: OptionalEventCallable[OneSignalChangeEvent] = None,
        on_did_display_in_app_messages: OptionalEventCallable[OneSignalChangeEvent] = None,
        on_will_dismiss_in_app_messages: OptionalEventCallable[OneSignalChangeEvent] = None,
        on_did_dismiss_in_app_messages: OptionalEventCallable[OneSignalChangeEvent] = None,
        on_error: OptionalControlEventCallable = None,
    ):
        Control.__init__(
            self,
            ref=ref,
            data=data,
        )
        # handlers attributes
        self.__on_notification_opened = EventHandler(result_converter=lambda e: OneSignalChangeEvent(e))
        self._add_event_handler(event_name="notification_opened", handler=self.__on_notification_opened.get_handler())
        self.__on_notification_received = EventHandler(result_converter=lambda e: OneSignalChangeEvent(e))
        self._add_event_handler(event_name="notification_received", handler=self.__on_notification_received.get_handler())
        self.__on_click_in_app_messages = EventHandler(result_converter=lambda e: OneSignalChangeEvent(e))
        self._add_event_handler(event_name="click_in_app_messages", handler=self.__on_click_in_app_messages.get_handler())
        self.__on_will_display_in_app_messages = EventHandler(result_converter=lambda e: OneSignalChangeEvent(e))
        self._add_event_handler(event_name="will_display_in_app_messages", handler=self.__on_will_display_in_app_messages.get_handler())
        self.__on_did_display_in_app_messages = EventHandler(result_converter=lambda e: OneSignalChangeEvent(e))
        self._add_event_handler(event_name="did_display_in_app_messages", handler=self.__on_did_display_in_app_messages.get_handler())
        self.__on_will_dismiss_in_app_messages = EventHandler(result_converter=lambda e: OneSignalChangeEvent(e))
        self._add_event_handler(event_name="will_dismiss_in_app_messages", handler=self.__on_will_dismiss_in_app_messages.get_handler())
        self.__on_did_dismiss_in_app_messages = EventHandler(result_converter=lambda e: OneSignalChangeEvent(e))
        self._add_event_handler(event_name="did_dismiss_in_app_messages", handler=self.__on_did_dismiss_in_app_messages.get_handler())
        #
        #
        self.on_notification_opened = on_notification_opened
        self.on_notification_received = on_notification_received
        self.on_click_in_app_messages = on_click_in_app_messages
        self.on_will_display_in_app_messages = on_will_display_in_app_messages
        self.on_did_display_in_app_messages = on_did_display_in_app_messages
        self.on_will_dismiss_in_app_messages = on_will_dismiss_in_app_messages
        self.on_did_dismiss_in_app_messages = on_did_dismiss_in_app_messages
        self.on_error = on_error
        self.settings = settings

    def _get_control_name(self):
        return "flet_onesignal"

    def before_update(self):
        if self.settings is not None:
            self._set_attr_json("settings", self.settings)

    def get_onesignal_id(self, wait_timeout: Optional[float] = 25) -> str:
        """Returns the OneSignal ID for the current user, which may be None."""

        result = self.invoke_method(
            method_name="get_onesignal_id",
            wait_for_result=True,
            wait_timeout=wait_timeout
        )

        return result

    async def get_onesignal_id_async(self, wait_timeout: Optional[float] = 25) -> str:
        """Returns the OneSignal ID for the current user, which may be None."""

        result = await self.invoke_method_async(
            method_name="get_onesignal_id",
            wait_for_result=True,
            wait_timeout=wait_timeout
        )

        return result

    def get_external_user_id(self, wait_timeout: Optional[float] = 25):
        """Returns the External ID for the current user, which may be None."""

        result = self.invoke_method(
            method_name="get_external_user_id",
            wait_for_result=True,
            wait_timeout=wait_timeout
        )

        return result

    async def get_external_user_id_async(self, wait_timeout: Optional[float] = 25):
        """Returns the External ID for the current user, which may be None."""

        result = await self.invoke_method_async(
            method_name="get_external_user_id",
            wait_for_result=True,
            wait_timeout=wait_timeout
        )

        return result

    def login(self, external_user_id: str) -> bool:
        """Login to OneSignal under the user identified by the [external_user_id] provided. The act of logging a user into
        the OneSignal SDK will switch the user context to that specific user."""

        self.invoke_method(
            method_name="login",
            arguments={"external_user_id": external_user_id},
            wait_for_result=True,
        )

        if  self.get_external_user_id():
            return True

        return False

    async def login_async(self, external_user_id: str) -> bool:
        """Login to OneSignal under the user identified by the [external_user_id] provided. The act of logging a user into
        the OneSignal SDK will switch the user context to that specific user."""

        await self.invoke_method_async(
            method_name="login",
            arguments={"external_user_id": external_user_id},
            wait_for_result=True,
        )

        if await self.get_external_user_id_async():
            return True

        return False


    def logout(self) -> None:
        """Logout the user previously logged in via [login]. The user property now references a new device-scoped user.
        A device-scoped user has no user identity that can later be retrieved, except through this device as long as the
        app remains installed and the app data is not cleared."""

        self.invoke_method(
            method_name="logout",
            wait_for_result=True,
        )

    async def logout_async(self) -> None:
        """Logout the user previously logged in via [login]. The user property now references a new device-scoped user.
        A device-scoped user has no user identity that can later be retrieved, except through this device as long as the
        app remains installed and the app data is not cleared."""

        await self.invoke_method_async(
            method_name="logout",
            wait_for_result=True,
        )

    def add_alias(self, alias: str, id_alias: any) -> None:
        """Set an [alias] for the current user. If this [alias] label already exists on this user, it will be
        overwritten with the new alias [id]."""

        args = {
            'alias': alias,
            'id_alias': id_alias,
        }

        self.invoke_method(
            method_name="add_alias",
            arguments=args,
            wait_for_result=True,
        )

    async def add_alias_async(self, alias: str, id_alias: any) -> None:
        """Set an [alias] for the current user. If this [alias] label already exists on this user, it will be
        overwritten with the new alias [id]."""

        args = {
            'alias': alias,
            'id_alias': id_alias,
        }

        await self.invoke_method_async(
            method_name="add_alias",
            arguments=args,
            wait_for_result=True,
        )

    def remove_alias(self, alias: str) -> None:
        """Remove an [alias] from the current user."""

        self.invoke_method(
            method_name="remove_alias",
            arguments={'alias': alias},
            wait_for_result=True,
        )

    async def remove_alias_async(self, alias: str) -> None:
        """Remove an [alias] from the current user."""

        await self.invoke_method_async(
            method_name="remove_alias",
            arguments={'alias': alias},
            wait_for_result=True,
        )

    def set_language(self, language_code: str = 'en') -> str:
        """Sets the user's language.
        Sets the user's language to [language] this also applies to the email and/or SMS player if those are logged in
        on the device."""

        if language_code in Language._value2member_map_:
            self.invoke_method(
                method_name="set_language",
                arguments={'language': language_code},
                wait_for_result=True,
            )
            return 'Language set successfully.'

        return 'Language not found.'

    async def set_language_async(self, language_code: str = 'en') -> str:
        """Sets the user's language.
        Sets the user's language to [language] this also applies to the email and/or SMS player if those are logged in
        on the device."""

        if language_code in Language._value2member_map_:
            await self.invoke_method_async(
                method_name="set_language",
                arguments={'language': language_code},
                wait_for_result=True,
            )
            return 'Language set successfully.'

        return 'Language not found.'

    def remove_notification(self, notification_id: int) -> None:
        """Removes a single notification on Android devices."""

        platform = self.page.platform.value

        if platform == 'android':
            self.invoke_method(
                method_name="remove_notification",
                arguments={"notification_id": str(notification_id)},
                wait_for_result=True,
            )

    async def remove_notification_async(self, notification_id: int) -> None:
        """Removes a single notification on Android devices."""

        platform = self.page.platform.value

        if platform == 'android':
            await self.invoke_method_async(
                method_name="remove_notification",
                arguments={"notification_id": str(notification_id)},
                wait_for_result=True,
            )

    def remove_grouped_notifications(self, notification_group: str) -> None:
        """Removes a grouped notification on Android devices."""

        platform = self.page.platform.value

        if platform == 'android':
            self.invoke_method(
                method_name="remove_grouped_notifications",
                arguments={"notification_group": notification_group},
                wait_for_result=True,
            )

    async def remove_grouped_notifications_async(self, notification_group: str) -> None:
        """Removes a grouped notification on Android devices."""

        platform = self.page.platform.value

        if platform == 'android':
            await self.invoke_method_async(
                method_name="remove_grouped_notifications",
                arguments={"notification_group": notification_group},
                wait_for_result=True,
            )

    def clear_all_notifications(self) -> None:
        """Removes all OneSignal notifications."""

        self.invoke_method(
            method_name="clear_all_notifications",
            wait_for_result=True,
        )

    async def clear_all_notifications_async(self) -> None:
        """Removes all OneSignal notifications."""

        await self.invoke_method_async(
            method_name="clear_all_notifications",
            wait_for_result=True,
        )

    def consent_required(self, consent: bool = True) -> None:
        """Allows you to completely disable the SDK until your app calls the OneSignal.consentGiven(true) function.
        This is useful if you want to show a Terms and Conditions or privacy popup for GDPR."""

        data_str = json.dumps({"consent": consent})

        self.invoke_method(
            method_name="consent_required",
            arguments={'data': data_str},
            wait_for_result=True,
        )

    async def consent_required_async(self, consent: bool = True) -> None:
        """Allows you to completely disable the SDK until your app calls the OneSignal.consentGiven(true) function.
        This is useful if you want to show a Terms and Conditions or privacy popup for GDPR."""

        data_str = json.dumps({"consent": consent})

        await self.invoke_method_async(
            method_name="consent_required",
            arguments={'data': data_str},
            wait_for_result=True,
        )

    def request_permission(self, fallback_to_settings: bool = True,  wait_timeout: Optional[float] = 25) -> bool:
        """Prompt the user for permission to receive push notifications. This will display the native system prompt to
        request push notification permission."""

        data_str = json.dumps({"fallback_to_settings": fallback_to_settings})

        result = self.invoke_method(
            method_name="request_permission",
            arguments={'data': data_str},
            wait_for_result=True,
            wait_timeout=wait_timeout
        )

        return result == "true"

    async def request_permission_async(self, fallback_to_settings: bool = True,  wait_timeout: Optional[float] = 25) -> bool:
        """Prompt the user for permission to receive push notifications. This will display the native system prompt to
        request push notification permission."""

        data_str = json.dumps({"fallback_to_settings": fallback_to_settings})

        result = await self.invoke_method_async(
            method_name="request_permission",
            arguments={'data': data_str},
            wait_for_result=True,
            wait_timeout=wait_timeout
        )

        return result == "true"

    # Métodos para integração com o OneSignal Notifications
    def register_for_provisional_authorization(self, wait_timeout: Optional[float] = 25) -> bool:
        """Instead of having to prompt the user for permission to send them push notifications, your app can request
        provisional authorization."""

        result = self.invoke_method(
            method_name="register_for_provisional_authorization",
            wait_for_result=True,
            wait_timeout=wait_timeout
        )
        return result == "true"

    async def register_for_provisional_authorization_async(self, wait_timeout: Optional[float] = 25) -> bool:
        """Instead of having to prompt the user for permission to send them push notifications, your app can request
        provisional authorization."""

        result = await self.invoke_method_async(
            method_name="register_for_provisional_authorization",
            wait_for_result=True,
            wait_timeout=wait_timeout
        )
        return result == "true"

    def can_request_permission(self, wait_timeout: Optional[float] = 25) -> bool:
        """Whether attempting to request notification permission will show a prompt. Returns true if the device has not
        been prompted for push notification permission already."""

        result = self.invoke_method(
            method_name="can_request_permission",
            wait_for_result=True,
            wait_timeout=wait_timeout
        )
        return result == "true"

    async def can_request_permission_async(self, wait_timeout: Optional[float] = 25) -> bool:
        """Whether attempting to request notification permission will show a prompt. Returns true if the device has not
        been prompted for push notification permission already."""

        result = await self.invoke_method_async(
            method_name="can_request_permission",
            wait_for_result=True,
            wait_timeout=wait_timeout
        )
        return result == "true"

    def opt_in(self) -> None:
        """Call this method to receive push notifications on the device or to resume receiving of push notifications
        after calling optOut. If needed, this method will prompt the user for push notifications permission."""

        self.invoke_method(
            method_name="opt_in",
            wait_for_result=True,
        )

    async def opt_in_async(self) -> None:
        """Call this method to receive push notifications on the device or to resume receiving of push notifications
        after calling optOut. If needed, this method will prompt the user for push notifications permission."""

        await self.invoke_method_async(
            method_name="opt_in",
            wait_for_result=True,
        )

    def opt_out(self) -> None:
        """If at any point you want the user to stop receiving push notifications on the current device (regardless of
        system-level permission status), you can call this method to opt out."""

        self.invoke_method(
            method_name="opt_in",
            wait_for_result=True,
        )

    async def opt_out_async(self) -> None:
        """If at any point you want the user to stop receiving push notifications on the current device (regardless of
        system-level permission status), you can call this method to opt out."""

        await self.invoke_method_async(
            method_name="opt_in",
            wait_for_result=True,
        )

    def prevent_default(self, notification_id: str) -> None:
        """The notification willDisplay listener is called whenever a notification arrives and the application is in
        foreground"""

        self.invoke_method(
            method_name="prevent_default",
            arguments={"notification_id": notification_id},
        )

    @property
    def on_notification_opened(
            self,
    ) -> OptionalEventCallable[OneSignalChangeEvent]:
        return self.__on_notification_opened.handler

    @on_notification_opened.setter
    def on_notification_opened(
            self, handler: OptionalEventCallable[OneSignalChangeEvent]
    ):
        self.__on_notification_opened.handler = handler
        self._set_attr("notification_opened", True if handler is not None else None)

    @property
    def on_notification_received(
            self,
    ) -> OptionalEventCallable[OneSignalChangeEvent]:
        return self.__on_notification_received.handler

    @on_notification_received.setter
    def on_notification_received(
            self, handler: OptionalEventCallable[OneSignalChangeEvent]
    ):
        self.__on_notification_received.handler = handler
        self._set_attr("notification_received", True if handler is not None else None)

    @property
    def on_click_in_app_messages(
            self,
    ) -> OptionalEventCallable[OneSignalChangeEvent]:
        return self.__on_click_in_app_messages.handler

    @on_click_in_app_messages.setter
    def on_click_in_app_messages(
            self, handler: OptionalEventCallable[OneSignalChangeEvent]
    ):
        self.__on_click_in_app_messages.handler = handler
        self._set_attr("click_in_app_messages", True if handler is not None else None)

    @property
    def on_will_display_in_app_messages(
            self,
    ) -> OptionalEventCallable[OneSignalChangeEvent]:
        return self.__on_will_display_in_app_messages.handler

    @on_will_display_in_app_messages.setter
    def on_will_display_in_app_messages(
            self, handler: OptionalEventCallable[OneSignalChangeEvent]
    ):
        self.__on_will_display_in_app_messages.handler = handler
        self._set_attr("will_display_in_app_messages", True if handler is not None else None)

    @property
    def on_did_display_in_app_messages(
            self,
    ) -> OptionalEventCallable[OneSignalChangeEvent]:
        return self.__on_did_display_in_app_messages.handler

    @on_did_display_in_app_messages.setter
    def on_did_display_in_app_messages(
            self, handler: OptionalEventCallable[OneSignalChangeEvent]
    ):
        self.__on_did_display_in_app_messages.handler = handler
        self._set_attr("did_display_in_app_messages", True if handler is not None else None)

    @property
    def on_will_dismiss_in_app_messages(
            self,
    ) -> OptionalEventCallable[OneSignalChangeEvent]:
        return self.__on_will_dismiss_in_app_messages.handler

    @on_will_dismiss_in_app_messages.setter
    def on_will_dismiss_in_app_messages(
            self, handler: OptionalEventCallable[OneSignalChangeEvent]
    ):
        self.__on_will_dismiss_in_app_messages.handler = handler
        self._set_attr("will_dismiss_in_app_messages", True if handler is not None else None)

    @property
    def on_did_dismiss_in_app_messages(
            self,
    ) -> OptionalEventCallable[OneSignalChangeEvent]:
        return self.__on_did_dismiss_in_app_messages.handler

    @on_did_dismiss_in_app_messages.setter
    def on_did_dismiss_in_app_messages(
            self, handler: OptionalEventCallable[OneSignalChangeEvent]
    ):
        self.__on_did_dismiss_in_app_messages.handler = handler
        self._set_attr("did_dismiss_in_app_messages", True if handler is not None else None)

    @property
    def on_error(self) -> OptionalControlEventCallable:
        return self._get_attr("error")

    @on_error.setter
    def on_error(self, handler: OptionalControlEventCallable):
        self._add_event_handler("error", handler)
