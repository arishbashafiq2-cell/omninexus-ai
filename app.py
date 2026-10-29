import os
import re
import json
import time
import hmac
import base64
import hashlib
import secrets
import smtplib
import urllib.parse
from datetime import datetime, timezone, timedelta
from email.message import EmailMessage

import requests
import pandas as pd
import plotly.express as px
import streamlit as st
import streamlit.components.v1 as components

# ============================================================
# OmniNexus AI — Streamlit application
# Environment variables are configured in Streamlit Cloud Secrets.
# ============================================================

APP_NAME = "OmniNexus AI"
SUPABASE_URL = os.getenv("SUPABASE_URL", "").rstrip("/")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_EMAIL = os.getenv("SMTP_EMAIL", "")
SMTP_APP_PASSWORD = os.getenv("SMTP_APP_PASSWORD", "")
OTP_TTL_MINUTES = 10
MAX_OTP_ATTEMPTS = 5

st.set_page_config(
    page_title=f"{APP_NAME} | Intelligence, reimagined",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------- Styling ----------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Manrope:wght@400;500;600;700;800&display=swap');
:root { --bg:#080b14; --panel:#101522; --panel2:#141a2b; --line:rgba(154,170,220,.15);
        --muted:#929bb5; --text:#f4f6ff; --violet:#9b87ff; --cyan:#64e6e2; }
html, body, [class*="css"] { font-family:'Manrope',sans-serif; }
.stApp { background:
 radial-gradient(ellipse at 12% 0%, rgba(112,83,255,.13), transparent 33%),
 radial-gradient(ellipse at 90% 12%, rgba(47,218,210,.07), transparent 27%), var(--bg);
 color:var(--text); }
[data-testid="stHeader"] { background:rgba(8,11,20,.72); backdrop-filter:blur(16px); }
[data-testid="stSidebar"] { background:linear-gradient(180deg,#0d1120,#0a0e18); border-right:1px solid var(--line); }
[data-testid="stSidebar"] > div:first-child { padding-top:1.2rem; }
h1,h2,h3 { letter-spacing:-.04em !important; color:var(--text) !important; }
p, label, .stMarkdown { color:#dce1f4; }
small, .muted { color:var(--muted); }
.brand { display:flex; align-items:center; gap:12px; margin:5px 0 26px; }
.brand-icon { width:42px;height:42px;border-radius:14px; display:grid;place-items:center;
 background:linear-gradient(135deg,#9a7bff,#56deda); color:#101322;font-size:23px;font-weight:900;
 box-shadow:0 0 28px rgba(139,112,255,.25); }
.brand-name { font-size:18px;font-weight:800;letter-spacing:-.7px;color:#f7f7ff; }
.brand-sub { font:10px 'DM Mono'; letter-spacing:2px;color:#929bb5;text-transform:uppercase; }
.eyebrow { color:var(--cyan); font:11px 'DM Mono',monospace; text-transform:uppercase; letter-spacing:2.3px; }
.hero-title { font-size:clamp(2.3rem,5vw,4.5rem); line-height:1.03; font-weight:800; letter-spacing:-.07em;
 background:linear-gradient(100deg,#fff 12%,#c9c0ff 54%,#73e9e1);-webkit-background-clip:text;-webkit-text-fill-color:transparent; }
.hero-copy { color:#aab3cd; max-width:760px; font-size:1.05rem; line-height:1.8; }
.glass { background:linear-gradient(145deg,rgba(22,28,47,.91),rgba(13,17,30,.88));
 border:1px solid var(--line); border-radius:22px; padding:22px; box-shadow:0 18px 65px rgba(0,0,0,.12); }
.metric { background:linear-gradient(145deg,rgba(24,31,52,.88),rgba(13,17,30,.8));border:1px solid var(--line);
 border-radius:18px;padding:18px 20px; transition:transform .2s,border-color .2s; }
.metric:hover { transform:translateY(-3px);border-color:rgba(155,135,255,.5); }
.metric-label { font-size:11px;color:#9ca6c3;text-transform:uppercase;letter-spacing:1.5px; }
.metric-value { font-size:28px;font-weight:800;letter-spacing:-1.5px;color:#fff;margin-top:6px; }
.metric-note { font-size:11px;color:#75ded6;margin-top:4px; }
.pill { display:inline-block;padding:6px 10px;border-radius:99px;border:1px solid rgba(100,230,226,.23);
 color:#8ef2e7;background:rgba(100,230,226,.06);font:10px 'DM Mono';letter-spacing:1px; }
hr { border-color:var(--line) !important; }
.stButton > button, .stDownloadButton > button { border-radius:12px; border:1px solid rgba(155,135,255,.42);
 background:linear-gradient(115deg,rgba(132,105,255,.25),rgba(83,215,213,.13));color:#fff;font-weight:700;
 min-height:42px;transition:all .18s ease; }
.stButton > button:hover, .stDownloadButton > button:hover { border-color:var(--cyan);transform:translateY(-1px);
 box-shadow:0 8px 24px rgba(90,215,216,.1); }
.stTextInput input, .stTextArea textarea, .stNumberInput input, .stSelectbox [data-baseweb="select"] {
 background:#0b1020 !important;border:1px solid rgba(154,170,220,.22) !important;border-radius:11px !important;color:#fff !important; }
[data-testid="stChatMessage"] { background:rgba(17,22,38,.78);border:1px solid var(--line);border-radius:16px; }
div[data-testid="stMetric"] { background:#111729;border:1px solid var(--line);padding:15px;border-radius:16px; }
.stTabs [data-baseweb="tab-list"] { gap:8px; background:transparent; }
.stTabs [data-baseweb="tab"] { border-radius:10px; padding:9px 15px; }
.stTabs [aria-selected="true"] { background:rgba(155,135,255,.16); }
div[data-testid="stAlert"] { border-radius:14px; }
footer {visibility:hidden;}
@keyframes floatGlow { 0%,100%{transform:translateY(0)} 50%{transform:translateY(-5px)} }
.float-icon { animation:floatGlow 4s ease-in-out infinite;display:inline-block; }
@media(max-width:700px){ .glass{padding:16px}.hero-title{font-size:2.5rem}.metric-value{font-size:23px} }
</style>
""", unsafe_allow_html=True)

# ------------------------- Session state -------------------------
defaults = {
    "authenticated": False, "user": None, "pending_email": None,
    "auth_mode": "Login", "page": "Overview", "chat_history": [],
    "activity_log": [], "otp_attempts": 0, "last_otp_sent": 0,
    "image_result": None, "last_summary": "",
}
for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

# ------------------------- Utility functions -------------------------
def utc_now():
    return datetime.now(timezone.utc)

def iso_after(minutes):
    return (utc_now() + timedelta(minutes=minutes)).isoformat()

def valid_email(email):
    return bool(re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email.strip()))

def password_hash(password, salt=None):
    salt = salt or secrets.token_bytes(16)
    digest = hashlib.scrypt(password.encode("utf-8"), salt=salt, n=2**14, r=8, p=1, dklen=32)
    return base64.b64encode(salt).decode() + "$" + base64.b64encode(digest).decode()

def verify_password(password, stored):
    try:
        salt_b64, digest_b64 = stored.split("$", 1)
        salt = base64.b64decode(salt_b64)
        expected = base64.b64decode(digest_b64)
        actual = hashlib.scrypt(password.encode("utf-8"), salt=salt, n=2**14, r=8, p=1, dklen=32)
        return hmac.compare_digest(actual, expected)
    except Exception:
        return False

def otp_hash(code, email):
    secret = os.getenv("OTP_PEPPER", "")
    return hashlib.sha256(f"{secret}:{email.lower()}:{code}".encode()).hexdigest()

def db_ready():
    return bool(SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY)

def db_request(method, table, params=None, payload=None, prefer=None):
    if not db_ready():
        raise RuntimeError("Persistent account storage is not configured. Add SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY in Streamlit Secrets.")
    url = f"{SUPABASE_URL}/rest/v1/{table}"
    headers = {
        "apikey": SUPABASE_SERVICE_ROLE_KEY,
        "Authorization": f"Bearer {SUPABASE_SERVICE_ROLE_KEY}",
        "Content-Type": "application/json",
    }
    if prefer:
        headers["Prefer"] = prefer
    response = requests.request(method, url, headers=headers, params=params, json=payload, timeout=20)
    if response.status_code >= 400:
        detail = response.text[:400]
        raise RuntimeError(f"Database request failed ({response.status_code}): {detail}")
    if not response.text.strip():
        return []
    return response.json()

def get_user(email):
    rows = db_request("GET", "nexus_users", {"email": f"eq.{email.lower()}", "select": "*", "limit": "1"})
    return rows[0] if rows else None

def save_user(row):
    return db_request("POST", "nexus_users", {"on_conflict": "email"}, row, "resolution=merge-duplicates,return=representation")

def send_otp_email(email, code, purpose):
    if not (SMTP_EMAIL and SMTP_APP_PASSWORD):
        raise RuntimeError("Email delivery is not configured. Set SMTP_EMAIL and SMTP_APP_PASSWORD in Streamlit Secrets.")
    message = EmailMessage()
    message["Subject"] = f"{APP_NAME} verification code"
    message["From"] = f"{APP_NAME} <{SMTP_EMAIL}>"
    message["To"] = email
    message.set_content(
        f"Your {APP_NAME} verification code is: {code}\n\n"
        f"Purpose: {purpose}\nThis code expires in {OTP_TTL_MINUTES} minutes.\n"
        "If you did not request this code, you can ignore this email."
    )
    with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=20) as server:
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(SMTP_EMAIL, SMTP_APP_PASSWORD)
        server.send_message(message)

def create_and_send_otp(email, purpose):
    now = time.time()
    if now - st.session_state.last_otp_sent < 30:
        raise RuntimeError("Please wait 30 seconds before requesting another code.")
    code = f"{secrets.randbelow(1_000_000):06d}"
    user = get_user(email)
    if purpose == "registration" and user:
        raise RuntimeError("An account with this email already exists. Please log in.")
    if purpose == "login" and not user:
        raise RuntimeError("No account found for this email. Please create an account first.")
    if purpose == "login" and not user.get("email_verified", False):
        raise RuntimeError("This email is not verified yet. Choose Sign up to complete verification.")
    send_otp_email(email, code, purpose)
    if purpose == "registration":
        row = {
            "email": email.lower(),
            "password_hash": st.session_state.pending_password_hash,
            "display_name": st.session_state.pending_name,
            "email_verified": False,
            "otp_hash": otp_hash(code, email),
            "otp_expires_at": iso_after(OTP_TTL_MINUTES),
            "otp_purpose": purpose,
            "otp_attempts": 0,
            "updated_at": utc_now().isoformat(),
        }
        save_user(row)
    else:
        db_request("PATCH", "nexus_users", {"email": f"eq.{email.lower()}"}, {
            "otp_hash": otp_hash(code, email),
            "otp_expires_at": iso_after(OTP_TTL_MINUTES),
            "otp_purpose": purpose,
            "otp_attempts": 0,
            "updated_at": utc_now().isoformat(),
        }, "return=minimal")
    st.session_state.pending_email = email.lower()
    st.session_state.last_otp_sent = now
    st.session_state.otp_attempts = 0

def record_activity(label, detail=""):
    st.session_state.activity_log.append({
        "time": utc_now().strftime("%Y-%m-%d %H:%M UTC"),
        "activity": label,
        "details": detail[:160],
    })
    st.session_state.activity_log = st.session_state.activity_log[-100:]

def verify_otp(email, code):
    user = get_user(email)
    if not user or not user.get("otp_hash"):
        return False, "No active verification request. Request a new code."
    if int(user.get("otp_attempts") or 0) >= MAX_OTP_ATTEMPTS:
        return False, "Too many incorrect attempts. Request a new code after the cooldown."
    try:
        expiry = datetime.fromisoformat(user["otp_expires_at"].replace("Z", "+00:00"))
        if expiry.tzinfo is None:
            expiry = expiry.replace(tzinfo=timezone.utc)
    except Exception:
        return False, "Verification code expired. Request a new one."
    if utc_now() > expiry:
        return False, "Verification code expired. Request a new one."
    expected = user["otp_hash"]
    if not hmac.compare_digest(expected, otp_hash(code, email)):
        db_request("PATCH", "nexus_users", {"email": f"eq.{email}"}, {"otp_attempts": int(user.get("otp_attempts") or 0) + 1}, "return=minimal")
        return False, "Incorrect code. Check the email and try again."
    db_request("PATCH", "nexus_users", {"email": f"eq.{email}"}, {
        "email_verified": True,
        "otp_hash": None,
        "otp_expires_at": None,
        "otp_purpose": None,
        "otp_attempts": 0,
        "updated_at": utc_now().isoformat(),
    }, "return=minimal")
    fresh = get_user(email)
    st.session_state.authenticated = True
    st.session_state.user = {"email": fresh["email"], "name": fresh.get("display_name") or email.split("@")[0]}
    st.session_state.pending_email = None
    record_activity("Secure sign-in", "Email verification completed")
    return True, "Verified successfully."

def groq_chat(messages, system_prompt=None, temperature=0.7):
    if not GROQ_API_KEY:
        raise RuntimeError("AI chat is not configured. Add GROQ_API_KEY to Streamlit Secrets.")
    payload_messages = []
    if system_prompt:
        payload_messages.append({"role": "system", "content": system_prompt})
    payload_messages.extend(messages)
    response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"},
        json={"model": GROQ_MODEL, "messages": payload_messages, "temperature": temperature, "max_tokens": 1800},
        timeout=90,
    )
    if response.status_code >= 400:
        raise RuntimeError(f"AI provider error ({response.status_code}): {response.text[:350]}")
    return response.json()["choices"][0]["message"]["content"]

def generate_image(prompt, width=1024, height=1024):
    # Pollinations image endpoint; no API key is required by this public endpoint.
    encoded = urllib.parse.quote(prompt[:900], safe="")
    seed = secrets.randbelow(2_000_000_000)
    url = f"https://image.pollinations.ai/prompt/{encoded}?width={width}&height={height}&seed={seed}&nologo=true"
    response = requests.get(url, timeout=120)
    response.raise_for_status()
    if not response.headers.get("content-type", "").startswith("image/"):
        raise RuntimeError("Image provider did not return an image. Try a simpler prompt.")
    return response.content

def audio_component(text, key):
    safe_text = json.dumps(text[:5000])
    components.html(f"""
    <div style="font-family:Arial;color:#dfe5ff;background:#111729;border:1px solid #303650;padding:12px;border-radius:12px">
      <div style="font-size:12px;opacity:.75;margin-bottom:8px">VOICE PLAYBACK · uses your browser's speech engine</div>
      <button id="speak-{key}" style="cursor:pointer;border:1px solid #8274e8;border-radius:9px;padding:8px 12px;background:#272447;color:white">▶ Play response</button>
      <button id="stop-{key}" style="cursor:pointer;border:1px solid #414862;border-radius:9px;padding:8px 12px;background:#171d2e;color:white">■ Stop</button>
      <script>
        const text = {safe_text};
        const speak = document.getElementById("speak-{key}");
        const stop = document.getElementById("stop-{key}");
        speak.onclick = () => {{ if (!("speechSynthesis" in window)) {{ alert("Speech playback is not supported by this browser."); return; }}
          window.speechSynthesis.cancel(); const u = new SpeechSynthesisUtterance(text); u.rate=1; window.speechSynthesis.speak(u); }};
        stop.onclick = () => window.speechSynthesis.cancel();
      </script>
    </div>
    """, height=80)

def speech_input_component(key):
    result = components.html(f"""
    <div style="font-family:Arial;color:#e7eaff;background:#111729;border:1px solid #303650;padding:14px;border-radius:13px">
      <div style="font-size:12px;letter-spacing:1px;color:#83e6df;margin-bottom:9px">VOICE INPUT · SPEECH TO TEXT</div>
      <button id="start-{key}" style="cursor:pointer;border:1px solid #8274e8;border-radius:9px;padding:9px 13px;background:#272447;color:white">🎙 Start listening</button>
      <span id="status-{key}" style="font-size:12px;margin-left:10px;color:#aab3cd">Ready</span>
      <div id="result-{key}" style="margin-top:10px;line-height:1.5;word-break:break-word"></div>
      <script>
        const btn=document.getElementById("start-{key}"), status=document.getElementById("status-{key}"), out=document.getElementById("result-{key}");
        const SR=window.SpeechRecognition||window.webkitSpeechRecognition;
        btn.onclick=()=>{{ if(!SR){{status.textContent="Speech recognition unavailable. Try Chrome over HTTPS.";return;}}
          const r=new SR(); r.lang="en-US";r.interimResults=true;r.continuous=false;status.textContent="Listening…";
          r.onresult=(e)=>{{let t="";for(let i=e.resultIndex;i<e.results.length;i++)t+=e.results[i][0].transcript;out.textContent=t;out.dataset.final=t;}};
          r.onerror=(e)=>status.textContent="Microphone error: "+e.error;
          r.onend=()=>{{status.textContent="Finished. Copy the recognized text into the chat box below."; }};
          r.start(); }};
      </script>
      <div style="font-size:11px;color:#8d97b2;margin-top:8px">Browser support and microphone permission are required. Paste the recognized text into the chat input.</div>
    </div>
    """, height=175, key=key)
    return result

# ----------------------------- Sidebar -----------------------------
def render_sidebar():
    with st.sidebar:
        st.markdown(f"""<div class="brand"><div class="brand-icon">✦</div><div><div class="brand-name">OmniNexus AI</div><div class="brand-sub">INTELLIGENCE OS</div></div></div>""", unsafe_allow_html=True)
        if st.session_state.authenticated:
            user = st.session_state.user
            st.markdown(f"""<div style="padding:13px;border:1px solid rgba(154,170,220,.15);border-radius:14px;background:#111729;margin-bottom:18px">
              <div style="font-size:11px;color:#8f9ab8;letter-spacing:1px">SIGNED IN AS</div>
              <div style="font-weight:800;margin-top:5px">{user['name']}</div>
              <div style="font-size:11px;color:#8f9ab8;overflow-wrap:anywhere">{user['email']}</div>
              <div style="margin-top:9px"><span class="pill">● VERIFIED</span></div></div>""", unsafe_allow_html=True)
            pages = ["Overview", "Remix AI Hub", "Image Studio", "Executive Brief", "Productivity", "Settings"]
            current = st.session_state.page
            selected = st.radio("WORKSPACE", pages, index=pages.index(current) if current in pages else 0, label_visibility="visible")
            if selected != st.session_state.page:
                st.session_state.page = selected
                st.rerun()
            st.divider()
            st.caption("WORKSPACE STATUS")
            st.markdown('<span class="pill">● SYSTEM READY</span>', unsafe_allow_html=True)
            st.caption("Your conversations and usage metrics are stored in this browser session. Account credentials are stored in your configured database.")
            if st.button("↗  Sign out", use_container_width=True):
                st.session_state.authenticated = False
                st.session_state.user = None
                st.session_state.pending_email = None
                st.session_state.chat_history = []
                st.session_state.page = "Overview"
                st.rerun()
        else:
            st.markdown('<div class="eyebrow">PRIVATE AI WORKSPACE</div>', unsafe_allow_html=True)
            st.markdown("Your tools. One intelligent space.")
            st.markdown("---")
            st.caption("Secure access requires email verification.")
            st.markdown('<span class="pill">● ENCRYPTED PASSWORDS</span>', unsafe_allow_html=True)

# --------------------------- Authentication ---------------------------
def auth_screen():
    st.markdown('<div style="height:5vh"></div>', unsafe_allow_html=True)
    left, right = st.columns([1.15, 0.85], gap="large")
    with left:
        st.markdown('<div class="eyebrow">✦ YOUR INTELLIGENCE OPERATING SYSTEM</div>', unsafe_allow_html=True)
        st.markdown('<div class="hero-title">Think bigger.<br>Build faster.</div>', unsafe_allow_html=True)
        st.markdown('<p class="hero-copy">A unified AI workspace for conversations, creative generation, executive summaries, and personal productivity — designed for people who build what comes next.</p>', unsafe_allow_html=True)
        st.markdown('<div class="glass"><div class="eyebrow">THE NEXUS ADVANTAGE</div><br>✦ &nbsp; Context-aware AI conversations<br><br>◈ &nbsp; Prompt-to-image creative studio<br><br>⌁ &nbsp; Voice-enabled interaction<br><br>⟡ &nbsp; Insightful productivity analytics<br><br>◉ &nbsp; Email-verified account access</div>', unsafe_allow_html=True)
    with right:
        st.markdown('<div class="glass">', unsafe_allow_html=True)
        if st.session_state.pending_email:
            st.markdown("### Verify your email")
            st.write(f"Enter the 6-digit code sent to **{st.session_state.pending_email}**.")
            with st.form("otp_form", clear_on_submit=False):
                otp = st.text_input("6-digit verification code", max_chars=6, placeholder="000000")
                submitted = st.form_submit_button("Verify & enter workspace", use_container_width=True)
            if submitted:
                if not re.fullmatch(r"\d{6}", otp.strip()):
                    st.error("Enter exactly six digits.")
                else:
                    try:
                        ok, message = verify_otp(st.session_state.pending_email, otp.strip())
                        if ok:
                            st.success(message)
                            st.rerun()
                        else:
                            st.error(message)
                    except Exception as exc:
                        st.error(str(exc))
            if st.button("Send a new code", use_container_width=True):
                try:
                    email = st.session_state.pending_email
                    user = get_user(email)
                    purpose = "registration" if user and not user.get("email_verified") else "login"
                    create_and_send_otp(email, purpose)
                    st.success("A new code has been sent.")
                except Exception as exc:
                    st.error(str(exc))
            if st.button("Back to sign in", use_container_width=True):
                st.session_state.pending_email = None
                st.rerun()
        else:
            st.markdown("### Welcome to your Nexus")
            st.caption("Your next idea starts here.")
            mode = st.segmented_control("Choose access", options=["Login", "Sign up"], default=st.session_state.auth_mode, key="auth_mode_selector")
            if mode:
                st.session_state.auth_mode = mode
            with st.form("auth_form", clear_on_submit=False):
                name = st.text_input("Full name", placeholder="Your name") if st.session_state.auth_mode == "Sign up" else None
                email = st.text_input("Email address", placeholder="you@example.com")
                password = st.text_input("Password", type="password", placeholder="At least 10 characters")
                if st.session_state.auth_mode == "Sign up":
                    confirm = st.text_input("Confirm password", type="password")
                    agree = st.checkbox("I understand this is an AI workspace and agree to use it responsibly.")
                else:
                    confirm, agree = "", True
                submitted = st.form_submit_button("Continue securely →", use_container_width=True)
            if submitted:
                email = email.strip().lower()
                if not valid_email(email):
                    st.error("Enter a valid email address.")
                elif len(password) < 10:
                    st.error("Use a password with at least 10 characters.")
                elif st.session_state.auth_mode == "Sign up" and (password != confirm or not agree or not name.strip()):
                    st.error("Enter your name, confirm the same password, and accept the usage notice.")
                else:
                    try:
                        if st.session_state.auth_mode == "Sign up":
                            if get_user(email):
                                st.error("This account already exists. Please log in.")
                            else:
                                st.session_state.pending_password_hash = password_hash(password)
                                st.session_state.pending_name = name.strip()
                                create_and_send_otp(email, "registration")
                                st.success("Verification code sent. Check your inbox.")
                                st.rerun()
                        else:
                            user = get_user(email)
                            if not user or not verify_password(password, user["password_hash"]):
                                st.error("Email or password is incorrect.")
                            elif not user.get("email_verified", False):
                                st.error("Email not verified. Choose Sign up to complete verification.")
                            else:
                                create_and_send_otp(email, "login")
                                st.success("Verification code sent to your email.")
                                st.rerun()
                    except Exception as exc:
                        st.error(str(exc))
            st.markdown('</div>', unsafe_allow_html=True)
        if not db_ready():
            st.warning("Setup required: configure Supabase database secrets and Gmail SMTP secrets before registering or signing in.")
    st.markdown("<div style='text-align:center;color:#727d9b;font-size:11px;margin-top:35px'>OMNINEXUS AI · PRIVATE WORKSPACE · BUILT FOR POSSIBILITY</div>", unsafe_allow_html=True)

# ------------------------------ Dashboard ------------------------------
def metric_card(label, value, note):
    st.markdown(f'<div class="metric"><div class="metric-label">{label}</div><div class="metric-value">{value}</div><div class="metric-note">{note}</div></div>', unsafe_allow_html=True)

def overview_page():
    user = st.session_state.user
    st.markdown('<div class="eyebrow">COMMAND CENTER / 01</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="hero-title" style="font-size:3.1rem">Good to see you,<br>{user["name"].split()[0]}.</div>', unsafe_allow_html=True)
    st.markdown('<p class="hero-copy">Your creative intelligence workspace is ready. What will you make today?</p>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    activities = st.session_state.activity_log
    messages = len(st.session_state.chat_history)
    images = sum(1 for a in activities if a["activity"] == "Image generated")
    summaries = sum(1 for a in activities if a["activity"] == "Summary created")
    c1,c2,c3,c4 = st.columns(4)
    with c1: metric_card("AI messages", messages, "This session")
    with c2: metric_card("Images created", images, "Creative outputs")
    with c3: metric_card("Briefs generated", summaries, "Executive insights")
    with c4: metric_card("Workspace", "ONLINE", "All systems ready")
    st.markdown("<br>", unsafe_allow_html=True)
    left, right = st.columns([1.25,.75], gap="large")
    with left:
        st.markdown('<div class="glass"><div class="eyebrow">✦ QUICK LAUNCH</div><h3>Where to next?</h3>', unsafe_allow_html=True)
        q1,q2 = st.columns(2)
        with q1:
            if st.button("✧  Start an AI conversation", use_container_width=True):
                st.session_state.page="Remix AI Hub"; st.rerun()
            if st.button("▧  Create an image", use_container_width=True):
                st.session_state.page="Image Studio"; st.rerun()
        with q2:
            if st.button("≋  Summarize a document", use_container_width=True):
                st.session_state.page="Executive Brief"; st.rerun()
            if st.button("◷  Track productivity", use_container_width=True):
                st.session_state.page="Productivity"; st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    with right:
        st.markdown('<div class="glass"><div class="eyebrow">YOUR WORKFLOW</div><h3>Momentum, measured.</h3><p style="color:#aab3cd">Activity metrics update as you use the workspace. Session analytics reset when this session is cleared.</p><span class="pill">LIVE SESSION DATA</span></div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    if activities:
        st.markdown("### Recent activity")
        st.dataframe(pd.DataFrame(activities[::-1][:8]), use_container_width=True, hide_index=True)
    else:
        st.info("Your recent activity will appear here as you chat, create images, and generate briefs.")

def chat_page():
    st.markdown('<div class="eyebrow">REMIX HUB / 02</div>', unsafe_allow_html=True)
    st.markdown("## Remix AI Hub")
    st.caption("A context-aware assistant for brainstorming, building, learning, and problem-solving.")
    with st.expander("Conversation settings", expanded=False):
        system_prompt = st.text_area("Assistant instructions", value="You are OmniNexus, a thoughtful, accurate, concise AI assistant. Explain technical concepts clearly and flag uncertainty.", height=90)
        temperature = st.slider("Creativity", 0.0, 1.2, 0.7, 0.1)
        if st.button("Clear conversation"):
            st.session_state.chat_history = []
            st.rerun()
    speech_input_component("voicein")
    for idx, item in enumerate(st.session_state.chat_history):
        with st.chat_message(item["role"], avatar="✦" if item["role"] == "assistant" else "◉"):
            st.markdown(item["content"])
            if item["role"] == "assistant":
                if st.button("🔊 Play response", key=f"play_{idx}"):
                    audio_component(item["content"], f"chat{idx}")
    prompt = st.chat_input("Ask OmniNexus anything…")
    if prompt:
        st.session_state.chat_history.append({"role":"user","content":prompt})
        record_activity("AI message", prompt)
        with st.chat_message("user", avatar="◉"):
            st.markdown(prompt)
        with st.chat_message("assistant", avatar="✦"):
            with st.spinner("Thinking across the Nexus…"):
                try:
                    recent = st.session_state.chat_history[-16:]
                    answer = groq_chat(recent, system_prompt=system_prompt, temperature=temperature)
                    st.markdown(answer)
                    st.session_state.chat_history.append({"role":"assistant","content":answer})
                except Exception as exc:
                    st.error(str(exc))
        st.rerun()
    st.caption("Voice input uses browser speech recognition when available. Paste its recognized text into the message field. Voice playback uses your browser's speech synthesis.")

def image_page():
    st.markdown('<div class="eyebrow">CREATIVE STUDIO / 03</div>', unsafe_allow_html=True)
    st.markdown("## Image Studio")
    st.markdown('<p class="hero-copy">Turn a clear idea into a visual. Describe the subject, mood, composition, lighting, and style.</p>', unsafe_allow_html=True)
    with st.form("image_form"):
        prompt = st.text_area("Image prompt", placeholder="A cinematic glass observatory floating above a midnight ocean, bioluminescent cyan details, editorial lighting, ultra-detailed...", height=120)
        c1,c2 = st.columns(2)
        with c1: aspect = st.selectbox("Canvas", ["Square · 1024×1024", "Portrait · 768×1024", "Landscape · 1024×768"])
        with c2: style = st.selectbox("Art direction", ["Cinematic realism", "Editorial photography", "3D render", "Digital illustration", "Minimalist design", "Fantasy concept art"])
        submitted = st.form_submit_button("✦ Generate image", use_container_width=True)
    if submitted:
        if len(prompt.strip()) < 5:
            st.warning("Write a more descriptive prompt first.")
        else:
            dims = {"Square · 1024×1024":(1024,1024), "Portrait · 768×1024":(768,1024), "Landscape · 1024×768":(1024,768)}
            width,height = dims[aspect]
            final_prompt = f"{prompt.strip()}. Art direction: {style}. High quality, thoughtful composition, no unwanted text."
            with st.spinner("Creating your visual… image generation may take a little while."):
                try:
                    data = generate_image(final_prompt, width, height)
                    st.session_state.image_result = {"data":data, "prompt":final_prompt, "created":utc_now().strftime("%Y-%m-%d %H:%M UTC")}
                    record_activity("Image generated", prompt[:120])
                except Exception as exc:
                    st.error(f"Image generation failed: {exc}")
    result = st.session_state.image_result
    if result:
        st.markdown("---")
        st.markdown("### Your creation")
        st.image(result["data"], use_container_width=True)
        st.caption(result["prompt"])
        st.download_button("⬇ Download PNG", data=result["data"], file_name="omninexus-creation.png", mime="image/png", use_container_width=True)
        st.info("Sharing: download the image and share it using your preferred app. The app does not publish images publicly.")
    else:
        st.markdown('<div class="glass"><div class="eyebrow">YOUR CANVAS AWAITS</div><h3>Imagine it. Prompt it. Create it.</h3><p style="color:#9ca6c3">Your generated image appears here with a download option.</p></div>', unsafe_allow_html=True)

def summary_page():
    st.markdown('<div class="eyebrow">EXECUTIVE INTELLIGENCE / 04</div>', unsafe_allow_html=True)
    st.markdown("## Executive Brief")
    st.caption("Convert long notes, reports, meeting transcripts, or research into decision-ready insights.")
    with st.form("summary_form"):
        source = st.text_area("Paste your content", height=260, placeholder="Paste a report, meeting notes, article, or project update here…")
        format_choice = st.selectbox("Brief format", ["Executive summary", "Key points and action items", "SWOT analysis", "Meeting minutes", "Study notes"])
        audience = st.selectbox("Audience", ["Leadership", "Project team", "Client", "Student / learner", "General"])
        submitted = st.form_submit_button("Generate executive brief", use_container_width=True)
    if submitted:
        if len(source.strip()) < 40:
            st.warning("Please add a little more source content (at least 40 characters).")
        else:
            instruction = f"""Create a {format_choice} for {audience}. Preserve important facts and caveats. Do not invent details not present in the source. Use clear headings, concise bullets, and concrete next steps when relevant. If the source lacks information, say so."""
            with st.spinner("Distilling the signal from the noise…"):
                try:
                    result = groq_chat([{"role":"user","content":instruction + "\n\nSOURCE CONTENT:\n" + source[:24000]}], temperature=0.3)
                    st.session_state.last_summary = result
                    record_activity("Summary created", format_choice)
                except Exception as exc:
                    st.error(str(exc))
    if st.session_state.last_summary:
        st.markdown("### Your brief")
        st.markdown(st.session_state.last_summary)
        st.download_button("⬇ Download brief (.md)", data=st.session_state.last_summary, file_name="omninexus-executive-brief.md", mime="text/markdown")

def productivity_page():
    st.markdown('<div class="eyebrow">PERSONAL OPERATIONS / 05</div>', unsafe_allow_html=True)
    st.markdown("## Productivity Lab")
    st.caption("A lightweight tracker for planned work, completed tasks, and focus time. Data is held in the current session.")
    if "tasks" not in st.session_state:
        st.session_state.tasks = []
    with st.form("task_add", clear_on_submit=True):
        task = st.text_input("Task", placeholder="e.g., Finish portfolio landing page")
        col1,col2 = st.columns(2)
        with col1: category = st.selectbox("Category", ["Development", "Design", "Learning", "Admin", "Personal"])
        with col2: minutes = st.number_input("Estimated focus minutes", min_value=5, max_value=600, value=30, step=5)
        add = st.form_submit_button("＋ Add task", use_container_width=True)
    if add and task.strip():
        st.session_state.tasks.append({"Task":task.strip(), "Category":category, "Focus minutes":int(minutes), "Done":False})
        record_activity("Task added", task.strip())
        st.rerun()
    tasks = st.session_state.tasks
    if tasks:
        st.markdown("### Your task board")
        for i, t in enumerate(tasks):
            col1,col2,col3 = st.columns([.08,.72,.2])
            with col1:
                done = st.checkbox("Done", value=t["Done"], key=f"done_{i}", label_visibility="collapsed")
            with col2:
                st.markdown(("~~" + t["Task"] + "~~") if done else f"**{t['Task']}**")
                st.caption(f"{t['Category']} · {t['Focus minutes']} min")
            with col3:
                st.caption("COMPLETE" if done else "IN PROGRESS")
            if done != t["Done"]:
                t["Done"] = done
                if done: record_activity("Task completed", t["Task"])
        total = len(tasks)
        completed = sum(1 for t in tasks if t["Done"])
        focus = sum(t["Focus minutes"] for t in tasks if t["Done"])
        a,b,c = st.columns(3)
        with a: metric_card("Tasks completed", f"{completed}/{total}", "Delivery progress")
        with b: metric_card("Completion rate", f"{completed/total:.0%}", "Current task board")
        with c: metric_card("Focus planned done", f"{focus} min", "Completed task estimates")
        df = pd.DataFrame(tasks)
        fig = px.pie(df, names="Category", title="Tasks by category", hole=.62, template="plotly_dark")
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#dfe5ff", legend_title_text="")
        st.plotly_chart(fig, use_container_width=True)
        if st.button("Clear completed tasks"):
            st.session_state.tasks = [t for t in tasks if not t["Done"]]
            st.rerun()
        st.download_button("Download task board CSV", data=pd.DataFrame(tasks).to_csv(index=False), file_name="omninexus-tasks.csv", mime="text/csv")
    else:
        st.info("Add your first task to see completion metrics and category analytics.")

def settings_page():
    st.markdown('<div class="eyebrow">CONTROL PLANE / 06</div>', unsafe_allow_html=True)
    st.markdown("## Settings & security")
    user = st.session_state.user
    a,b = st.columns(2)
    with a:
        st.markdown('<div class="glass"><div class="eyebrow">ACCOUNT</div><h3>Identity</h3>', unsafe_allow_html=True)
        st.write("**Display name**", user["name"])
        st.write("**Verified email**", user["email"])
        st.write("**Authentication**", "Email OTP + password")
        st.write("**Password storage**", "Salted scrypt hash")
        st.markdown('</div>', unsafe_allow_html=True)
    with b:
        st.markdown('<div class="glass"><div class="eyebrow">RUNTIME</div><h3>Workspace health</h3>', unsafe_allow_html=True)
        st.write("**Database**", "Connected" if db_ready() else "Not configured")
        st.write("**Text AI**", "Configured" if GROQ_API_KEY else "API key required")
        st.write("**Email delivery**", "Configured" if SMTP_EMAIL and SMTP_APP_PASSWORD else "SMTP credentials required")
        st.write("**Image generation**", "Pollinations public endpoint")
        st.markdown('</div>', unsafe_allow_html=True)
    st.markdown("### Privacy notes")
    st.markdown("""
    - Passwords are hashed using Python's `scrypt`; plaintext passwords are never written to the database.
    - OTPs expire after 10 minutes and are stored as hashes. Incorrect attempts are capped.
    - Chat history, task-board data, and generated image bytes live in Streamlit session state and are not a durable cloud archive.
    - Use HTTPS (provided by Streamlit Community Cloud), keep service-role credentials private, and never commit secrets to GitHub.
    - For a higher-assurance production deployment, add server-side rate limiting, account recovery, audit logging, and a managed identity provider.
    """)

# ------------------------------- Main -------------------------------
render_sidebar()
if not st.session_state.authenticated:
    auth_screen()
else:
    page = st.session_state.page
    if page == "Overview":
        overview_page()
    elif page == "Remix AI Hub":
        chat_page()
    elif page == "Image Studio":
        image_page()
    elif page == "Executive Brief":
        summary_page()
    elif page == "Productivity":
        productivity_page()
    elif page == "Settings":
        settings_page()
    else:
        overview_page()
