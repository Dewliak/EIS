import 'package:flutter/material.dart';
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

    // Open the alert; 'I am safe' should change state, not stay a button.
    await tester.tap(find.text('View instructions'));
    await tester.pumpAndSettle();
    expect(find.text('Emergency instructions'), findsOneWidget);
    await tester.scrollUntilVisible(find.text('I am safe'), 300, scrollable: find.byType(Scrollable).last);
    await tester.tap(find.text('I am safe'));
    await tester.pumpAndSettle();
    expect(find.text('You reported yourself safe'), findsOneWidget);
    expect(find.text('I am safe'), findsNothing);
  });

  testWidgets('multiple trips: add a second, delete one via hold menu', (WidgetTester tester) async {
    Future<void> informOnce(Finder trigger) async {
      await tester.tap(trigger);
      await tester.pumpAndSettle();
      await tester.tap(find.text('Sign with EU ID Wallet & inform'));
      await tester.pumpAndSettle();
      await tester.tap(find.text('Approve & share'));
      await tester.pump();
      await tester.pump(const Duration(seconds: 2));
      await tester.pumpAndSettle();
    }

    await tester.pumpWidget(const CitizenApp());
    await informOnce(find.text('Inform your government'));
    expect(find.text('Guarded'), findsOneWidget);

    await informOnce(find.text('Add another trip'));
    expect(find.text('Guarded'), findsNWidgets(2));

    // Hold a card -> Delete -> confirm.
    await tester.longPress(find.text('Guarded').first);
    await tester.pumpAndSettle();
    await tester.tap(find.text('Delete trip'));
    await tester.pumpAndSettle();
    expect(find.text('Delete this trip?'), findsOneWidget);
    await tester.tap(find.text('Delete'));
    await tester.pumpAndSettle();

    expect(find.text('Guarded'), findsOneWidget);
  });
}
