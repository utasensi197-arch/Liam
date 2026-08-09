from flask import Flask, request, render_template_string, redirect, url_for
import sqlite3
import secrets
import os

app = Flask(__name__)

if os.environ.get("BELMO") or os.environ.get("PORT") == "3000":
    DB = "/tmp/vibely.db"
else:
    DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
    os.makedirs(DATA_DIR, exist_ok=True)
    DB = os.path.join(DATA_DIR, "vibely.db")

STYLES = {
    "cute": ("🌸", "Cute", "Soft • Sweet • Lovely", "cute"),
    "rare": ("💎", "Rare", "Unique • Special • Different", "rare"),
    "wild": ("🔥", "Wild", "Bold • Free • Powerful", "wild"),
    "dreamy": ("🌙", "Dreamy", "Dream • Moon • Magic", "dreamy"),
    "royal": ("👑", "Royal", "Elegant • Luxury • Crown", "royal"),
    "dark": ("🖤", "Dark", "Mystery • Shadow • Night", "dark")
}


def db():
    os.makedirs(os.path.dirname(DB), exist_ok=True)
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    return con


def init_db():
    con = db()

    con.execute("""
        CREATE TABLE IF NOT EXISTS pages (
            code TEXT PRIMARY KEY,
            text TEXT NOT NULL,
            style TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    con.commit()
    con.close()


HTML = """
<!DOCTYPE html>
<html>
<head>

<meta charset="UTF-8">

<meta name="viewport"
content="width=device-width,initial-scale=1">

<title>{{ title }}</title>

<style>

*{
    box-sizing:border-box;
}

body{
    margin:0;
    min-height:100vh;
    font-family:Arial,sans-serif;
    color:white;

    background:
    radial-gradient(circle at 20% 10%,#ffffff55,transparent 30%),
    linear-gradient(135deg,#ffb6e6,#9dbdff);
}

body.rare{
    background:linear-gradient(135deg,#172554,#7c3aed);
}

body.wild{
    background:linear-gradient(135deg,#ff512f,#7f0000);
}

body.dreamy{
    background:linear-gradient(135deg,#667eea,#764ba2);
}

body.royal{
    background:linear-gradient(135deg,#3b0764,#a16207);
}


body.cat{
    background:
    radial-gradient(circle at 20% 20%, #fff5fb 0%, transparent 30%),
    linear-gradient(135deg,#fbc2eb,#a6c1ee);
}

body.flower{
    background:
    radial-gradient(circle at 20% 20%, #ffd6e8 0%, transparent 30%),
    linear-gradient(135deg,#fbc2eb,#f8d9a8);
}

body.ocean{
    background:
    radial-gradient(circle at 80% 10%, #ffffff55 0%, transparent 30%),
    linear-gradient(135deg,#00c6ff,#0072ff);
}

body.night{
    background:
    radial-gradient(circle at 50% 15%, #ffffff33 0%, transparent 25%),
    linear-gradient(135deg,#0f172a,#312e81,#581c87);
}

body.fire{
    background:
    radial-gradient(circle at 70% 20%, #ffd16655 0%, transparent 25%),
    linear-gradient(135deg,#7f1d1d,#ea580c,#facc15);
}

body.forest{
    background:
    radial-gradient(circle at 20% 20%, #bbf7d055 0%, transparent 30%),
    linear-gradient(135deg,#064e3b,#166534,#365314);
}

body.sky{
    background:
    radial-gradient(circle at 30% 10%, #ffffff66 0%, transparent 30%),
    linear-gradient(135deg,#38bdf8,#818cf8,#f0abfc);
}

body.dark{
    background:linear-gradient(135deg,#020617,#111827);
}

.container{
    width:100%;
    max-width:620px;
    margin:auto;
    padding:22px 16px;
}

.card{
    padding:28px;
    border-radius:30px;

    background:rgba(255,255,255,.16);

    border:1px solid rgba(255,255,255,.3);

    backdrop-filter:blur(20px);

    box-shadow:
    0 25px 70px rgba(0,0,0,.25);
}

.logo{
    text-align:center;
    font-size:44px;
    font-weight:900;
}

.subtitle{
    text-align:center;
    opacity:.9;
    margin:8px 0 28px;
}

textarea{
    width:100%;
    min-height:140px;

    padding:17px;

    border:0;
    outline:0;

    border-radius:20px;

    font-size:16px;

    resize:vertical;
}

.styles{
    display:grid;
    grid-template-columns:repeat(2,1fr);
    gap:10px;
    margin-top:10px;
}

.style{
    padding:14px;

    border-radius:16px;

    background:rgba(255,255,255,.12);

    text-align:center;

    cursor:pointer;
}

.style input{
    display:none;
}

.style:has(input:checked){
    background:rgba(255,255,255,.4);
    border:1px solid white;
}

button{
    width:100%;

    padding:16px;

    margin-top:18px;

    border:0;

    border-radius:17px;

    background:white;

    color:#6d28d9;

    font-size:17px;

    font-weight:bold;
}

.linkbox{
    margin-top:20px;

    padding:16px;

    border-radius:18px;

    background:rgba(0,0,0,.18);
}

.link{
    display:block;

    margin-top:10px;

    padding:12px;

    border-radius:12px;

    background:rgba(255,255,255,.12);

    color:white;

    text-decoration:none;

    word-break:break-all;
}

.vibe{
    min-height:65vh;

    display:flex;

    flex-direction:column;

    justify-content:center;

    align-items:center;

    text-align:center;
}

.emoji{
    font-size:75px;
}

.vibe-title{
    font-size:36px;
    font-weight:900;
    margin:12px;
}

.vibe-text{
    font-size:21px;
    line-height:1.6;

    white-space:pre-wrap;
    word-break:break-word;
}

.badge{
    margin-top:18px;

    padding:9px 16px;

    border-radius:30px;

    background:rgba(255,255,255,.18);
}

.home{
    display:inline-block;

    margin-top:25px;

    padding:13px 20px;

    border-radius:15px;

    background:white;

    color:#6d28d9;

    text-decoration:none;

    font-weight:bold;
}

.footer{
    text-align:center;

    margin-top:15px;

    opacity:.65;

    font-size:13px;
}

</style>

</head>

<body class="{{ page_class }}">

<div class="container">

<div class="card">

{% if page %}

<div class="vibe">

<div class="emoji">
{{ page[0] }}
</div>

<div class="vibe-title">
{{ page[1] }}
</div>

<div class="vibe-text">
{{ page[3] }}
</div>

<div class="badge">
{{ page[2] }}
</div>

<a class="home"
href="/">
✨ Create Your Vibely
</a>

</div>

{% else %}

<div class="logo">
✨ Vibely
</div>

<div class="subtitle">
Turn your words into a unique vibe
</div>

<form method="POST">

<textarea
name="text"
maxlength="1000"
placeholder="ကိုယ်လိုချင်တဲ့ပုံစံကိုရေးပါ...

ဥပမာ -
cute pink cat,
dreamy sky,
magical night..."
required></textarea>

<div class="styles">

{% for key, value in styles.items() %}

<label class="style">

<input
type="radio"
name="style"
value="{{ key }}"
{% if key == "cute" %}checked{% endif %}
>

{{ value[0] }} {{ value[1] }}

</label>

{% endfor %}

</div>

<button type="submit">
✨ Create My Vibely
</button>

</form>

{% if link %}

<div class="linkbox">

🔗 Your Vibely Link

<a class="link" href="{{ link }}">
{{ link }}
</a>

</div>

{% endif %}

{% endif %}

</div>

<div class="footer">
✨ Vibely
</div>

</div>

</body>
</html>
"""



def detect_background(text, style):
    """
    Choose a visual background from the user's words.
    """
    t = text.lower()

    themes = {
        "cat": [
            "cat", "kitten", "kitty", "ကြောင်", "ကြောင်လေး"
        ],
        "flower": [
            "flower", "flowers", "rose", "garden",
            "ပန်း", "နှင်းဆီ", "ဥယျာဉ်"
        ],
        "ocean": [
            "ocean", "sea", "beach", "wave",
            "ပင်လယ်", "ကမ်းခြေ", "လှိုင်း"
        ],
        "night": [
            "night", "moon", "star", "stars", "galaxy",
            "ည", "လ", "ကြယ်", "ကြယ်တွေ", "အာကာသ"
        ],
        "fire": [
            "fire", "flame", "hot", "power",
            "မီး", "အပူ", "စွမ်းအား"
        ],
        "forest": [
            "forest", "tree", "nature", "jungle",
            "သစ်တော", "သစ်ပင်", "သဘာဝ"
        ],
        "sky": [
            "sky", "cloud", "clouds", "sunset",
            "မိုးကောင်းကင်", "တိမ်", "နေဝင်"
        ]
    }

    for theme, words in themes.items():
        if any(word in t for word in words):
            return theme

    return style


@app.route("/", methods=["GET", "POST"])
def home():

    link = None

    if request.method == "POST":

        text = request.form.get("text", "").strip()
        style = request.form.get("style", "cute")

        if not text:
            return redirect(url_for("home"))

        if style not in STYLES:
            style = "cute"

        code = secrets.token_urlsafe(8)

        con = db()

        con.execute(
            """
            INSERT INTO pages
            (code,text,style)
            VALUES (?,?,?)
            """,
            (code, text, style)
        )

        con.commit()
        con.close()

        link = request.host_url + "v/" + code

    return render_template_string(
        HTML,
        title="Vibely",
        page=None,
        page_class="",
        styles=STYLES,
        link=link
    )


@app.route("/v/<code>")
def vibe(code):

    con = db()

    row = con.execute(
        """
        SELECT code,text,style
        FROM pages
        WHERE code=?
        """,
        (code,)
    ).fetchone()

    con.close()

    if not row:
        return """
        <h1 style="text-align:center">
        😢 Vibely not found
        </h1>
        """, 404

    style = STYLES.get(
        row[2],
        STYLES["cute"]
    )

    page = (
        style[0],
        style[1],
        style[2],
        row[1]
    )

    return render_template_string(
        HTML,
        title="Vibely • " + style[1],
        page=page,
        page_class=detect_background(page[3], row[2]),
        styles=STYLES,
        link=None
    )


if __name__ == "__main__":

    init_db()

    print("")
    print("=========================")
    print("        VIBELY")
    print("=========================")
    print("Database: SQLite")
    print("http://127.0.0.1:5000")
    print("")

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )
