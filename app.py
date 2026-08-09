from flask import Flask, request, render_template_string, redirect, url_for
import sqlite3
import secrets
import os
import re

app = Flask(__name__)

# Writable database path for both Termux and Belmo.
if os.environ.get("PREFIX", "").startswith("/data/data/com.termux"):
    DB = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "data",
        "vibely.db"
    )
else:
    DB = "/tmp/vibely.db"

MOODS = {
    "love": {
        "emoji": "❤️",
        "title": "Love",
        "class": "love",
        "particles": ["❤️", "💕", "💗", "💖", "💘"]
    },
    "miss": {
        "emoji": "🥺",
        "title": "Miss You",
        "class": "miss",
        "particles": ["💕", "🥺", "💭", "💗"]
    },
    "sorry": {
        "emoji": "🥺",
        "title": "Sorry",
        "class": "sorry",
        "particles": ["🥺", "💔", "🌸", "🤍"]
    },
    "birthday": {
        "emoji": "🎂",
        "title": "Birthday",
        "class": "birthday",
        "particles": ["🎉", "🎈", "🎂", "✨", "🎊"]
    },
    "night": {
        "emoji": "🌙",
        "title": "Good Night",
        "class": "night",
        "particles": ["🌙", "⭐", "✨", "💫"]
    },
    "friend": {
        "emoji": "🫶",
        "title": "Friendship",
        "class": "friend",
        "particles": ["🫶", "💛", "✨", "🌸"]
    },
    "cute": {
        "emoji": "🌸",
        "title": "Cute",
        "class": "cute",
        "particles": ["🌸", "💗", "✨", "🦋"]
    },
    "hype": {
        "emoji": "🔥",
        "title": "Hype",
        "class": "hype",
        "particles": ["🔥", "⚡", "💥", "✨"]
    },
    "dreamy": {
        "emoji": "✨",
        "title": "Dreamy",
        "class": "dreamy",
        "particles": ["✨", "🌙", "💫", "🦋"]
    },
}

KEYWORDS = {
    "love": [
        "love", "lover", "baby", "bby", "babe", "darling",
        "sweetheart", "crush", "ချစ်", "ချစ်တယ်", "အချစ်",
        "ချစ်သူ", "ဘေဘီ", "babyလေး"
    ],
    "miss": [
        "miss you", "miss u", "missing you", "လွမ်း",
        "လွမ်းတယ်", "သတိရ", "သတိရတယ်"
    ],
    "sorry": [
        "sorry", "forgive", "တောင်းပန်", "တောင်းပန်ပါတယ်",
        "ခွင့်လွှတ်"
    ],
    "birthday": [
        "happy birthday", "birthday", "မွေးနေ့",
        "မွေးနေ့ပျော်ရွှင်ပါစေ"
    ],
    "night": [
        "good night", "gn", "sweet dreams", "sleep well",
        "အိပ်တော့", "အိပ်ကောင်းကောင်း", "ညနေကောင်း"
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
    ],
}


def db():
    con = sqlite3.connect(DB, timeout=10)
    con.row_factory = sqlite3.Row

    con.execute("""
        CREATE TABLE IF NOT EXISTS pages (
            code TEXT PRIMARY KEY,
            text TEXT NOT NULL,
            mood TEXT,
            style TEXT DEFAULT 'cute',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Upgrade old databases that were created before style was added.
    columns = {
        row[1]
        for row in con.execute("PRAGMA table_info(pages)").fetchall()
    }

    if "style" not in columns:
        con.execute(
            "ALTER TABLE pages ADD COLUMN style TEXT DEFAULT 'cute'"
        )

    if "mood" not in columns:
        con.execute(
            "ALTER TABLE pages ADD COLUMN mood TEXT DEFAULT 'cute'"
        )

    con.commit()
    return con


def detect_mood(text):
    t = text.lower().strip()

    # Check longer phrases first.
    matches = []

    for mood, words in KEYWORDS.items():
        for word in words:
            if word.lower() in t:
                matches.append((len(word), mood))

    if matches:
        matches.sort(reverse=True)
        return matches[0][1]

    return "cute"


def particle_html(particles):
    result = []

    for i in range(18):
        emoji = particles[i % len(particles)]
        left = (i * 37) % 100
        delay = (i % 7) * 0.7
        duration = 6 + (i % 5)

        result.append(
            f'<span class="particle" '
            f'style="left:{left}%;animation-delay:{delay}s;'
            f'animation-duration:{duration}s">{emoji}</span>'
        )

    return "".join(result)

def init_db():
    con = db()
    con.close()


HTML = """
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
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
    transition: background 1s ease;
}

body.home-bg {
    background:
        radial-gradient(circle at 20% 10%, #ffffff66, transparent 28%),
        linear-gradient(135deg,#ffb6e6,#9dbdff);
}

body.love {
    background:
        radial-gradient(circle at 50% 20%, #ffb6e655, transparent 30%),
        linear-gradient(135deg,#7f1d3d,#db2777,#be185d);
}

body.miss {
    background:
        radial-gradient(circle at 70% 15%, #ffffff33, transparent 25%),
        linear-gradient(135deg,#312e81,#7e22ce,#be185d);
}

body.sorry {
    background:
        radial-gradient(circle at 20% 20%, #ffffff33, transparent 25%),
        linear-gradient(135deg,#334155,#7c3aed,#be123c);
}

body.birthday {
    background:
        radial-gradient(circle at 20% 20%, #ffffff66, transparent 25%),
        linear-gradient(135deg,#2563eb,#db2777,#f59e0b);
}

body.night {
    background:
        radial-gradient(circle at 50% 10%, #ffffff33, transparent 25%),
        linear-gradient(135deg,#020617,#312e81,#581c87);
}

body.friend {
    background:
        radial-gradient(circle at 20% 20%, #ffffff55, transparent 30%),
        linear-gradient(135deg,#0f766e,#16a34a,#65a30d);
}

body.cute {
    background:
        radial-gradient(circle at 20% 10%, #ffffff66, transparent 30%),
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
    z-index: 2;
}

.card {
    padding: 28px;
    border-radius: 30px;
    background: rgba(255,255,255,.15);
    border: 1px solid rgba(255,255,255,.30);
    backdrop-filter: blur(20px);
    box-shadow: 0 25px 80px rgba(0,0,0,.25);
}

.logo {
    text-align: center;
    font-size: 45px;
    font-weight: 900;
}

.subtitle {
    text-align: center;
    opacity: .9;
    margin: 8px 0 25px;
}

textarea {
    width: 100%;
    min-height: 150px;
    padding: 17px;
    border: 0;
    outline: 0;
    border-radius: 20px;
    font-size: 16px;
    resize: vertical;
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
    font-weight: bold;
    cursor: pointer;
}

button:active {
    transform: scale(.98);
}

.linkbox {
    margin-top: 20px;
    padding: 16px;
    border-radius: 18px;
    background: rgba(0,0,0,.18);
}

.link {
    display: block;
    margin-top: 10px;
    padding: 12px;
    border-radius: 12px;
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
    position: relative;
}

.emoji {
    font-size: 75px;
    animation: pop .8s ease;
}

.vibe-title {
    font-size: 34px;
    font-weight: 900;
    margin: 10px;
}

.vibe-text {
    font-size: 22px;
    line-height: 1.65;
    white-space: pre-wrap;
    word-break: break-word;
    opacity: 0;
    animation: reveal 1.5s ease forwards;
    animation-delay: .5s;
}

.badge {
    margin-top: 18px;
    padding: 9px 16px;
    border-radius: 30px;
    background: rgba(255,255,255,.18);
}

.footer {
    text-align: center;
    margin-top: 15px;
    opacity: .65;
    font-size: 13px;
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
    bottom: -60px;
    font-size: 25px;
    opacity: 0;
    animation-name: float;
    animation-timing-function: linear;
    animation-iteration-count: infinite;
}

@keyframes float {
    0% {
        transform: translateY(0) rotate(0deg) scale(.7);
        opacity: 0;
    }
    15% {
        opacity: .9;
    }
    85% {
        opacity: .8;
    }
    100% {
        transform: translateY(-115vh) rotate(360deg) scale(1.2);
        opacity: 0;
    }
}

@keyframes pop {
    from {
        transform: scale(.3);
        opacity: 0;
    }
    to {
        transform: scale(1);
        opacity: 1;
    }
}

@keyframes reveal {
    from {
        opacity: 0;
        transform: translateY(15px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

@media(max-width:500px) {
    .card {
        padding: 20px;
        border-radius: 25px;
    }

    .logo {
        font-size: 38px;
    }

    .vibe-title {
        font-size: 29px;
    }

    .vibe-text {
        font-size: 19px;
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
<button type="button">✨ Create Your Vibely</button></a>

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

<a class="link" href="{{ link }}" id="vibelyLink">
{{ link }}
</a>

<div class="actions">
<button type="button" onclick="copyLink()">
📋 Copy Link
</button>

<button type="button" onclick="shareLink()">
📤 Share
</button>
</div>

</div>

<script>
function copyLink() {
    const link = document.getElementById("vibelyLink").href;

    navigator.clipboard.writeText(link).then(function() {
        alert("✨ Link copied!");
    }).catch(function() {
        prompt("Copy your Vibely link:", link);
    });
}

function shareLink() {
    const link = document.getElementById("vibelyLink").href;

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

        mood = detect_mood(text)

        style = request.form.get("style", "cute")

        if not style:
            style = "cute"

        code = secrets.token_urlsafe(8)

        con = db()

        con.execute(
            """
            INSERT INTO pages(code,text,style,mood)
            VALUES(?,?,?,?)
            """,
            (code, text, style, mood)
        )

        con.commit()
        con.close()

        link = request.host_url + "v/" + code

    return render_template_string(
        HTML,
        title="Vibely",
        page=None,
        page_class="home-bg",
        link=link,
        particles="",
    )


@app.route("/v/<code>")
def vibe(code):

    con = db()

    row = con.execute(
        """
        SELECT code,text,mood
        FROM pages
        WHERE code=?
        """,
        (code,)
    ).fetchone()

    con.close()

    if not row:
        return "<h1 style='text-align:center'>😢 Vibely not found</h1>", 404

    mood = MOODS.get(row["mood"], MOODS["cute"])

    page = {
        "emoji": mood["emoji"],
        "title": mood["title"],
        "text": row["text"],
    }

    return render_template_string(
        HTML,
        title="Vibely • " + mood["title"],
        page=page,
        page_class=mood["class"],
        particles=particle_html(mood["particles"]),
        link=None,
    )


if __name__ == "__main__":

    init_db()

    print("")
    print("=========================")
    print("        VIBELY 2.0")
    print("=========================")
    print("Database:", DB)
    print("http://127.0.0.1:5000")
    print("")

    port = int(os.environ.get("PORT", "5000"))

    app.run(
        host="0.0.0.0",
        port=port,
        debug=True
    )
