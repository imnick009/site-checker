# 🩺 SiteCheck — Free Website Health Checker

**🔴 Live Demo:** [https://site-checker-bav1.vercel.app](https://site-checker-bav1.vercel.app)

SiteCheck is a free, instant website audit tool. Enter any URL and get a professional health report covering speed, security, mobile-friendliness and SEO — in seconds.

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-2.x-green.svg)
![License](https://img.shields.io/badge/license-MIT-lightgrey.svg)

---

## ✨ Features

- ⚡ **Speed Test** — page load time & page weight analysis
- 🔒 **Security Check** — SSL / HTTPS validation
- 📱 **Mobile Ready** — responsive design (viewport) verification
- 🔍 **SEO Audit** — title, meta description, H1 heading, image alt tags
- 📊 **Health Score** — 0–100 score with plain-English fix suggestions

Every report ends with actionable fixes — not just problems.

---

## 🛠️ Tech Stack

| Layer     | Technology                        |
|-----------|-----------------------------------|
| Backend   | Python + Flask                    |
| Scraping  | Requests + BeautifulSoup          |
| Frontend  | Hand-written HTML/CSS (no frameworks) |
| Hosting   | Vercel (serverless)               |

---

## 🚀 Run Locally

```bash
git clone https://github.com/imnick009/site-checker.git
cd site-checker
python3 -m venv venv
venv/bin/pip install -r requirements.txt
venv/bin/python app.py
