import 'dart:convert';
import 'package:flet/flet.dart';
import 'package:flet_onesignal/src/utils/funcs.dart';
import 'package:flutter/material.dart';
import 'package:onesignal_flutter/onesignal_flutter.dart';

class FletOneSignalControl extends StatefulWidget {
  final Control? parent;
  final Control control;
  final FletControlBackend backend;

  const FletOneSignalControl({
    super.key,
    required this.parent,
    required this.control,
    required this.backend,
  });

  @override
  State<FletOneSignalControl> createState() => _FletOneSignalControlState();
}

class _FletOneSignalControlState extends State<FletOneSignalControl>
    with FletStoreMixin {
  @override
  void initState() {
    super.initState();
    _initializeOneSignal();
  }

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    _setupNotificationHandler();
  }

  void _initializeOneSignal() {
    final settings = widget.control.attrString("settings", "{}")!;

    Map<String, dynamic> settingsData;

    if (settings != "{}") {
      try {
        settingsData = jsonDecode(settings);
        final appId = settingsData["app_id"] ?? "DEFAULT_APP_ID";
        OneSignal.initialize(appId);
      } catch (error, stackTrace) {
        debugPrint("Error:\nerror: $error\nstackTrace: $stackTrace");
        handleFlutterError(
          method: "_initializeOneSignal",
          error: error,
          stackTrace: stackTrace,
          trigger: widget.backend.triggerControlEvent,
          controlId: widget.control.id,
        );
      }
    }
  }

  void _setupNotificationHandler() {
    OneSignal.Notifications.addClickListener((event) {
      try {
        debugPrint("Notifications-addClickListener");

        final jsonData = jsonEncode({
          "json_data": event.notification.jsonRepresentation(),
        });

        widget.backend.triggerControlEvent(
          widget.control.id,
          "notification_received",
          jsonData,
        );
      } catch (error, stackTrace) {
        debugPrint("Error:\nerror: $error\nstackTrace: $stackTrace");
        handleFlutterError(
          method: "_setupNotificationHandler",
          error: error,
          stackTrace: stackTrace,
          trigger: widget.backend.triggerControlEvent,
          controlId: widget.control.id,
        );
      }
    });

    OneSignal.Notifications.addForegroundWillDisplayListener((event) {
      try {
        debugPrint("Notifications-addForegroundWillDisplayListener");

        final jsonData = jsonEncode({
          "json_data": event.notification.jsonRepresentation(),
        });

        widget.backend.triggerControlEvent(widget.control.id, "notification_opened", jsonData);

      } catch (error, stackTrace) {
        debugPrint("Error:\nerror: $error\nstackTrace: $stackTrace");
        handleFlutterError(
          method: "_setupNotificationHandler",
          error: error,
          stackTrace: stackTrace,
          trigger: widget.backend.triggerControlEvent,
          controlId: widget.control.id,
        );
      }
    });

    OneSignal.InAppMessages.addClickListener((event) async {
      try {
        debugPrint("InAppMessages-addClickListener");

        var messageMap = jsonDecode(event.message.jsonRepresentation());
        var resultMap = jsonDecode(event.result.jsonRepresentation());

        final jsonData = jsonEncode({
          "json_data": {
            "message": messageMap,
            "result": resultMap,
          }
        });

        widget.backend.triggerControlEvent(widget.control.id, "click_in_app_messages", jsonData);

      } catch (error, stackTrace) {
        debugPrint("Error:\nerror: $error\nstackTrace: $stackTrace");
        handleFlutterError(
          method: "_setupNotificationHandler",
          error: error,
          stackTrace: stackTrace,
          trigger: widget.backend.triggerControlEvent,
          controlId: widget.control.id,
        );
      }
    });

    OneSignal.InAppMessages.addWillDisplayListener((event) async {
      try {
        debugPrint("InAppMessages-addWillDisplayListener");

        var messageMap = jsonDecode(event.message.jsonRepresentation());

        final jsonData = jsonEncode({
          "json_data": messageMap,
        });

        debugPrint("dataStr: $jsonData");

        widget.backend.triggerControlEvent(
            widget.control.id, "will_display_in_app_messages", jsonData);
      } catch (error, stackTrace) {
        debugPrint("Error:\nerror: $error\nstackTrace: $stackTrace");
        handleFlutterError(
          method: "_setupNotificationHandler",
          error: error,
          stackTrace: stackTrace,
          trigger: widget.backend.triggerControlEvent,
          controlId: widget.control.id,
        );
      }
    });

    OneSignal.InAppMessages.addDidDisplayListener((event) async {
      try {
        debugPrint("InAppMessages-addDidDisplayListener");

        var messageMap = jsonDecode(event.message.jsonRepresentation());

        final jsonData = jsonEncode({
          "json_data": messageMap,
        });

        debugPrint("dataStr: $jsonData");

        widget.backend.triggerControlEvent(
            widget.control.id, "did_display_in_app_messages", jsonData);
      } catch (error, stackTrace) {
        debugPrint("Error:\nerror: $error\nstackTrace: $stackTrace");
        handleFlutterError(
          method: "_setupNotificationHandler",
          error: error,
          stackTrace: stackTrace,
          trigger: widget.backend.triggerControlEvent,
          controlId: widget.control.id,
        );
      }
    });

    OneSignal.InAppMessages.addWillDismissListener((event) async {
      try {
        debugPrint("InAppMessages-addWillDismissListener");

        var messageMap = jsonDecode(event.message.jsonRepresentation());

        final jsonData = jsonEncode({
          "json_data": messageMap,
        });

        debugPrint("dataStr: $jsonData");

        widget.backend.triggerControlEvent(
            widget.control.id, "will_dismiss_in_app_messages", jsonData);
      } catch (error, stackTrace) {
        debugPrint("Error:\nerror: $error\nstackTrace: $stackTrace");
        handleFlutterError(
          method: "_setupNotificationHandler",
          error: error,
          stackTrace: stackTrace,
          trigger: widget.backend.triggerControlEvent,
          controlId: widget.control.id,
        );
      }
    });

    OneSignal.InAppMessages.addDidDismissListener((event) async {
      try {
        debugPrint("InAppMessages-addDidDismissListener");

        var messageMap = jsonDecode(event.message.jsonRepresentation());

        final jsonData = jsonEncode({
          "json_data": messageMap,
        });

        debugPrint("dataStr: $jsonData");

        widget.backend.triggerControlEvent(
            widget.control.id, "did_dismiss_in_app_messages", jsonData);
      } catch (error, stackTrace) {
        debugPrint("Error:\nerror: $error\nstackTrace: $stackTrace");
        handleFlutterError(
          method: "_setupNotificationHandler",
          error: error,
          stackTrace: stackTrace,
          trigger: widget.backend.triggerControlEvent,
          controlId: widget.control.id,
        );
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    debugPrint("OneSignal build: ${widget.control.id} (${widget.control.hashCode})");

    () async {
      try {
        widget.backend.subscribeMethods(widget.control.id,
                (methodName, args) async {
              try {
                return switch (methodName) {
                  "get_onesignal_id" => _getOnesignalId(),
                  "get_external_user_id" => _getExternalUserId(),
                  "login" => _login(args),
                  "logout" => _logout(),
                  "add_alias" => _addAlias(args),
                  "remove_alias" => _removeAlias(args),
                  "set_language" => _setLanguage(args),
                  "consent_required" => _consentRequired(args),
                  "request_permission" => _requestPermission(args),
                  "opt_in" => _optIn(),
                  "opt_out" => _optOut(),
                  "register_for_provisional_authorization" => _registerForProvisionalAuthorization(),
                  "can_request_permission" => _canRequestPermission(),
                  "remove_notification" => _removeNotification(args),
                  "remove_grouped_notifications" => _removeGroupedNotifications(args),
                  "clear_all_notifications" => _clearAllNotifications(),
                  "prevent_default" => _preventDefault(args),
                  _ => null,
                };
              } catch (error, stackTrace) {
                debugPrint("Error:\nerror: $error\nstackTrace: $stackTrace");
                handleFlutterError(
                  method: methodName,
                  error: error,
                  stackTrace: stackTrace,
                  trigger: widget.backend.triggerControlEvent,
                  controlId: widget.control.id,
                );
                return error.toString();
              }
            });
      } catch (error, stackTrace) {
        debugPrint("Error:\nerror: $error\nstackTrace: $stackTrace");
        handleFlutterError(
          method: "subscribeMethods",
          error: error,
          stackTrace: stackTrace,
          trigger: widget.backend.triggerControlEvent,
          controlId: widget.control.id,
        );
      }
    }();

    return const SizedBox.shrink();
  }

  Future<String?> _getOnesignalId() async {
    var result = await OneSignal.User.getOnesignalId() ?? "The OneSignal ID does not exist.";
    return result;
  }

  Future<String?> _getExternalUserId() async {
    var result = await OneSignal.User.getExternalId() ?? "The external user ID does not yet exist.";
    return result;
  }

  Future<String?> _login(Map<String, dynamic> args) async {
    var externalUserId = args["external_user_id"] ?? "";
    await OneSignal.login(externalUserId);
    return null;
  }

  Future<String?> _logout() async {
    await OneSignal.logout();
    return null;
  }

  Future<String?> _addAlias(Map<String, dynamic> args) async {
    String alias = args["alias"] ?? "";
    dynamic idAlias = args["id_alias"];
    await OneSignal.User.addAlias(alias, idAlias);
    return null;
  }

  Future<String?> _removeAlias(Map<String, dynamic> args) async {
    String alias = args["alias"] ?? "";
    await OneSignal.User.removeAlias(alias);
    return null;
  }

  Future<String?> _setLanguage(Map<String, dynamic> args) async {
    String language = args["language"] ?? "en";
    await OneSignal.User.setLanguage(language);
    return null;
  }

  Future<String?> _consentRequired(Map<String, dynamic> args) async {
    String dataStr = args["data"]!;
    Map<String, dynamic> dataMap = json.decode(dataStr);
    bool consent = dataMap["consent"] as bool;
    await OneSignal.consentRequired(consent);
    return null;
  }

  Future<String?> _requestPermission(Map<String, dynamic> args) async {
    String dataStr = args["data"]!;
    Map<String, dynamic> dataMap = json.decode(dataStr);
    bool fallbackToSettings = dataMap["fallback_to_settings"] as bool;
    var result = await OneSignal.Notifications.requestPermission(fallbackToSettings);
    return result.toString();
  }

  Future<String?> _optIn() async {
    await OneSignal.User.pushSubscription.optIn();
    return null;
  }

  Future<String?> _optOut() async {
    await OneSignal.User.pushSubscription.optOut();
    return null;
  }

  Future<String?> _registerForProvisionalAuthorization() async {
    var result = await OneSignal.Notifications.registerForProvisionalAuthorization(true);
    return result.toString();
  }

  Future<String?> _canRequestPermission() async {
    var result = await OneSignal.Notifications.canRequest();
    return result.toString();
  }

  Future<String?> _removeNotification(Map<String, dynamic> args) async {
    int notificationId = args["notification_id"] as int;
    await OneSignal.Notifications.removeNotification(notificationId);
    return null;
  }

  Future<String?> _removeGroupedNotifications(Map<String, dynamic> args) async {
    var notificationGroup = args["notification_group"] ?? "";
    await OneSignal.Notifications.removeGroupedNotifications(
        notificationGroup);
    return null;
  }

  Future<String?> _clearAllNotifications() async {
    await OneSignal.Notifications.clearAll();
    return null;
  }

  Future<String?> _preventDefault(Map<String, dynamic> args) async {
    var notificationId = args["notification_id"] ?? "";
    OneSignal.Notifications.preventDefault(notificationId);
    return null;
  }
}
