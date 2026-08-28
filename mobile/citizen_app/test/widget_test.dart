import 'package:flutter_test/flutter_test.dart';
import 'package:shared_preferences/shared_preferences.dart';

import 'package:eu_data_compass_citizen/main.dart';

void main() {
  setUp(() {
    TestWidgetsFlutterBinding.ensureInitialized();
    SharedPreferences.setMockInitialValues({});
  });

  testWidgets('inform (no phone) -> guarded -> emergency appears after the delay', (WidgetTester tester) async {
    await tester.pumpWidget(const CitizenApp());
    expect(find.text('Inform your government'), findsOneWidget);

    await tester.tap(find.text('Inform your government'));
    await tester.pumpAndSettle();
    // Phone is optional; submit without entering one.
    expect(find.text('Sign with EU ID Wallet & inform'), findsOneWidget);

    await tester.tap(find.text('Sign with EU ID Wallet & inform'));
    await tester.pumpAndSettle();
    expect(find.text('Approve & share'), findsOneWidget);

    await tester.tap(find.text('Approve & share'));
    await tester.pump();
    await tester.pump(const Duration(seconds: 2)); // wallet round-trip
    await tester.pumpAndSettle();

    expect(find.text('Guarded'), findsOneWidget);
    expect(find.textContaining('not shared'), findsOneWidget); // optional phone omitted
    expect(find.text('Flood warning · Berlin'), findsNothing);

    await tester.pump(const Duration(seconds: emergencyDelaySeconds + 1));
    await tester.pumpAndSettle();
    expect(find.text('Flood warning · Berlin'), findsOneWidget);
  });
}
