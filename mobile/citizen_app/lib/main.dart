import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:geolocator/geolocator.dart';
import 'package:http/http.dart' as http;

const apiBaseUrl = String.fromEnvironment('API_BASE_URL', defaultValue: 'http://10.0.2.2:8080');

class ApiClient {
  String? token;
  Map<String, String> get headers => {'Content-Type': 'application/json', if (token != null) 'Authorization': 'Bearer $token'};
  Future<Map<String, dynamic>> post(String path, [Map<String, dynamic>? body]) async {
    final response = await http.post(Uri.parse('$apiBaseUrl$path'), headers: headers, body: jsonEncode(body ?? {}));
    if (response.statusCode >= 400) throw Exception(response.body);
    return jsonDecode(response.body) as Map<String, dynamic>;
  }
  Future<Map<String, dynamic>> get(String path) async {
    final response = await http.get(Uri.parse('$apiBaseUrl$path'), headers: headers);
    if (response.statusCode >= 400) throw Exception(response.body);
    return jsonDecode(response.body) as Map<String, dynamic>;
  }
}

void main() => runApp(const CitizenApp());

class CitizenApp extends StatelessWidget {
  const CitizenApp({super.key});
  @override
  Widget build(BuildContext context) => MaterialApp(
    title: 'EU Data Compass',
    theme: ThemeData(colorSchemeSeed: const Color(0xff174ea6), useMaterial3: true),
    home: const EmergencyHome(),
  );
}

class EmergencyHome extends StatefulWidget {
  const EmergencyHome({super.key});
  @override State<EmergencyHome> createState() => _EmergencyHomeState();
}

class _EmergencyHomeState extends State<EmergencyHome> {
  final api = ApiClient();
  List<dynamic> alerts = [];
  String message = 'Connect to load your emergency status.';
  bool loading = false;

  Future<void> start() async {
    setState(() => loading = true);
    try {
      final session = await api.post('/api/demo/citizen/session');
      api.token = session['access_token'];
      await api.post('/api/citizen/registrations', {
        'destination_country': 'DE', 'destination_region': 'Berlin',
        'travel_start': '2026-01-01T00:00:00+00:00', 'travel_end': '2027-12-31T23:59:59+00:00',
        'push_enabled': true,
      });
      await refresh();
    } catch (error) { setState(() => message = 'Unable to connect: $error'); }
    if (mounted) setState(() => loading = false);
  }

  Future<void> refresh() async {
    final result = await api.get('/api/citizen/alerts');
    if (mounted) setState(() { alerts = result['alerts'] as List<dynamic>; message = alerts.isEmpty ? 'No active emergency alerts.' : 'Emergency information requires your attention.'; });
  }

  Future<void> verifyWithWallet() async {
    // Mocked EUDI Wallet round-trip: hand off to the wallet screen, and only
    // continue (open the session) once the user "approves" in the wallet.
    final approved = await Navigator.of(context).push<bool>(
      MaterialPageRoute(builder: (_) => const WalletMockScreen()),
    );
    if (approved == true) await start();
  }

  Future<void> action(int id, String action) async { await api.post('/api/citizen/alerts/$id/$action'); await refresh(); }

  Future<void> shareLocation(int id) async {
    final permission = await Geolocator.requestPermission();
    if (permission == LocationPermission.denied || permission == LocationPermission.deniedForever) throw Exception('Location permission was not granted');
    final position = await Geolocator.getCurrentPosition();
    await api.post('/api/citizen/alerts/$id/location-consent');
    await api.post('/api/citizen/alerts/$id/location-checkins', {
      'latitude': position.latitude, 'longitude': position.longitude,
      'accuracy_meters': position.accuracy, 'captured_at': DateTime.now().toUtc().toIso8601String(),
    });
    setState(() => message = 'Location check-in sent. The next check-in is available tomorrow.');
  }

  @override
  Widget build(BuildContext context) => Scaffold(
    appBar: AppBar(leading: Padding(padding: const EdgeInsets.all(8), child: Image.asset('assets/logo.png')), title: const Text('EU Data Compass'), actions: [IconButton(onPressed: api.token == null ? null : refresh, icon: const Icon(Icons.refresh))]),
    body: Padding(padding: const EdgeInsets.all(20), child: loading ? const Center(child: CircularProgressIndicator()) : ListView(children: [
      const Text('Emergency mode', style: TextStyle(fontSize: 28, fontWeight: FontWeight.bold)),
      const SizedBox(height: 8),
      Text(message, style: const TextStyle(fontSize: 17)),
      const SizedBox(height: 20),
      if (api.token == null) FilledButton.icon(onPressed: verifyWithWallet, icon: const Icon(Icons.verified_user), label: const Text('Verify with EU ID Wallet')),
      ...alerts.map((raw) { final alert = raw as Map<String, dynamic>; final id = alert['id'] as int; return Card(color: Colors.red.shade50, child: Padding(padding: const EdgeInsets.all(16), child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        Text(alert['severity'].toString().toUpperCase(), style: const TextStyle(fontWeight: FontWeight.bold, color: Colors.red)),
        Text(alert['title'].toString(), style: const TextStyle(fontSize: 21, fontWeight: FontWeight.bold)),
        Text(alert['body'].toString()), const SizedBox(height: 8), Text('Instructions: ${alert['instructions']}'),
        const SizedBox(height: 12), Wrap(spacing: 8, children: [OutlinedButton(onPressed: () => action(id, 'acknowledge'), child: const Text('Acknowledge')), OutlinedButton(onPressed: () => action(id, 'safe'), child: const Text('I am safe')), FilledButton(onPressed: () => shareLocation(id), child: const Text('Share location once'))]),
        const SizedBox(height: 6), Text('Source: ${alert['source_url']}'), Text('Satellite status: ${alert['satellite_status']}'),
      ]))); }),
    ])),
  );
}

class WalletMockScreen extends StatefulWidget {
  const WalletMockScreen({super.key});
  @override State<WalletMockScreen> createState() => _WalletMockScreenState();
}

class _WalletMockScreenState extends State<WalletMockScreen> {
  bool verifying = false;

  Future<void> approve() async {
    setState(() => verifying = true);
    await Future.delayed(const Duration(milliseconds: 1400)); // simulate the wallet round-trip
    if (mounted) Navigator.pop(context, true);
  }

  @override
  Widget build(BuildContext context) => Scaffold(
    backgroundColor: const Color(0xff0b1f4d),
    body: SafeArea(child: Padding(padding: const EdgeInsets.all(24), child: Column(crossAxisAlignment: CrossAxisAlignment.stretch, children: [
      const SizedBox(height: 12),
      Center(child: Image.asset('assets/logo.png', height: 96)),
      const SizedBox(height: 16),
      const Text('EU Digital Identity Wallet', textAlign: TextAlign.center, style: TextStyle(color: Colors.white, fontSize: 22, fontWeight: FontWeight.bold)),
      const SizedBox(height: 4),
      const Text('Simulated — demo verification only', textAlign: TextAlign.center, style: TextStyle(color: Colors.white70)),
      const SizedBox(height: 28),
      const Card(child: Padding(padding: EdgeInsets.all(18), child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        Text('EU Data Compass is requesting:', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
        SizedBox(height: 10),
        ListTile(contentPadding: EdgeInsets.zero, leading: Icon(Icons.flag), title: Text('Nationality'), subtitle: Text('Portugal (PT)')),
        ListTile(contentPadding: EdgeInsets.zero, leading: Icon(Icons.person), title: Text('Name'), subtitle: Text('Demo Traveller')),
        SizedBox(height: 6),
        Text('Only these attributes are shared. Selective disclosure keeps everything else private.', style: TextStyle(color: Colors.black54)),
      ]))),
      const Spacer(),
      if (verifying)
        const Column(children: [CircularProgressIndicator(color: Colors.white), SizedBox(height: 12), Text('Verifying with your wallet…', style: TextStyle(color: Colors.white))])
      else
        Column(children: [
          FilledButton(onPressed: approve, style: FilledButton.styleFrom(minimumSize: const Size.fromHeight(52)), child: const Text('Approve & share')),
          const SizedBox(height: 10),
          OutlinedButton(onPressed: () => Navigator.pop(context, false), style: OutlinedButton.styleFrom(minimumSize: const Size.fromHeight(52), foregroundColor: Colors.white, side: const BorderSide(color: Colors.white54)), child: const Text('Cancel')),
        ]),
      const SizedBox(height: 8),
    ]))),
  );
}
