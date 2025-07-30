import 'package:flet/flet.dart';
import 'flet_onesignal.dart';


CreateControlFactory createControl = (CreateControlArgs args) {
  switch (args.control.type) {
    case 'flet_onesignal':
      if (args.parent == null) {
        throw ArgumentError('Parent cannot be null');
      }
      return FletOneSignalControl(
          parent: args.parent!, // Força a não nulidade após a verificação
          control: args.control,
          backend: args.backend
      );
    default:
      return null;
  }
};

void ensureInitialized() {
  // Required initializations, if any
  // Se houver inicializações necessárias
}
