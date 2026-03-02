name: Build APK
on: [push, pull_request]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Build with Buildozer
        uses: Enteleform/buildozer-action@v1.2.1
        with:
          buildozer_version: master
     
command: android debug
    HEBREW_FONT = "hebrew.ttf"
- name: Upload APK
        uses: actions/upload-artifact@v4
        with:
          name: carpool-app
          path: bin/*.apk


