import os
import time
import yt_dlp
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ForceReply

# --- কনফিগারেশন ---
API_ID = 34850757
API_HASH = "f35b510c4b5b28851b715f349eb9a4d9"
BOT_TOKEN = "8373972531:AAEbOKuzUbF2e-qcWEhwqoPz4qEcj-nXiEM"

DEV_NAME = "Apu Jeet"
DEV_FB = "https://www.facebook.com/share/1DLXmXHthS/"
DEV_PHOTO = "1000005188.jpg" # আপনার ছবি

app = Client("ultimate_multi_downloader", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@app.on_message(filters.command("start"))
def start(client, message):
    text = (
        f"🚀 **{DEV_NAME} মাল্টি-ডাউনলোডার প্রো**\n\n"
        "✅ **ভিডিও, অডিও এবং ছবি সাপোর্ট যুক্ত!**\n"
        "👇 নিচের বাটনে ক্লিক করে লিঙ্ক দিন।"
    )
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("👤 ডেভেলপার ফেসবুক", url=DEV_FB)],
        [InlineKeyboardButton("📥 ডাউনলোড শুরু করুন", callback_data="ask_link")]
    ])
    try:
        # অনুযায়ী স্টার্ট মেসেজ
        message.reply_photo(photo=DEV_PHOTO, caption=text, reply_markup=buttons)
    except:
        message.reply_text(text, reply_markup=buttons)

@app.on_callback_query(filters.regex("ask_link"))
def ask_link(client, callback_query):
    callback_query.message.reply_text(
        "🔗 **আপনার লিঙ্কটি এখানে পাঠান (FB, YT, TikTok, Insta):**",
        reply_markup=ForceReply(selective=True)
    )
    callback_query.answer()

@app.on_message(filters.text & filters.regex(r'http'))
def handle_link(client, message):
    url = message.text
    status = message.reply_text("🔍 **লিঙ্ক চেক করছি...**", quote=True)
    
    ydl_opts = {'quiet': True, 'no_warnings': True}
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            formats = info.get('formats', [])
            title = info.get('title', 'Media File')[:50]
            thumb = info.get('thumbnail')

            buttons_list = []
            seen_res = set()
            row = []
            
            # রেজুলেশন বাটন তৈরি
            for f in formats:
                res = f.get('height')
                if res and res >= 360 and res <= 1080 and res not in seen_res:
                    row.append(InlineKeyboardButton(f"🎬 {res}p", callback_data=f"dl|{res}|{url}"))
                    seen_res.add(res)
                    if len(row) == 2:
                        buttons_list.append(row)
                        row = []
            
            if row: buttons_list.append(row)
            
            # অডিও ও ছবি বাটন
            buttons_list.append([
                InlineKeyboardButton("🎵 MP3 অডিও", callback_data=f"dl|mp3|{url}"),
                InlineKeyboardButton("🖼️ ছবি/থাম্বনেইল", callback_data=f"dl|photo|{url}")
            ])

        caption = f"✅ **মিডিয়া পাওয়া গেছে!**\n\n📝 **টাইটেল:** `{title}...`"
        if thumb:
            message.reply_photo(photo=thumb, caption=caption, reply_markup=InlineKeyboardMarkup(buttons_list))
            status.delete()
        else:
            status.edit(caption, reply_markup=InlineKeyboardMarkup(buttons_list))

    except Exception:
        status.edit("❌ ভুল হয়েছে! সঠিক লিঙ্ক দিন।")

@app.on_callback_query(filters.regex(r'^dl\|'))
def download_handler(client, callback_query):
    _, mode, url = callback_query.data.split("|")
    callback_query.message.edit(f"⚙️ **আপনার {mode} ফাইলটি তৈরি হচ্ছে...**")
    
    file_id = str(int(time.time()))
    
    # --- ইমেজ ডাউনলোড ফিচার ---
    if mode == "photo":
        try:
            with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
                info = ydl.extract_info(url, download=False)
                photo_url = info.get('thumbnail')
                callback_query.message.reply_photo(photo=photo_url, caption=f"✅ ছবি ডাউনলোড সম্পন্ন!\n👤 {DEV_NAME}")
                callback_query.message.delete()
            return
        except:
            return callback_query.message.edit("❌ ছবি পাওয়া যায়নি!")

    file_name = f"file_{file_id}.mp4" if mode != "mp3" else f"file_{file_id}.mp3"
    
    # রেজুলেশন ও অডিও সেটিংস
    if mode.isdigit():
        ydl_opts = {
            'format': f'bestvideo[height<={mode}]+bestaudio/best[height<={mode}]',
            'outtmpl': file_name,
            'merge_output_format': 'mp4',
        }
    elif mode == "mp3":
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': file_name,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        
        callback_query.message.edit("📤 **আপলোড হচ্ছে...**")
        
        if mode == "mp3":
            callback_query.message.reply_audio(audio=file_name, caption=f"🎵 অডিও বাই {DEV_NAME}")
        else:
            callback_query.message.reply_video(video=file_name, caption=f"✅ {mode}p ভিডিও সম্পন্ন!")
        
        callback_query.message.delete()
    except Exception:
        # এরর হ্যান্ডেলিং
        callback_query.message.edit("❌ ডাউনলোড ব্যর্থ! সার্ভারে FFmpeg টুলটি নেই।")
    finally:
        if os.path.exists(file_name): os.remove(file_name)

app.run()
