# Movisinú Android research

Reviewed 2026-11-25.

## Confirmed public sources
- [Google Play listing](https://play.google.com/store/apps/details?id=com.recaudar.movisinu): Movisinu Rutas Bus Montería, GeekCorp Tech Lab; package `com.recaudar.movisinu`, listing reports update 2026-05-16. Advertises live bus location, route/service notifications, account and card functions.
- [Recaudar Sinú app page](https://recaudarsinu.com/apps/movisinu): describes real-time routes and schedules and journey planning.
- [Privacy notice](https://recaudarsinu.com/politica-de-datos): gives a different Android package, `com.recaudarsinu.movisinu`. Do not assume these identify the same binary/version.
- [GeekCorp MoviSinú portfolio](https://geekcorp.co/portfolio/movi-sinu): React, TypeScript, Capacitor, Ionic, MicroPython; describes real-time route/schedule consultation.
- [GeekCorp Op-Tra portfolio](https://geekcorp.co/portfolio/transporte-monteria): related transport management project for Recaudar Sinú and Metrosinú, Node.js, AWS Serverless, AWS IoT Core, React/microfrontends, Python and Roboflow. The relationship between the current passenger app and specific Op-Tra endpoints is unverified.

## APK acquisition and analysis
No verified APK download mirror found in targeted searches. No APK obtained or inspected. Prefer installing the Play Store version on the user's device and retrieving installed APK(s) with adb (including split APKs if present). Record package, version and SHA-256. Do not commit APKs or complete proprietary bundles to the public repository.

Inspect AndroidManifest and assets/public or equivalent packaged web assets, then JavaScript bundle route, stop, direction, schedule and vehicle-position references. Record only relevant technical metadata, distinguishing public passenger data from account, payment and internal fleet management operations. Test ordinary public read-only endpoints only; do not use extracted credentials, circumvent access restrictions, or collect account data. Confirm actual responses and reuse permission before publishing. Existing web API uses data.recaudarsinu.com; app backend is not yet verified.

Priority: schedule/frequency coverage and route/stop metadata beyond the web API. Investigate public real-time vehicle positions separately as potential GTFS-RT input. Stop geocoding remains parked per user request.

## Status: parked (2026-11-25)
The user reports that Google Play does not allow downloading the app in the Netherlands. No trusted APK is available for analysis. User requested postponing APK acquisition, static analysis and related backend research until later.
