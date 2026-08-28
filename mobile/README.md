# EU Data Compass mobile clients

These Android-first Flutter scaffolds implement the emergency-mode demo. They use the FastAPI service for travel registration, authority review/publication, alerts, acknowledgement and consent-based daily location check-ins.

The first slice labels satellite observations and delivery as simulated. Copernicus data ingestion, Galileo EWSS broadcast and production Firebase credentials are integration work for a later phase.

## Run

From each app directory:

```bash
flutter pub get
flutter run --dart-define=API_BASE_URL=http://10.0.2.2:8080
```

Use `http://10.0.2.2:8080` for an Android emulator, the computer's LAN address for a physical phone, or the HTTPS Cloudflare URL when testing remotely. Railway uses its HTTPS service URL.

The citizen app does not track ordinary travel. It requests location only after an active emergency alert and explicit consent, at most once per day. A production build should add Firebase configuration and secure persistent authentication before release.
