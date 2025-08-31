[app]

# Tên ứng dụng
title = Notification Monitor

# Tên package
package.name = notificationmonitor

# Tên domain
package.domain = org.example

# Source code
source.dir = .
source.include_exts = py,png,jpg,kv,atlas

# Version
version = 1.0

# Requirements
requirements = python3,kivy,requests,android

# Permissions
android.permissions = INTERNET,ACCESS_NETWORK_STATE,POST_NOTIFICATIONS

# API level
android.api = 33
android.minapi = 21
android.ndk = 23b

# Orientation
orientation = portrait

# Services
android.allow_backup = True
android.services = service:NotificationService

# Buildozer
log_level = 2
warn_on_root = 1
