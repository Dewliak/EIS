# EU Data Compass mobile clients

These Android-first Flutter clients implement the emergency-mode demo: travel registration, authority review/publication, alerts, acknowledgement, and consent-based location check-ins. The wallet step is a simulated EU Digital Identity Wallet screen.

The first slice labels satellite observations and delivery as simulated. Copernicus data ingestion, Galileo EWSS broadcast and production Firebase credentials are integration work for a later phase.

## Run — no backend needed

The apps run **standalone with mock data by default** (`USE_MOCK=true`). Just:

```bash
flutter pub get
flutter run
```

- **Citizen:** tap *Verify with EU ID Wallet* → approve in the simulated wallet → a sample emergency alert appears; acknowledge / mark safe / share-location all work locally.
- **Authority:** *Simulate, review and publish* shows the published-alert confirmation locally.

### Optional: run against a real backend

If/when the FastAPI backend is running, point the apps at it and disable mock data:

```bash
flutter run --dart-define=USE_MOCK=false --dart-define=API_BASE_URL=http://10.0.2.2:8080
```

Use `http://10.0.2.2:8080` for an Android emulator, the computer's LAN address for a physical phone, or the HTTPS Cloudflare/Railway URL when testing remotely.

The citizen app does not track ordinary travel. It requests location only after an active emergency alert and explicit consent, at most once per day. A production build should add Firebase configuration and secure persistent authentication before release.
