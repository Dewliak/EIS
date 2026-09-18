import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:eu_data_compass_authority/main.dart';

void main() {
  testWidgets('Authority app builds', (WidgetTester tester) async {
    await tester.pumpWidget(const AuthorityApp());
    expect(find.byType(MaterialApp), findsOneWidget);
  });
}
