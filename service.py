from kivy.app import App
from kivy.clock import Clock
from jnius import autoclass, cast
import requests
import json
from android import api_version, mActivity

# Các lớp Java
PythonService = autoclass('org.kivy.android.PythonService')
Context = autoclass('android.content.Context')
Intent = autoclass('android.content.Intent')
NotificationManager = autoclass('android.app.NotificationManager')
NotificationChannel = autoclass('android.app.NotificationChannel')
Notification = autoclass('android.app.Notification')
NotificationBuilder = autoclass('android.app.Notification$Builder')
PendingIntent = autoclass('android.app.PendingIntent')

class NotificationService:
    def __init__(self):
        self.last_notifications = set()
        self.telegram_bot_token = None
        self.chat_id = None
        self.notification_manager = None
        
    def initialize_service(self, intent):
        if intent:
            self.telegram_bot_token = intent.getStringExtra("telegram_bot_token")
            self.chat_id = intent.getStringExtra("chat_id")
        
        self.setup_notification_channel()
        self.start_monitoring()
        
    def setup_notification_channel(self):
        if api_version >= 26:
            channel_id = "notification_monitor_channel"
            channel_name = "Notification Monitor"
            importance = NotificationManager.IMPORTANCE_DEFAULT
            
            channel = NotificationChannel(channel_id, channel_name, importance)
            self.notification_manager = mActivity.getSystemService(Context.NOTIFICATION_SERVICE)
            self.notification_manager.createNotificationChannel(channel)
    
    def start_monitoring(self):
        # Bắt đầu theo dõi thông báo mỗi 5 giây
        Clock.schedule_interval(self.check_notifications, 5)
    
    def check_notifications(self, dt):
        try:
            # Lấy thông báo hiện tại
            current_notifications = self.get_current_notifications()
            new_notifications = current_notifications - self.last_notifications
            
            for notification in new_notifications:
                self.send_to_telegram(notification)
            
            self.last_notifications = current_notifications
            
        except Exception as e:
            print(f"Lỗi khi kiểm tra thông báo: {e}")
    
    def get_current_notifications(self):
        # Phương thức này cần được triển khai để lấy thông báo thực tế
        # Đây là phần phức tạp nhất và có thể cần sử dụng AccessibilityService
        notifications = set()
        
        # Tạm thời trả về set rỗng - cần triển khai thực tế
        return notifications
    
    def send_to_telegram(self, notification_data):
        if not self.telegram_bot_token or not self.chat_id:
            return
        
        try:
            url = f"https://api.telegram.org/bot{self.telegram_bot_token}/sendMessage"
            payload = {
                "chat_id": self.chat_id,
                "text": f"📱 Thông báo mới:\n{notification_data}",
                "parse_mode": "HTML"
            }
            
            response = requests.post(url, json=payload, timeout=10)
            if response.status_code == 200:
                print("Đã gửi thông báo đến Telegram")
            else:
                print(f"Lỗi gửi Telegram: {response.text}")
                
        except Exception as e:
            print(f"Lỗi khi gửi đến Telegram: {e}")

# Khởi tạo service
service = NotificationService()

def start_service(intent):
    service.initialize_service(intent)
    return 1  # START_STICKY

def stop_service():
    # Dọn dẹp khi service dừng
    pass
