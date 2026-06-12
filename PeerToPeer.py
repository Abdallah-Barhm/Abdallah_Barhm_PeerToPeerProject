import hashlib
import time
import json
from PIL import ImageTk
from typing import List, Dict, Any, Optional
import uuid
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, simpledialog
import threading
import os
import pickle
from dataclasses import dataclass
from enum import Enum

# استيراد اختياري مع معالجة الخطأ
try:
    import qrcode
    from PIL import Image, ImageTk
    QR_AVAILABLE = True
except ImportError:
    QR_AVAILABLE = False
    print("⚠️ مكتبة QR Code غير متوفرة. سيتم تعطيل ميزة QR Code.")

# استيراد winsound مع معالجة الخطأ
try:
    import winsound
    SOUND_AVAILABLE = True
except ImportError:
    SOUND_AVAILABLE = False
    print("⚠️ نظام الصوت غير متوفر على هذا النظام.")

# ================ نظام متعدد اللغات ================

class Language(Enum):
    ARABIC = "ar"
    ENGLISH = "en"

class Localization:
    """نظام الترجمة واللغات المتعددة"""
    
    translations = {
        "ar": {
            "app_title": "🏦 نظام المحفظة الرقمية P2P",
            "dashboard": "📊 لوحة التحكم",
            "create_wallet": "📝 إنشاء محفظة",
            "send_money": "💸 إرسال أموال",
            "all_wallets": "📋 جميع المحافظ",
            "mining": "⛏️ تعدين المعاملات",
            "blockchain": "📜 سلسلة الكتل",
            "quick_send": "⚡ إرسال سريع",
            "qr_code": "📱 رمز QR",
            "settings": "⚙️ الإعدادات",
            "login": "🔐 تسجيل الدخول",
            "logout": "🚪 تسجيل الخروج",
            "welcome": "مرحباً بك في نظام المحفظة الرقمية P2P!",
            "login_required": "الرجاء تسجيل الدخول أولاً",
            "username": "اسم المستخدم",
            "password": "كلمة المرور",
            "login_btn": "دخول",
            "register_btn": "تسجيل جديد",
            "success": "نجاح",
            "error": "خطأ",
            "balance": "الرصيد",
            "currency": "العملة",
            "select_currency": "اختر العملة",
            "amount": "المبلغ",
            "send": "إرسال",
            "theme": "المظهر",
            "light_theme": "فاتح",
            "dark_theme": "داكن",
            "language": "اللغة",
            "sound_on": "الصوت مفعل",
            "sound_off": "الصوت معطل",
            "add_favorite": "إضافة للمفضلة",
            "favorites": "المفضلة",
            "transaction_history": "سجل المعاملات",
            "qr_not_available": "ميزة QR Code غير متوفرة",
            "install_qr": "يرجى تثبيت: pip install qrcode[pil] Pillow",
        },
        "en": {
            "app_title": "🏦 P2P Digital Wallet System",
            "dashboard": "📊 Dashboard",
            "create_wallet": "📝 Create Wallet",
            "send_money": "💸 Send Money",
            "all_wallets": "📋 All Wallets",
            "mining": "⛏️ Mining",
            "blockchain": "📜 Blockchain",
            "quick_send": "⚡ Quick Send",
            "qr_code": "📱 QR Code",
            "settings": "⚙️ Settings",
            "login": "🔐 Login",
            "logout": "🚪 Logout",
            "welcome": "Welcome to P2P Digital Wallet System!",
            "login_required": "Please login first",
            "username": "Username",
            "password": "Password",
            "login_btn": "Login",
            "register_btn": "Register",
            "success": "Success",
            "error": "Error",
            "balance": "Balance",
            "currency": "Currency",
            "select_currency": "Select Currency",
            "amount": "Amount",
            "send": "Send",
            "theme": "Theme",
            "light_theme": "Light",
            "dark_theme": "Dark",
            "language": "Language",
            "sound_on": "Sound On",
            "sound_off": "Sound Off",
            "add_favorite": "Add to Favorites",
            "favorites": "Favorites",
            "transaction_history": "Transaction History",
            "qr_not_available": "QR Code feature not available",
            "install_qr": "Please install: pip install qrcode[pil] Pillow",
        }
    }
    
    def __init__(self, language: Language = Language.ARABIC):
        self.language = language
    
    def get(self, key: str) -> str:
        """الحصول على الترجمة"""
        lang_code = self.language.value
        if lang_code in self.translations and key in self.translations[lang_code]:
            return self.translations[lang_code][key]
        return key
    
    def switch_language(self):
        """تبديل اللغة"""
        if self.language == Language.ARABIC:
            self.language = Language.ENGLISH
        else:
            self.language = Language.ARABIC
        return self.language


# ================ نظام العملات المتعددة ================

@dataclass
class Currency:
    """فئة تمثل عملة رقمية"""
    def __init__(self, code: str, name: str, symbol: str, exchange_rate: float, icon: str = ""):
        self.code = code
        self.name = name
        self.symbol = symbol
        self.exchange_rate = exchange_rate  # سعر الصرف مقابل العملة الأساسية
        self.icon = icon



class CurrencySystem:
    """نظام إدارة العملات المتعددة"""
    
    CURRENCIES = {
        "P2P": Currency("P2P", "Peer Coin", "🪙", 1.0),
        "BTC": Currency("BTC", "Bitcoin", "₿", 0.00001),
        "ETH": Currency("ETH", "Ethereum", "⟠", 0.0001),
        "GOLD": Currency("GOLD", "Digital Gold", "🥇", 0.5),
        "SILVER": Currency("SILVER", "Digital Silver", "🥈", 10.0),
    }
    
    @classmethod
    def get_currency(cls, code: str) -> Optional[Currency]:
        return cls.CURRENCIES.get(code)
    
    @classmethod
    def get_all_currencies(cls) -> Dict[str, Currency]:
        return cls.CURRENCIES
    
    @classmethod
    def convert(cls, amount: float, from_currency: str, to_currency: str) -> float:
        """تحويل المبلغ بين العملات"""
        if from_currency not in cls.CURRENCIES or to_currency not in cls.CURRENCIES:
            return amount
        
        # التحويل للعملة الأساسية P2P أولاً
        base_amount = amount / cls.CURRENCIES[from_currency].exchange_rate
        # التحويل للعملة المطلوبة
        return base_amount * cls.CURRENCIES[to_currency].exchange_rate


# ================ نظام المستخدمين والمصادقة ================

@dataclass
class User:
    """فئة تمثل مستخدم النظام"""
    user_id: str
    username: str
    password_hash: str
    created_at: datetime
    last_login: Optional[datetime] = None

class AuthSystem:
    """نظام المصادقة وإدارة المستخدمين"""
    
    def __init__(self):
        self.users: Dict[str, User] = {}
        self.current_user: Optional[User] = None
        self.load_users()
    
    def hash_password(self, password: str) -> str:
        """تشفير كلمة المرور"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def register(self, username: str, password: str) -> tuple:
        """تسجيل مستخدم جديد"""
        if not username or not password:
            return False, "اسم المستخدم وكلمة المرور مطلوبان"
        
        if len(password) < 4:
            return False, "كلمة المرور يجب أن تكون 4 أحرف على الأقل"
        
        # التحقق من عدم وجود المستخدم
        for user in self.users.values():
            if user.username == username:
                return False, "اسم المستخدم موجود مسبقاً"
        
        user_id = str(uuid.uuid4())[:8]
        user = User(
            user_id=user_id,
            username=username,
            password_hash=self.hash_password(password),
            created_at=datetime.now()
        )
        self.users[user_id] = user
        self.save_users()
        return True, "تم التسجيل بنجاح"
    
    def login(self, username: str, password: str) -> tuple:
        """تسجيل الدخول"""
        for user in self.users.values():
            if user.username == username:
                if user.password_hash == self.hash_password(password):
                    user.last_login = datetime.now()
                    self.current_user = user
                    self.save_users()
                    return True, "تم تسجيل الدخول بنجاح"
                else:
                    return False, "كلمة المرور غير صحيحة"
        return False, "اسم المستخدم غير موجود"
    
    def logout(self):
        """تسجيل الخروج"""
        self.current_user = None
    
    def is_logged_in(self) -> bool:
        """التحقق من تسجيل الدخول"""
        return self.current_user is not None
    
    def save_users(self):
        """حفظ بيانات المستخدمين"""
        try:
            with open('users_data.pkl', 'wb') as f:
                pickle.dump(self.users, f)
        except:
            pass
    
    def load_users(self):
        """تحميل بيانات المستخدمين"""
        try:
            if os.path.exists('users_data.pkl'):
                with open('users_data.pkl', 'rb') as f:
                    self.users = pickle.load(f)
        except:
            pass


# ================ نظام المفضلة والمعاملات السريعة ================

class FavoritesSystem:
    """نظام المفضلة والإرسال السريع"""
    
    def __init__(self):
        self.favorites: Dict[str, List[Dict]] = {}
        self.load_favorites()
    
    def add_favorite(self, user_id: str, wallet_id: str, nickname: str):
        """إضافة محفظة للمفضلة"""
        if user_id not in self.favorites:
            self.favorites[user_id] = []
        
        for fav in self.favorites[user_id]:
            if fav['wallet_id'] == wallet_id:
                return False, "المحفظة موجودة مسبقاً في المفضلة"
        
        self.favorites[user_id].append({
            'wallet_id': wallet_id,
            'nickname': nickname,
            'added_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        self.save_favorites()
        return True, "تمت الإضافة للمفضلة"
    
    def remove_favorite(self, user_id: str, wallet_id: str):
        """حذف من المفضلة"""
        if user_id in self.favorites:
            self.favorites[user_id] = [
                fav for fav in self.favorites[user_id] 
                if fav['wallet_id'] != wallet_id
            ]
            self.save_favorites()
    
    def get_favorites(self, user_id: str) -> List[Dict]:
        """الحصول على قائمة المفضلة"""
        return self.favorites.get(user_id, [])
    
    def save_favorites(self):
        """حفظ المفضلة"""
        try:
            with open('favorites_data.pkl', 'wb') as f:
                pickle.dump(self.favorites, f)
        except:
            pass
    
    def load_favorites(self):
        """تحميل المفضلة"""
        try:
            if os.path.exists('favorites_data.pkl'):
                with open('favorites_data.pkl', 'rb') as f:
                    self.favorites = pickle.load(f)
        except:
            pass


# ================ نظام الصوت (معدل ليعمل على جميع الأنظمة) ================

class SoundSystem:
    """نظام التأثيرات الصوتية - متوافق مع جميع الأنظمة"""
    
    def __init__(self):
        self.enabled = True
        self.sound_available = SOUND_AVAILABLE
    
    def play_sound(self, sound_type="success"):
        """تشغيل صوت حسب النوع"""
        if not self.enabled or not self.sound_available:
            return
        
        try:
            if sound_type == "success":
                winsound.MessageBeep(winsound.MB_OK)
            elif sound_type == "error":
                winsound.MessageBeep(winsound.MB_ICONHAND)
            elif sound_type == "transaction":
                winsound.MessageBeep(winsound.MB_ICONASTERISK)
            else:
                winsound.Beep(1000, 100)  # صوت تنبيه قصير
        except:
            pass
    
    def play_transaction_sound(self):
        """تشغيل صوت المعاملة"""
        self.play_sound("transaction")
    
    def play_success_sound(self):
        """تشغيل صوت النجاح"""
        self.play_sound("success")
    
    def play_error_sound(self):
        """تشغيل صوت الخطأ"""
        self.play_sound("error")
    
    def toggle_sound(self):
        """تشغيل/إيقاف الصوت"""
        self.enabled = not self.enabled
        return self.enabled


# ================ نظام QR Code (معدل ليعمل بدون المكتبة) ================

class QRCodeSystem:
    """نظام رموز QR - يعمل حتى بدون المكتبة"""
    
    def __init__(self):
        self.qr_available = QR_AVAILABLE
    
    def generate_qr_code(self, data: str, size: tuple = (200, 200)):
        """إنشاء رمز QR أو إرجاع None إذا لم تكن المكتبة متوفرة"""
        if not self.qr_available:
            return None
        
        try:
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(data)
            qr.make(fit=True)
            
            qr_image = qr.make_image(fill_color="black", back_color="white")
            qr_image = qr_image.resize(size, Image.Resampling.LANCZOS)
            return qr_image
        except Exception as e:
            print(f"خطأ في إنشاء QR: {e}")
            return None
    
    def qr_to_photoimage(self, qr_image) -> Optional[ImageTk.PhotoImage]:
        """تحويل صورة QR إلى PhotoImage لـ tkinter"""
        if qr_image is None or not self.qr_available:
            return None
        
        try:
          
            return ImageTk.PhotoImage(qr_image)
        except:
            return None
    
    def is_available(self) -> bool:
        """التحقق من توفر مكتبة QR"""
        return self.qr_available


# ================ الفئات الأساسية ================

class Transaction:
    """فئة تمثل معاملة مالية بين مستخدمين"""
    
    def __init__(self, sender: str, receiver: str, amount: float, currency: str = "P2P"):
        self.sender = sender
        self.receiver = receiver
        self.amount = amount
        self.currency = currency
        self.timestamp = time.time()
        self.transaction_id = self.generate_transaction_id()
    
    def generate_transaction_id(self) -> str:
        transaction_string = f"{self.sender}{self.receiver}{self.amount}{self.currency}{self.timestamp}"
        return hashlib.sha256(transaction_string.encode()).hexdigest()
    
    def to_dict(self) -> Dict:
        return {
            "transaction_id": self.transaction_id,
            "sender": self.sender,
            "receiver": self.receiver,
            "amount": self.amount,
            "currency": self.currency,
            "timestamp": self.timestamp
        }


class Block:
    """فئة تمثل كتلة في سلسلة الكتل"""
    
    def __init__(self, index: int, transactions: List[Transaction], previous_hash: str):
        self.index = index
        self.timestamp = time.time()
        self.transactions = transactions
        self.previous_hash = previous_hash
        self.nonce = 0
        self.hash = self.calculate_hash()
    
    def calculate_hash(self) -> str:
        block_string = json.dumps({
            "index": self.index,
            "timestamp": self.timestamp,
            "transactions": [t.to_dict() for t in self.transactions],
            "previous_hash": self.previous_hash,
            "nonce": self.nonce
        }, sort_keys=True)
        return hashlib.sha256(block_string.encode()).hexdigest()
    
    def mine_block(self, difficulty: int):
        target = "0" * difficulty
        while self.hash[:difficulty] != target:
            self.nonce += 1
            self.hash = self.calculate_hash()
    
    def to_dict(self) -> Dict:
        return {
            "index": self.index,
            "timestamp": self.timestamp,
            "transactions": [t.to_dict() for t in self.transactions],
            "previous_hash": self.previous_hash,
            "hash": self.hash,
            "nonce": self.nonce
        }


class Wallet:
    """فئة تمثل محفظة رقمية متعددة العملات"""
    
    def __init__(self, owner_name: str, initial_balance: float = 0, currency: str = "P2P"):
        self.wallet_id = str(uuid.uuid4())[:8]
        self.owner_name = owner_name
        self.balances: Dict[str, float] = {currency: initial_balance}
        self.transaction_history: List[Transaction] = []
        self.created_at = datetime.now()
        
    def add_transaction(self, transaction: Transaction):
        self.transaction_history.append(transaction)
    
    def get_balance(self, currency: str = "P2P") -> float:
        return self.balances.get(currency, 0)
    
    def update_balance(self, amount: float, currency: str = "P2P"):
        if currency not in self.balances:
            self.balances[currency] = 0
        self.balances[currency] += amount
    
    def get_all_balances(self) -> Dict[str, float]:
        return self.balances


class P2PDigitalWallet:
    """النظام الرئيسي للمحفظة الرقمية"""
    
    def __init__(self, difficulty: int = 3):
        self.wallets: Dict[str, Wallet] = {}
        self.pending_transactions: List[Transaction] = []
        self.blockchain: List[Block] = []
        self.difficulty = difficulty
        self.mining_reward = 10
        self.default_currency = "P2P"
        self.create_genesis_block()
    
    def create_genesis_block(self):
        genesis_transaction = Transaction("النظام", "النظام", 0)
        genesis_block = Block(0, [genesis_transaction], "0")
        self.blockchain.append(genesis_block)
    
    def create_wallet(self, owner_name: str, initial_balance: float = 0, currency: str = "P2P") -> Wallet:
        wallet = Wallet(owner_name, initial_balance, currency)
        self.wallets[wallet.wallet_id] = wallet
        return wallet
    
    def get_wallet(self, wallet_id: str) -> Optional[Wallet]:
        return self.wallets.get(wallet_id)
    
    def send_money(self, sender_id: str, receiver_id: str, amount: float, currency: str = "P2P") -> tuple:
        sender_wallet = self.get_wallet(sender_id)
        receiver_wallet = self.get_wallet(receiver_id)
        
        if not sender_wallet:
            return False, "المحفظة المرسلة غير موجودة"
        
        if not receiver_wallet:
            return False, "المحفظة المستقبلة غير موجودة"
        
        if sender_id == receiver_id:
            return False, "لا يمكنك إرسال الأموال إلى نفس المحفظة"
        
        if sender_wallet.get_balance(currency) < amount:
            return False, f"رصيد غير كافٍ. الرصيد الحالي: {sender_wallet.get_balance(currency)} {currency}"
        
        if amount <= 0:
            return False, "المبلغ يجب أن يكون أكبر من صفر"
        
        transaction = Transaction(sender_wallet.wallet_id, receiver_wallet.wallet_id, amount, currency)
        self.pending_transactions.append(transaction)
        sender_wallet.update_balance(-amount, currency)
        receiver_wallet.update_balance(amount, currency)
        sender_wallet.add_transaction(transaction)
        receiver_wallet.add_transaction(transaction)
        
        return True, f"تم إرسال {amount} {currency} بنجاح"
    
    def mine_pending_transactions(self, miner_wallet_id: str) -> tuple:
        if not self.pending_transactions:
            return False, "لا توجد معاملات معلقة للتعدين"
        
        miner_wallet = self.get_wallet(miner_wallet_id)
        if not miner_wallet:
            return False, "محفظة المعدّن غير موجودة"
        
        reward_transaction = Transaction("النظام", miner_wallet.wallet_id, self.mining_reward)
        transactions_to_mine = self.pending_transactions.copy()
        transactions_to_mine.append(reward_transaction)
        
        previous_block = self.blockchain[-1]
        new_block = Block(len(self.blockchain), transactions_to_mine, previous_block.hash)
        new_block.mine_block(self.difficulty)
        
        self.blockchain.append(new_block)
        miner_wallet.update_balance(self.mining_reward)
        miner_wallet.add_transaction(reward_transaction)
        self.pending_transactions = []
        
        return True, f"تم تعدين الكتلة بنجاح! المكافأة: {self.mining_reward} عملة"
    
    def get_all_wallets(self) -> List[Dict]:
        wallet_list = []
        for wallet_id, wallet in self.wallets.items():
            wallet_list.append({
                "wallet_id": wallet_id,
                "owner_name": wallet.owner_name,
                "balances": wallet.get_all_balances(),
                "created_at": wallet.created_at.strftime("%Y-%m-%d %H:%M:%S")
            })
        return wallet_list


# ================ واجهة المستخدم الرسومية ================

class DigitalWalletGUI:
    """الواجهة الرسومية المطورة"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("🏦 P2P Digital Wallet")
        self.root.geometry("1300x750")
        
        # الأنظمة المساعدة
        self.wallet_system = P2PDigitalWallet(difficulty=3)
        self.auth_system = AuthSystem()
        self.favorites_system = FavoritesSystem()
        self.sound_system = SoundSystem()
        self.qr_system = QRCodeSystem()
        self.localization = Localization(Language.ARABIC)
        
        # المتغيرات
        self.current_theme = "light"
        self.log_text = None
        
        # إعداد الألوان
        self.setup_colors()
        
        # إعداد الواجهة
        self.setup_ui()
        
        # عرض رسالة حول QR Code إذا لم يكن متوفراً
        if not self.qr_system.is_available():
            print("📱 ميزة QR Code غير متوفرة. لتثبيتها: pip install qrcode[pil] Pillow")
        
        # التحقق من تسجيل الدخول
        self.check_login()
    
    def setup_colors(self):
        """إعداد أنظمة الألوان للثيمات"""
        self.themes = {
            "light": {
                'primary': '#2196F3', 'success': '#4CAF50', 'warning': '#FF9800',
                'danger': '#f44336', 'dark': '#333333', 'light': '#ffffff',
                'bg': '#f5f5f5', 'secondary': '#9C27B0', 'text': '#333333',
                'text_light': '#ffffff', 'frame_bg': '#ffffff',
                'entry_bg': '#ffffff', 'entry_fg': '#333333',
            },
            "dark": {
                'primary': '#1976D2', 'success': '#388E3C', 'warning': '#F57C00',
                'danger': '#D32F2F', 'dark': '#1a1a1a', 'light': '#2d2d2d',
                'bg': '#121212', 'secondary': '#7B1FA2', 'text': '#ffffff',
                'text_light': '#ffffff', 'frame_bg': '#2d2d2d',
                'entry_bg': '#3d3d3d', 'entry_fg': '#ffffff',
            }
        }
        self.colors = self.themes[self.current_theme]
        self.fonts = {
            'title': ('Arial', 18, 'bold'), 'subtitle': ('Arial', 14, 'bold'),
            'normal': ('Arial', 11), 'small': ('Arial', 9),
            'button': ('Arial', 11, 'bold')
        }
    
    def toggle_theme(self):
        """تبديل الثيم"""
        self.current_theme = "dark" if self.current_theme == "light" else "light"
        self.colors = self.themes[self.current_theme]
        self.root.configure(bg=self.colors['bg'])
        for widget in self.root.winfo_children():
            widget.destroy()
        self.setup_ui()
        self.show_dashboard()
    
    def setup_ui(self):
        """إعداد واجهة المستخدم"""
        self.root.configure(bg=self.colors['bg'])
        
        main_frame = tk.Frame(self.root, bg=self.colors['bg'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # العنوان
        title_frame = tk.Frame(main_frame, bg=self.colors['primary'], height=60)
        title_frame.pack(fill=tk.X, pady=(0, 10))
        title_frame.pack_propagate(False)
        
        title_label = tk.Label(
            title_frame,
            text=self.localization.get("app_title"),
            font=self.fonts['title'],
            bg=self.colors['primary'],
            fg=self.colors['text_light']
        )
        title_label.pack(expand=True)
        
        # شريط الحالة
        status_frame = tk.Frame(main_frame, bg=self.colors['primary'], height=30)
        status_frame.pack(fill=tk.X, pady=(0, 5))
        status_frame.pack_propagate(False)
        
        if self.auth_system.is_logged_in():
            status_text = f"👤 {self.auth_system.current_user.username} | {'🇸🇦 العربية' if self.localization.language == Language.ARABIC else '🇺🇸 English'}"
        else:
            status_text = "🔒 " + self.localization.get("login_required")
        
        self.status_label = tk.Label(
            status_frame, text=status_text, font=self.fonts['small'],
            bg=self.colors['primary'], fg=self.colors['text_light']
        )
        self.status_label.pack(side=tk.LEFT, padx=10)
        
        # أزرار التحكم
        control_frame = tk.Frame(status_frame, bg=self.colors['primary'])
        control_frame.pack(side=tk.RIGHT, padx=10)
        
        sound_text = "🔊" if self.sound_system.enabled else "🔇"
        self.sound_btn = tk.Button(
            control_frame, text=sound_text, command=self.toggle_sound,
            font=self.fonts['small'], bg=self.colors['primary'],
            fg=self.colors['text_light'], relief=tk.FLAT, cursor='hand2'
        )
        self.sound_btn.pack(side=tk.LEFT, padx=2)
        
        tk.Button(
            control_frame, text="🇸🇦/🇺🇸", command=self.toggle_language,
            font=self.fonts['small'], bg=self.colors['primary'],
            fg=self.colors['text_light'], relief=tk.FLAT, cursor='hand2'
        ).pack(side=tk.LEFT, padx=2)
        
        tk.Button(
            control_frame, text="🌓", command=self.toggle_theme,
            font=self.fonts['small'], bg=self.colors['primary'],
            fg=self.colors['text_light'], relief=tk.FLAT, cursor='hand2'
        ).pack(side=tk.LEFT, padx=2)
        
        # الشريط الجانبي والمحتوى
        self.create_sidebar(main_frame)
        
        self.content_frame = tk.Frame(
            main_frame, bg=self.colors['frame_bg'],
            relief=tk.RAISED, bd=2
        )
        self.content_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))
    
    def create_sidebar(self, parent):
        """إنشاء الشريط الجانبي"""
        sidebar = tk.Frame(parent, bg=self.colors['dark'], width=220)
        sidebar.pack(side=tk.LEFT, fill=tk.Y)
        sidebar.pack_propagate(False)
        
        logo_frame = tk.Frame(sidebar, bg=self.colors['dark'], height=80)
        logo_frame.pack(fill=tk.X, pady=20)
        logo_frame.pack_propagate(False)
        
        tk.Label(
            logo_frame, text="💰\nMulti-Currency Wallet",
            font=('Arial', 14, 'bold'), bg=self.colors['dark'],
            fg=self.colors['text_light']
        ).pack(expand=True)
        
        buttons = [
            (self.localization.get("dashboard"), self.show_dashboard, self.colors['primary']),
            (self.localization.get("create_wallet"), self.show_create_wallet, self.colors['success']),
            (self.localization.get("send_money"), self.show_send_money, self.colors['warning']),
            (self.localization.get("quick_send"), self.show_quick_send, self.colors['secondary']),
            (self.localization.get("qr_code"), self.show_qr_code, self.colors['primary']),
            (self.localization.get("all_wallets"), self.show_all_wallets, self.colors['success']),
            (self.localization.get("mining"), self.show_mining, self.colors['danger']),
            (self.localization.get("blockchain"), self.show_blockchain, self.colors['warning']),
        ]
        
        for text, command, color in buttons:
            btn = tk.Button(
                sidebar, text=text, command=command,
                font=self.fonts['button'], bg=color,
                fg=self.colors['text_light'], relief=tk.FLAT,
                cursor='hand2', height=2
            )
            btn.pack(pady=3, padx=10, fill=tk.X)
            btn.bind('<Enter>', lambda e, b=btn, c=color: b.configure(bg=self.lighten_color(c)))
            btn.bind('<Leave>', lambda e, b=btn, c=color: b.configure(bg=c))
    
    def lighten_color(self, color):
        color_map = {
            '#2196F3': '#42A5F5', '#4CAF50': '#66BB6A', '#FF9800': '#FFA726',
            '#f44336': '#EF5350', '#9C27B0': '#AB47BC', '#1976D2': '#1E88E5',
            '#388E3C': '#43A047', '#F57C00': '#FB8C00', '#D32F2F': '#E53935',
            '#7B1FA2': '#8E24AA'
        }
        return color_map.get(color, color)
    
    def check_login(self):
        """التحقق من تسجيل الدخول"""
        if not self.auth_system.is_logged_in():
            self.show_login()
        else:
            self.show_dashboard()
    
    def show_login(self):
        """عرض صفحة تسجيل الدخول"""
        self.clear_content()
        
        login_frame = tk.Frame(self.content_frame, bg=self.colors['frame_bg'])
        login_frame.pack(expand=True)
        
        tk.Label(
            login_frame, text="🔐 " + self.localization.get("login"),
            font=('Arial', 24, 'bold'), bg=self.colors['frame_bg'],
            fg=self.colors['text']
        ).pack(pady=20)
        
        # اسم المستخدم
        tk.Label(
            login_frame, text=self.localization.get("username") + ":",
            font=self.fonts['normal'], bg=self.colors['frame_bg'],
            fg=self.colors['text']
        ).pack(pady=5)
        
        username_entry = tk.Entry(
            login_frame, font=self.fonts['normal'], width=30,
            bg=self.colors['entry_bg'], fg=self.colors['entry_fg']
        )
        username_entry.pack(pady=5)
        
        # كلمة المرور
        tk.Label(
            login_frame, text=self.localization.get("password") + ":",
            font=self.fonts['normal'], bg=self.colors['frame_bg'],
            fg=self.colors['text']
        ).pack(pady=5)
        
        password_entry = tk.Entry(
            login_frame, font=self.fonts['normal'], width=30,
            show="*", bg=self.colors['entry_bg'], fg=self.colors['entry_fg']
        )
        password_entry.pack(pady=5)
        
        def do_login():
            username = username_entry.get().strip()
            password = password_entry.get().strip()
            success, message = self.auth_system.login(username, password)
            if success:
                self.sound_system.play_success_sound()
                messagebox.showinfo(self.localization.get("success"), message)
                self.update_status()
                self.show_dashboard()
            else:
                self.sound_system.play_error_sound()
                messagebox.showerror(self.localization.get("error"), message)
        
        def do_register():
            username = username_entry.get().strip()
            password = password_entry.get().strip()
            success, message = self.auth_system.register(username, password)
            if success:
                self.sound_system.play_success_sound()
                messagebox.showinfo(self.localization.get("success"), message)
            else:
                self.sound_system.play_error_sound()
                messagebox.showerror(self.localization.get("error"), message)
        
        btn_frame = tk.Frame(login_frame, bg=self.colors['frame_bg'])
        btn_frame.pack(pady=20)
        
        tk.Button(
            btn_frame, text=self.localization.get("login_btn"),
            command=do_login, font=self.fonts['button'],
            bg=self.colors['primary'], fg=self.colors['text_light'],
            width=15, height=2, cursor='hand2'
        ).pack(side=tk.LEFT, padx=10)
        
        tk.Button(
            btn_frame, text=self.localization.get("register_btn"),
            command=do_register, font=self.fonts['button'],
            bg=self.colors['success'], fg=self.colors['text_light'],
            width=15, height=2, cursor='hand2'
        ).pack(side=tk.LEFT, padx=10)
    
    def show_dashboard(self):
        """عرض لوحة التحكم الرئيسية"""
        self.clear_content()
        
        if not self.auth_system.is_logged_in():
            self.show_login()
            return
        
        tk.Label(
            self.content_frame, text=self.localization.get("dashboard"),
            font=self.fonts['title'], bg=self.colors['frame_bg'],
            fg=self.colors['text']
        ).pack(pady=20)
        
        # بطاقات المعلومات
        info_frame = tk.Frame(self.content_frame, bg=self.colors['frame_bg'])
        info_frame.pack(fill=tk.X, padx=20, pady=10)
        
        cards = [
            ("👥 " + self.localization.get("all_wallets"), str(len(self.wallet_system.wallets)), self.colors['primary']),
            ("💸 " + self.localization.get("mining"), str(len(self.wallet_system.pending_transactions)), self.colors['warning']),
            ("📦 " + self.localization.get("blockchain"), str(len(self.wallet_system.blockchain)), self.colors['success']),
        ]
        
        for title, value, color in cards:
            card = tk.Frame(info_frame, bg=color, width=200, height=100)
            card.pack(side=tk.LEFT, padx=10, expand=True)
            card.pack_propagate(False)
            
            tk.Label(
                card, text=title, font=self.fonts['subtitle'],
                bg=color, fg=self.colors['text_light']
            ).pack(pady=(20, 5))
            
            tk.Label(
                card, text=value, font=('Arial', 24, 'bold'),
                bg=color, fg=self.colors['text_light']
            ).pack()
        
        # العملات المتاحة
        currencies_frame = tk.Frame(self.content_frame, bg=self.colors['frame_bg'])
        currencies_frame.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Label(
            currencies_frame, text="💱 العملات المدعومة:",
            font=self.fonts['subtitle'], bg=self.colors['frame_bg'],
            fg=self.colors['text']
        ).pack(anchor='w')
        
        for code, currency in CurrencySystem.get_all_currencies().items():
            tk.Label(
                currencies_frame,
                text=f"{currency.icon} {currency.name} ({currency.symbol}) - سعر الصرف: {currency.exchange_rate}",
                font=self.fonts['normal'], bg=self.colors['frame_bg'],
                fg=self.colors['text']
            ).pack(anchor='w', padx=20)
        
        # حالة QR Code
        if not self.qr_system.is_available():
            tk.Label(
                currencies_frame,
                text="⚠️ " + self.localization.get("qr_not_available"),
                font=self.fonts['small'], bg=self.colors['frame_bg'],
                fg=self.colors['danger']
            ).pack(anchor='w', padx=20)
        
        # سجل العمليات
        tk.Label(
            self.content_frame,
            text="📋 " + self.localization.get("transaction_history"),
            font=self.fonts['subtitle'], bg=self.colors['frame_bg'],
            fg=self.colors['text']
        ).pack(pady=(20, 10))
        
        log_frame = tk.Frame(self.content_frame, bg=self.colors['frame_bg'])
        log_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        self.log_text = scrolledtext.ScrolledText(
            log_frame, height=10, font=('Courier', 10),
            bg=self.colors['entry_bg'], fg=self.colors['entry_fg'],
            wrap=tk.WORD
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        self.log_message(self.localization.get("welcome"))
    
    def show_create_wallet(self):
        """عرض صفحة إنشاء محفظة جديدة"""
        self.clear_content()
        
        if not self.auth_system.is_logged_in():
            self.show_login()
            return
        
        tk.Label(
            self.content_frame, text=self.localization.get("create_wallet"),
            font=self.fonts['title'], bg=self.colors['frame_bg'],
            fg=self.colors['text']
        ).pack(pady=20)
        
        form_frame = tk.Frame(self.content_frame, bg=self.colors['frame_bg'])
        form_frame.pack(pady=20)
        
        # الاسم
        tk.Label(
            form_frame, text="👤 " + self.localization.get("username") + ":",
            font=self.fonts['normal'], bg=self.colors['frame_bg'],
            fg=self.colors['text']
        ).grid(row=0, column=0, sticky='w', pady=10)
        
        name_entry = tk.Entry(
            form_frame, font=self.fonts['normal'], width=30,
            bg=self.colors['entry_bg'], fg=self.colors['entry_fg']
        )
        name_entry.grid(row=0, column=1, pady=10, padx=10)
        
        # الرصيد
        tk.Label(
            form_frame, text="💰 " + self.localization.get("balance") + ":",
            font=self.fonts['normal'], bg=self.colors['frame_bg'],
            fg=self.colors['text']
        ).grid(row=1, column=0, sticky='w', pady=10)
        
        balance_entry = tk.Entry(
            form_frame, font=self.fonts['normal'], width=30,
            bg=self.colors['entry_bg'], fg=self.colors['entry_fg']
        )
        balance_entry.grid(row=1, column=1, pady=10, padx=10)
        balance_entry.insert(0, "0")
        
        # اختيار العملة
        tk.Label(
            form_frame, text="💱 " + self.localization.get("currency") + ":",
            font=self.fonts['normal'], bg=self.colors['frame_bg'],
            fg=self.colors['text']
        ).grid(row=2, column=0, sticky='w', pady=10)
        
        currency_var = tk.StringVar(value="P2P")
        currency_menu = ttk.Combobox(
            form_frame, textvariable=currency_var,
            values=list(CurrencySystem.CURRENCIES.keys()),
            state="readonly", width=27, font=self.fonts['normal']
        )
        currency_menu.grid(row=2, column=1, pady=10, padx=10)
        
        def create_wallet():
            name = name_entry.get().strip()
            if not name:
                messagebox.showerror(self.localization.get("error"), "الرجاء إدخال اسم صاحب المحفظة")
                return
            
            try:
                balance = float(balance_entry.get())
            except ValueError:
                messagebox.showerror(self.localization.get("error"), "الرجاء إدخال رصيد صحيح")
                return
            
            currency = currency_var.get()
            wallet = self.wallet_system.create_wallet(name, balance, currency)
            
            result_text = f"""✅ {self.localization.get("success")}!

👤 {self.localization.get("username")}: {wallet.owner_name}
🔑 ID: {wallet.wallet_id}
💰 {self.localization.get("balance")}: {wallet.get_balance(currency)} {currency}
📅 {wallet.created_at.strftime('%Y-%m-%d %H:%M:%S')}

⚠️ هام: احفظ معرف المحفظة!"""
            
            self.sound_system.play_success_sound()
            messagebox.showinfo(self.localization.get("success"), result_text)
            self.log_message(f"تم إنشاء محفظة جديدة: {name}")
            
            name_entry.delete(0, tk.END)
            balance_entry.delete(0, tk.END)
            balance_entry.insert(0, "0")
        
        tk.Button(
            form_frame, text="🚀 " + self.localization.get("create_wallet"),
            command=create_wallet, font=self.fonts['button'],
            bg=self.colors['success'], fg=self.colors['text_light'],
            cursor='hand2', height=2, width=20
        ).grid(row=3, column=0, columnspan=2, pady=20)
    
    def show_send_money(self):
        """عرض صفحة إرسال الأموال"""
        self.clear_content()
        
        if not self.auth_system.is_logged_in():
            self.show_login()
            return
        
        tk.Label(
            self.content_frame, text=self.localization.get("send_money"),
            font=self.fonts['title'], bg=self.colors['frame_bg'],
            fg=self.colors['text']
        ).pack(pady=20)
        
        wallets = self.wallet_system.get_all_wallets()
        if not wallets:
            tk.Label(
                self.content_frame, text="❌ لا توجد محافظ!",
                font=self.fonts['subtitle'], bg=self.colors['frame_bg'],
                fg=self.colors['danger']
            ).pack(pady=20)
            return
        
        # جدول المحافظ
        table_frame = tk.Frame(self.content_frame, bg=self.colors['frame_bg'])
        table_frame.pack(fill=tk.X, padx=20, pady=10)
        
        columns = ('المعرف', 'الاسم', 'الأرصدة')
        tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=5)
        
        tree.heading('المعرف', text='🔑 المعرف')
        tree.heading('الاسم', text='👤 الاسم')
        tree.heading('الأرصدة', text='💰 الأرصدة')
        
        for w in wallets:
            balances_str = ", ".join([f"{k}: {v}" for k, v in w['balances'].items()])
            tree.insert('', tk.END, values=(w['wallet_id'], w['owner_name'], balances_str))
        
        tree.pack(fill=tk.X)
        
        # نموذج الإرسال
        form_frame = tk.Frame(self.content_frame, bg=self.colors['frame_bg'])
        form_frame.pack(pady=20)
        
        labels = ["📤 المرسل:", "📥 المستلم:", "💸 " + self.localization.get("amount") + ":", "💱 " + self.localization.get("currency") + ":"]
        entries = []
        
        for i, label in enumerate(labels):
            tk.Label(
                form_frame, text=label, font=self.fonts['normal'],
                bg=self.colors['frame_bg'], fg=self.colors['text']
            ).grid(row=i, column=0, sticky='w', pady=5)
            
            if i == 3:  # اختيار العملة
                currency_var = tk.StringVar(value="P2P")
                entry = ttk.Combobox(
                    form_frame, textvariable=currency_var,
                    values=list(CurrencySystem.CURRENCIES.keys()),
                    state="readonly", width=27, font=self.fonts['normal']
                )
            else:
                entry = tk.Entry(
                    form_frame, font=self.fonts['normal'], width=30,
                    bg=self.colors['entry_bg'], fg=self.colors['entry_fg']
                )
            
            entry.grid(row=i, column=1, pady=5)
            entries.append(entry)
        
        def send_money():
            sender_id = entries[0].get().strip()
            receiver_id = entries[1].get().strip()
            
            if not sender_id or not receiver_id:
                messagebox.showerror(self.localization.get("error"), "الرجاء إدخال المعرفات")
                return
            
            try:
                amount = float(entries[2].get())
            except ValueError:
                messagebox.showerror(self.localization.get("error"), "مبلغ غير صحيح")
                return
            
            currency = entries[3].get()
            success, message = self.wallet_system.send_money(sender_id, receiver_id, amount, currency)
            
            if success:
                self.sound_system.play_transaction_sound()
                # إضافة للمفضلة تلقائياً
                receiver_wallet = self.wallet_system.get_wallet(receiver_id)
                if receiver_wallet:
                    self.favorites_system.add_favorite(
                        self.auth_system.current_user.user_id,
                        receiver_id,
                        receiver_wallet.owner_name
                    )
                messagebox.showinfo(self.localization.get("success"), message)
                self.show_send_money()  # تحديث الصفحة
            else:
                self.sound_system.play_error_sound()
                messagebox.showerror(self.localization.get("error"), message)
        
        tk.Button(
            form_frame, text="💸 " + self.localization.get("send"),
            command=send_money, font=self.fonts['button'],
            bg=self.colors['warning'], fg=self.colors['text_light'],
            cursor='hand2', height=2, width=20
        ).grid(row=4, column=0, columnspan=2, pady=20)
    
    def show_quick_send(self):
        """عرض صفحة الإرسال السريع"""
        self.clear_content()
        
        if not self.auth_system.is_logged_in():
            self.show_login()
            return
        
        tk.Label(
            self.content_frame, text=self.localization.get("quick_send"),
            font=self.fonts['title'], bg=self.colors['frame_bg'],
            fg=self.colors['text']
        ).pack(pady=20)
        
        favorites = self.favorites_system.get_favorites(self.auth_system.current_user.user_id)
        
        if not favorites:
            tk.Label(
                self.content_frame,
                text="❌ لا توجد مفضلات! قم بإرسال أموال أولاً",
                font=self.fonts['subtitle'], bg=self.colors['frame_bg'],
                fg=self.colors['text']
            ).pack(pady=20)
            return
        
        for fav in favorites:
            wallet = self.wallet_system.get_wallet(fav['wallet_id'])
            if wallet:
                fav_frame = tk.Frame(
                    self.content_frame, bg=self.colors['frame_bg'],
                    relief=tk.RAISED, bd=1
                )
                fav_frame.pack(fill=tk.X, padx=20, pady=5)
                
                tk.Label(
                    fav_frame,
                    text=f"👤 {wallet.owner_name} - 🔑 {fav['wallet_id']}",
                    font=self.fonts['normal'], bg=self.colors['frame_bg'],
                    fg=self.colors['text']
                ).pack(side=tk.LEFT, padx=10)
                
                tk.Button(
                    fav_frame, text="💸 إرسال سريع",
                    command=lambda wid=fav['wallet_id']: self.quick_send_dialog(wid),
                    font=self.fonts['small'], bg=self.colors['primary'],
                    fg=self.colors['text_light'], cursor='hand2'
                ).pack(side=tk.RIGHT, padx=10)
    
    def quick_send_dialog(self, receiver_id: str):
        """حوار الإرسال السريع"""
        amount = simpledialog.askfloat(
            self.localization.get("quick_send"),
            self.localization.get("amount") + ":",
            parent=self.root
        )
        
        if amount:
            currency = simpledialog.askstring(
                self.localization.get("currency"),
                f"{self.localization.get('select_currency')} (P2P/BTC/ETH/GOLD/SILVER):",
                initialvalue="P2P",
                parent=self.root
            )
            
            if currency and currency.upper() in CurrencySystem.CURRENCIES:
                wallets = self.wallet_system.get_all_wallets()
                if wallets:
                    sender_id = wallets[0]['wallet_id']
                    success, message = self.wallet_system.send_money(
                        sender_id, receiver_id, amount, currency.upper()
                    )
                    
                    if success:
                        self.sound_system.play_transaction_sound()
                        messagebox.showinfo(self.localization.get("success"), message)
                    else:
                        self.sound_system.play_error_sound()
                        messagebox.showerror(self.localization.get("error"), message)
    
    def show_qr_code(self):
        """عرض صفحة رموز QR"""
        self.clear_content()
        
        tk.Label(
            self.content_frame, text=self.localization.get("qr_code"),
            font=self.fonts['title'], bg=self.colors['frame_bg'],
            fg=self.colors['text']
        ).pack(pady=20)
        
        if not self.qr_system.is_available():
            tk.Label(
                self.content_frame,
                text=f"❌ {self.localization.get('qr_not_available')}\n{self.localization.get('install_qr')}",
                font=self.fonts['subtitle'], bg=self.colors['frame_bg'],
                fg=self.colors['danger'], justify=tk.CENTER
            ).pack(pady=50)
            return
        
        qr_frame = tk.Frame(self.content_frame, bg=self.colors['frame_bg'])
        qr_frame.pack(pady=20)
        
        tk.Label(
            qr_frame, text="🔑 معرف المحفظة:",
            font=self.fonts['normal'], bg=self.colors['frame_bg'],
            fg=self.colors['text']
        ).pack(side=tk.LEFT, padx=10)
        
        wallet_entry = tk.Entry(
            qr_frame, font=self.fonts['normal'], width=30,
            bg=self.colors['entry_bg'], fg=self.colors['entry_fg']
        )
        wallet_entry.pack(side=tk.LEFT, padx=10)
        
        qr_display = tk.Label(self.content_frame, bg=self.colors['frame_bg'])
        qr_display.pack(pady=20)
        
        def generate_qr():
            wallet_id = wallet_entry.get().strip()
            if wallet_id:
                wallet = self.wallet_system.get_wallet(wallet_id)
                if wallet:
                    qr_data = f"P2P_WALLET:{wallet_id}:{wallet.owner_name}"
                    qr_image = self.qr_system.generate_qr_code(qr_data)
                    if qr_image:
                        qr_photo = self.qr_system.qr_to_photoimage(qr_image)
                        if qr_photo:
                            qr_display.config(image=qr_photo)
                            qr_display.image = qr_photo
                            self.sound_system.play_success_sound()
                        else:
                            messagebox.showerror(self.localization.get("error"), "فشل في إنشاء صورة QR")
                    else:
                        messagebox.showerror(self.localization.get("error"), "فشل في إنشاء QR Code")
                else:
                    messagebox.showerror(self.localization.get("error"), "المحفظة غير موجودة")
        
        tk.Button(
            qr_frame, text="📱 إنشاء QR", command=generate_qr,
            font=self.fonts['button'], bg=self.colors['primary'],
            fg=self.colors['text_light'], cursor='hand2'
        ).pack(side=tk.LEFT, padx=10)
    
    def show_all_wallets(self):
        """عرض جميع المحافظ"""
        self.clear_content()
        
        tk.Label(
            self.content_frame, text=self.localization.get("all_wallets"),
            font=self.fonts['title'], bg=self.colors['frame_bg'],
            fg=self.colors['text']
        ).pack(pady=20)
        
        wallets = self.wallet_system.get_all_wallets()
        
        if not wallets:
            tk.Label(
                self.content_frame, text="❌ لا توجد محافظ",
                font=self.fonts['subtitle'], bg=self.colors['frame_bg'],
                fg=self.colors['text']
            ).pack(pady=20)
            return
        
        table_frame = tk.Frame(self.content_frame, bg=self.colors['frame_bg'])
        table_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        columns = ('المعرف', 'الاسم', 'الأرصدة', 'التاريخ')
        tree = ttk.Treeview(table_frame, columns=columns, show='headings')
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=150)
        
        for w in wallets:
            balances_str = ", ".join([f"{k}: {v}" for k, v in w['balances'].items()])
            tree.insert('', tk.END, values=(w['wallet_id'], w['owner_name'], balances_str, w['created_at']))
        
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def show_mining(self):
        """عرض صفحة التعدين"""
        self.clear_content()
        
        tk.Label(
            self.content_frame, text=self.localization.get("mining"),
            font=self.fonts['title'], bg=self.colors['frame_bg'],
            fg=self.colors['text']
        ).pack(pady=20)
        
        pending_frame = tk.Frame(self.content_frame, bg=self.colors['frame_bg'])
        pending_frame.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Label(
            pending_frame,
            text=f"📋 المعاملات المعلقة: {len(self.wallet_system.pending_transactions)}",
            font=self.fonts['subtitle'], bg=self.colors['frame_bg'],
            fg=self.colors['text']
        ).pack(anchor='w')
        
        miner_frame = tk.Frame(self.content_frame, bg=self.colors['frame_bg'])
        miner_frame.pack(fill=tk.X, padx=20, pady=20)
        
        tk.Label(
            miner_frame, text="🔑 معرف المعدّن:",
            font=self.fonts['normal'], bg=self.colors['frame_bg'],
            fg=self.colors['text']
        ).pack(side=tk.LEFT)
        
        miner_entry = tk.Entry(
            miner_frame, font=self.fonts['normal'], width=30,
            bg=self.colors['entry_bg'], fg=self.colors['entry_fg']
        )
        miner_entry.pack(side=tk.LEFT, padx=10)
        
        progress_frame = tk.Frame(self.content_frame, bg=self.colors['frame_bg'])
        progress_frame.pack(fill=tk.X, padx=20, pady=10)
        
        self.progress_bar = ttk.Progressbar(progress_frame, mode='indeterminate', length=400)
        self.progress_bar.pack()
        
        self.mining_status = tk.Label(
            progress_frame, text="", font=self.fonts['normal'],
            bg=self.colors['frame_bg'], fg=self.colors['text']
        )
        self.mining_status.pack(pady=10)
        
        def start_mining():
            miner_id = miner_entry.get().strip()
            if not miner_id:
                messagebox.showerror(self.localization.get("error"), "الرجاء إدخال معرف المحفظة")
                return
            
            self.mining_status.config(text="⛏️ جاري التعدين...")
            self.progress_bar.start(10)
            
            def mine():
                success, message = self.wallet_system.mine_pending_transactions(miner_id)
                self.root.after(0, mining_complete, success, message)
            
            threading.Thread(target=mine, daemon=True).start()
        
        def mining_complete(success, message):
            self.progress_bar.stop()
            if success:
                self.sound_system.play_success_sound()
                self.mining_status.config(text="✅ " + message, fg=self.colors['success'])
                messagebox.showinfo(self.localization.get("success"), message)
            else:
                self.sound_system.play_error_sound()
                self.mining_status.config(text="❌ " + message, fg=self.colors['danger'])
        
        tk.Button(
            miner_frame, text="⛏️ بدء التعدين", command=start_mining,
            font=self.fonts['button'], bg=self.colors['danger'],
            fg=self.colors['text_light'], cursor='hand2', height=2
        ).pack(side=tk.LEFT, padx=20)
    
    def show_blockchain(self):
        """عرض سلسلة الكتل"""
        self.clear_content()
        
        tk.Label(
            self.content_frame, text=self.localization.get("blockchain"),
            font=self.fonts['title'], bg=self.colors['frame_bg'],
            fg=self.colors['text']
        ).pack(pady=20)
        
        blockchain = self.wallet_system.blockchain
        
        info_frame = tk.Frame(self.content_frame, bg=self.colors['frame_bg'])
        info_frame.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Label(
            info_frame, text=f"📊 عدد الكتل: {len(blockchain)}",
            font=self.fonts['subtitle'], bg=self.colors['frame_bg'],
            fg=self.colors['text']
        ).pack(anchor='w')
        
        blocks_frame = tk.Frame(self.content_frame, bg=self.colors['frame_bg'])
        blocks_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        canvas = tk.Canvas(blocks_frame, bg=self.colors['frame_bg'])
        scrollbar = ttk.Scrollbar(blocks_frame, orient=tk.VERTICAL, command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.colors['frame_bg'])
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        for block in blockchain[-10:]:
            block_frame = tk.Frame(
                scrollable_frame, bg=self.colors['frame_bg'],
                relief=tk.RAISED, bd=2
            )
            block_frame.pack(fill=tk.X, pady=10, padx=10)
            
            tk.Label(
                block_frame, text=f"📦 كتلة #{block.index}",
                font=self.fonts['subtitle'], bg=self.colors['primary'],
                fg=self.colors['text_light']
            ).pack(fill=tk.X)
            
            info = [
                f"⏰ {datetime.fromtimestamp(block.timestamp).strftime('%Y-%m-%d %H:%M:%S')}",
                f"🔗 {block.previous_hash[:30]}...",
                f"🔐 {block.hash[:30]}...",
                f"📊 معاملات: {len(block.transactions)}"
            ]
            
            for line in info:
                tk.Label(
                    block_frame, text=line, font=self.fonts['small'],
                    bg=self.colors['frame_bg'], fg=self.colors['text']
                ).pack(fill=tk.X, padx=10, pady=2)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def toggle_sound(self):
        """تشغيل/إيقاف الصوت"""
        enabled = self.sound_system.toggle_sound()
        self.sound_btn.config(text="🔊" if enabled else "🔇")
    
    def toggle_language(self):
        """تبديل اللغة"""
        self.localization.switch_language()
        self.update_status()
        for widget in self.root.winfo_children():
            widget.destroy()
        self.setup_ui()
        self.show_dashboard()
    
    def update_status(self):
        """تحديث شريط الحالة"""
        if self.auth_system.is_logged_in():
            status_text = f"👤 {self.auth_system.current_user.username} | {'🇸🇦 العربية' if self.localization.language == Language.ARABIC else '🇺🇸 English'}"
        else:
            status_text = "🔒 " + self.localization.get("login_required")
        
        if hasattr(self, 'status_label'):
            self.status_label.config(text=status_text)
    
    def clear_content(self):
        """مسح المحتوى الحالي"""
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        self.log_text = None
    
    def log_message(self, message):
        """إضافة رسالة إلى السجل"""
        if self.log_text is not None:
            try:
                if self.log_text.winfo_exists():
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
                    self.log_text.see(tk.END)
            except (tk.TclError, AttributeError):
                pass


# ================ تشغيل التطبيق ================

def main():
    print("=" * 60)
    print("🚀 بدء تشغيل نظام المحفظة الرقمية P2P...")
    print("=" * 60)
    
    root = tk.Tk()
    app = DigitalWalletGUI(root)
    
    # توسيط النافذة
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')
    
    print("✅ التطبيق جاهز!")
    if not QR_AVAILABLE:
        print("⚠️ ملاحظة: ميزة QR Code غير متوفرة")
        print("   لتثبيتها: pip install qrcode[pil] Pillow")
    
    root.mainloop()


if __name__ == "__main__":
    main()