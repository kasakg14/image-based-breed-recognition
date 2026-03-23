# Pashupahachan Android Starter

This folder contains a Flutter-based Android starter app for `पशुपहचान`.

## What is included

- Multilingual UI: English, Hindi, Marathi
- Hero screen and farm-themed design
- Camera and gallery image picker flow
- Mock prediction result screen
- Unique breed feature panel

## What is not connected yet

- Real model inference
- Real API call to Python backend
- TensorFlow Lite integration

## Recommended next implementation paths

1. API-based Android app
   - Build a FastAPI/Flask backend from the current Python recognizer
   - Send image from Android app to API
   - Return breed prediction JSON

2. Offline Android app
   - Convert model to TensorFlow Lite
   - Run prediction directly on device

## How to open

1. Install Flutter
2. Open `android_app` in Android Studio or VS Code
3. Run:

```bash
flutter pub get
flutter run
```

## Main file

- `lib/main.dart`
