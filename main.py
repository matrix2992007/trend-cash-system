import os
import telebot
from telebot import types
from dotenv import load_dotenv
import database # استدعاء ملف القاعدة اللي عملناه فوق

# تحميل الإعدادات السرية
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = os.getenv("ADMIN_ID") # الآيدي بتاعك عشان تجيلك عليه الإشعارات

bot = telebot.TeleBot(BOT_TOKEN)
database.init_db()

# --- قائمة القنوات (حط يوزرات قنواتك هنا) ---
CHANNELS = ["@channel1", "@channel2"] 

def check_sub(user_id):
    """التحقق من الاشتراك الإجباري"""
    for channel in CHANNELS:
        status = bot.get_chat_member(channel, user_id).status
        if status in ['left', 'kicked']:
            return False
    return True

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    username = message.from_user.username or "User"
    ip = "0.0.0.0" # هنا هنربط مكتبة الـ IP لاحقاً
    
    # تسجيل المستخدم في القاعدة
    database.register_user(user_id, username, ip)
    
    if not check_sub(user_id):
        markup = types.InlineKeyboardMarkup()
        for ch in CHANNELS:
            markup.add(types.InlineKeyboardButton(f"اشترك في {ch}", url=f"https://t.me/{ch[1:]}"))
        markup.add(types.InlineKeyboardButton("✅ تم الاشتراك", callback_data="check_subscription"))
        bot.send_message(message.chat.id, "⚠️ يجب الاشتراك في القنوات أولاً لفتح عجلة الحظ!", reply_markup=markup)
        return

    # لو مشترك تظهر الواجهة الاحترافية
    main_menu(message.chat.id, username)

def main_menu(chat_id, name):
    markup = types.InlineKeyboardMarkup(row_width=2)
    buttons = [
        types.InlineKeyboardButton("🎡 عجلة الحظ", callback_data="spin_wheel"),
        types.InlineKeyboardButton("🎁 المهام (قيد الانتظار)", callback_data="tasks"),
        types.InlineKeyboardButton("👥 دعوة الأصدقاء", callback_data="referral"),
        types.InlineKeyboardButton("💰 محفظتي", callback_data="wallet")
    ]
    markup.add(*buttons)
    bot.send_message(chat_id, f"مرحباً بك في Trend Cash يا {name}! 🚀\nرصيدك جاهز للزيادة، ابدأ الآن.", reply_markup=markup)

# --- نظام استقبال الصور (بوت الإشعارات) ---
@bot.message_handler(content_types=['photo'])
def handle_screenshot(message):
    user = message.from_user
    # إرسال الإشعار للأدمن
    bot.send_message(ADMIN_ID, f"📩 **إشعار جديد**\nمن: @{user.username}\nID: `{user.id}`\nيرسل إسكرين شوت للمراجعة 👇")
    bot.forward_message(ADMIN_ID, message.chat.id, message.message_id)
    
    bot.reply_to(message, "✅ تم استلام الإسكرين بنجاح! سيتم مراجعته وإضافة القسائم لحسابك خلال 4 ساعات.")

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == "check_subscription":
        if check_sub(call.from_user.id):
            bot.answer_callback_query(call.id, "تم التحقق بنجاح! ✅")
            main_menu(call.message.chat.id, call.from_user.first_name)
        else:
            bot.answer_callback_query(call.id, "لم تشترك في جميع القنوات بعد! ❌", show_alert=True)

print("✅ Trend Cash Bot is Online and Protected.")
bot.polling()

