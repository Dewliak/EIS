# eu_data_compass_citizen

The **citizen** side of the EU Compass emergency-alert demo (Flutter, Android-first). Part of the
[EIS monorepo](../../readme.md) — see [`mobile/README.md`](../README.md) for how to run it and
[`docs/07-emergency/EMERGENCY-DEMO.md`](../../docs/07-emergency/EMERGENCY-DEMO.md) for what the
demo actually implements versus what's mocked.

## What this app does

All screens live in `lib/main.dart`:

| Screen | What it does |
|---|---|
| `WalletMockScreen` | Simulated "Verify with EU ID Wallet" step. Not a real wallet integration — see the limitation note below. |
| `HomeScreen` | List of the citizen's registered trips; tap a trip to update or delete it; shows a banner when an emergency alert is active. |
| `InformScreen` | "Inform with ID" — register or update a trip (destination, dates, optional phone number with OS autofill). |
| `AlertDetailScreen` | An active emergency alert: instructions, acknowledge / mark-safe / need-help actions, and an opt-in, once-per-day location check-in. |

Local device notifications (via `flutter_local_notifications`, with timezone data initialised
through the `timezone` package) fire when a matched alert appears. This is a **local** notification
shown by the app while it's running — not a server-sent push; see the mocking notes in
[`docs/07-emergency/EMERGENCY-DEMO.md`](../../docs/07-emergency/EMERGENCY-DEMO.md#whats-mocked).

## Limitation: wallet step is not real

The wallet screen is a simulated approval step, not an actual EUDI Wallet integration. Once
"approved," the app authenticates against the backend with a **demo bearer token** tied to a fixed
citizen id, the same for every install — see
[`docs/07-emergency/EMERGENCY-DEMO.md`](../../docs/07-emergency/EMERGENCY-DEMO.md#auth-model-important-limitation).

## Privacy

The app does not track ordinary travel. It requests device location only after an active emergency
alert and explicit per-alert consent, at most once per day, and stops asking once the alert closes.

## Run

See [`mobile/README.md`](../README.md) for both run modes (standalone with mock data, or against a
real backend). Generic Flutter tooling links: [Flutter docs](https://docs.flutter.dev/).
