import json
import os
import hashlib
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window
import arabic_reshaper
from bidi.algorithm import get_display

# --- הגדרות מערכת ---
HEBREW_FONT = "arial.ttf" 
RIDES_FILE = "rides_db.json"
USERS_FILE = "users_db.json"
current_user = None 

def fix_heb(text):
    if not text: return ""
    return get_display(arabic_reshaper.reshape(text))

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

Window.clearcolor = (0.98, 0.98, 0.98, 1)

# --- 1. מסך כניסה ---
class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=40, spacing=15)
        layout.add_widget(Label(text=fix_heb("כניסה למערכת"), font_size='30sp', font_name=HEBREW_FONT, color=(0,0,0,1), bold=True))
        self.phone_input = TextInput(hint_text=fix_heb("מספר טלפון"), multiline=False, font_name=HEBREW_FONT, halign='right')
        self.pass_input = TextInput(hint_text=fix_heb("סיסמה"), password=True, multiline=False, font_name=HEBREW_FONT, halign='right')
        layout.add_widget(self.phone_input); layout.add_widget(self.pass_input)
        btn_login = Button(text=fix_heb("התחבר"), font_name=HEBREW_FONT, size_hint_y=None, height=60, background_color=(0.1, 0.5, 0.8, 1))
        btn_login.bind(on_press=self.do_login)
        layout.add_widget(btn_login)
        btn_reg = Button(text=fix_heb("הרשמה למשתמש חדש"), font_name=HEBREW_FONT, size_hint_y=None, height=40, background_color=(0.4, 0.4, 0.4, 1))
        btn_reg.bind(on_press=lambda x: setattr(self.manager, 'current', 'register'))
        layout.add_widget(btn_reg)
        self.error_label = Label(text="", color=(1, 0, 0, 1), font_name=HEBREW_FONT)
        layout.add_widget(self.error_label)
        self.add_widget(layout)

    def do_login(self, instance):
        global current_user
        if os.path.exists(USERS_FILE):
            with open(USERS_FILE, "r", encoding="utf-8") as f:
                users = json.load(f)
                phone = self.phone_input.text
                if phone in users and users[phone]['pass'] == hash_password(self.pass_input.text):
                    current_user = users[phone]
                    self.manager.current = 'menu'
                    return
        self.error_label.text = fix_heb("טלפון או סיסמה שגויים")

# --- 2. מסך הרשמה ---
class RegisterScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=40, spacing=15)
        layout.add_widget(Label(text=fix_heb("יצירת חשבון"), font_size='30sp', font_name=HEBREW_FONT, color=(0,0,0,1)))
        self.full_name = TextInput(hint_text=fix_heb("שם מלא"), multiline=False, font_name=HEBREW_FONT, halign='right')
        self.reg_phone = TextInput(hint_text=fix_heb("מספר טלפון"), multiline=False, font_name=HEBREW_FONT, halign='right')
        self.reg_pass = TextInput(hint_text=fix_heb("בחר סיסמה"), password=True, multiline=False, font_name=HEBREW_FONT, halign='right')
        layout.add_widget(self.full_name); layout.add_widget(self.reg_phone); layout.add_widget(self.reg_pass)
        btn_done = Button(text=fix_heb("הירשם עכשיו"), font_name=HEBREW_FONT, size_hint_y=None, height=60, background_color=(0.1, 0.6, 0.3, 1))
        btn_done.bind(on_press=self.create_account)
        layout.add_widget(btn_done)
        self.add_widget(layout)

    def create_account(self, instance):
        if not (self.full_name.text and self.reg_phone.text and self.reg_pass.text): return
        users = {}
        if os.path.exists(USERS_FILE):
            with open(USERS_FILE, "r", encoding="utf-8") as f: users = json.load(f)
        users[self.reg_phone.text] = {"name": self.full_name.text, "phone": self.reg_phone.text, "pass": hash_password(self.reg_pass.text)}
        with open(USERS_FILE, "w", encoding="utf-8") as f: json.dump(users, f, ensure_ascii=False, indent=4)
        self.manager.current = 'login'

# --- 3. תפריט ראשי ---
class MenuScreen(Screen):
    def on_enter(self):
        self.layout.clear_widgets()
        self.layout.add_widget(Label(text=fix_heb(f"שלום, {current_user['name']}"), font_size='28sp', font_name=HEBREW_FONT, color=(0,0,0,1), bold=True))
        btn_post = Button(text=fix_heb("אני נהג - פרסם נסיעה"), font_name=HEBREW_FONT, size_hint_y=None, height=80, background_color=(0.1, 0.4, 0.7, 1))
        btn_post.bind(on_press=lambda x: setattr(self.manager, 'current', 'post'))
        btn_view = Button(text=fix_heb("אני נוסע - חפש נסיעה"), font_name=HEBREW_FONT, size_hint_y=None, height=80, background_color=(0.1, 0.6, 0.3, 1))
        btn_view.bind(on_press=self.go_to_view)
        self.layout.add_widget(btn_post); self.layout.add_widget(btn_view)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', padding=50, spacing=25)
        self.add_widget(self.layout)

    def go_to_view(self, instance):
        self.manager.get_screen('view').load_rides()
        self.manager.current = 'view'

# --- 4. מסך פרסום נסיעה ---
class PostScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=30, spacing=15)
        layout.add_widget(Label(text=fix_heb("פרסום נסיעה"), font_size='24sp', font_name=HEBREW_FONT, color=(0,0,0,1)))
        self.origin = TextInput(hint_text=fix_heb("מאיפה?"), multiline=False, font_name=HEBREW_FONT, halign='right')
        self.dest = TextInput(hint_text=fix_heb("לאן?"), multiline=False, font_name=HEBREW_FONT, halign='right')
        self.time = TextInput(hint_text=fix_heb("שעה"), multiline=False, font_name=HEBREW_FONT, halign='right')
        layout.add_widget(self.origin); layout.add_widget(self.dest); layout.add_widget(self.time)
        btn_save = Button(text=fix_heb("פרסם נסיעה"), font_name=HEBREW_FONT, size_hint_y=None, height=60, background_color=(0.1, 0.4, 0.7, 1))
        btn_save.bind(on_press=self.save_ride)
        layout.add_widget(btn_save)
        btn_back = Button(text=fix_heb("חזור"), font_name=HEBREW_FONT, size_hint_y=None, height=50)
        btn_back.bind(on_press=lambda x: setattr(self.manager, 'current', 'menu'))
        layout.add_widget(btn_back)
        self.add_widget(layout)

    def save_ride(self, instance):
        if not (self.origin.text and self.dest.text): return
        # הוספנו מזהה ייחודי לכל נסיעה (timestamp) כדי שנוכל למחוק אותה בקלות
        import time
        ride_id = str(time.time())
        ride = {"id": ride_id, "driver_phone": current_user['phone'], "driver": current_user['name'], "origin": self.origin.text, "dest": self.dest.text, "time": self.time.text, "phone": current_user['phone']}
        rides = []
        if os.path.exists(RIDES_FILE):
            with open(RIDES_FILE, "r", encoding="utf-8") as f: rides = json.load(f)
        rides.append(ride)
        with open(RIDES_FILE, "w", encoding="utf-8") as f: json.dump(rides, f, ensure_ascii=False, indent=4)
        self.manager.current = 'menu'

# --- 5. מסך צפייה בנסיעות (עם אפשרות מחיקה) ---
class ViewScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        self.layout.add_widget(Label(text=fix_heb("נסיעות זמינות"), font_size='24sp', font_name=HEBREW_FONT, color=(0,0,0,1)))
        self.scroll = ScrollView()
        self.rides_list = BoxLayout(orientation='vertical', size_hint_y=None, spacing=15, padding=10)
        self.rides_list.bind(minimum_height=self.rides_list.setter('height'))
        self.scroll.add_widget(self.rides_list)
        self.layout.add_widget(self.scroll)
        btn_back = Button(text=fix_heb("חזור"), font_name=HEBREW_FONT, size_hint_y=None, height=50)
        btn_back.bind(on_press=lambda x: setattr(self.manager, 'current', 'menu'))
        self.layout.add_widget(btn_back)
        self.add_widget(self.layout)

    def load_rides(self):
        self.rides_list.clear_widgets()
        if os.path.exists(RIDES_FILE):
            with open(RIDES_FILE, "r", encoding="utf-8") as f:
                rides = json.load(f)
                for r in reversed(rides):
                    # יצירת כרטיס נסיעה
                    card = BoxLayout(orientation='horizontal', size_hint_y=None, height=120, padding=5)
                    
                    # אם אני הנהג - מוסיף כפתור מחיקה
                    if r.get('driver_phone') == current_user['phone']:
                        del_btn = Button(text=fix_heb("מחק"), font_name=HEBREW_FONT, size_hint_x=0.2, background_color=(0.8, 0.2, 0.2, 1))
                        del_btn.bind(on_press=lambda x, rid=r.get('id'): self.delete_ride(rid))
                        card.add_widget(del_btn)
                    
                    info_text = f"נהג: {r['driver']}\nמ:{r['origin']} ל:{r['dest']} | שעה: {r['time']}\nטלפון: {r['phone']}"
                    lbl = Label(text=fix_heb(info_text), font_name=HEBREW_FONT, color=(0,0,0,1), halign='right')
                    card.add_widget(lbl)
                    
                    self.rides_list.add_widget(card)

    def delete_ride(self, ride_id):
        if not ride_id: return
        if os.path.exists(RIDES_FILE):
            with open(RIDES_FILE, "r", encoding="utf-8") as f:
                rides = json.load(f)
            # סינון הרשימה ללא הנסיעה שנמחקה
            new_rides = [r for r in rides if r.get('id') != ride_id]
            with open(RIDES_FILE, "w", encoding="utf-8") as f:
                json.dump(new_rides, f, ensure_ascii=False, indent=4)
            self.load_rides() # רענון הרשימה

# --- הרצת האפליקציה ---
class CarpoolApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(LoginScreen(name='login'))
        sm.add_widget(RegisterScreen(name='register'))
        sm.add_widget(MenuScreen(name='menu'))
        sm.add_widget(PostScreen(name='post'))
        sm.add_widget(ViewScreen(name='view'))
        return sm

if __name__ == "__main__":
    CarpoolApp().run()