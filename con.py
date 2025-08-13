# التعديل بواسطة إيثن — نسخة موحّدة ومُعاد صياغتها نصياً
# تأكد من تحديث api_id, api_hash, bot_token, story_admin_id قبل التشغيل
import os
import json
import asyncio
from datetime import datetime
from telethon import TelegramClient, events, Button, errors
from flask import Flask
import threading

app = Flask('')

@app.route('/')
def home():
    return "البوت شغال ✅"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = threading.Thread(target=run)
    t.start()
import platform, psutil, socket, time, requests, os

@j_f_v.on(events.NewMessage(pattern='/ping'))
async def ping_command(event):
    if event.sender_id != story_admin_id:
        return
    
    start_time = time.time()
    await event.respond("🏓 جارِ الفحص...")
    latency = round((time.time() - start_time) * 1000)

    # معلومات النظام
    os_info = f"{platform.system()} {platform.release()} ({platform.machine()})"
    uptime_seconds = time.time() - psutil.boot_time()
    uptime_str = time.strftime("%H:%M:%S", time.gmtime(uptime_seconds))
    cpu_percent = psutil.cpu_percent()
    ram_percent = psutil.virtual_memory().percent

    # IPs
    local_ip = socket.gethostbyname(socket.gethostname())
    try:
        public_ip = requests.get("https://api.ipify.org").text
    except:
        public_ip = "غير متاح"

    msg = (
        f"🏓 **سرعة الاستجابة:** {latency} ms\n"
        f"🌐 **IP الداخلي:** {local_ip}\n"
        f"🌍 **IP الخارجي:** {public_ip}\n"
        f"💻 **النظام:** {os_info}\n"
        f"📆 **مدة التشغيل:** {uptime_str}\n"
        f"🖥 **المعالج:** {cpu_percent}%\n"
        f"🧠 **الذاكرة:** {ram_percent}%"
    )

    await event.respond(msg)    
# === إعدادات المبرمج: عدِّل القيم التالية قبل التشغيل ===
api_id = '20067911'
api_hash = 'ef381695bc379545f9115a282be721c2'
bot_token = '8262533887:AAEFUoQH3fDmUY6SUdWy4A1ge7I0StS8n-c'
story_admin_id = 6430670316  # أيدي الأدمن الرئيسي
# ======================================================

# اسم الجلسة كما لديك
j_f_v = TelegramClient('tw9el_joker', api_id, api_hash).start(bot_token=bot_token)

# --- ملفات البيانات ---
DATA_USERS = 'users.json'
DATA_MODS = 'moderators.json'
DATA_SETTINGS = 'settings.json'
BANNED_FILE = 'banned_users.txt'

# --- هياكل البيانات في الذاكرة ---
messages = {}            # مفتاح: (user_id, user_msg_id) -> info عن الرسالة
moderators = {}          # str(user_id) -> {permissions..., added_at, added_by}
users = {}               # str(user_id) -> {id, username, first_name, date}
settings = {
    "start_message": "مرحبًا. يمكنك إرسال رسالتك، سيتم توصيلها إلى فريق الإدارة إما مَجهولًا أو مَكشوفًا حسب اختيارك.",
    "allow_media": True,
    "allow_links": True
}

pending_actions = {}     # user_id -> { action: ..., data: {...} }

banned_users = set()

# --- دوال مساعدة للملفات ---

def save_json(path, data):
    try:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print('Error saving', path, e)


def load_json(path, default):
    if not os.path.exists(path):
        return default
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return default


def load_all():
    global moderators, users, settings, banned_users
    moderators = load_json(DATA_MODS, {})
    users = load_json(DATA_USERS, {})
    settings = load_json(DATA_SETTINGS, settings)
    if os.path.exists(BANNED_FILE):
        with open(BANNED_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                line=line.strip()
                if line:
                    try:
                        banned_users.add(int(line))
                    except:
                        pass


def save_banned():
    try:
        with open(BANNED_FILE, 'w', encoding='utf-8') as f:
            for uid in banned_users:
                f.write(f"{uid}\n")
    except Exception as e:
        print('Error saving banned file', e)


def save_all():
    save_json(DATA_MODS, moderators)
    save_json(DATA_USERS, users)
    save_json(DATA_SETTINGS, settings)
    save_banned()

# تحميل البيانات عند بدء التشغيل
load_all()

# --- صلاحيات ---

def is_admin(user_id):
    return user_id == story_admin_id


def is_moderator(user_id):
    return str(user_id) in moderators


def mod_perms(user_id):
    return moderators.get(str(user_id), {
        "can_read": True,
        "can_reply": True,
        "can_view_info": True,
        "can_broadcast": False,
        "can_view_stats": False
    })

# --- ازرار ولوحات ---

def start_buttons_for(user_id):
    if is_admin(user_id):
        return [
            [Button.inline('⚙️ لوحة الإدارة', b'start:admin_panel')],
            
            [Button.url('المبرمج', 'https://t.me/j_f_v')]
        ]
    elif is_moderator(user_id):
        return [
            [Button.inline('⚙️ لوحة الإدارة (محدودة)', b'start:admin_panel')],
            
            [Button.url('المبرمج', 'https://t.me/j_f_v')]
        ]
    else:
        return [
            
            [Button.url('المبرمج', 'https://t.me/j_f_v')]
        ]


def admin_keyboard():
    return [
        [Button.inline('🛠️ إدارة المشرفين', b'admin:mods')],
        [Button.inline('📢 إرسال/إذاعة', b'admin:broadcast'), Button.inline('📊 إحصائيات', b'admin:stats')],
        [Button.inline('✏️ تغيير رسالة البداية', b'admin:change_start')],
        [Button.inline('🔁 الوسائط', b'admin:media'), Button.inline('🔗 الروابط', b'admin:links')],
        [Button.inline('🗳️ المحظورون', b'admin:banned'), Button.url('المبرمج', 'https://t.me/j_f_v')]        
    ]


def admin_mods_panel_buttons():
    # إدارة المشرفين — تظهر دائمًا خيارات الإضافة/الحذف/قائمة
    return [
        [Button.inline('➕ إضافة مشرف ', b'admin:addmod')],
        [Button.inline('➖ إزالة مشرف ', b'admin:removemod')],
        [Button.inline('📋 عرض قائمة المشرفين', b'admin:listmods')],
        [Button.inline('🔙 رجوع', b'admin:back')]
    ]


def mod_keyboard(user_id):
    perms = mod_perms(user_id)
    buttons = []
    if perms.get('can_read'):
        buttons.append(Button.inline('📥 مشاهدة الرسائل', b'mod:view_msgs'))
    if perms.get('can_reply'):
        buttons.append(Button.inline('↩️ رد على مرسل', b'mod:reply'))
    if perms.get('can_view_info'):
        buttons.append(Button.inline('ℹ️ عرض معلومات المستخدم', b'mod:view_info'))
    if perms.get('can_broadcast'):
        buttons.append(Button.inline('📢 إذاعة', b'mod:broadcast'))
    if perms.get('can_view_stats'):
        buttons.append(Button.inline('📊 إحصائيات', b'mod:stats'))
    if not buttons:
        buttons = [Button.inline('🔒 لا توجد صلاحيات', b'mod:no_perm')]
    # صفوف ثنائية
    return [buttons[i:i+2] for i in range(0, len(buttons), 2)] + [[Button.inline('🔙 رجوع', b'mod:back')]]

# --- مساعدات تنسيق ---

def fmt_user_short(u):
    if not u:
        return 'مجهول'
    return f"{u.get('first_name','')}{' (@'+u.get('username')+')' if u.get('username') else ''} — id: {u.get('id')}"


def fmt_mod_info(mod_id):
    m = moderators.get(str(mod_id), {})
    perms = [k for k,v in m.items() if k.startswith('can_') and v]
    added = m.get('added_at','-')
    added_by = m.get('added_by','-')
    userinfo = users.get(str(mod_id), {})
    return f"👤 المشرف: {userinfo.get('first_name','—')}\n@{userinfo.get('username','لا يوجد')}\nID: {mod_id}\nانضم كمشرف في: {added}\nأضيف بواسطة: {added_by}\n\nالصلاحيات المفعلة: {', '.join(perms) or 'لا صلاحيات'}"

# --- أوامر البداية ---

@j_f_v.on(events.NewMessage(pattern='/start'))
async def story_start(event):
    uid = event.sender_id
    # تسجيل المستخدم
    try:
        sender = await event.get_sender()
    except:
        sender = None

    # منع استقبال أو إرسال رسائل لبوتات أخرى
    if sender and sender.bot:
        await event.reply("❌ لا يمكن للبوت استقبال أو إرسال رسائل لبوتات أخرى.")
        return

    # إذا المستخدم جديد فقط
    if sender and str(uid) not in users:
        users[str(uid)] = {
            'id': uid,
            'username': getattr(sender, 'username', None),
            'first_name': getattr(sender, 'first_name', '') or '',
            'date': datetime.utcnow().isoformat()
        }
        save_json(DATA_USERS, users)

        # إشعار للأدمن
        info_text = f"🆕 مستخدم جديد:\n- الاسم: {sender.first_name}\n- اسم المستخدم: @{sender.username if sender.username else 'لا يوجد'}\n- المعرف (ID): {uid}\n- تاريخ التسجيل: {users[str(uid)]['date']}"
        try:
            await j_f_v.send_message(story_admin_id, info_text)
        except:
            pass

        # إشعار لكل المشرفين اللي عندهم صلاحية عرض المعلومات
        for mod_id, perms in moderators.items():
            if perms.get('can_view_info'):
                try:
                    await j_f_v.send_message(int(mod_id), info_text)
                except:
                    pass

    # حظر
    if uid in banned_users:
        await event.reply("❌ عذرًا، لقد تم حظرك من استخدام البوت.")
        return

    # أرسل رسالة البداية
    await event.reply(settings.get('start_message', ''), buttons=start_buttons_for(uid))
# أمر /admin يظهر للأدمن والمشرفين (لكن صلاحيات المشرف محدودة)
@j_f_v.on(events.NewMessage(pattern='/admin'))
async def cmd_admin(event):
    uid = event.sender_id
    if is_admin(uid):
        await event.reply('⚙️ لوحة الإدارة الرئيسية', buttons=admin_keyboard())
    elif is_moderator(uid):
        # عرض لوحة مشرف (محدودة ـ بدون تعديل مشرفين)
        await event.reply('🧑‍💻 لوحة المشرف (حدود الصلاحيات حسب التعيين)', buttons=mod_keyboard(uid))
    else:
        await event.reply('❌ هذه الأوامر متاحة فقط للإدارة والمشرفين.')

# --- التعامل مع الأزرار (CallbackQuery) ---

@j_f_v.on(events.CallbackQuery)
async def callback_handler(event):
    user_id = event.sender_id
    data = event.data.decode('utf-8')

    
    # فتح لوحة الإدارة من /start
    if data == 'start:admin_panel':
        if not is_admin(user_id):
            await event.answer('❌ هذا مخصص للأدمن فقط.', alert=True)
            return
        await event.edit('⚙️ لوحة الإدارة الرئيسية', buttons=admin_keyboard())
        return

    # ----- أوامر الأدمن -----
    if data.startswith('admin:'):
        if not is_admin(user_id):
            await event.answer('❌ هذا مخصص للأدمن فقط.', alert=True)
            return
        cmd = data.split(':',1)[1]

        if cmd == 'mods':
            # نعرض إدارة المشرفين — حتى لو فارغة
            await event.edit('🛠️ إدارة المشرفين', buttons=admin_mods_panel_buttons())
            return

        if cmd == 'listmods':
            if not moderators:
                await event.answer('لا يوجد مشرفين حالياً.', alert=True)
                return
            btns = []
            for mid, minfo in moderators.items():
                try:
                    u = users.get(str(mid), {})
                    label = u.get('first_name') or str(mid)
                    if u.get('username'):
                        label += f" (@{u.get('username')})"
                except:
                    label = str(mid)
                btns.append([Button.inline(f"👤 {label}", f"admin:showmod:{mid}".encode())])
            btns.append([Button.inline('🔙 رجوع', b'admin:mods')])
            await event.edit('📋 قائمة المشرفين', buttons=btns)
            return

        if cmd.startswith('showmod:'):
            mid = cmd.split(':',1)[1]
            # عرض معلومات المشرف وتبديل الصلاحيات
            if str(mid) not in moderators:
                await event.answer('❌ هذا المستخدم ليس مشرفاً.', alert=True)
                return
            text = fmt_mod_info(int(mid))
            perms = moderators.get(str(mid), {})
            kb = [
                [Button.inline(f"🔁 قراءة: {'✅' if perms.get('can_read') else '❌'}", f"admin:toggleperm:{mid}:can_read".encode()),
                 Button.inline(f"↩️ رد: {'✅' if perms.get('can_reply') else '❌'}", f"admin:toggleperm:{mid}:can_reply".encode())],
                [Button.inline(f"ℹ️ عرض معلومات: {'✅' if perms.get('can_view_info') else '❌'}", f"admin:toggleperm:{mid}:can_view_info".encode()),
                 Button.inline(f"📢 إذاعة: {'✅' if perms.get('can_broadcast') else '❌'}", f"admin:toggleperm:{mid}:can_broadcast".encode())],
                [Button.inline(f"📊 إحصائيات: {'✅' if perms.get('can_view_stats') else '❌'}", f"admin:toggleperm:{mid}:can_view_stats".encode())],
                [Button.inline('🔙 رجوع', b'admin:listmods')]
            ]
            await event.edit(text, buttons=kb)
            return

        if cmd.startswith('toggleperm:'):
            # admin:toggleperm:<mid>:<perm>
            parts = cmd.split(':')
            if len(parts) >= 3:
                mid = parts[1]
                perm = parts[2]
            else:
                await event.answer('بيانات غير صحيحة.', alert=True)
                return
            # تبديل
            if str(mid) not in moderators:
                await event.answer('❌ هذا المستخدم ليس مشرفاً.', alert=True)
                return
            moderators[str(mid)][perm] = not moderators[str(mid)].get(perm, False)
            save_json(DATA_MODS, moderators)
            await event.answer('✅ تم تحديث الصلاحية.', alert=True)
            # إعادة عرض صفحة المشرف
            await event.click(1) if False else None
            # نعيد عرض تفاصيل المشرف
            await event.edit(fmt_mod_info(int(mid)), buttons=[
                [Button.inline(f"🔁 قراءة: {'✅' if moderators[str(mid)].get('can_read') else '❌'}", f"admin:toggleperm:{mid}:can_read".encode()),
                 Button.inline(f"↩️ رد: {'✅' if moderators[str(mid)].get('can_reply') else '❌'}", f"admin:toggleperm:{mid}:can_reply".encode())],
                [Button.inline(f"ℹ️ عرض معلومات: {'✅' if moderators[str(mid)].get('can_view_info') else '❌'}", f"admin:toggleperm:{mid}:can_view_info".encode()),
                 Button.inline(f"📢 إذاعة: {'✅' if moderators[str(mid)].get('can_broadcast') else '❌'}", f"admin:toggleperm:{mid}:can_broadcast".encode())],
                [Button.inline(f"📊 إحصائيات: {'✅' if moderators[str(mid)].get('can_view_stats') else '❌'}", f"admin:toggleperm:{mid}:can_view_stats".encode())],
                [Button.inline('🔙 رجوع', b'admin:listmods')]
            ])
            return

        if cmd == 'addmod':
            pending_actions[user_id] = {'action':'addmod_by_input', 'data':{}}
            await event.respond('📥 أرسل الآن معرف المستخدم (ID) أو اليوزر بدون @ لترقيته إلى مشرف.')
            return

        if cmd == 'removemod':
            pending_actions[user_id] = {'action':'removemod_by_input', 'data':{}}
            await event.respond('📥 أرسل الآن معرف المستخدم (ID) أو اليوزر بدون @ لإزالته من المشرفين.')
            return

        if cmd == 'broadcast':
            pending_actions[user_id] = {'action':'broadcast_wait','data':{}}
            await event.answer('📢 أرسل الآن الرسالة التي تريد إذاعتها إلى جميع المستخدمين.', alert=True)
            return

        if cmd == 'stats':
            total_users = len(users)
            total_banned = len(banned_users)
            total_mods = len(moderators)
            msg = f"📊 إحصائيات البوت:\n- عدد المستخدمين: {total_users}\n- عدد المحظورين: {total_banned}\n- عدد المشرفين: {total_mods}\n- إرسال وسائط مفعل: {settings.get('allow_media')}\n- إرسال روابط مفعل: {settings.get('allow_links')}"
            await event.respond(msg)
            return

        if cmd == 'change_start':
            pending_actions[user_id] = {'action':'change_start','data':{}}
            await event.answer('✏️ أرسل الآن رسالة البداية الجديدة (نص).', alert=True)
            return

        if cmd == 'media':
            # نعرض مفاتيح لتشغيل/إيقاف
            kb = [[Button.inline(f"حالة الوسائط: {'مُفعلة' if settings.get('allow_media') else 'معطلة'}", b'admin:toggle_media_now')],[Button.inline('🔙 رجوع', b'admin:back')]]
            await event.edit('🔁 إعدادات الوسائط', buttons=kb)
            return

        if cmd == 'links':
            kb = [[Button.inline(f"حالة الروابط: {'مُفعلة' if settings.get('allow_links') else 'معطلة'}", b'admin:toggle_links_now')],[Button.inline('🔙 رجوع', b'admin:back')]]
            await event.edit('🔗 إعدادات الروابط', buttons=kb)
            return

        if cmd == 'toggle_media_now':
            settings['allow_media'] = not settings.get('allow_media', True)
            save_json(DATA_SETTINGS, settings)
            await event.answer(f"✅ إرسال الوسائط الآن: {settings['allow_media']}", alert=True)
            # تحديث الزر
            await event.click(1) if False else None
            await event.edit('🔁 إعدادات الوسائط', buttons=[[Button.inline(f"حالة الوسائط: {'مُفعلة' if settings.get('allow_media') else 'معطلة'}", b'admin:toggle_media_now')],[Button.inline('🔙 رجوع', b'admin:back')]])
            return

        if cmd == 'toggle_links_now':
            settings['allow_links'] = not settings.get('allow_links', True)
            save_json(DATA_SETTINGS, settings)
            await event.answer(f"✅ إرسال الروابط الآن: {settings['allow_links']}", alert=True)
            await event.edit('🔗 إعدادات الروابط', buttons=[[Button.inline(f"حالة الروابط: {'مُفعلة' if settings.get('allow_links') else 'معطلة'}", b'admin:toggle_links_now')],[Button.inline('🔙 رجوع', b'admin:back')]])
            return

        if cmd == 'banned':
            # عرض المحظورين وخيارات
            if not banned_users:
                await event.answer('قائمة المحظورين فارغة.', alert=True)
                return
            text = '📛 قائمة المحظورين:\n' + '\n'.join([str(x) for x in banned_users])
            kb = [[Button.inline('🗑️ إلغاء حظر الكل', b'admin:unban_all')],[Button.inline('🔙 رجوع', b'admin:back')]]
            await event.edit(text, buttons=kb)
            return

        if cmd == 'unban_all':
            banned_users.clear()
            save_banned()
            await event.answer('✅ تم إلغاء حظر جميع المستخدمين.', alert=True)
            await event.edit('✅ تم إلغاء حظر جميع المستخدمين.', buttons=[[Button.inline('🔙 رجوع', b'admin:back')]])
            return

        if cmd == 'back':
            await event.edit('⚙️ لوحة الإدارة الرئيسية', buttons=admin_keyboard())
            return

    # ----- أوامر خاصة بالمشرف (غير مُخول له تعديل مشرفين) -----
    if data.startswith('mod:'):
        if not is_moderator(user_id):
            await event.answer('❌ أنت لست مشرفاً.', alert=True)
            return
        cmd = data.split(':',1)[1]
        perms = mod_perms(user_id)
        if cmd == 'view_msgs':
            if not perms.get('can_read'):
                await event.answer('❌ ليس لديك صلاحية مشاهدة الرسائل.', alert=True)
                return
            if not messages:
                await event.answer('لا توجد رسائل حالياً.', alert=True)
                return
            txt = '📥 آخر الرسائل:\n\n'
            i = 0
            for key, info in list(messages.items())[-10:]:
                i += 1
                uid = info['story_user_id']
                text = info.get('story_message_text') or '<وسائط>'
                txt += f"{i}. من {uid}: {text[:80]}...\n"
            await event.answer(txt, alert=True)
            return
        if cmd == 'reply':
            if not perms.get('can_reply'):
                await event.answer('❌ ليس لديك صلاحية الرد.', alert=True)
                return
            pending_actions[user_id] = {'action':'mod_reply_wait','data':{}}
            await event.answer('↩️ قم الآن بالرد على نسخة الرسالة المرسلة لك للرد على المرسل.', alert=True)
            return
        if cmd == 'view_info':
            if not perms.get('can_view_info'):
                await event.answer('❌ ليس لديك صلاحية عرض المعلومات.', alert=True)
                return
            txt = 'ℹ️ آخر المستخدمين:\n\n'
            i = 0
            for uid, info in list(users.items())[-10:]:
                i += 1
                txt += f"{i}. {info.get('first_name','')} — @{info.get('username','لا يوجد')} — id: {uid}\n"
            await event.answer(txt, alert=True)
            return
        if cmd == 'broadcast':
            if not perms.get('can_broadcast'):
                await event.answer('❌ ليس لديك صلاحية الإذاعة.', alert=True)
                return
            pending_actions[user_id] = {'action':'mod_broadcast_wait','data':{}}
            await event.answer('📢 أرسل الآن رسالة الإذاعة (كمشرف).', alert=True)
            return
        if cmd == 'stats':
            if not perms.get('can_view_stats'):
                await event.answer('❌ ليس لديك صلاحية عرض الإحصائيات.', alert=True)
                return
            total_users = len(users)
            total_banned = len(banned_users)
            total_mods = len(moderators)
            msg = f"📊 إحصائيات البوت:\n- المستخدمين: {total_users}\n- المحظورين: {total_banned}\n- عدد المشرفين: {total_mods}"
            await event.answer(msg, alert=True)
            return
        if cmd == 'back':
            await event.edit('🧑‍💻 لوحة المشرف', buttons=mod_keyboard(user_id))
            return

    # ----- رد افتراضي للضغطات غير المعالجة -----
    await event.answer('🔘 تم الضغط على الزر.', alert=True)

# === استقبال الرسائل الخاصة (الأساس) ===
@j_f_v.on(events.NewMessage)
async def handle_private_messages(event):
    # تجاهل رسائل من البوت أو من المحظورين
    if event.sender_id == story_admin_id or (event.sender_id in banned_users):
        return
    # تجاهل الرسائل في المجموعات أو الأوامر
    if not event.is_private:
        return
    if event.raw_text and event.raw_text.startswith('/'):
        return

    uid = event.sender_id
    sender = await event.get_sender()

    # تسجيل المستخدم إذا لم يكن موجود
    if str(uid) not in users:
        users[str(uid)] = {
            'id': uid,
            'username': getattr(sender, 'username', None),
            'first_name': getattr(sender, 'first_name', '') or '',
            'date': datetime.utcnow().isoformat()
        }
        save_json(DATA_USERS, users)

    # تخزين الرسالة في الذاكرة
    key = (uid, event.message.id)
    messages[key] = {
        'story_user_id': uid,
        'story_message_text': event.message.message,
        'story_media': event.message.media
    }

    # تجهيز النص المرسل
    username = f"@{sender.username}" if sender.username else "لا يوجد"
    text = event.message.message or ''
    msg_to_send = f"الاسم: {sender.first_name}\nاليوزر: {username}\nID: {uid}\n{text}"

    # إرسال للإدمن
    # إرسال للإدمن مع التخزين
    try:
        sent = await j_f_v.send_message(
            story_admin_id,
            msg_to_send,
            file=event.message.media if settings.get('allow_media') and event.message.media else None
        )
        messages[(story_admin_id, sent.id)] = uid  # تخزين المرسل الأصلي
    except Exception:
        pass

    # إرسال للمشرفين الذين لديهم صلاحية القراءة مع التخزين
    for mid, perms in moderators.items():
        if perms.get('can_read'):
            try:
                sent = await j_f_v.send_message(
                    int(mid),
                    msg_to_send,
                    file=event.message.media if settings.get('allow_media') and event.message.media else None
                )
                messages[(int(mid), sent.id)] = uid  # تخزين المرسل الأصلي
            except:
                pass

    # تأكيد للمستخدم
    await event.reply('✅ تم إرسال رسالتك.')
@j_f_v.on(events.NewMessage)
async def reply_by_admin_or_mod(event):
    # أدمن يقدر يرد مباشرة على الرسائل المرسلة له
    if not event.is_reply:
        # معالجة pending actions (إضافة/إزالة مشرف، إذاعة، تغيير رسالة بداية، رد المشرف)
        uid = event.sender_id
        if uid not in pending_actions:
            return
        action = pending_actions[uid]['action']

        # إضافة مشرف عن طريق إدخال ID أو Username
        if action == 'addmod_by_input' and is_admin(uid):
            user_input = event.raw_text.strip()
            target_id = None

            if user_input.isdigit():
                target_id = int(user_input)
            else:
                if not user_input.startswith('@'):
                    user_input = '@' + user_input
                try:
                    entity = await j_f_v.get_entity(user_input)
                    target_id = entity.id
                except:
                    await event.reply('❌ لم أتمكن من العثور على هذا المستخدم.')
                    pending_actions.pop(uid, None)
                    return

            moderators[str(target_id)] = {
                'can_read': True,
                'can_reply': True,
                'can_view_info': True,
                'can_broadcast': False,
                'can_view_stats': False,
                'added_at': datetime.utcnow().isoformat(),
                'added_by': str(uid)
            }
            save_json(DATA_MODS, moderators)
            await event.reply(f'✅ تم ترقية المستخدم {target_id} إلى مشرف.')
            pending_actions.pop(uid, None)
            return

        # إزالة مشرف عن طريق إدخال ID أو Username
        if action == 'removemod_by_input' and is_admin(uid):
            user_input = event.raw_text.strip()
            target_id = None

            if user_input.isdigit():
                target_id = int(user_input)
            else:
                if not user_input.startswith('@'):
                    user_input = '@' + user_input
                try:
                    entity = await j_f_v.get_entity(user_input)
                    target_id = entity.id
                except:
                    await event.reply('❌ لم أتمكن من العثور على هذا المستخدم.')
                    pending_actions.pop(uid, None)
                    return

            if str(target_id) in moderators:
                moderators.pop(str(target_id))
                save_json(DATA_MODS, moderators)
                await event.reply(f'✅ تم إزالة المشرف {target_id}.')
            else:
                await event.reply('❌ هذا المستخدم ليس مشرفاً.')
            pending_actions.pop(uid, None)
            return

        # تغيير رسالة البداية
        if action == 'change_start' and is_admin(uid):
            new_text = event.raw_text
            settings['start_message'] = new_text
            save_json(DATA_SETTINGS, settings)
            await event.reply('✅ تم تحديث رسالة البداية.')
            pending_actions.pop(uid, None)
            return

        # إذاعة من الأدمن
        if action == 'broadcast_wait' and is_admin(uid):
            total = 0
            failed = 0
            for user_id_str in list(users.keys()):
                try:
                    target = int(user_id_str)
                    if settings.get('allow_media') and event.message.media:
                        await j_f_v.send_message(target, event.message.message or '', file=event.message.media)
                    else:
                        await j_f_v.send_message(target, event.message.message or '')
                    total += 1
                except Exception:
                    failed += 1
                    continue
            await event.reply(f'📢 تم الإرسال إلى {total} مستخدمين. فشل: {failed}')
            pending_actions.pop(uid, None)
            return

        # إذاعة كمشرف
        if action == 'mod_broadcast_wait' and is_moderator(uid):
            perms = mod_perms(uid)
            if not perms.get('can_broadcast'):
                await event.reply('❌ ليس لديك صلاحية الإذاعة.')
                pending_actions.pop(uid, None)
                return
            total = 0
            failed = 0
            for user_id_str in list(users.keys()):
                try:
                    target = int(user_id_str)
                    if settings.get('allow_media') and event.message.media:
                        await j_f_v.send_message(target, event.message.message or '', file=event.message.media)
                    else:
                        await j_f_v.send_message(target, event.message.message or '')
                    total += 1
                except Exception:
                    failed += 1
                    continue
            await event.reply(f'📢 (مشرف) تم الإرسال إلى {total} مستخدمين. فشل: {failed}')
            pending_actions.pop(uid, None)
            return

        # رد المشرف
        # رد المشرف
        if action == 'mod_reply_wait' and is_moderator(uid):
            if not event.is_reply:
                await event.reply('❌ يرجى الرد على نسخة الرسالة المرسلة لك للرد على المرسل.')
                pending_actions.pop(uid, None)
                return
            replied = await event.get_reply_message()
            target_user_id = None
            try:
                if getattr(replied, 'forward', None) and getattr(replied.forward, 'sender_id', None):
                    target_user_id = replied.forward.sender_id
                elif getattr(replied, 'fwd_from', None) and getattr(replied.fwd_from, 'from_id', None):
                    fid = replied.fwd_from.from_id
                    if isinstance(fid, int):
                        target_user_id = fid
                elif getattr(replied, 'sender_id', None):
                    target_user_id = replied.sender_id
            except Exception:
                target_user_id = None

            if not target_user_id:
                await event.reply('❌ لم أتمكن من تحديد المرسل الأصلي. حاول الرد على نسخة الرسالة المرسلة لك.')
                pending_actions.pop(uid, None)
                return

            try:
                # حاول نعرف إذا الهدف بوت
                try:
                    entity = await j_f_v.get_entity(int(target_user_id))
                    is_bot_target = getattr(entity, 'bot', False)
                except Exception:
                    # لو فشلنا في الحصول على الكيان، نخلي is_bot_target False
                    is_bot_target = False

                if is_bot_target:
                    await event.reply('❌ لا يمكن إرسال رسائل إلى حسابات من نوع بوت.')
                else:
                    await j_f_v.send_message(int(target_user_id), event.message.message)
                    await event.reply('✅ تم إرسال ردك إلى المرسل.')
            except Exception as e:
                await event.reply(f'❌ فشل الإرسال: {e}')
            pending_actions.pop(uid, None)
            return
            try:
                await j_f_v.send_message(int(target_user_id), event.message.message)
                await event.reply('✅ تم إرسال ردك إلى المرسل.')
            except Exception as e:
                await event.reply(f'❌ فشل الإرسال: {e}')
            pending_actions.pop(uid, None)
            return

        # إفلات أي أكشن غير معروف
        pending_actions.pop(uid, None)
        await event.reply('تم إلغاء العملية.')
        return

 
    # إذا كانت رسالة رد من الأدمن
    if event.is_reply and event.sender_id == story_admin_id:
        replied = await event.get_reply_message()
        original_uid = messages.get((story_admin_id, replied.id))
        if not original_uid:
            await event.reply('❌ لم أتمكن من تحديد المرسل لإرسال الرد.')
            return

        txt = event.message.message or ''

        if 'حظر' in txt:
            banned_users.add(original_uid)
            save_banned()
            try:
                await j_f_v.send_message(original_uid, '❌ تم حظرك من البوت.')
            except:
                pass
            await event.reply('✅ تم حظر المستخدم.')
            return

        if 'فك حظر' in txt or 'فك_حظر' in txt:
            if original_uid in banned_users:
                banned_users.remove(original_uid)
                save_banned()
                try:
                    await j_f_v.send_message(original_uid, '✅ تم إلغاء الحظر عنك.')
                except:
                    pass
                await event.reply('✅ تم إلغاء حظر المستخدم.')
            else:
                await event.reply('❌ المستخدم غير محظور.')
            return

        try:
            await j_f_v.send_message(original_uid, txt, file=event.message.media if event.message.media else None)
            await event.reply('✅ تم إرسال ردك.')
        except Exception as e:
            await event.reply(f'❌ فشل الإرسال: {e}')
# تنظيف وإغلاق آمن
async def shutdown():
    save_all()
    await j_f_v.disconnect()

import signal

def handle_exit(sig, frame):
    asyncio.get_event_loop().create_task(shutdown())

signal.signal(signal.SIGINT, handle_exit)
signal.signal(signal.SIGTERM, handle_exit)
keep_alive()
print('البوت شغال ✓')
j_f_v.run_until_disconnected()
