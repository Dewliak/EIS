import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:eu_data_compass_citizen/main.dart';

void main() {
  testWidgets('wallet approve shows a mock alert without hanging', (WidgetTester tester) async {
    await tester.pumpWidget(const CitizenApp());
    expect(find.text('Verify with EU ID Wallet'), findsOneWidget);

    await tester.tap(find.text('Verify with EU ID Wallet'));
    await tester.pumpAndSettle();
    expect(find.text('EU Digital Identity Wallet'), findsOneWidget);

    await tester.tap(find.text('Approve & share'));
    await tester.pump(); // spinner
    await tester.pump(const Duration(seconds: 2)); // wallet round-trip
    await tester.pumpAndSettle(); // return + mock start()

    // Mock alert is shown; no infinite spinner.
    expect(find.text('Flood warning for Berlin'), findsOneWidget);
    expect(find.byType(CircularProgressIndicator), findsNothing);
  });
}
