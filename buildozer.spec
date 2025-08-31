[app]
title = NotificationReader
package.name = notificationreader
package.domain = com.yourname

[buildozer]
log_level = 2

[app]
requirements = python3,kivy,requests,pyjnius
permissions = INTERNET,ACCESS_NETWORK_STATE,WAKE_LOCK,FOREGROUND_SERVICE,BIND_NOTIFICATION_LISTENER_SERVICE
android.add_src = java_src/
