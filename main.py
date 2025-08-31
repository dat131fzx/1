from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.utils import platform
from kivy.uix.webview import WebView
from android.permissions import request_permissions, Permission
from android import api_version
import requests
import json
import threading
from jnius import autoclass

# Các lớp Java để truy cập thông báo Android
PythonService = autoclass('org.kivy.android.PythonService')
Context = autoclass('android.content.Context')
NotificationManager = autoclass('android.app.NotificationManager')
Intent = autoclass('android.content.Intent')
PendingIntent = autoclass('android.app.PendingIntent')

class MainScreen(BoxLayout):
    def __init__(self, **kwargs):
        super(MainScreen, self).__init__(**kwargs)
        self.orientation = 'vertical'
        
        # Tạo WebView để hiển thị iframe
        self.webview = WebView(
            url='https://example.com',  # Thay bằng URL của bạn
            size_hint=(1, 0.9)
        )
        
        # Tạo layout cho các nút
        button_layout = BoxLayout(size_hint=(1, 0.1))
        
        # Nút cấp quyền
        self.permission_btn = Button(
            text='Cấp quyền thông báo',
            on_press=self.request_notification_permission
        )
        
        # Nút dừng service
        self.stop_btn = Button(
            text='Dừng theo dõi',
            on_press=self.stop_service
        )
        
        button_layout.add_widget(self.permission_btn)
        button_layout.add_widget(self.stop_btn)
        
        self.add_widget(self.webview)
        self.add_widget(button_layout)
        
        # Kiểm tra quyền khi khởi động
        Clock.schedule_once(self.check_permissions, 1)

    def check_permissions(self, dt):
        if platform == 'android':
            if not self.has_notification_permission():
                self.show_permission_warning()

    def has_notification_permission(self):
        if platform == 'android':
            if api_version >= 33:
                # Android 13+ cần quyền POST_NOTIFICATIONS
                from android.permissions import check_permission
                return check_permission(Permission.POST_NOTIFICATIONS)
            else:
                # Android <13 tự động có quyền thông báo
                return True
        return False

    def request_notification_permission(self, instance):
        if platform == 'android':
            if api_version >= 33:
                request_permissions([Permission.POST_NOTIFICATIONS])
                Clock.schedule_once(lambda dt: self.verify_permission(), 2)
            else:
                self.start_notification_service()
        else:
            print("Chỉ hỗ trợ trên Android")

    def verify_permission(self):
        if self.has_notification_permission():
            self.start_notification_service()
        else:
            self.show_permission_warning()

    def start_notification_service(self):
        try:
            # Khởi động service để theo dõi thông báo
            service_intent = Intent(Context(), PythonService)
            service_intent.putExtra("telegram_bot_token", "YOUR_BOT_TOKEN")  # Thay bằng token của bạn
            service_intent.putExtra("chat_id", "YOUR_CHAT_ID")  # Thay bằng chat ID của bạn
            Context().startService(service_intent)
            
            self.show_popup("Thành công", "Đã bật theo dõi thông báo!")
        except Exception as e:
            self.show_popup("Lỗi", f"Không thể khởi động service: {str(e)}")

    def stop_service(self, instance):
        try:
            service_intent = Intent(Context(), PythonService)
            Context().stopService(service_intent)
            self.show_popup("Thông báo", "Đã dừng theo dõi thông báo")
        except Exception as e:
            self.show_popup("Lỗi", f"Không thể dừng service: {str(e)}")

    def show_permission_warning(self):
        popup = Popup(
            title='Cảnh báo',
            content=Label(text='Bạn chưa cấp quyền thông báo. Ứng dụng sẽ thoát.'),
            size_hint=(0.8, 0.4)
        )
        popup.open()
        Clock.schedule_once(lambda dt: App.get_running_app().stop(), 3)

    def show_popup(self, title, message):
        popup = Popup(
            title=title,
            content=Label(text=message),
            size_hint=(0.8, 0.4)
        )
        popup.open()

class NotificationApp(App):
    def build(self):
        return MainScreen()

    def on_start(self):
        # Yêu cầu quyền khi app khởi động
        if platform == 'android':
            permissions = [Permission.INTERNET, Permission.ACCESS_NETWORK_STATE]
            if api_version >= 33:
                permissions.append(Permission.POST_NOTIFICATIONS)
            request_permissions(permissions)

if __name__ == '__main__':
    NotificationApp().run()
