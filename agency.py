import os
import json
import requests
import google.generativeai as genai
from playwright.sync_api import sync_playwright

# GitHub Secrets-ൽ നിന്ന് കീകൾ എടുക്കുന്നു
GEMINI_KEY = os.environ["GEMINI_API_KEY"]
BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

genai.configure(api_key=GEMINI_KEY)

def get_daily_content():
    model = genai.GenerativeModel('gemini-1.5-pro')
    prompt = """
    You are the Marketing Head for 'PocketMates', a gamified English learning app 
    with Islands (35-50 user capacity), Defense mechanics, Pocket Talks, and a 90-day challenge.
    Generate fresh daily content for Malayalam speakers.
    Return ONLY valid raw JSON (no markdown, no backticks) with these exact keys:
    {
        "wrong_sentence": "A common wrong English sentence used in daily life",
        "correct_sentence": "The correct natural English sentence",
        "malayalam_meaning": "Clear Malayalam explanation of when to use it",
        "insta_hook": "1-line catchy Reels hook (under 5 seconds) linking Island defense/attacks with speaking English",
        "insta_caption": "Engaging Instagram caption with 5 relevant hashtags",
        "fcm_notification": "Short push notification text to bring users back to defend their island"
    }
    """
    response = model.generate_content(prompt)
    text = response.text.strip().removeprefix("```json").removesuffix("```").strip()
    return json.loads(text)

def generate_poster(data):
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;700;900&family=Noto+Sans+Malayalam:wght@500;700&display=swap" rel="stylesheet">
    </head>
    <body style="margin:0; width:1080px; height:1080px; background:linear-gradient(135deg,#0f172a 0%,#1e3a8a 100%); color:#ffffff; font-family:'Inter','Noto Sans Malayalam',sans-serif; display:flex; flex-direction:column; justify-content:space-between; padding:80px; box-sizing:border-box;">
        <div style="display:flex; justify-content:space-between; align-items:center; font-size:28px; font-weight:700; color:#93c5fd; letter-spacing:2px;">
            <span>POCKETMATES</span>
            <span>SPOKEN ENGLISH TIP</span>
        </div>
        <div style="background:rgba(255,255,255,0.07); border:2px solid rgba(255,255,255,0.15); border-radius:32px; padding:60px; display:flex; flex-direction:column; gap:40px;">
            <div>
                <div style="font-size:24px; color:#fca5a5; margin-bottom:10px; font-weight:700;">❌ DON'T SAY:</div>
                <div style="color:#f87171; font-size:42px; font-weight:700; text-decoration:line-through;">"{data['wrong_sentence']}"</div>
            </div>
            <div>
                <div style="font-size:24px; color:#86efac; margin-bottom:10px; font-weight:700;">✅ SAY THIS INSTEAD:</div>
                <div style="color:#4ade80; font-size:50px; font-weight:900;">"{data['correct_sentence']}"</div>
            </div>
            <div style="color:#e2e8f0; font-size:36px; line-height:1.5;">💡 {data['malayalam_meaning']}</div>
        </div>
        <div style="display:flex; justify-content:space-between; align-items:center; border-top:1px solid rgba(255,255,255,0.2); padding-top:30px; font-size:26px; color:#cbd5e1;">
            <span>Defend Your Island. Speak English Daily.</span>
            <span style="background:#3b82f6; color:white; padding:14px 30px; border-radius:50px; font-weight:700;">Join 90-Day Challenge</span>
        </div>
    </body>
    </html>
    """
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={{'width': 1080, 'height': 1080}})
        page.set_content(html)
        page.wait_for_timeout(2000)
        page.screenshot(path="poster.png")
        browser.close()

def send_to_telegram(data):
    photo_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
    with open("poster.png", "rb") as img:
        requests.post(photo_url, data={"chat_id": CHAT_ID, "caption": "✅ ഇന്നത്തെ ഇൻസ്റ്റാഗ്രാം പോസ്റ്റർ റെഡി!"}, files={"photo": img})
    
    msg_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    report = (
        f"🚀 *POCKETMATES DAILY AGENCY REPORT*\n\n"
        f"🎬 *Reels Hook (First 3 sec):*\n{data['insta_hook']}\n\n"
        f"📝 *Instagram Caption:*\n{data['insta_caption']}\n\n"
        f"🔔 *FCM Push Notification:*\n`{data['fcm_notification']}`"
    )
    requests.post(msg_url, data={"chat_id": CHAT_ID, "text": report, "parse_mode": "Markdown"})

if __name__ == "__main__":
    content = get_daily_content()
    generate_poster(content)
    send_to_telegram(content)