# my_notes_app

A Flutter application for managing notes. Users can log in, view and save notes tied to their location and receive push notifications through Firebase.

## Setup

1. Install Flutter by following the [official guide](https://docs.flutter.dev/get-started/install).
2. Open the project directory:

   ```bash
   cd my_notes_app
   ```

3. Fetch the required packages:

   ```bash
   flutter pub get
   ```

   The repository already contains `google-services.json` for Firebase Android configuration.
   The file is located in `android/app` so no additional setup is required.

## Running

Ensure that a device or emulator is available and execute:

```bash
flutter run
```

This command builds the app and launches it on the connected device.
