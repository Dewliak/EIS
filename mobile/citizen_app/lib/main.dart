import 'dart:async';
import 'package:flutter/material.dart';
import 'package:geolocator/geolocator.dart';
import 'package:flutter_local_notifications/flutter_local_notifications.dart';
import 'package:timezone/data/latest.dart' as tzdata;
import 'package:timezone/timezone.dart' as tz;
import 'package:shared_preferences/shared_preferences.dart';

// How long after informing the (simulated) emergency arrives. Small for the demo.
const emergencyDelaySeconds = int.fromEnvironment('EMERGENCY_DELAY', defaultValue: 2);

// Test hook: lets widget tests that don't exercise the emergency turn the
// auto-fire off so its timer doesn't perturb the UI. Always true in the app.
bool autoEmergencyEnabled = true;

const _channelId = 'emergency_alerts';
final FlutterLocalNotificationsPlugin _fln = FlutterLocalNotificationsPlugin();
final GlobalKey<NavigatorState> _navKey = GlobalKey<NavigatorState>();
// Flipped when the user taps the OS notification; HomeScreen listens.
final ValueNotifier<bool> _notificationTapped = ValueNotifier(false);

// Emergency response state, shared between the alert screen and the home screen.
final ValueNotifier<bool> _safeReported = ValueNotifier(false);
final ValueNotifier<bool> _locationShared = ValueNotifier(false);
String? _sharedLocationText;

void _resetEmergencyResponse() {
  _safeReported.value = false;
  _locationShared.value = false;
  _sharedLocationText = null;
}

// --- Mock emergency content (personalised for Portuguese travellers) --------
const _alert = {
  'severity': 'severe',
  'title': 'Flood warning · Berlin',
  'body': 'A simulated satellite observation indicates flooding risk in central Berlin.',
  'source': 'Simulated — Copernicus EMS demo',
};
const _ptInstructions = [
  'Seek higher ground immediately — move to upper floors or elevated areas.',
  'Do not walk or drive through flood water.',
  'Keep your phone charged and this app open for updates.',
  'Call 112 for immediate danger.',
];
const _collectionPoint = {
  'name': 'Portuguese community collection point (simulated)',
  'address': 'Portugiesische Gemeinde, Kurfürstenstraße, 10785 Berlin',
  'lat': 52.5006,
  'lon': 13.3620,
  'note': 'After the water recedes, Portuguese citizens can gather here. '
      'Portuguese consular staff assist with shelter, documents and contact home.',
};

Future<void> _initNotifications() async {
  try {
    tzdata.initializeTimeZones();
    // Without a local location, `tz.local` throws and scheduling silently fails.
    // UTC is fine here: we only schedule relative offsets from "now".
    tz.setLocalLocation(tz.getLocation('UTC'));
    const androidInit = AndroidInitializationSettings('@mipmap/ic_launcher');
    await _fln.initialize(
      const InitializationSettings(android: androidInit),
      onDidReceiveNotificationResponse: (_) => _notificationTapped.value = true,
    );
    final android = _fln.resolvePlatformSpecificImplementation<AndroidFlutterLocalNotificationsPlugin>();
    await android?.requestNotificationsPermission();
    await android?.requestExactAlarmsPermission();
    await android?.createNotificationChannel(const AndroidNotificationChannel(
      _channelId, 'Emergency alerts',
      description: 'Emergency alerts for your informed travel period',
      importance: Importance.max,
    ));
  } catch (_) {/* notifications unavailable (e.g. tests) — the in-app timer still works */}
}

// Post a notification immediately from the running app. More reliable across
// OEMs (incl. Samsung One UI) than background AlarmManager delivery. The app is
// alive whenever our in-app timer fires, so we post from there.
Future<void> _showNow(int id, String title, String body) async {
  try {
    final details = NotificationDetails(android: AndroidNotificationDetails(
      _channelId, 'Emergency alerts',
      importance: Importance.max, priority: Priority.high,
      icon: '@mipmap/ic_launcher',
      ticker: title,
      styleInformation: BigTextStyleInformation(body, contentTitle: title)));
    await _fln.show(id, title, body, details);
  } catch (_) {/* no plugin (tests) */}
}

Future<void> _scheduleEmergencyNotification() async {/* no-op: posted on timer fire */}

Future<void> _cancelEmergencyNotification() async {
  try { await _fln.cancel(1); } catch (_) {}
}

// Ask for notification + exact-alarm permission. Called on a user gesture so
// the Android 13+ system dialog reliably appears.
Future<bool> _ensureNotificationPermissions() async {
  try {
    final android = _fln.resolvePlatformSpecificImplementation<AndroidFlutterLocalNotificationsPlugin>();
    final granted = await android?.requestNotificationsPermission();
    await android?.requestExactAlarmsPermission();
    final enabled = await android?.areNotificationsEnabled();
    return enabled ?? granted ?? false;
  } catch (_) { return false; }
}


void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await _initNotifications();
  runApp(const CitizenApp());
}

class Trip {
  final String countryCode, countryName, region, phone;
  final DateTime from, to;
  Trip({required this.countryCode, required this.countryName, required this.region,
        required this.phone, required this.from, required this.to});
  bool get guarded {
    final now = DateTime.now();
    return !now.isBefore(DateTime(from.year, from.month, from.day)) &&
           !now.isAfter(DateTime(to.year, to.month, to.day, 23, 59, 59));
  }
}

String _fmt(DateTime d) => '${d.year}-${d.month.toString().padLeft(2, '0')}-${d.day.toString().padLeft(2, '0')}';

class CitizenApp extends StatelessWidget {
  const CitizenApp({super.key});
  @override
  Widget build(BuildContext context) => MaterialApp(
    title: 'EU Compass',
    navigatorKey: _navKey,
    theme: ThemeData(colorSchemeSeed: const Color(0xff174ea6), useMaterial3: true),
    home: const HomeScreen(),
  );
}

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});
  @override State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  final List<Trip> trips = [];
  bool emergencyActive = false;
  bool _notifEnabled = true;
  Timer? _timer;

  // The mock emergency is a Berlin flood: it only reaches trips whose
  // destination is Berlin (location) AND are within their dates (guarded).
  List<Trip> get affectedTrips =>
      trips.where((t) => t.guarded && t.region == 'Berlin').toList();

  void _refresh() { if (mounted) setState(() {}); }

  @override
  void initState() {
    super.initState();
    _notificationTapped.addListener(_onNotificationTapped);
    _safeReported.addListener(_refresh);
    _locationShared.addListener(_refresh);
    _ensureNotificationPermissions().then((ok) { if (mounted) setState(() => _notifEnabled = ok); });
  }

  @override
  void dispose() {
    _notificationTapped.removeListener(_onNotificationTapped);
    _safeReported.removeListener(_refresh);
    _locationShared.removeListener(_refresh);
    _timer?.cancel();
    super.dispose();
  }

  void _onNotificationTapped() {
    if (!_notificationTapped.value) return;
    _notificationTapped.value = false;
    if (affectedTrips.isNotEmpty) {
      setState(() => emergencyActive = true);
      _openAlert();
    }
  }

  Future<void> _inform({Trip? existing}) async {
    final result = await Navigator.of(context).push<Trip>(
      MaterialPageRoute(builder: (_) => InformScreen(initial: existing)),
    );
    if (result == null) return;
    setState(() {
      if (existing != null) {
        final i = trips.indexOf(existing);
        if (i >= 0) { trips[i] = result; } else { trips.add(result); }
      } else {
        trips.add(result);
      }
    });
    final ok = await _ensureNotificationPermissions();
    if (mounted) setState(() => _notifEnabled = ok);
    await _reevaluate();
  }

  Future<void> _delete(Trip t) async {
    final ok = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Delete this trip?'),
        content: Text('Remove your ${t.countryName} · ${t.region} trip? Emergency alerts for it will stop.'),
        actions: [
          TextButton(onPressed: () => Navigator.pop(ctx, false), child: const Text('Keep')),
          FilledButton(onPressed: () => Navigator.pop(ctx, true), child: const Text('Delete')),
        ],
      ),
    );
    if (ok != true) return;
    setState(() => trips.remove(t));
    await _reevaluate();
  }

  // Arm or clear the emergency depending on whether any trip matches the
  // affected location and is currently within its dates.
  Future<void> _reevaluate() async {
    if (affectedTrips.isEmpty) {
      _timer?.cancel(); _timer = null;
      await _cancelEmergencyNotification();
      _resetEmergencyResponse();
      if (mounted) setState(() => emergencyActive = false);
      return;
    }
    if (!emergencyActive && _timer == null && autoEmergencyEnabled) {
      _resetEmergencyResponse();
      await _scheduleEmergencyNotification();
      _timer = Timer(const Duration(seconds: emergencyDelaySeconds), () {
        _timer = null;
        if (mounted && affectedTrips.isNotEmpty) {
          setState(() => emergencyActive = true);
          _showNow(1, '⚠ ${_alert['title']}',
            'Flooding risk in central Berlin. Seek higher ground now, avoid flood water, '
            'and call 112 in immediate danger. Tap to open EU Compass for full instructions '
            'and your nearest Portuguese collection point.');
        }
      });
    }
  }

  void _tripMenu(Trip t) {
    showModalBottomSheet(context: context, builder: (ctx) => SafeArea(child: Column(mainAxisSize: MainAxisSize.min, children: [
      ListTile(leading: const Icon(Icons.edit), title: const Text('Update trip'),
        onTap: () { Navigator.pop(ctx); _inform(existing: t); }),
      ListTile(leading: const Icon(Icons.delete_outline), title: const Text('Delete trip'),
        onTap: () { Navigator.pop(ctx); _delete(t); }),
      ListTile(leading: const Icon(Icons.close), title: const Text('Cancel'), onTap: () => Navigator.pop(ctx)),
    ])));
  }

  void _openAlert() {
    _navKey.currentState?.push(MaterialPageRoute(builder: (_) => const AlertDetailScreen()));
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        leading: Padding(padding: const EdgeInsets.all(8), child: Image.asset('assets/logo.png')),
        title: const Text('EU Compass'),
      ),
      body: Padding(
        padding: const EdgeInsets.all(20),
        child: ListView(children: [
          const Text('Travel & emergency', style: TextStyle(fontSize: 28, fontWeight: FontWeight.bold)),
          const SizedBox(height: 8),
          if (trips.isEmpty) ...[
            const Text('Inform your government about your trips so they can reach you in an '
                'emergency while you are abroad.', style: TextStyle(fontSize: 17)),
            const SizedBox(height: 20),
            FilledButton.icon(
              onPressed: () => _inform(),
              icon: const Icon(Icons.assignment_turned_in),
              label: const Text('Inform your government'),
            ),
          ] else ...[
            if (emergencyActive && affectedTrips.isNotEmpty) ...[
              _alertCard(),
              const SizedBox(height: 16),
            ],
            if (!_notifEnabled)
              Card(color: Colors.amber.shade100, child: ListTile(
                leading: const Icon(Icons.notifications_off),
                title: const Text('Notifications are off'),
                subtitle: const Text('Enable them to receive emergency alerts.'),
                trailing: TextButton(
                  onPressed: () async {
                    final ok = await _ensureNotificationPermissions();
                    if (mounted) setState(() => _notifEnabled = ok);
                  },
                  child: const Text('Enable'),
                ),
              )),
            const Text('Your trips', style: TextStyle(fontWeight: FontWeight.bold)),
            const SizedBox(height: 8),
            ...trips.map(_tripCard),
            const SizedBox(height: 8),
            OutlinedButton.icon(onPressed: () => _inform(),
              icon: const Icon(Icons.add), label: const Text('Add another trip')),
          ],
        ]),
      ),
    );
  }

  Widget _tripCard(Trip t) {
    final guarded = t.guarded;
    final affected = emergencyActive && affectedTrips.contains(t);
    return Card(
      child: InkWell(
        onLongPress: () => _tripMenu(t),
        borderRadius: BorderRadius.circular(12),
        child: Padding(padding: const EdgeInsets.all(18), child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          Row(children: [
            Icon(guarded ? Icons.verified_user : Icons.shield_outlined, color: guarded ? Colors.green.shade700 : Colors.grey),
            const SizedBox(width: 8),
            Expanded(child: Text(guarded ? 'Guarded' : 'Not active',
              style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold, color: guarded ? Colors.green.shade700 : Colors.grey.shade700))),
          ]),
          const SizedBox(height: 6),
          Text('Destination: ${t.countryName} · ${t.region}'),
          Text('Period: ${_fmt(t.from)} → ${_fmt(t.to)}'),
          Text('Phone: ${t.phone.isEmpty ? "not shared" : t.phone}'),
          if (affected) Padding(padding: const EdgeInsets.only(top: 8),
            child: Text('⚠ Active emergency in ${t.region}', style: TextStyle(color: Colors.red.shade700, fontWeight: FontWeight.bold))),
          const SizedBox(height: 8),
          Text(guarded ? 'Hold for options' : 'Outside your dates · hold for options',
            style: const TextStyle(color: Colors.black38, fontSize: 12)),
        ])),
      ),
    );
  }

  Widget _alertCard() {
    final where = affectedTrips.map((t) => '${t.countryName} · ${t.region}').toSet().join(', ');
    return Card(
      color: Colors.red.shade50,
      child: Padding(padding: const EdgeInsets.all(16), child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        Row(children: [
          Expanded(child: Text((_alert['severity'] as String).toUpperCase(),
            style: const TextStyle(fontWeight: FontWeight.bold, color: Colors.red))),
          IconButton(onPressed: _openAlert, icon: const Icon(Icons.info_outline), tooltip: 'More information'),
        ]),
        Text(_alert['title'] as String, style: const TextStyle(fontSize: 21, fontWeight: FontWeight.bold)),
        const SizedBox(height: 6),
        Text(_alert['body'] as String),
        const SizedBox(height: 6),
        Text('Affects: $where', style: const TextStyle(fontStyle: FontStyle.italic)),
        if (_safeReported.value || _locationShared.value) Padding(
          padding: const EdgeInsets.only(top: 8),
          child: Wrap(spacing: 6, children: [
            if (_safeReported.value) Chip(avatar: const Icon(Icons.check_circle, color: Colors.green, size: 18), label: const Text('You reported safe')),
            if (_locationShared.value) const Chip(avatar: Icon(Icons.my_location, size: 18), label: Text('Location shared')),
          ]),
        ),
        const SizedBox(height: 12),
        FilledButton.icon(onPressed: _openAlert, icon: const Icon(Icons.menu_book), label: const Text('View instructions')),
      ])),
    );
  }
}

// --- Inform flow ------------------------------------------------------------
class InformScreen extends StatefulWidget {
  const InformScreen({super.key, this.initial});
  final Trip? initial; // when set, we are editing an existing trip
  @override State<InformScreen> createState() => _InformScreenState();
}

class _InformScreenState extends State<InformScreen> {
  final destinations = const [
    {'code': 'DE', 'name': 'Germany', 'region': 'Berlin'},
    {'code': 'ES', 'name': 'Spain', 'region': 'Madrid'},
    {'code': 'FR', 'name': 'France', 'region': 'Paris'},
  ];
  late Map<String, String> destination = destinations.first;
  late DateTime from = DateTime.now();
  late DateTime to = DateTime.now().add(const Duration(days: 14));
  final phone = TextEditingController();
  bool sharePhone = true;

  static const _phoneKey = 'saved_phone';

  bool get _isEdit => widget.initial != null;

  @override
  void initState() {
    super.initState();
    final init = widget.initial;
    if (init != null) {
      // Editing: prefill from the existing trip.
      destination = destinations.firstWhere((d) => d['code'] == init.countryCode, orElse: () => destinations.first);
      from = init.from;
      to = init.to;
      sharePhone = init.phone.isNotEmpty;
      if (init.phone.isNotEmpty) phone.text = init.phone;
    } else {
      // New trip: prefill from the locally-saved number (if any).
      SharedPreferences.getInstance().then((prefs) {
        final saved = prefs.getString(_phoneKey);
        if (saved != null && saved.isNotEmpty && mounted) setState(() => phone.text = saved);
      });
    }
  }

  @override
  void dispose() { phone.dispose(); super.dispose(); }

  Future<void> _pick(bool isFrom) async {
    final now = DateTime.now();
    final picked = await showDatePicker(
      context: context,
      initialDate: isFrom ? from : to,
      firstDate: DateTime(now.year - 1),
      lastDate: DateTime(now.year + 3),
    );
    if (picked != null) setState(() { if (isFrom) { from = picked; } else { to = picked; } });
  }

  Future<void> _submit() async {
    if (to.isBefore(from)) {
      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('End date must be after start date.')));
      return;
    }
    final entered = phone.text.trim();
    // Save whatever was typed locally for next time (even if not shared now).
    final prefs = await SharedPreferences.getInstance();
    if (entered.isEmpty) {
      await prefs.remove(_phoneKey);
    } else {
      await prefs.setString(_phoneKey, entered);
    }
    if (!mounted) return;
    final approved = await Navigator.of(context).push<bool>(
      MaterialPageRoute(builder: (_) => const WalletMockScreen()),
    );
    if (approved != true || !mounted) return;
    // Phone is optional; only include it when the user opted in and provided one.
    final shared = (sharePhone && entered.isNotEmpty) ? entered : '';
    Navigator.pop(context, Trip(
      countryCode: destination['code']!, countryName: destination['name']!,
      region: destination['region']!, phone: shared, from: from, to: to,
    ));
  }

  @override
  Widget build(BuildContext context) => Scaffold(
    appBar: AppBar(title: Text(_isEdit ? 'Update trip' : 'Inform your government')),
    body: Padding(padding: const EdgeInsets.all(20), child: ListView(children: [
      const Text('Where are you going?', style: TextStyle(fontWeight: FontWeight.bold)),
      const SizedBox(height: 8),
      DropdownButtonFormField<Map<String, String>>(
        initialValue: destination,
        decoration: const InputDecoration(border: OutlineInputBorder()),
        items: destinations.map((d) => DropdownMenuItem(value: d, child: Text('${d['name']} · ${d['region']}'))).toList(),
        onChanged: (v) => setState(() => destination = v ?? destination),
      ),
      const SizedBox(height: 18),
      const Text('For how long?', style: TextStyle(fontWeight: FontWeight.bold)),
      const SizedBox(height: 8),
      Row(children: [
        Expanded(child: OutlinedButton(onPressed: () => _pick(true), child: Text('From: ${_fmt(from)}'))),
        const SizedBox(width: 10),
        Expanded(child: OutlinedButton(onPressed: () => _pick(false), child: Text('To: ${_fmt(to)}'))),
      ]),
      const SizedBox(height: 18),
      const Text('Mobile phone number (optional)', style: TextStyle(fontWeight: FontWeight.bold)),
      const SizedBox(height: 8),
      AutofillGroup(child: TextField(
        controller: phone,
        keyboardType: TextInputType.phone,
        autofillHints: const [AutofillHints.telephoneNumber],
        decoration: const InputDecoration(
          border: OutlineInputBorder(), prefixIcon: Icon(Icons.phone),
          hintText: 'e.g. +351 912 345 678',
        ),
      )),
      CheckboxListTile(
        contentPadding: EdgeInsets.zero,
        controlAffinity: ListTileControlAffinity.leading,
        value: sharePhone,
        onChanged: (v) => setState(() => sharePhone = v ?? true),
        title: const Text('Share my phone number with the government'),
        subtitle: const Text('Used only to reach you in an emergency. Saved on this device either way.'),
      ),
      const SizedBox(height: 16),
      FilledButton.icon(onPressed: _submit, icon: const Icon(Icons.verified_user),
        style: FilledButton.styleFrom(minimumSize: const Size.fromHeight(52)),
        label: Text(_isEdit ? 'Sign with EU ID Wallet & update' : 'Sign with EU ID Wallet & inform')),
      const SizedBox(height: 8),
      const Text('You sign this notification with your wallet. Only nationality, name and your '
          'chosen dates + phone are shared.', style: TextStyle(color: Colors.black54, fontSize: 13)),
    ])),
  );
}

// --- Alert detail -----------------------------------------------------------
class AlertDetailScreen extends StatefulWidget {
  const AlertDetailScreen({super.key});
  @override State<AlertDetailScreen> createState() => _AlertDetailScreenState();
}

class _AlertDetailScreenState extends State<AlertDetailScreen> {
  String? error;

  Future<void> _shareLocation() async {
    setState(() => error = null);
    try {
      final permission = await Geolocator.requestPermission();
      if (permission == LocationPermission.denied || permission == LocationPermission.deniedForever) {
        throw Exception('Location permission was not granted');
      }
      final p = await Geolocator.getCurrentPosition();
      _sharedLocationText = '${p.latitude.toStringAsFixed(4)}, ${p.longitude.toStringAsFixed(4)}';
      _locationShared.value = true;
      if (mounted) setState(() {});
    } catch (e) {
      setState(() => error = 'Could not share location: $e');
    }
  }

  @override
  Widget build(BuildContext context) => Scaffold(
    appBar: AppBar(title: const Text('Emergency instructions')),
    body: Padding(padding: const EdgeInsets.all(20), child: ListView(children: [
      Text(_alert['title'] as String, style: const TextStyle(fontSize: 24, fontWeight: FontWeight.bold)),
      Text(_alert['source'] as String, style: const TextStyle(color: Colors.black54)),
      const SizedBox(height: 12),
      Text(_alert['body'] as String, style: const TextStyle(fontSize: 16)),
      const SizedBox(height: 20),
      const Text('What to do now (Portuguese citizens)', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 18)),
      const SizedBox(height: 8),
      ..._ptInstructions.map((s) => Padding(padding: const EdgeInsets.only(bottom: 6),
        child: Row(crossAxisAlignment: CrossAxisAlignment.start, children: [
          const Text('•  '), Expanded(child: Text(s, style: const TextStyle(fontSize: 16)))]))),
      const SizedBox(height: 16),
      Card(color: Colors.blue.shade50, child: Padding(padding: const EdgeInsets.all(16),
        child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          Row(children: const [Icon(Icons.place, color: Color(0xff174ea6)), SizedBox(width: 6),
            Expanded(child: Text('Collection point after the flood', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16)))]),
          const SizedBox(height: 8),
          Text(_collectionPoint['name'] as String, style: const TextStyle(fontWeight: FontWeight.w600)),
          Text(_collectionPoint['address'] as String),
          Text('Coordinates: ${_collectionPoint['lat']}, ${_collectionPoint['lon']}', style: const TextStyle(color: Colors.black54)),
          const SizedBox(height: 8),
          Text(_collectionPoint['note'] as String),
        ]))),
      const SizedBox(height: 16),
      const Text('Your response', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 18)),
      const SizedBox(height: 8),
      // Safe status — changes state instead of leaving you on the same screen.
      if (_safeReported.value)
        Card(color: Colors.green.shade50, child: ListTile(
          leading: Icon(Icons.check_circle, color: Colors.green.shade700),
          title: const Text('You reported yourself safe', style: TextStyle(fontWeight: FontWeight.w600)),
          subtitle: const Text('Your government has been notified (simulated).'),
          trailing: TextButton(onPressed: () { _safeReported.value = false; setState(() {}); }, child: const Text('Undo')),
        ))
      else
        FilledButton.icon(
          icon: const Icon(Icons.verified),
          style: FilledButton.styleFrom(minimumSize: const Size.fromHeight(50)),
          onPressed: () { _safeReported.value = true; setState(() {}); },
          label: const Text('I am safe'),
        ),
      const SizedBox(height: 10),
      // Location status.
      if (_locationShared.value)
        Card(color: Colors.blue.shade50, child: ListTile(
          leading: const Icon(Icons.my_location, color: Color(0xff174ea6)),
          title: const Text('Location shared', style: TextStyle(fontWeight: FontWeight.w600)),
          subtitle: Text(_sharedLocationText == null ? 'Shared with responders.' : 'At $_sharedLocationText · shared with responders.'),
          trailing: TextButton(onPressed: () { _locationShared.value = false; _sharedLocationText = null; setState(() {}); }, child: const Text('Stop')),
        ))
      else
        OutlinedButton.icon(
          icon: const Icon(Icons.share_location),
          style: OutlinedButton.styleFrom(minimumSize: const Size.fromHeight(50)),
          onPressed: _shareLocation,
          label: const Text('Share my location once'),
        ),
      if (error != null) Padding(padding: const EdgeInsets.only(top: 12), child: Text(error!, style: TextStyle(color: Colors.red.shade700, fontWeight: FontWeight.w600))),
    ])),
  );
}

// --- Mocked EU Digital Identity Wallet screen -------------------------------
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
      Expanded(child: SingleChildScrollView(child: Column(crossAxisAlignment: CrossAxisAlignment.stretch, children: [
        const SizedBox(height: 12),
        Center(child: Image.asset('assets/logo.png', height: 96)),
        const SizedBox(height: 16),
        const Text('EU Digital Identity Wallet', textAlign: TextAlign.center, style: TextStyle(color: Colors.white, fontSize: 22, fontWeight: FontWeight.bold)),
        const SizedBox(height: 4),
        const Text('Simulated — demo verification only', textAlign: TextAlign.center, style: TextStyle(color: Colors.white70)),
        const SizedBox(height: 28),
        const Card(child: Padding(padding: EdgeInsets.all(18), child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          Text('EU Compass is requesting:', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
          SizedBox(height: 10),
          ListTile(contentPadding: EdgeInsets.zero, leading: Icon(Icons.flag), title: Text('Nationality'), subtitle: Text('Portugal (PT)')),
          ListTile(contentPadding: EdgeInsets.zero, leading: Icon(Icons.person), title: Text('Name'), subtitle: Text('Demo Traveller')),
          SizedBox(height: 6),
          Text('Only these attributes are shared. Selective disclosure keeps everything else private.', style: TextStyle(color: Colors.black54)),
        ]))),
        const SizedBox(height: 16),
      ]))),
      if (verifying)
        const Padding(padding: EdgeInsets.symmetric(vertical: 8), child: Column(children: [CircularProgressIndicator(color: Colors.white), SizedBox(height: 12), Text('Verifying with your wallet…', style: TextStyle(color: Colors.white))]))
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
