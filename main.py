from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.clock import Clock
from kivy.logger import Logger
from kivy.utils import platform

import requests
import threading
import time
import json

# Android specific imports
if platform == 'android':
    from android.permissions import request_permissions, Permission
    from jnius import autoclass, cast
    from android.runnable import run_on_ui_thread
    
    # Java classes
    PythonActivity = autoclass('org.kivy.android.PythonActivity')
    NotificationListenerService = autoclass('android.service.notification.NotificationListenerService')
    Context = autoclass('android.content.Context')
    Intent = autoclass('android.content.Intent')
    Settings = autoclass('android.provider.Settings')

class NotificationReader:
    def __init__(self, telegram_bot_token, telegram_chat_id):
        self.bot_token = telegram_bot_token
        self.chat_id = telegram_chat_id
        self.is_running = False
        
    def send_to_telegram(self, message):
        """Gửi tin nhắn về Telegram bot"""
        try:
            url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
            data = {
                'chat_id': self.chat_id,
                'text': message,
                'parse_mode': 'HTML'
            }
            response = requests.post(url, data=data, timeout=10)
            if response.status_code == 200:
                Logger.info(f"Sent to Telegram: {message[:50]}...")
            else:
                Logger.error(f"Telegram error: {response.status_code}")
        except Exception as e:
            Logger.error(f"Error sending to Telegram: {e}")
    
    def start_monitoring(self):
        """Bắt đầu theo dõi thông báo"""
        self.is_running = True
        if platform == 'android':
            self._start_android_monitoring()
        else:
            self._start_desktop_simulation()
    
    def stop_monitoring(self):
        """Dừng theo dõi thông báo"""
        self.is_running = False
    
    def _start_android_monitoring(self):
        """Theo dõi thông báo trên Android"""
        def monitor():
            # Yêu cầu quyền truy cập thông báo
            try:
                # Mở cài đặt để user cấp quyền Notification Access
                intent = Intent(Settings.ACTION_NOTIFICATION_LISTENER_SETTINGS)
                intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
                PythonActivity.mActivity.startActivity(intent)
                
                self.send_to_telegram("📱 Ứng dụng đã khởi động và yêu cầu quyền truy cập thông báo")
                
                # Simulation cho đến khi có NotificationListenerService thực sự
                while self.is_running:
                    time.sleep(30)  # Kiểm tra mỗi 30 giây
                    self.send_to_telegram("🔔 App đang hoạt động - kiểm tra thông báo...")
                    
            except Exception as e:
                Logger.error(f"Android monitoring error: {e}")
                self.send_to_telegram(f"❌ Lỗi: {str(e)}")
        
        threading.Thread(target=monitor, daemon=True).start()
    
    def _start_desktop_simulation(self):
        """Simulation cho desktop testing"""
        def simulate():
            count = 0
            while self.is_running:
                time.sleep(60)  # Gửi test message mỗi phút
                count += 1
                self.send_to_telegram(f"🧪 Test notification #{count} - App running")
        
        threading.Thread(target=simulate, daemon=True).start()

class WebViewWidget(BoxLayout):
    """Widget hiển thị iframe/webview"""
    def __init__(self, url="https://www.google.com", **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        
        # Header
        header = BoxLayout(size_hint_y=0.1)
        title = Label(text=f"WebView: {url}", size_hint_x=0.8)
        header.add_widget(title)
        
        # WebView placeholder (thực tế cần WebView component)
        webview_label = Label(
            text=f"🌐 WebView Loading...\nURL: {url}\n\n(Trên Android thực tế sẽ hiển thị iframe)",
            text_size=(None, None),
            halign='center',
            valign='middle'
        )
        
        self.add_widget(header)
        self.add_widget(webview_label)

class MainApp(App):
    def __init__(self):
        super().__init__()
        self.notification_reader = None
        
    def build(self):
        # Layout chính
        main_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Title
        title = Label(
            text="📱 Notification Reader & Telegram Bot",
            size_hint_y=0.1,
            font_size='20sp'
        )
        main_layout.add_widget(title)
        
        # Config section
        config_layout = BoxLayout(orientation='vertical', size_hint_y=0.3, spacing=5)
        
        # Bot Token
        config_layout.add_widget(Label(text="Telegram Bot Token:", size_hint_y=0.3))
        self.bot_token_input = TextInput(
            hint_text="Nhập bot token của bạn...",
            multiline=False,
            size_hint_y=0.3
        )
        config_layout.add_widget(self.bot_token_input)
        
        # Chat ID
        config_layout.add_widget(Label(text="Telegram Chat ID:", size_hint_y=0.3))
        self.chat_id_input = TextInput(
            hint_text="Nhập chat ID...",
            multiline=False,
            size_hint_y=0.3
        )
        config_layout.add_widget(self.chat_id_input)
        
        # URL for iframe
        config_layout.add_widget(Label(text="URL hiển thị:", size_hint_y=0.3))
        self.url_input = TextInput(
            text="https://www.google.com",
            multiline=False,
            size_hint_y=0.3
        )
        config_layout.add_widget(self.url_input)
        
        main_layout.add_widget(config_layout)
        
        # Control buttons
        button_layout = BoxLayout(size_hint_y=0.1, spacing=10)
        
        self.start_btn = Button(text="🚀 Bắt đầu")
        self.start_btn.bind(on_press=self.start_service)
        
        self.stop_btn = Button(text="⏹️ Dừng", disabled=True)
        self.stop_btn.bind(on_press=self.stop_service)
        
        button_layout.add_widget(self.start_btn)
        button_layout.add_widget(self.stop_btn)
        main_layout.add_widget(button_layout)
        
        # Status
        self.status_label = Label(
            text="📊 Trạng thái: Chưa khởi động",
            size_hint_y=0.1
        )
        main_layout.add_widget(self.status_label)
        
        # WebView area
        self.webview_container = BoxLayout(size_hint_y=0.5)
        main_layout.add_widget(self.webview_container)
        
        # Request permissions on Android
        if platform == 'android':
            self.request_android_permissions()
        
        return main_layout
    
    def request_android_permissions(self):
        """Yêu cầu quyền cần thiết trên Android"""
        try:
            request_permissions([
                Permission.READ_EXTERNAL_STORAGE,
                Permission.WRITE_EXTERNAL_STORAGE,
                Permission.INTERNET,
                Permission.ACCESS_NETWORK_STATE,
                Permission.WAKE_LOCK,
                Permission.FOREGROUND_SERVICE
            ])
        except Exception as e:
            Logger.error(f"Permission error: {e}")
    
    def start_service(self, instance):
        """Khởi động dịch vụ đọc thông báo"""
        bot_token = self.bot_token_input.text.strip()
        chat_id = self.chat_id_input.text.strip()
        url = self.url_input.text.strip()
        
        if not bot_token or not chat_id:
            self.status_label.text = "❌ Vui lòng nhập Bot Token và Chat ID"
            return
        
        # Khởi tạo notification reader
        self.notification_reader = NotificationReader(bot_token, chat_id)
        
        # Bắt đầu monitoring
        self.notification_reader.start_monitoring()
        
        # Update UI
        self.start_btn.disabled = True
        self.stop_btn.disabled = False
        self.status_label.text = "✅ Đang chạy ngầm..."
        
        # Load WebView
        self.load_webview(url)
        
        # Gửi thông báo khởi động
        self.notification_reader.send_to_telegram(
            "🚀 <b>Notification Reader Started</b>\n"
            f"📱 Device: Android\n"
            f"🌐 WebView URL: {url}\n"
            f"⏰ Time: {time.strftime('%Y-%m-%d %H:%M:%S')}"
        )
    
    def stop_service(self, instance):
        """Dừng dịch vụ"""
        if self.notification_reader:
            self.notification_reader.stop_monitoring()
            self.notification_reader.send_to_telegram("⏹️ Notification Reader đã dừng")
        
        self.start_btn.disabled = False
        self.stop_btn.disabled = True
        self.status_label.text = "⏹️ Đã dừng"
        
        # Clear WebView
        self.webview_container.clear_widgets()
    
    def load_webview(self, url):
        """Load WebView với URL"""
        self.webview_container.clear_widgets()
        webview = WebViewWidget(url=url)
        self.webview_container.add_widget(webview)
    
    def on_start(self):
        """Chạy khi app khởi động"""
        # Tự động minimize sau 3 giây (simulation)
        Clock.schedule_once(self.minimize_simulation, 3)
    
    def minimize_simulation(self, dt):
        """Simulation việc minimize app"""
        self.status_label.text += " (Chạy ngầm)"

# Notification Listener Service (cần tạo file Java riêng cho Android)
NOTIFICATION_SERVICE_JAVA = '''
// File: NotificationListenerService.java (cần thêm vào buildozer.spec)
public class NotificationListenerService extends NotificationListenerService {
    @Override
    public void onNotificationPosted(StatusBarNotification sbn) {
        // Gửi thông báo về Python
        String packageName = sbn.getPackageName();
        String title = sbn.getNotification().extras.getString("android.title");
        String text = sbn.getNotification().extras.getString("android.text");
        
        // Call Python method để xử lý
        sendToPython(packageName, title, text);
    }
    
    private void sendToPython(String pkg, String title, String text) {
        // Implementation để gọi Python method
    }
}
'''

# Buildozer config
BUILDOZER_SPEC = '''
# buildozer.spec additions:
android.permissions = INTERNET, ACCESS_NETWORK_STATE, WAKE_LOCK, FOREGROUND_SERVICE, BIND_NOTIFICATION_LISTENER_SERVICE
android.add_src = java_src/
android.gradle_dependencies = 
'''

if __name__ == '__main__':
    MainApp().run()
