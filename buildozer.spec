[app]
title = My Carpool App
package.name = carpoolapp
package.domain = org.test
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 0.1
requirements = python3,kivy
orientation = portrait
fullscreen = 0

# הגדרות אנדרואיד ספציפיות ליציבות
android.archs = arm64-v8a
android.allow_backup = True
android.accept_sdk_license = True
android.api = 31
android.minapi = 21
android.sdk_build_tools_version = 33.0.0

[buildozer]
log_level = 2
warn_on_root = 1
