from flask import Flask, request
import requests as req
import time
from bs4 import BeautifulSoup

app = Flask(__name__)

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

LANDING = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>SiteCheck — Free Website Health Report by Nikhil</title>
<style>
:root{--bg:#0b0f14;--panel:#101820;--line:#1e2a36;--text:#e6edf3;--muted:#9aa9b8;--accent:#4ade80}
*{margin:0;padding:0;box-sizing:border-box}
body{background:var(--bg);color:var(--text);font-family:"Segoe UI",system-ui,sans-serif;line-height:1.6;min-height:100vh;display:flex;align-items:center;justify-content:center;padding:24px}
.box{max-width:640px;width:100%;background:var(--panel);border:1px solid var(--line);border-radius:16px;padding:40px}
h1{font-size:2rem;margin-bottom:6px}
h1 span{color:var(--accent)}
p.sub{color:var(--muted);margin-bottom:24px}
form{display:flex;gap:10px;flex-wrap:wrap}
input{flex:1;min-width:220px;padding:13px 16px;border-radius:10px;border:1px solid var(--line);background:var(--bg);color:var(--text);font-size:1rem}
button{padding:13px 24px;border-radius:10px;border:none;background:var(--accent);color:#08130b;font-weight:700;font-size:1rem;cursor:pointer}
ul{margin:24px 0 0 18px;color:var(--muted);font-size:.92rem}
footer{margin-top:28px;color:var(--muted);font-size:.85rem}
footer a{color:var(--accent);text-decoration:none}
</style>
</head>
<body>
<div class="box">
<h1>🩺 Site<span>Check</span></h1>
<p class="sub">Free instant website health report — speed, mobile, SEO & security. Enter any website URL.</p>
<form action="/api/check" method="POST">
<input type="text" name="url" placeholder="https://yourbusiness.com" required>
<button type="submit">Run Free Check</button>
</form>
<ul>
<li>Page load speed & weight</li>
<li>HTTPS / SSL security</li>
<li>Mobile-friendliness</li>
<li>SEO: title, meta description, H1, alt tags</li>
</ul>
<footer>Built by <a href="https://imnick009.github.io">Nikhil</a> · <a href="https://github.com/imnick009">GitHub</a> · osmnick999@gmail.com</footer>
</div>
</body>
</html>"""

CSS = """
:root{--bg:#0b0f14;--panel:#101820;--line:#1e2a36;--text:#e6edf3;--muted:#9aa9b8;--accent:#4ade80}
*{margin:0;padding:0;box-sizing:border-box}
body{background:var(--bg);color:var(--text);font-family:"Segoe UI",system-ui,sans-serif;line-height:1.6;padding:24px}
.wrap{max-width:720px;margin:0 auto}
h1{font-size:1.8rem;margin-bottom:4px} h1 span{color:var(--accent)}
.score{font-size:2.4rem;font-weight:800;margin:18px 0 4px}
.sub{color:var(--muted);margin-bottom:20px}
.row{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:16px 18px;margin-bottom:10px}
.row .name{font-weight:700}
.row .detail{color:var(--muted);font-size:.92rem;margin-top:2px}
.row .fix{color:var(--accent);font-size:.88rem;margin-top:6px}
.cta{background:var(--panel);border:1px solid var(--line);border-radius:14px;padding:26px;margin-top:26px;text-align:center}
.cta a{color:var(--accent)}
a.back{color:var(--muted);font-size:.9rem;text-decoration:none}
"""

def audit(url):
    checks = []
    try:
        t0 = time.time()
        r = req.get(url, timeout=15, headers=UA, allow_redirects=True)
        load = round(time.time() - t0, 2)
        final_url = r.url
        soup = BeautifulSoup(r.text, "html.parser")

        checks.append(("Page Load Speed", load <= 3, f"{load}s",
                       "Compress images, enable caching, use a CDN."))
        checks.append(("HTTPS / SSL Security", final_url.startswith("https"),
                       "Secure" if final_url.startswith("https") else "NOT secure",
                       "Install a free SSL certificate (Let's Encrypt / Cloudflare)."))
        vp = soup.find("meta", attrs={"name": "viewport"}) is not None
        checks.append(("Mobile Friendly", vp,
                       "Viewport set" if vp else "No viewport tag",
                       "Add mobile viewport meta tag + responsive theme."))
        title = soup.title.string.strip() if soup.title and soup.title.string else ""
        checks.append(("Page Title (SEO)", len(title) >= 10,
                       title or "Missing",
                       "Write a 30-60 character title with your main keyword."))
        m = soup.find("meta", attrs={"name": "description"})
        desc = m.get("content", "") if m and m.get("content") else ""
        checks.append(("Meta Description (SEO)", len(desc) >= 50,
                       (desc[:60] + "...") if desc else "Missing",
                       "Add a 120-160 char description - this is what Google shows."))
        h1 = soup.find("h1")
        checks.append(("H1 Heading", h1 is not None,
                       h1.get_text(strip=True)[:60] if h1 else "Missing",
                       "Use exactly one H1 that states what the page is about."))
        imgs = soup.find_all("img")
        no_alt = [i for i in imgs if not i.get("alt")]
        checks.append(("Image Alt Tags", len(no_alt) == 0,
                       f"{len(no_alt)}/{len(imgs)} images missing alt",
                       "Add alt text to every image (SEO + accessibility)."))
        kb = round(len(r.content) / 1024)
        checks.append(("Page Weight", kb <= 1500, f"{kb} KB",
                       "Compress images & remove unused scripts."))
        return checks, None
    except Exception as e:
        return None, str(e)

def report_html(u, checks):
    passed = sum(1 for c in checks if c[1])
    score = round(passed / len(checks) * 100)
    color = "#4ade80" if score >= 80 else ("#fbbf24" if score >= 50 else "#f87171")
    rows = ""
    for name, ok, detail, fix in checks:
        icon = "✅" if ok else "❌"
        fixline = "" if ok else f'<div class="fix">🔧 Fix: {fix}</div>'
        rows += f'<div class="row"><div class="name">{icon} {name}</div><div class="detail">{detail}</div>{fixline}</div>'
    return f"""<!DOCTYPE html><html><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>SiteCheck Report</title><style>{CSS}</style></head>
<body><div class="wrap">
<a class="back" href="/">← New check</a>
<h1>🩺 Site<span>Check</span> Report</h1>
<div class="sub">Scanned: {u}</div>
<div class="score" style="color:{color}">{score}/100</div>
<div class="sub">Health Score</div>
{rows}
<div class="cta">
<h2>Want these issues fixed for you?</h2>
<p class="sub">I fix exactly these problems for businesses in 2-4 days, fixed price.</p>
<p>📧 <a href="mailto:osmnick999@gmail.com">osmnick999@gmail.com</a> ·
🌐 <a href="https://imnick009.github.io">Portfolio</a> ·
🐙 <a href="https://github.com/imnick009">GitHub</a></p>
</div>
</div></body></html>"""

def error_html(msg):
    return f"""<!DOCTYPE html><html><head><meta charset="UTF-8"><style>{CSS}</style></head>
<body><div class="wrap"><a class="back" href="/">← New check</a>
<h1> Site<span>Check</span></h1>
<div class="row"><div class="name">❌ Could not scan</div>
<div class="detail">{msg}</div></div></div></body></html>"""

@app.route("/")
def home():
    return LANDING

@app.route("/api/check", methods=["POST"])
def check():
    url = request.form.get("url", "").strip()
    if not url:
        return error_html("No URL provided.")
    u = url if url.startswith("http") else "https://" + url
    checks, err = audit(u)
    if err:
        return error_html(err)
    return report_html(u, checks)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
