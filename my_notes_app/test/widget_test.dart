// This is a basic Flutter widget test.
//
// To perform an interaction with a widget in your test, use the WidgetTester
// utility in the flutter_test package. For example, you can send tap and scroll
// gestures. You can also use WidgetTester to find child widgets in the widget
// tree, read text, and verify that the values of widget properties are correct.

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:my_notes_app/main.dart';

void main() {
  testWidgets('initial login screen is shown', (WidgetTester tester) async {
    // Build the app and trigger a frame.
    await tester.pumpWidget(const NotesApp());

    // Verify that the login screen title is present.
    expect(find.text('Вход'), findsOneWidget);
  });
}
