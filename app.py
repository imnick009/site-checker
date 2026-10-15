from flask import Flask, request, send_file
import requests as req
import time
import io
import urllib.parse
from bs4 import BeautifulSoup
from fpdf import FPDF

app = Flask(__name__)

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

LANDING="""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>SiteCheck — Free Website Health Report by Nikhil</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<style>
*{margin:0;padding:0;box-sizing:border-box}
:root{
--bg:#0a0e27;
--panel:rgba(16,24,32,.85);
--line:rgba(255,255,255,.08);
--text:#e6edf3;
--muted:#9aa9b8;
--accent:#4ade80;
--accent2:#60a5fa;
--gradient:linear-gradient(135deg,#4ade80 0%,#60a5fa 100%);
}
body{
background:var(--bg);
color:var(--text);
font-family:'Inter',system-ui,sans-serif;
line-height:1.6;
min-height:100vh;
overflow-x:hidden;
position:relative;
}
body::before{
content:'';
position:fixed;
top:0;left:0;right:0;bottom:0;
background:
radial-gradient(circle at 20% 50%,rgba(74,222,128,.15) 0%,transparent 50%),
radial-gradient(circle at 80% 80%,rgba(96,165,250,.15) 0%,transparent 50%),
radial-gradient(circle at 40% 20%,rgba(168,85,247,.1) 0%,transparent 40%);
animation:bgMove 20s ease-in-out infinite;
z-index:0;
}
@keyframes bgMove{
0%,100%{transform:translate(0,0)}
50%{transform:translate(-20px,20px)}
}
.container{
position:relative;
z-index:1;
min-height:100vh;
display:flex;
align-items:center;
justify-content:center;
padding:24px;
}
.box{
max-width:680px;
width:100%;
background:var(--panel);
backdrop-filter:blur(20px);
border:1px solid var(--line);
border-radius:24px;
padding:48px;
box-shadow:0 20px 60px rgba(0,0,0,.5);
animation:fadeInUp .6s ease;
}
@keyframes fadeInUp{
from{opacity:0;transform:translateY(30px)}
to{opacity:1;transform:translateY(0)}
}
.logo{
display:inline-block;
padding:8px 16px;
background:var(--gradient);
border-radius:999px;
font-size:.85rem;
font-weight:600;
margin-bottom:20px;
animation:pulse 2s ease-in-out infinite;
}
@keyframes pulse{
0%,100%{opacity:1}
50%{opacity:.8}
}
h1{
font-size:2.8rem;
font-weight:800;
line-height:1.1;
margin-bottom:12px;
letter-spacing:-.02em;
}
h1 span{
background:var(--gradient);
-webkit-background-clip:text;
-webkit-text-fill-color:transparent;
background-clip:text;
}
p.sub{
color:var(--muted);
font-size:1.1rem;
margin-bottom:32px;
}
form{
display:flex;
gap:12px;
margin-bottom:28px;
}
input{
flex:1;
padding:16px 20px;
border-radius:12px;
border:1px solid var(--line);
background:rgba(255,255,255,.05);
color:var(--text);
font-size:1rem;
transition:all .3s;
}
input:focus{
outline:none;
border-color:var(--accent);
background:rgba(255,255,255,.08);
box-shadow:0 0 0 3px rgba(74,222,128,.1);
}
button{
padding:16px 28px;
border-radius:12px;
border:none;
background:var(--gradient);
color:#0a0e27;
font-weight:700;
font-size:1rem;
cursor:pointer;
transition:all .3s;
position:relative;
overflow:hidden;
}
button::before{
content:'';
position:absolute;
top:50%;left:50%;
width:0;height:0;
border-radius:50%;
background:rgba(255,255,255,.3);
transform:translate(-50%,-50%);
transition:width .6s,height .6s;
}
button:hover::before{
width:300px;height:300px;
}
button:hover{
transform:translateY(-2px);
box-shadow:0 8px 24px rgba(74,222,128,.3);
}
.features{
display:grid;
grid-template-columns:repeat(auto-fit,minmax(200px,1fr));
gap:16px;
margin-bottom:28px;
}
.feature{
background:rgba(255,255,255,.03);
border:1px solid var(--line);
border-radius:12px;
padding:16px;
transition:all .3s;
}
.feature:hover{
background:rgba(255,255,255,.06);
transform:translateY(-2px);
}
.feature-icon{
font-size:1.5rem;
margin-bottom:8px;
}
.feature-title{
font-weight:600;
font-size:.95rem;
margin-bottom:4px;
}
.feature-desc{
color:var(--muted);
font-size:.85rem;
}
footer{
padding-top:28px;
border-top:1px solid var(--line);
color:var(--muted);
font-size:.9rem;
display:flex;
gap:20px;
flex-wrap:wrap;
align-items:center;
}
footer a{
color:var(--accent);
text-decoration:none;
transition:color .2s;
cursor:pointer;
}
footer a:hover{
color:var(--accent2);
}
.toast{
position:fixed;
bottom:30px;
left:50%;
transform:translateX(-50%) translateY(100px);
background:var(--gradient);
color:#0a0e27;
padding:14px 28px;
border-radius:12px;
font-weight:700;
font-size:.95rem;
box-shadow:0 8px 32px rgba(74,222,128,.4);
transition:transform .3s ease;
z-index:9999;
}
.toast.show{
transform:translateX(-50%) translateY(0);
}
@media(max-width:640px){
.box{padding:32px 24px}
h1{font-size:2rem}
form{flex-direction:column}
button{width:100%}
}
</style>
</head>
<body>
<div class="container">
<div class="box">
<div class="logo">🩺 Free Tool</div>
<h1>Website Health <span>Check</span></h1>
<p class="sub">Get an instant professional audit of any website — speed, mobile, SEO & security issues revealed in seconds.</p>
<form action="/api/check" method="POST" id="checkForm">
<input type="text" name="url" placeholder="https://yourbusiness.com" required id="urlInput">
<button type="submit" id="submitBtn">Scan Website</button>
</form>
<div class="features">
<div class="feature">
<div class="feature-icon">⚡</div>
<div class="feature-title">Speed Test</div>
<div class="feature-desc">Load time & page weight analysis</div>
</div>
<div class="feature">
<div class="feature-icon">🔒</div>
<div class="feature-title">Security Check</div>
<div class="feature-desc">SSL certificate & HTTPS validation</div>
</div>
<div class="feature">
<div class="feature-icon">📱</div>
<div class="feature-title">Mobile Ready</div>
<div class="feature-desc">Responsive design verification</div>
</div>
<div class="feature">
<div class="feature-icon">🔍</div>
<div class="feature-title">SEO Audit</div>
<div class="feature-desc">Title, meta tags, headings check</div>
</div>
</div>
<footer>
<span>Built by <strong>Nikhil</strong></span>
<a href="https://imnick009.github.io" target="_blank">Portfolio</a>
<a href="https://github.com/imnick009" target="_blank">GitHub</a>
<a href="#" onclick="copyEmail(event)">osmnick999@gmail.com</a>
</footer>
</div>
</div>
<div class="toast" id="toast">✓ Email copied to clipboard!</div>
<script>
function copyEmail(e) {
e.preventDefault();
const email = 'osmnick999@gmail.com';
navigator.clipboard.writeText(email).then(() => {
const toast = document.getElementById('toast');
toast.classList.add('show');
setTimeout(() => toast.classList.remove('show'), 2500);
});
}
document.getElementById('checkForm').addEventListener('submit', function(e) {
const btn = document.getElementById('submitBtn');
const input = document.getElementById('urlInput');
if (!input.value.trim()) {
e.preventDefault();
return;
}
btn.innerHTML = '<span style="display:inline-block;animation:spin 1s linear infinite;">⏳</span> Scanning...';
btn.disabled = true;
btn.style.opacity = '.7';
});
</script>
</body>
</html>"""

CSS="""
*{margin:0;padding:0;box-sizing:border-box}
:root{
--bg:#0a0e27;
--panel:rgba(16,24,32,.85);
--line:rgba(255,255,255,.08);
--text:#e6edf3;
--muted:#9aa9b8;
--accent:#4ade80;
--accent2:#60a5fa;
--danger:#f87171;
--warning:#fbbf24;
--gradient:linear-gradient(135deg,#4ade80 0%,#60a5fa 100%);
}
body{
background:var(--bg);
color:var(--text);
font-family:'Inter',system-ui,sans-serif;
line-height:1.6;
min-height:100vh;
padding:32px 24px;
}
body::before{
content:'';
position:fixed;
top:0;left:0;right:0;bottom:0;
background:
radial-gradient(circle at 20% 50%,rgba(74,222,128,.15) 0%,transparent 50%),
radial-gradient(circle at 80% 80%,rgba(96,165,250,.15) 0%,transparent 50%);
z-index:0;
}
.wrap{
max-width:800px;
margin:0 auto;
position:relative;
z-index:1;
animation:fadeIn .5s ease;
}
@keyframes fadeIn{
from{opacity:0}
to{opacity:1}
}
@keyframes slideUp{
from{opacity:0;transform:translateY(20px)}
to{opacity:1;transform:translateY(0)}
}
.back{
display:inline-flex;
align-items:center;
gap:6px;
color:var(--muted);
text-decoration:none;
font-size:.9rem;
margin-bottom:20px;
transition:color .2s;
}
.back:hover{color:var(--accent)}
h1{
font-size:2rem;
font-weight:800;
margin-bottom:8px;
letter-spacing:-.02em;
}
h1 span{
background:var(--gradient);
-webkit-background-clip:text;
-webkit-text-fill-color:transparent;
background-clip:text;
}
.url-display{
color:var(--muted);
font-size:.95rem;
margin-bottom:24px;
word-break:break-all;
}
.score-card{
background:var(--panel);
backdrop-filter:blur(20px);
border:1px solid var(--line);
border-radius:20px;
padding:32px;
margin-bottom:28px;
text-align:center;
animation:slideUp .5s ease .1s both;
}
.score-number{
font-size:5rem;
font-weight:800;
line-height:1;
margin-bottom:8px;
background:var(--gradient);
-webkit-background-clip:text;
-webkit-text-fill-color:transparent;
background-clip:text;
}
.score-label{
font-size:1.1rem;
color:var(--muted);
margin-bottom:16px;
}
.progress-bar{
height:8px;
background:rgba(255,255,255,.1);
border-radius:999px;
overflow:hidden;
max-width:400px;
margin:0 auto;
}
.progress-fill{
height:100%;
background:var(--gradient);
border-radius:999px;
transition:width 1s ease;
animation:progressGrow 1s ease;
}
@keyframes progressGrow{
from{width:0}
}
.section-title{
font-size:1.3rem;
font-weight:700;
margin-bottom:16px;
display:flex;
align-items:center;
gap:10px;
}
.row{
background:var(--panel);
backdrop-filter:blur(20px);
border:1px solid var(--line);
border-radius:14px;
padding:20px;
margin-bottom:12px;
transition:all .3s;
animation:slideUp .5s ease both;
}
.row:hover{
border-color:rgba(255,255,255,.15);
transform:translateX(4px);
}
.row-header{
display:flex;
align-items:start;
gap:12px;
margin-bottom:8px;
}
.row-icon{
font-size:1.5rem;
flex-shrink:0;
}
.row-content{flex:1}
.row-name{
font-weight:700;
font-size:1.05rem;
margin-bottom:4px;
}
.row-detail{
color:var(--muted);
font-size:.92rem;
word-break:break-word;
}
.row-fix{
margin-top:12px;
padding:12px 16px;
background:rgba(74,222,128,.1);
border-left:3px solid var(--accent);
border-radius:8px;
font-size:.9rem;
color:var(--text);
}
.row-fail .row-fix{
background:rgba(248,113,113,.1);
border-left-color:var(--danger);
}
.cta{
background:var(--panel);
backdrop-filter:blur(20px);
border:1px solid var(--line);
border-radius:20px;
padding:36px;
margin-top:32px;
text-align:center;
animation:slideUp .5s ease .3s both;
}
.cta h2{
font-size:1.5rem;
font-weight:700;
margin-bottom:12px;
}
.cta p{
color:var(--muted);
margin-bottom:20px;
}
.cta-links{
display:flex;
gap:16px;
justify-content:center;
flex-wrap:wrap;
align-items:center;
}
.cta-links a{
color:var(--accent);
text-decoration:none;
font-weight:600;
transition:color .2s;
cursor:pointer;
}
.cta-links a:hover{
color:var(--accent2);
}
.cta-links a.email-btn{
display:inline-block;
padding:14px 32px;
border-radius:12px;
background:var(--gradient);
color:#0a0e27;
font-weight:700;
font-size:1rem;
box-shadow:0 4px 16px rgba(74,222,128,.25);
transition:all .3s;
}
.cta-links a.email-btn:hover{
transform:translateY(-2px);
box-shadow:0 8px 24px rgba(74,222,128,.4);
color:#0a0e27;
}
.toast{
position:fixed;
bottom:30px;
left:50%;
transform:translateX(-50%) translateY(100px);
background:var(--gradient);
color:#0a0e27;
padding:14px 28px;
border-radius:12px;
font-weight:700;
font-size:.95rem;
box-shadow:0 8px 32px rgba(74,222,128,.4);
transition:transform .3s ease;
z-index:9999;
}
.toast.show{
transform:translateX(-50%) translateY(0);
}
@keyframes spin{
to{transform:rotate(360deg)}
}
@media(max-width:640px){
.score-number{font-size:4rem}
.row{padding:16px}
}
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
                       "Compress images, enable caching, use a CDN.",
                       "⚡"))
        checks.append(("HTTPS / SSL Security", final_url.startswith("https"),
                       "Secure" if final_url.startswith("https") else "NOT secure",
                       "Install a free SSL certificate (Let's Encrypt / Cloudflare).",
                       "🔒"))
        vp = soup.find("meta", attrs={"name": "viewport"}) is not None
        checks.append(("Mobile Friendly", vp,
                       "Viewport set" if vp else "No viewport tag",
                       "Add mobile viewport meta tag + responsive theme.",
                       "📱"))
        title = soup.title.string.strip() if soup.title and soup.title.string else ""
        checks.append(("Page Title (SEO)", len(title) >= 10,
                       title or "Missing",
                       "Write a 30-60 character title with your main keyword.",
                       "🏷️"))
        m = soup.find("meta", attrs={"name": "description"})
        desc = m.get("content", "") if m and m.get("content") else ""
        checks.append(("Meta Description (SEO)", len(desc) >= 50,
                       (desc[:60] + "...") if desc else "Missing",
                       "Add a 120-160 char description - this is what Google shows.",
                       "📝"))
        h1 = soup.find("h1")
        checks.append(("H1 Heading", h1 is not None,
                       h1.get_text(strip=True)[:60] if h1 else "Missing",
                       "Use exactly one H1 that states what the page is about.",
                       "📋"))
        imgs = soup.find_all("img")
        no_alt = [i for i in imgs if not i.get("alt")]
        checks.append(("Image Alt Tags", len(no_alt) == 0,
                       f"{len(no_alt)}/{len(imgs)} images missing alt",
                       "Add alt text to every image (SEO + accessibility).",
                       "🖼️"))
        kb = round(len(r.content) / 1024)
        checks.append(("Page Weight", kb <= 1500, f"{kb} KB",
                       "Compress images & remove unused scripts.",
                       "📦"))
        return checks, None
    except Exception as e:
        return None, str(e)

def _pdf_text(value):
    text = str(value)
    fancy = {
        "\u2013": "-", "\u2014": "-", "\u2015": "-",
        "\u2018": "'", "\u2019": "'",
        "\u201c": '"', "\u201d": '"',
        "\u2026": "...", "\u00a0": " ", "\u20b9": "Rs ",
    }
    for old, new in fancy.items():
        text = text.replace(old, new)
    return text.encode("latin-1", "replace").decode("latin-1")

def report_html(u, checks):
    passed = sum(1 for c in checks if c[1])
    score = round(passed / len(checks) * 100)
    rows = ""
    for i, (name, ok, detail, fix, icon) in enumerate(checks):
        status_class = "" if ok else "row-fail"
        status_icon = "✅" if ok else "❌"
        fix_html = f'<div class="row-fix">🔧 <strong>Fix:</strong> {fix}</div>' if not ok else ""
        rows += f"""
<div class="row {status_class}" style="animation-delay:{.15+i*.05}s">
<div class="row-header">
<div class="row-icon">{icon}</div>
<div class="row-content">
<div class="row-name">{status_icon}{name}</div>
<div class="row-detail">{detail}</div>
{fix_html}
</div>
</div>
</div>"""
    safe_u = urllib.parse.quote(u)
    return f"""<!DOCTYPE html>
<html><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<title>SiteCheck Report</title><style>{CSS}</style></head>
<body><div class="wrap">
<a class="back" href="/">← Scan another website</a>
<h1>🩺 Site<span>Check</span> Report</h1>
<div class="url-display">Scanned: {u}</div>
<div class="score-card">
<div class="score-number">{score}</div>
<div class="score-label">Health Score</div>
<div class="progress-bar">
<div class="progress-fill" style="width:{score}%"></div>
</div>
</div>
<div class="section-title">📊 Detailed Analysis</div>
{rows}
<div class="cta">
<h2>Want these issues fixed for you?</h2>
<p>I fix exactly these problems for businesses in 2-4 days, fixed price. No surprises.</p>
<div class="cta-links">
<a href="/download-pdf?site={safe_u}" target="_blank" class="email-btn" style="background: linear-gradient(135deg, #60a5fa 0%, #4ade80 100%);">📥 Download PDF Report</a>
<a href="#" class="email-btn" onclick="copyEmail(event)">osmnick999@gmail.com</a>
<a href="https://imnick009.github.io" target="_blank">🌐 Portfolio</a>
<a href="https://github.com/imnick009" target="_blank">🐙 GitHub</a>
</div>
</div>
<div class="toast" id="toast">✓ Email copied to clipboard!</div>
<script>
function copyEmail(e) {{
e.preventDefault();
const email = 'osmnick999@gmail.com';
navigator.clipboard.writeText(email).then(() => {{
const toast = document.getElementById('toast');
toast.classList.add('show');
setTimeout(() => toast.classList.remove('show'), 2500);
}});
}}
</script>
</div></body></html>"""

def error_html(msg):
    return f"""<!DOCTYPE html>
<html><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<style>{CSS}</style></head>
<body><div class="wrap">
<a class="back" href="/">← Try again</a>
<h1>🩺 Site<span>Check</span></h1>
<div class="row row-fail">
<div class="row-header">
<div class="row-icon">❌</div>
<div class="row-content">
<div class="row-name">Could not scan this website</div>
<div class="row-detail">{msg}</div>
<div class="row-fix">Please check the URL and try again. Make sure the website is publicly accessible.</div>
</div>
</div>
</div>
</div></body></html>"""

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

@app.route("/download-pdf")
@app.route("/download-pdf")
def download_pdf():
    url = request.args.get("site", "").strip()
    if not url:
        return "No URL provided", 400

    u = url if url.startswith("http") else "https://" + url
    checks, err = audit(u)
    if err:
        return f"Error scanning site: {err}", 500

    passed = sum(1 for c in checks if c[1])
    score = round(passed / len(checks) * 100) if checks else 0

    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)

        left = pdf.l_margin
        full = pdf.w - pdf.l_margin - pdf.r_margin

        # Header
        pdf.set_x(left)
        pdf.set_font("Helvetica", "B", 22)
        pdf.set_text_color(20, 120, 80)
        pdf.cell(full, 12, "SiteCheck Health Report", align="C")
        pdf.ln(12)

        pdf.set_x(left)
        pdf.set_font("Helvetica", "", 11)
        pdf.set_text_color(110, 110, 110)
        pdf.cell(full, 8, _pdf_text("Generated for: " + u), align="C")
        pdf.ln(8)
        pdf.ln(4)

        # Score
        if score >= 70:
            color = (20, 130, 80)
        elif score >= 40:
            color = (190, 130, 20)
        else:
            color = (200, 60, 60)
        pdf.set_x(left)
        pdf.set_font("Helvetica", "B", 18)
        pdf.set_text_color(*color)
        pdf.cell(full, 12, "Overall Health Score: " + str(score) + "/100", align="C")
        pdf.ln(12)
        pdf.ln(4)

        # Details
        pdf.set_x(left)
        pdf.set_font("Helvetica", "B", 14)
        pdf.set_text_color(0, 0, 0)
        pdf.cell(full, 10, "Detailed Analysis & Fixes")
        pdf.ln(10)
        pdf.ln(2)

        for name, ok, detail, fix, icon in checks:
            status = "PASS" if ok else "FAIL"

            pdf.set_x(left)
            pdf.set_font("Helvetica", "B", 12)
            if ok:
                pdf.set_text_color(20, 130, 80)
            else:
                pdf.set_text_color(200, 60, 60)
            pdf.cell(18, 8, "[" + status + "]")
            pdf.set_text_color(0, 0, 0)
            pdf.cell(full - 18, 8, _pdf_text(name))
            pdf.ln(8)

            pdf.set_x(left)
            pdf.set_font("Helvetica", "", 10)
            pdf.set_text_color(90, 90, 90)
            pdf.multi_cell(full, 5, _pdf_text("Status: " + str(detail)))

            if not ok:
                pdf.set_x(left)
                pdf.set_text_color(40, 60, 180)
                pdf.multi_cell(full, 5, _pdf_text("Fix: " + str(fix)))

            pdf.set_x(left)
            pdf.ln(3)

        # Footer CTA
        pdf.set_x(left)
        pdf.ln(4)
        pdf.set_font("Helvetica", "B", 13)
        pdf.set_text_color(0, 0, 0)
        pdf.cell(full, 9, "Want these issues fixed?")
        pdf.ln(9)

        pdf.set_x(left)
        pdf.set_font("Helvetica", "", 11)
        pdf.cell(full, 7, "Contact Nikhil to fix these problems for your business.")
        pdf.ln(7)

        pdf.set_x(left)
        pdf.set_font("Helvetica", "B", 11)
        pdf.set_text_color(20, 120, 80)
        pdf.cell(full, 7, "Email: osmnick999@gmail.com")
        pdf.ln(7)

        pdf_bytes = pdf.output()

        safe_filename = u.replace("https://", "").replace("http://", "").replace("/", "_").replace(":", "")
        if not safe_filename:
            safe_filename = "website"

        return send_file(
            io.BytesIO(pdf_bytes),
            mimetype="application/pdf",
            as_attachment=True,
            download_name="SiteCheck_" + safe_filename + ".pdf",
        )
    except Exception as e:
        return "PDF generation error: " + str(e), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
