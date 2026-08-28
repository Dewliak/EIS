import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:eu_data_compass_citizen/main.dart';

void main() {
  testWidgets('Citizen app builds', (WidgetTester tester) async {
    await tester.pumpWidget(const CitizenApp());
    expect(find.byType(MaterialApp), findsOneWidget);
  });
}
