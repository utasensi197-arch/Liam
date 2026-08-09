from flask import Flask, request, render_template_string, redirect, url_for
import sqlite3
import secrets
import os

app = Flask(__name__)

# Termux = persistent local DB
# Belmo/production = writable temporary DB
if os.environ.get("PREFIX", "").startswith("/data/data/com.termux"):
    DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
    os.makedirs(DATA_DIR, exist_ok=True)
    DB = os.path.join(DATA_DIR, "vibely.db")
else:
    DB = "/tmp/vibely.db"


MOODS = {
    "love": {
        "emoji": "❤️",
        "title": "Love",
        "class": "love",
        "particles": ["❤️", "💕", "💗", "💖", "💘", "💞"]
    },
    "miss": {
        "emoji": "🥺",
        "title": "Miss You",
        "class": "miss",
        "particles": ["🥺", "💕", "💭", "💗", "💔"]
    },
    "sorry": {
        "emoji": "🥺",
        "title": "Sorry",
        "class": "sorry",
        "particles": ["🥺", "💔", "🤍", "🌸"]
    },
    "birthday": {
        "emoji": "🎂",
        "title": "Happy Birthday",
        "class": "birthday",
        "particles": ["🎉", "🎈", "🎂", "✨", "🎊", "🥳"]
    },
    "night": {
        "emoji": "🌙",
        "title": "Good Night",
        "class": "night",
        "particles": ["🌙", "⭐", "✨", "💫", "🌌"]
    },
    "friend": {
        "emoji": "🫶",
        "title": "Friendship",
        "class": "friend",
        "particles": ["🫶", "💛", "✨", "🌸", "🤝"]
    },
    "cute": {
        "emoji": "🌸",
        "title": "Cute",
        "class": "cute",
        "particles": ["🌸", "💗", "✨", "🦋", "🌷"]
    },
    "hype": {
        "emoji": "🔥",
        "title": "Hype",
        "class": "hype",
        "particles": ["🔥", "⚡", "💥", "✨", "🚀"]
    },
    "dreamy": {
        "emoji": "✨",
        "title": "Dreamy",
        "class": "dreamy",
        "particles": ["✨", "🌙", "💫", "🦋", "⭐"]
    }
}


KEYWORDS = {
    "love": [
        "love", "lover", "baby", "bby", "babe", "darling",
        "sweetheart", "crush", "ချစ်", "ချစ်တယ်", "အချစ်",
        "ချစ်သူ", "ဘေဘီ", "ဘေဘီလေး", "yo baby", "my baby"
    ],
    "miss": [
        "miss you", "miss u", "missing you", "i miss",
        "လွမ်း", "လွမ်းတယ်", "သတိရ", "သတိရတယ်"
    ],
    "sorry": [
        "sorry", "forgive", "my bad",
        "တောင်းပန်", "တောင်းပန်ပါတယ်", "ခွင့်လွှတ်"
    ],
    "birthday": [
        "happy birthday", "birthday", "မွေးနေ့",
        "မွေးနေ့ပျော်ရွှင်ပါစေ"
    ],
    "night": [
        "good night", "gn", "sweet dreams", "sleep well",
        "အိပ်တော့", "အိပ်ကောင်းကောင်း", "ညနေကောင်း",
        "goodnight"
    ],
    "friend": [
        "best friend", "bestie", "friend", "သူငယ်ချင်း",
        "မိတ်ဆွေ", "အကောင်းဆုံးသူငယ်ချင်း"
    ],
    "hype": [
        "fire", "power", "powerful", "legend", "winner",
        "win", "champion", "မိုက်", "အမိုက်", "အောင်မြင်"
    ],
    "dreamy": [
        "dream", "dreamy", "magic", "magical", "moon",
        "star", "stars", "galaxy", "အိပ်မက်", "မှော်",
        "လ", "ကြယ်"
    ]
}


def db():
    con = sqlite3.connect(DB, timeout=15)
    con.row_factory = sqlite3.Row

    con.execute("""
        CREATE TABLE IF NOT EXISTS pages (
            code TEXT PRIMARY KEY,
            text TEXT NOT NULL,
            mood TEXT DEFAULT 'cute',
            style TEXT DEFAULT 'cute',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    columns = {
        row["name"]
        for row in con.execute("PRAGMA table_info(pages)").fetchall()
    }

    if "mood" not in columns:
        con.execute(
            "ALTER TABLE pages ADD COLUMN mood TEXT DEFAULT 'cute'"
        )

    if "style" not in columns:
        con.execute(
            "ALTER TABLE pages ADD COLUMN style TEXT DEFAULT 'cute'"
        )

    con.commit()
    return con


def init_db():
    con = db()
    con.close()


def detect_mood(text):
    t = text.lower().strip()

    matches = []

    for mood, words in KEYWORDS.items():
        for word in words:
            word = word.lower()

            if word in t:
                matches.append((len(word), mood))

    if matches:
        matches.sort(reverse=True)
        return matches[0][1]

    return "cute"


def particle_html(particles):
    result = []

    for i in range(28):
        emoji = particles[i % len(particles)]
        left = (i * 31) % 100
        delay = (i % 9) * 0.55
        duration = 5 + (i % 6)
        size = 18 + (i % 5) * 5

        result.append(
            f'<span class="particle" '
            f'style="left:{left}%;'
            f'animation-delay:{delay}s;'
            f'animation-duration:{duration}s;'
            f'font-size:{size}px">{emoji}</span>'
        )

    return "".join(result)


HTML = """
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport"
      content="width=device-width,initial-scale=1,maximum-scale=1">

<title>{{ title }}</title>

<style>

* {
    box-sizing: border-box;
}

html, body {
    margin: 0;
    min-height: 100%;
}

body {
    min-height: 100vh;
    font-family: Arial, sans-serif;
    color: white;
    overflow-x: hidden;
}

body.home {
    background:
        radial-gradient(circle at 20% 10%, #ffffff88, transparent 30%),
        linear-gradient(135deg,#ffb6e6,#9dbdff);
}

body.love {
    background:
        radial-gradient(circle at 50% 20%, #ffb6e655, transparent 35%),
        linear-gradient(135deg,#500724,#be185d,#f43f5e);
}

body.miss {
    background:
        radial-gradient(circle at 70% 10%, #ffffff33, transparent 25%),
        linear-gradient(135deg,#1e1b4b,#6d28d9,#be185d);
}

body.sorry {
    background:
        radial-gradient(circle at 20% 15%, #ffffff33, transparent 25%),
        linear-gradient(135deg,#1e293b,#475569,#7c3aed);
}

body.birthday {
    background:
        radial-gradient(circle at 20% 20%, #ffffff77, transparent 25%),
        linear-gradient(135deg,#2563eb,#db2777,#f59e0b);
}

body.night {
    background:
        radial-gradient(circle at 50% 5%, #ffffff44, transparent 25%),
        linear-gradient(135deg,#020617,#172554,#581c87);
}

body.friend {
    background:
        radial-gradient(circle at 20% 20%, #ffffff55, transparent 30%),
        linear-gradient(135deg,#064e3b,#16a34a,#65a30d);
}

body.cute {
    background:
        radial-gradient(circle at 20% 10%, #ffffff77, transparent 30%),
        linear-gradient(135deg,#fbc2eb,#a6c1ee);
}

body.hype {
    background:
        radial-gradient(circle at 70% 15%, #ffd16666, transparent 25%),
        linear-gradient(135deg,#7f1d1d,#ea580c,#facc15);
}

body.dreamy {
    background:
        radial-gradient(circle at 50% 10%, #ffffff44, transparent 25%),
        linear-gradient(135deg,#312e81,#7c3aed,#db2777);
}

.container {
    width: 100%;
    max-width: 680px;
    margin: auto;
    padding: 20px 15px;
    position: relative;
    z-index: 5;
}

.card {
    padding: 28px;
    border-radius: 30px;
    background: rgba(255,255,255,.14);
    border: 1px solid rgba(255,255,255,.30);
    backdrop-filter: blur(22px);
    -webkit-backdrop-filter: blur(22px);
    box-shadow: 0 25px 80px rgba(0,0,0,.28);
}

.logo {
    text-align: center;
    font-size: 48px;
    font-weight: 900;
    letter-spacing: -2px;
}

.subtitle {
    text-align: center;
    opacity: .9;
    margin: 8px 0 25px;
}

textarea {
    width: 100%;
    min-height: 160px;
    padding: 18px;
    border: 0;
    outline: 0;
    border-radius: 20px;
    font-size: 17px;
    resize: vertical;
    background: rgba(255,255,255,.95);
    color: #222;
}

textarea:focus {
    box-shadow: 0 0 0 4px rgba(255,255,255,.25);
}

button {
    width: 100%;
    padding: 16px;
    margin-top: 15px;
    border: 0;
    border-radius: 17px;
    background: white;
    color: #7c3aed;
    font-size: 17px;
    font-weight: 800;
    cursor: pointer;
}

button:active {
    transform: scale(.97);
}

.linkbox {
    margin-top: 20px;
    padding: 17px;
    border-radius: 20px;
    background: rgba(0,0,0,.20);
}

.link {
    display: block;
    margin-top: 10px;
    padding: 13px;
    border-radius: 13px;
    background: rgba(255,255,255,.14);
    color: white;
    text-decoration: none;
    word-break: break-all;
}

.actions {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 10px;
    margin-top: 10px;
}

.actions button {
    margin-top: 0;
}

.vibe {
    min-height: 70vh;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    text-align: center;
}

.emoji {
    font-size: 82px;
    animation: pop .8s cubic-bezier(.17,.67,.3,1.5);
    filter: drop-shadow(0 10px 20px rgba(0,0,0,.2));
}

.vibe-title {
    font-size: 36px;
    font-weight: 900;
    margin: 12px;
    animation: titleIn .8s ease;
}

.vibe-text {
    max-width: 100%;
    font-size: 22px;
    line-height: 1.65;
    white-space: pre-wrap;
    word-break: break-word;
    animation: textIn 1.1s ease;
}

.badge {
    margin-top: 20px;
    padding: 9px 17px;
    border-radius: 30px;
    background: rgba(255,255,255,.18);
    font-size: 13px;
}

.home {
    width: 100%;
    max-width: 280px;
    margin-top: 20px;
}

.home button {
    margin-top: 0;
}

.particles {
    position: fixed;
    inset: 0;
    pointer-events: none;
    overflow: hidden;
    z-index: 1;
}

.particle {
    position: absolute;
    bottom: -70px;
    opacity: 0;
    animation-name: float;
    animation-timing-function: linear;
    animation-iteration-count: infinite;
    user-select: none;
}

.footer {
    text-align: center;
    margin-top: 15px;
    opacity: .65;
    font-size: 13px;
}

@keyframes float {
    0% {
        transform: translateY(0) rotate(0deg) scale(.6);
        opacity: 0;
    }

    12% {
        opacity: .95;
    }

    80% {
        opacity: .75;
    }

    100% {
        transform:
            translateY(-115vh)
            rotate(360deg)
            scale(1.25);
        opacity: 0;
    }
}

@keyframes pop {
    from {
        transform: scale(.2) rotate(-15deg);
        opacity: 0;
    }

    to {
        transform: scale(1) rotate(0);
        opacity: 1;
    }
}

@keyframes titleIn {
    from {
        opacity: 0;
        transform: translateY(20px);
    }

    to {
        opacity: 1;
        transform: translateY(0);
    }
}

@keyframes textIn {
    from {
        opacity: 0;
        transform: translateY(25px);
    }

    to {
        opacity: 1;
        transform: translateY(0);
    }
}

@media(max-width:500px) {

    .container {
        padding: 12px;
    }

    .card {
        padding: 20px;
        border-radius: 25px;
    }

    .logo {
        font-size: 40px;
    }

    .emoji {
        font-size: 68px;
    }

    .vibe-title {
        font-size: 30px;
    }

    .vibe-text {
        font-size: 19px;
    }

    textarea {
        font-size: 16px;
    }
}

</style>
</head>

<body class="{{ page_class }}">

{% if page %}

<div class="particles">
{{ particles|safe }}
</div>

{% endif %}

<div class="container">

<div class="card">

{% if page %}

<div class="vibe">

<div class="emoji">
{{ page.emoji }}
</div>

<div class="vibe-title">
{{ page.title }}
</div>

<div class="vibe-text">
{{ page.text }}
</div>

<div class="badge">
✨ Created with Vibely
</div>

<a class="home" href="/">
<button type="button">
✨ Create Your Vibely
</button>
</a>

</div>

{% else %}

<div class="logo">
✨ Vibely
</div>

<div class="subtitle">
Write a feeling. Vibely turns it into a vibe.
</div>

<form method="POST">

<textarea
name="text"
maxlength="1000"
placeholder="ဥပမာ...

Yo baby ❤️
Good night sweet dreams 🌙
Happy birthday 🎂
I miss you 🥺
Best friend forever 🫶"
required></textarea>

<button type="submit">
✨ Create My Vibely
</button>

</form>

{% if link %}

<div class="linkbox">

🔗 Your Vibely Link

<a class="link"
   href="{{ link }}"
   id="vibelyLink">
{{ link }}
</a>

<div class="actions">

<button type="button" onclick="copyLink()">
📋 Copy
</button>

<button type="button" onclick="shareLink()">
📤 Share
</button>

</div>

</div>

<script>

function copyLink() {

    const link =
        document.getElementById("vibelyLink").href;

    if (navigator.clipboard) {

        navigator.clipboard.writeText(link)
        .then(() => alert("✨ Link copied!"))
        .catch(() => prompt("Copy link:", link));

    } else {

        prompt("Copy your Vibely link:", link);

    }
}


function shareLink() {

    const link =
        document.getElementById("vibelyLink").href;

    if (navigator.share) {

        navigator.share({
            title: "✨ My Vibely",
            text: "I made a Vibely for you 💕",
            url: link
        });

    } else {

        copyLink();

    }
}

</script>

{% endif %}

{% endif %}

</div>

<div class="footer">
✨ Vibely • Turn feelings into vibes
</div>

</div>

</body>
</html>
"""


@app.route("/", methods=["GET", "POST"])
def home():

    link = None

    if request.method == "POST":

        text = request.form.get("text", "").strip()

        if not text:
            return redirect(url_for("home"))

        if len(text) > 1000:
            text = text[:1000]

        mood = detect_mood(text)

        # Auto style follows the detected mood
        style = mood

        code = secrets.token_urlsafe(8)

        con = db()

        con.execute(
            """
            INSERT INTO pages
            (code, text, mood, style)
            VALUES (?, ?, ?, ?)
            """,
            (code, text, mood, mood)
        )

        con.commit()
        con.close()

        link = request.host_url + "v/" + code

    return render_template_string(
        HTML,
        title="Vibely",
        page=None,
        page_class="home",
        link=link,
        particles=""
    )


@app.route("/v/<code>")
def vibe(code):

    con = db()

    row = con.execute(
        """
        SELECT code, text, mood, style
        FROM pages
        WHERE code=?
        """,
        (code,)
    ).fetchone()

    con.close()

    if not row:

        return """
        <div style="
            font-family:Arial;
            text-align:center;
            padding:60px;
        ">
            <h1>😢 Vibely not found</h1>
            <a href="/">✨ Create a new Vibely</a>
        </div>
        """, 404

    mood = row["mood"] or row["style"] or "cute"

    if mood not in MOODS:
        mood = "cute"

    data = MOODS[mood]

    page = {
        "emoji": data["emoji"],
        "title": data["title"],
        "text": row["text"]
    }

    return render_template_string(
        HTML,
        title="Vibely • " + data["title"],
        page=page,
        page_class=data["class"],
        particles=particle_html(data["particles"]),
        link=None
    )


if __name__ == "__main__":

    init_db()

    port = int(os.environ.get("PORT", "5000"))

    print("")
    print("=========================")
    print("       VIBELY 2.0")
    print("=========================")
    print("Database:", DB)
    print("Port:", port)
    print("")

    app.run(
        host="0.0.0.0",
        port=port,
        debug=False
    )
