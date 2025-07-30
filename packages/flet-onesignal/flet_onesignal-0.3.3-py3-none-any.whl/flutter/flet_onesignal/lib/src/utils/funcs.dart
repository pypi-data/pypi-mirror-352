import 'dart:convert';
import 'package:flutter/material.dart';


void handleFlutterError({
  required String method,
  required Object error,
  required StackTrace stackTrace,
  required void Function(String, String, String) trigger,
  required String controlId,
}) {
  debugPrint("❌ Error in $method:\n$error\n$stackTrace");

  trigger(
    controlId,
    "error",
    jsonEncode({
      "method": method,
      "message": error.toString(),
      "stackTrace": stackTrace.toString(),
    }),
  );
}