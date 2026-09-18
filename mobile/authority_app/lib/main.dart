import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;

const apiBaseUrl = String.fromEnvironment('API_BASE_URL', defaultValue: 'http://10.0.2.2:8080');

// Standalone demo: no backend required. Pass --dart-define=USE_MOCK=false for a real backend.
const useMockData = bool.fromEnvironment('USE_MOCK', defaultValue: true);

void main() => runApp(const AuthorityApp());

class AuthorityApp extends StatelessWidget { const AuthorityApp({super.key}); @override Widget build(BuildContext context) => MaterialApp(title: 'EU Compass Authority', theme: ThemeData(colorSchemeSeed: const Color(0xff174ea6), useMaterial3: true), home: const AuthorityHome()); }

class AuthorityHome extends StatefulWidget { const AuthorityHome({super.key}); @override State<AuthorityHome> createState() => _AuthorityHomeState(); }
class _AuthorityHomeState extends State<AuthorityHome> {
  String? token; int? hazardId; String message = 'Sign in to the authority demo.'; final title = TextEditingController(text: 'Flood warning for Berlin');
  Map<String, String> get headers => {'Content-Type': 'application/json', if (token != null) 'Authorization': 'Bearer $token'};
  Future<Map<String, dynamic>> post(String path, [Map<String, dynamic>? body]) async { final r = await http.post(Uri.parse('$apiBaseUrl$path'), headers: headers, body: jsonEncode(body ?? {})).timeout(const Duration(seconds: 10), onTimeout: () => throw Exception('Timed out reaching $apiBaseUrl. Is the backend running?')); if (r.statusCode >= 400) throw Exception(r.body); return jsonDecode(r.body); }
  Future<void> runDemo() async {
    if (useMockData) {
      setState(() => message = 'Simulating…');
      await Future.delayed(const Duration(milliseconds: 900));
      setState(() => message = 'Alert "${title.text}" reviewed and published to matching demo travellers. Delivery is simulated.');
      return;
    }
    try { final s = await post('/api/demo/authority/session'); token = s['access_token']; final h = await post('/api/authority/hazards/simulate'); hazardId = h['id']; await post('/api/authority/hazards/$hazardId/review'); final a = await post('/api/authority/alerts', {'hazard_id': hazardId, 'title': title.text, 'body': 'A simulated satellite observation indicates flooding risk near Berlin.', 'instructions': 'Follow official instructions and call 112 for immediate danger.', 'valid_from': '2026-01-01T00:00:00+00:00', 'valid_until': '2027-12-31T23:59:59+00:00', 'source_url': 'https://www.copernicus.eu/en/copernicus-services/emergency'}); await post('/api/authority/alerts/${a['id']}/publish'); setState(() => message = 'Alert published to matching demo travellers. Delivery is simulated.'); } catch (e) { setState(() => message = 'Unable to complete demo: $e'); } }
  @override Widget build(BuildContext context) => Scaffold(appBar: AppBar(leading: Padding(padding: const EdgeInsets.all(8), child: Image.asset('assets/logo.png')), title: const Text('EU Compass Authority')), body: Padding(padding: const EdgeInsets.all(20), child: ListView(children: [const Text('Emergency control room', style: TextStyle(fontSize: 28, fontWeight: FontWeight.bold)), const SizedBox(height: 12), Text(message, style: const TextStyle(fontSize: 17)), const SizedBox(height: 20), TextField(controller: title, decoration: const InputDecoration(labelText: 'Alert title', border: OutlineInputBorder())), const SizedBox(height: 12), FilledButton.icon(onPressed: runDemo, icon: const Icon(Icons.satellite_alt), label: const Text('Simulate, review and publish alert')), const SizedBox(height: 20), const Text('Safeguards: satellite input is simulated, publication requires authority action, and citizen location is opt-in and emergency-only.')])));
}
