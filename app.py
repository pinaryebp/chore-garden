import streamlit as st
import json
import os
from datetime import datetime, timedelta
import pandas as pd
import time as _time

# ======================== CONFIG ========================
st.set_page_config(
    page_title="Chore Garden 🌱",
    page_icon="🌱",
    layout="centered",
    initial_sidebar_state="collapsed",
)

DATA_FILE = "chore_data.json"

PLAYERS = [
    {"name": "Pınar", "color": "#D4764E", "light": "#FDF2EC", "icon": "🌸", "cls": "pinar"},
    {"name": "Cris", "color": "#5B8C5A", "light": "#EEF5EE", "icon": "🌿", "cls": "cris"},
]

BLOOM_MAP = {1: "🌱", 2: "🌿", 3: "🌷", 4: "🌻", 5: "🌳"}

FREQ_OPTIONS = [
    {"value": "none", "label": "No repeat", "hours": None},
    {"value": "daily", "label": "Every day", "hours": 24},
    {"value": "every2", "label": "Every 2 days", "hours": 48},
    {"value": "every3", "label": "Every 3 days", "hours": 72},
    {"value": "weekly", "label": "Every week", "hours": 168},
]

FREQ_MAP = {f["value"]: f for f in FREQ_OPTIONS}

DEFAULT_CHORES = [
    {"id": "1", "name": "Dishes", "points": 2, "emoji": "🍽️", "freq": "daily"},
    {"id": "2", "name": "Vacuuming", "points": 3, "emoji": "🧹", "freq": "weekly"},
    {"id": "3", "name": "Laundry", "points": 3, "emoji": "👕", "freq": "every3"},
    {"id": "4", "name": "Cooking", "points": 4, "emoji": "🍳", "freq": "daily"},
    {"id": "5", "name": "Bathroom cleaning", "points": 4, "emoji": "🚿", "freq": "weekly"},
    {"id": "6", "name": "Mopping floors", "points": 3, "emoji": "🪣", "freq": "weekly"},
    {"id": "7", "name": "Grocery shopping", "points": 3, "emoji": "🛒", "freq": "weekly"},
    {"id": "8", "name": "Trash / recycling", "points": 1, "emoji": "🗑️", "freq": "every2"},
    {"id": "9", "name": "Ironing", "points": 2, "emoji": "👔", "freq": "weekly"},
    {"id": "10", "name": "Deep clean kitchen", "points": 5, "emoji": "✨", "freq": "weekly"},
    {"id": "11", "name": "Organize closet", "points": 5, "emoji": "🗄️", "freq": "none"},
    {"id": "12", "name": "Dusting", "points": 2, "emoji": "🪶", "freq": "weekly"},
    {"id": "13", "name": "Window cleaning", "points": 4, "emoji": "🪟", "freq": "none"},
    {"id": "14", "name": "Pet care", "points": 2, "emoji": "🐾", "freq": "daily"},
    {"id": "15", "name": "Bed making", "points": 1, "emoji": "🛏️", "freq": "daily"},
]

EMOJIS = [
    "🍽️", "🧹", "👕", "🍳", "🚿", "🪣", "🛒", "🗑️", "👔", "✨",
    "🗄️", "🪶", "🪟", "🐾", "🛏️", "🧽", "🌿", "🔧", "📦", "🧸",
]


# ======================== CUSTOM CSS ========================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800;900&family=Playfair+Display:wght@700;800&display=swap');

/* ── Global ── */
.stApp { background: #FEFCF6 !important; }
.block-container { padding-top: 0.8rem !important; max-width: 520px !important; padding-bottom: 2rem !important; }
#MainMenu, footer, header[data-testid="stHeader"] { display: none !important; }
div[data-testid="stToolbar"] { display: none !important; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-thumb { background: #C2D6B4; border-radius: 4px; }

/* ── Header Banner ── */
.garden-header {
    background: linear-gradient(135deg, #7BAF6E 0%, #A8C99B 50%, #D4E4C8 100%);
    padding: 24px 20px 18px; border-radius: 22px; text-align: center;
    margin-bottom: 18px; box-shadow: 0 6px 30px rgba(91,140,90,0.2);
    position: relative; overflow: hidden;
}
.garden-header::after {
    content: "🌸 🌿 🌷 🌻 🌱 🌼 🌳 🍃";
    position: absolute; bottom: 2px; left: 0; right: 0;
    font-size: 14px; letter-spacing: 4px; opacity: 0.3;
}
.garden-header h1 {
    font-family: 'Playfair Display', serif !important;
    font-size: 30px !important; color: #2C4A2B !important;
    margin: 0 !important; padding: 0 !important;
    text-shadow: 0 1px 3px rgba(255,255,255,0.4);
    line-height: 1.2 !important;
}
.garden-header p {
    color: #3D6B3A; font-size: 13px; font-weight: 700;
    margin: 4px 0 0 0 !important; font-family: 'Nunito', sans-serif;
}

/* ── Mini Score Cards ── */
.mini-garden {
    border-radius: 18px; padding: 14px 10px; text-align: center;
    transition: transform 0.2s;
}
.mini-garden.pinar { background: #FDF2EC; border: 2px solid #D4764E25; }
.mini-garden.cris { background: #EEF5EE; border: 2px solid #5B8C5A25; }
.mini-garden .m-icon { font-size: 20px; }
.mini-garden .m-name { font-weight: 800; font-size: 13px; font-family: 'Nunito', sans-serif; }
.mini-garden .m-name.pinar { color: #D4764E; }
.mini-garden .m-name.cris { color: #5B8C5A; }
.mini-garden .m-pts { font-weight: 900; font-size: 34px; line-height: 1.1; font-family: 'Nunito', sans-serif; }
.mini-garden .m-pts.pinar { color: #D4764E; }
.mini-garden .m-pts.cris { color: #5B8C5A; }
.mini-garden .m-label { font-size: 10px; color: #8B9B7A; font-weight: 600; font-family: 'Nunito', sans-serif; }

/* ── Garden Viz ── */
.garden-viz {
    background: linear-gradient(180deg, #E8F4E2 0%, #D4E4C8 100%);
    border-radius: 20px; padding: 18px 16px; text-align: center;
    border: 2px solid #C2D6B4; margin: 14px 0 18px;
    font-size: 22px; letter-spacing: 3px; line-height: 1.8;
    min-height: 40px;
}

/* ── Section Titles ── */
.sec-title {
    font-family: 'Nunito', sans-serif; font-weight: 800;
    font-size: 17px; color: #4A4238; margin: 18px 0 10px; padding: 0;
}

/* ── Todo Items ── */
.todo-item {
    background: white; border-radius: 16px; padding: 14px 16px;
    display: flex; align-items: center; gap: 12px;
    border: 2px solid #E8E0D0; margin-bottom: 8px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.03);
    font-family: 'Nunito', sans-serif;
    transition: all 0.2s;
}
.todo-item:hover { border-color: #C2D6B4; }
.todo-item.done { opacity: 0.55; }
.todo-checkbox {
    width: 26px; height: 26px; border-radius: 9px;
    border: 2.5px solid #C2D6B4; background: #FEFCF6;
    flex-shrink: 0;
}
.todo-checkbox.checked {
    background: #5B8C5A; border-color: #5B8C5A;
    color: white; display: flex; align-items: center;
    justify-content: center; font-weight: 800; font-size: 14px;
}
.todo-info { flex: 1; min-width: 0; }
.todo-name { font-weight: 700; font-size: 15px; color: #4A4238; }
.todo-name.done { text-decoration: line-through; color: #A0A090; }
.todo-meta { font-size: 11px; color: #8B9B7A; font-weight: 600; margin-top: 2px; }

/* ── Quick Log Buttons ── */
.quick-btns { display: flex; gap: 6px; flex-shrink: 0; }
.quick-btn {
    width: 36px; height: 36px; border-radius: 11px; border: none;
    color: white; font-size: 16px; display: flex;
    align-items: center; justify-content: center;
    cursor: pointer; box-shadow: 0 3px 10px rgba(0,0,0,0.1);
    transition: transform 0.15s;
}
.quick-btn:hover { transform: scale(1.1); }
.quick-btn.pinar { background: #D4764E; }
.quick-btn.cris { background: #5B8C5A; }

/* ── Big Score Cards ── */
.garden-score {
    border-radius: 22px; padding: 22px 16px; text-align: center;
    color: white; box-shadow: 0 8px 30px rgba(0,0,0,0.12);
    position: relative;
}
.garden-score.pinar { background: linear-gradient(135deg, #D4764E, #E8A87C); }
.garden-score.cris { background: linear-gradient(135deg, #5B8C5A, #8BBF88); }
.garden-score.winner { transform: scale(1.03); }
.gs-crown { font-size: 28px; margin-bottom: -4px; }
.gs-icon { font-size: 34px; }
.gs-name { font-family: 'Nunito', sans-serif; font-weight: 800; font-size: 18px; }
.gs-pts { font-family: 'Playfair Display', serif; font-size: 50px; line-height: 1.1; text-shadow: 0 2px 10px rgba(0,0,0,0.15); }
.gs-sub { font-size: 12px; opacity: 0.85; font-weight: 600; font-family: 'Nunito', sans-serif; }

/* ── Banners ── */
.bloom-banner {
    text-align: center; padding: 14px 20px; border-radius: 18px;
    font-size: 15px; font-weight: 700; font-family: 'Nunito', sans-serif;
    margin-top: 14px;
}
.bloom-banner.pinar { background: #FDF2EC; border: 2px solid #D4764E; color: #D4764E; }
.bloom-banner.cris { background: #EEF5EE; border: 2px solid #5B8C5A; color: #5B8C5A; }
.bloom-banner.tie { background: #F5F0E3; border: 2px solid #D4DBC8; color: #8B9B7A; }

/* ── Toast ── */
.g-toast {
    padding: 14px 24px; border-radius: 50px; color: white; font-weight: 700;
    font-size: 14px; text-align: center; margin-bottom: 16px;
    font-family: 'Nunito', sans-serif; box-shadow: 0 6px 25px rgba(0,0,0,0.15);
    animation: toastSlide 0.4s ease;
}
@keyframes toastSlide {
    from { opacity: 0; transform: translateY(-10px); }
    to { opacity: 1; transform: translateY(0); }
}
.g-toast.pinar { background: #D4764E; }
.g-toast.cris { background: #5B8C5A; }

/* ── Week Label ── */
.g-week {
    text-align: center; font-size: 14px; color: #8B9B7A; font-weight: 700;
    background: #F0EDE2; padding: 10px 18px; border-radius: 14px;
    font-family: 'Nunito', sans-serif; margin-bottom: 16px;
}

/* ── History Items ── */
.g-history {
    background: white; border-radius: 14px; padding: 12px 16px;
    border-left: 4px solid; box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    margin-bottom: 8px; font-family: 'Nunito', sans-serif; font-size: 14px;
}
.g-history.pinar { border-left-color: #D4764E; }
.g-history.cris { border-left-color: #5B8C5A; }

/* ── Stat Cards ── */
.g-stat {
    background: white; border-radius: 18px; padding: 18px 14px;
    text-align: center; box-shadow: 0 2px 10px rgba(0,0,0,0.04);
    border: 2px solid #F0EDE2;
}
.g-stat.pinar-top { border-top: 3px solid #D4764E; }
.g-stat.cris-top { border-top: 3px solid #5B8C5A; }
.g-stat .s-num { font-family: 'Playfair Display', serif; font-size: 30px; color: #4A4238; }
.g-stat .s-num.pinar { color: #D4764E; }
.g-stat .s-num.cris { color: #5B8C5A; }
.g-stat .s-label { font-size: 12px; color: #8B9B7A; font-weight: 600; font-family: 'Nunito', sans-serif; margin-top: 4px; }

/* ── Chart Container ── */
.chart-box {
    background: white; border-radius: 20px; padding: 12px 8px 4px;
    box-shadow: 0 2px 12px rgba(0,0,0,0.04); border: 2px solid #F0EDE2;
}

/* ── Chore List Items (settings) ── */
.chore-row {
    background: white; border-radius: 14px; padding: 12px 16px;
    display: flex; align-items: center; gap: 10px;
    border: 2px solid #F0EDE2; margin-bottom: 6px;
    font-family: 'Nunito', sans-serif;
    box-shadow: 0 1px 6px rgba(0,0,0,0.03);
}
.chore-row .cr-emoji { font-size: 22px; }
.chore-row .cr-name { flex: 1; font-weight: 700; font-size: 14px; color: #4A4238; }
.chore-row .cr-meta { font-size: 12px; color: #8B9B7A; font-weight: 700; }
.freq-tag {
    display: inline-block; background: #EEF5EE; color: #5B8C5A;
    border-radius: 8px; padding: 2px 8px; font-size: 10px; font-weight: 700;
    margin-left: 4px; font-family: 'Nunito', sans-serif;
}

/* ── Empty State ── */
.empty-state {
    text-align: center; padding: 30px 20px; color: #8B9B7A;
    font-size: 15px; font-weight: 600; background: white;
    border-radius: 18px; border: 2px solid #E8E0D0;
    font-family: 'Nunito', sans-serif;
}

/* ── Add Chore Form ── */
.add-form-box {
    background: white; border-radius: 20px; padding: 20px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.06);
    border: 2px solid #E8E0D0; margin-top: 16px;
}
.add-form-title {
    font-weight: 800; font-size: 17px; color: #5B8C5A;
    margin-bottom: 14px; font-family: 'Nunito', sans-serif;
}

/* ── Danger Zone ── */
.danger-box {
    background: #FFF5F5; border-radius: 16px; padding: 20px;
    border: 2px solid #FFDDDD; margin-top: 28px;
}
.danger-title { font-weight: 800; font-size: 14px; color: #CC4444; margin-bottom: 10px; font-family: 'Nunito', sans-serif; }

/* ── Streamlit Element Overrides ── */
.stButton > button {
    font-family: 'Nunito', sans-serif !important; font-weight: 700 !important;
    border-radius: 14px !important; border: 2px solid #E8E0D0 !important;
    background: white !important; color: #4A4238 !important;
    transition: all 0.2s !important; padding: 0.4rem 1rem !important;
}
.stButton > button:hover {
    border-color: #5B8C5A !important; color: #5B8C5A !important;
    background: #EEF5EE !important; transform: translateY(-1px) !important;
    box-shadow: 0 4px 12px rgba(91,140,90,0.15) !important;
}
.stButton > button:active {
    transform: translateY(0) !important;
}

/* Player pick buttons */
.player-pick > div > .stButton > button {
    padding: 1.2rem 1rem !important; font-size: 18px !important;
    font-weight: 800 !important; border-radius: 20px !important;
    box-shadow: 0 4px 15px rgba(0,0,0,0.08) !important;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    gap: 4px; background: #EDE8DC; border-radius: 16px; padding: 5px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.04);
}
.stTabs [data-baseweb="tab"] {
    font-family: 'Nunito', sans-serif !important; font-weight: 700 !important;
    border-radius: 12px !important; color: #8B9B7A !important;
    font-size: 14px !important; padding: 10px 8px !important;
}
.stTabs [aria-selected="true"] {
    background: white !important; color: #5B8C5A !important;
    box-shadow: 0 2px 10px rgba(0,0,0,0.06) !important;
}
.stTabs [data-baseweb="tab-highlight"], .stTabs [data-baseweb="tab-border"] { display: none !important; }

/* Select boxes */
.stSelectbox > div > div { border-radius: 12px !important; border-color: #E8E0D0 !important; font-family: 'Nunito', sans-serif !important; }
.stTextInput > div > div > input { border-radius: 12px !important; border-color: #E8E0D0 !important; font-family: 'Nunito', sans-serif !important; font-weight: 600 !important; }
.stSlider > div { font-family: 'Nunito', sans-serif !important; }

/* Expander */
.streamlit-expanderHeader { font-family: 'Nunito', sans-serif !important; font-weight: 700 !important; color: #4A4238 !important; border-radius: 14px !important; }
div[data-testid="stExpander"] { border-radius: 14px !important; border-color: #E8E0D0 !important; }

/* Radio (chart toggle) */
.stRadio > div { font-family: 'Nunito', sans-serif !important; }
.stRadio label { font-weight: 700 !important; color: #8B9B7A !important; }

/* Captions */
.stCaption, [data-testid="stCaptionContainer"] { font-family: 'Nunito', sans-serif !important; color: #8B9B7A !important; }
</style>
""", unsafe_allow_html=True)


# ======================== DATA ========================
def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    default = {"chores": DEFAULT_CHORES, "log": [], "todo": {}}
    save_data(default)
    return default


def save_data(d):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False)


# ======================== HELPERS ========================
def get_monday(d):
    return (d - timedelta(days=d.weekday())).replace(hour=0, minute=0, second=0, microsecond=0)


def get_sunday(d):
    return (get_monday(d) + timedelta(days=6)).replace(hour=23, minute=59, second=59)


def this_week_log(log):
    now = datetime.now()
    mon = get_monday(now)
    sun = get_sunday(now)
    return [e for e in log if mon <= datetime.fromisoformat(e["date"]) <= sun]


def get_scores(wlog):
    return {
        p["name"]: {
            "total": sum(e["points"] for e in wlog if e["player"] == p["name"]),
            "count": sum(1 for e in wlog if e["player"] == p["name"]),
        }
        for p in PLAYERS
    }


def blooms_for_log(log_entries):
    return " ".join(BLOOM_MAP.get(min(e["points"], 5), "🌱") for e in log_entries)


def is_done(chore, todo_state):
    entry = todo_state.get(chore["id"])
    if not entry or "doneAt" not in entry:
        return False
    freq = FREQ_MAP.get(chore.get("freq", "none"), {})
    hours = freq.get("hours")
    if not hours:
        return True  # no repeat = stays done
    elapsed_hours = (datetime.now().timestamp() * 1000 - entry["doneAt"]) / (1000 * 60 * 60)
    return elapsed_hours < hours


def time_until_reset(chore, todo_state):
    entry = todo_state.get(chore["id"])
    if not entry or "doneAt" not in entry:
        return None
    freq = FREQ_MAP.get(chore.get("freq", "none"), {})
    hours = freq.get("hours")
    if not hours:
        return None
    reset_at = entry["doneAt"] + hours * 3600000
    diff = reset_at - datetime.now().timestamp() * 1000
    if diff <= 0:
        return None
    h = int(diff // 3600000)
    m = int((diff % 3600000) // 60000)
    if h > 24:
        return f"{h // 24}d {h % 24}h"
    if h > 0:
        return f"{h}h {m}m"
    return f"{m}m"


# ======================== SESSION STATE ========================
if "just_logged" not in st.session_state:
    st.session_state.just_logged = None

# Load fresh data
data = load_data()
now = datetime.now()
wlog = this_week_log(data["log"])
scores = get_scores(wlog)


# ======================== HEADER ========================
st.markdown("""
<div class="garden-header">
    <h1>🌱 Chore Garden</h1>
    <p>Pınar & Cris — growing a tidy home together</p>
</div>
""", unsafe_allow_html=True)


# ======================== TABS ========================
tab_todo, tab_log, tab_garden, tab_charts, tab_chores = st.tabs([
    "📋 To Do", "🌱 Log", "🌻 Garden", "📊 Growth", "⚙️ Chores",
])


# ======================== TO DO TAB ========================
with tab_todo:
    # Toast
    if st.session_state.just_logged:
        jl = st.session_state.just_logged
        cls = "pinar" if jl["player"] == "Pınar" else "cris"
        bloom = BLOOM_MAP.get(min(jl["points"], 5), "🌱")
        st.markdown(
            f'<div class="g-toast {cls}">{bloom} {jl["player"]} planted '
            f'"{jl["chore"]}" in the garden! +{jl["points"]} seeds</div>',
            unsafe_allow_html=True,
        )
        st.session_state.just_logged = None

    # Mini scores
    c1, c2 = st.columns(2)
    for i, p in enumerate(PLAYERS):
        with [c1, c2][i]:
            st.markdown(f"""
            <div class="mini-garden {p['cls']}">
                <div class="m-icon">{p['icon']}</div>
                <div class="m-name {p['cls']}">{p['name']}</div>
                <div class="m-pts {p['cls']}">{scores[p['name']]['total']}</div>
                <div class="m-label">seeds this week</div>
            </div>
            """, unsafe_allow_html=True)

    # Garden preview
    if wlog:
        st.markdown(f'<div class="garden-viz">{blooms_for_log(wlog)}</div>', unsafe_allow_html=True)

    # Separate chores into recurring and one-off
    recurring = [c for c in data["chores"] if c.get("freq") and c["freq"] != "none"]
    one_off = [c for c in data["chores"] if not c.get("freq") or c["freq"] == "none"]

    pending = [c for c in recurring if not is_done(c, data.get("todo", {}))]
    done = [c for c in recurring if is_done(c, data.get("todo", {}))]

    # ── Pending chores ──
    st.markdown('<div class="sec-title">🌱 To do</div>', unsafe_allow_html=True)

    if not pending:
        st.markdown('<div class="empty-state">All done! Your garden is thriving 🌻</div>', unsafe_allow_html=True)

    for ch in pending:
        bloom = BLOOM_MAP.get(min(ch["points"], 5), "🌱")
        freq_label = FREQ_MAP.get(ch.get("freq", "none"), {}).get("label", "")

        st.markdown(f"""
        <div class="todo-item">
            <div class="todo-checkbox"></div>
            <div class="todo-info">
                <div class="todo-name">{ch['emoji']} {ch['name']}</div>
                <div class="todo-meta">{bloom} {ch['points']} seeds · {freq_label}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Action buttons
        bc1, bc2 = st.columns(2)
        with bc1:
            if st.button(f"🌸 Pınar did it", key=f"todo_p_{ch['id']}", use_container_width=True):
                entry = {
                    "id": str(int(datetime.now().timestamp() * 1000)),
                    "player": "Pınar", "choreId": ch["id"], "choreName": ch["name"],
                    "choreEmoji": ch["emoji"], "points": ch["points"],
                    "date": datetime.now().isoformat(),
                }
                data["log"].append(entry)
                if "todo" not in data:
                    data["todo"] = {}
                data["todo"][ch["id"]] = {"doneAt": datetime.now().timestamp() * 1000, "doneBy": "Pınar"}
                save_data(data)
                st.session_state.just_logged = {"player": "Pınar", "chore": ch["name"], "emoji": ch["emoji"], "points": ch["points"]}
                st.rerun()
        with bc2:
            if st.button(f"🌿 Cris did it", key=f"todo_c_{ch['id']}", use_container_width=True):
                entry = {
                    "id": str(int(datetime.now().timestamp() * 1000) + 1),
                    "player": "Cris", "choreId": ch["id"], "choreName": ch["name"],
                    "choreEmoji": ch["emoji"], "points": ch["points"],
                    "date": datetime.now().isoformat(),
                }
                data["log"].append(entry)
                if "todo" not in data:
                    data["todo"] = {}
                data["todo"][ch["id"]] = {"doneAt": datetime.now().timestamp() * 1000, "doneBy": "Cris"}
                save_data(data)
                st.session_state.just_logged = {"player": "Cris", "chore": ch["name"], "emoji": ch["emoji"], "points": ch["points"]}
                st.rerun()

    # ── Done chores ──
    if done:
        st.markdown('<div class="sec-title">✅ Done</div>', unsafe_allow_html=True)
        for ch in done:
            todo_entry = data.get("todo", {}).get(ch["id"], {})
            done_by = todo_entry.get("doneBy", "?")
            reset = time_until_reset(ch, data.get("todo", {}))
            reset_text = f" · resets in {reset}" if reset else ""

            st.markdown(f"""
            <div class="todo-item done">
                <div class="todo-checkbox checked">✓</div>
                <div class="todo-info">
                    <div class="todo-name done">{ch['emoji']} {ch['name']}</div>
                    <div class="todo-meta">Done by {done_by}{reset_text}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    # ── One-off chores ──
    if one_off:
        st.markdown('<div class="sec-title">📋 One-time chores</div>', unsafe_allow_html=True)
        for ch in one_off:
            ch_done = is_done(ch, data.get("todo", {}))
            bloom = BLOOM_MAP.get(min(ch["points"], 5), "🌱")

            if ch_done:
                st.markdown(f"""
                <div class="todo-item done">
                    <div class="todo-checkbox checked">✓</div>
                    <div class="todo-info">
                        <div class="todo-name done">{ch['emoji']} {ch['name']}</div>
                        <div class="todo-meta">{bloom} {ch['points']} seeds · Done ✓</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="todo-item">
                    <div class="todo-checkbox"></div>
                    <div class="todo-info">
                        <div class="todo-name">{ch['emoji']} {ch['name']}</div>
                        <div class="todo-meta">{bloom} {ch['points']} seeds</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                oc1, oc2 = st.columns(2)
                with oc1:
                    if st.button("🌸 Pınar", key=f"oo_p_{ch['id']}", use_container_width=True):
                        entry = {
                            "id": str(int(datetime.now().timestamp() * 1000)),
                            "player": "Pınar", "choreId": ch["id"], "choreName": ch["name"],
                            "choreEmoji": ch["emoji"], "points": ch["points"],
                            "date": datetime.now().isoformat(),
                        }
                        data["log"].append(entry)
                        if "todo" not in data:
                            data["todo"] = {}
                        data["todo"][ch["id"]] = {"doneAt": datetime.now().timestamp() * 1000, "doneBy": "Pınar"}
                        save_data(data)
                        st.session_state.just_logged = {"player": "Pınar", "chore": ch["name"], "emoji": ch["emoji"], "points": ch["points"]}
                        st.rerun()
                with oc2:
                    if st.button("🌿 Cris", key=f"oo_c_{ch['id']}", use_container_width=True):
                        entry = {
                            "id": str(int(datetime.now().timestamp() * 1000) + 1),
                            "player": "Cris", "choreId": ch["id"], "choreName": ch["name"],
                            "choreEmoji": ch["emoji"], "points": ch["points"],
                            "date": datetime.now().isoformat(),
                        }
                        data["log"].append(entry)
                        if "todo" not in data:
                            data["todo"] = {}
                        data["todo"][ch["id"]] = {"doneAt": datetime.now().timestamp() * 1000, "doneBy": "Cris"}
                        save_data(data)
                        st.session_state.just_logged = {"player": "Cris", "chore": ch["name"], "emoji": ch["emoji"], "points": ch["points"]}
                        st.rerun()


# ======================== LOG TAB ========================
with tab_log:
    # Mini scores
    c1, c2 = st.columns(2)
    for i, p in enumerate(PLAYERS):
        with [c1, c2][i]:
            st.markdown(f"""
            <div class="mini-garden {p['cls']}">
                <div class="m-icon">{p['icon']}</div>
                <div class="m-name {p['cls']}">{p['name']}</div>
                <div class="m-pts {p['cls']}">{scores[p['name']]['total']}</div>
                <div class="m-label">seeds this week</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("")

    # Player selection
    st.markdown('<div class="sec-title">Who\'s planting? 🌱</div>', unsafe_allow_html=True)

    player_choice = st.radio(
        "Select gardener",
        ["Choose...", "🌸 Pınar", "🌿 Cris"],
        horizontal=True,
        key="log_player",
        label_visibility="collapsed",
    )

    if player_choice != "Choose...":
        pname = "Pınar" if "Pınar" in player_choice else "Cris"
        player = next(p for p in PLAYERS if p["name"] == pname)

        st.markdown(
            f'<div class="sec-title" style="color:{player["color"]}">'
            f'{player["icon"]} What did {player["name"]} do?</div>',
            unsafe_allow_html=True,
        )

        chores = data["chores"]
        for row_start in range(0, len(chores), 2):
            cols = st.columns(2)
            for j in range(2):
                idx = row_start + j
                if idx < len(chores):
                    ch = chores[idx]
                    bloom = BLOOM_MAP.get(min(ch["points"], 5), "🌱")
                    with cols[j]:
                        st.markdown(f"""
                        <div style="background:white;border:2px solid #E8E0D0;border-radius:16px;
                            padding:14px 10px;text-align:center;margin-bottom:4px;
                            box-shadow:0 2px 8px rgba(0,0,0,0.03);">
                            <div style="font-size:28px">{ch['emoji']}</div>
                            <div style="font-weight:700;font-size:13px;color:#4A4238;
                                font-family:'Nunito',sans-serif;line-height:1.2">{ch['name']}</div>
                            <div style="display:inline-block;background:{player['light']};color:{player['color']};
                                border-radius:20px;padding:3px 12px;font-weight:800;font-size:12px;
                                margin-top:4px;font-family:'Nunito',sans-serif">{bloom} +{ch['points']}</div>
                        </div>
                        """, unsafe_allow_html=True)
                        if st.button("Plant it!", key=f"log_{ch['id']}_{pname}", use_container_width=True):
                            entry = {
                                "id": str(int(datetime.now().timestamp() * 1000)),
                                "player": pname, "choreId": ch["id"], "choreName": ch["name"],
                                "choreEmoji": ch["emoji"], "points": ch["points"],
                                "date": datetime.now().isoformat(),
                            }
                            data["log"].append(entry)
                            if "todo" not in data:
                                data["todo"] = {}
                            data["todo"][ch["id"]] = {"doneAt": datetime.now().timestamp() * 1000, "doneBy": pname}
                            save_data(data)
                            st.session_state.just_logged = {"player": pname, "chore": ch["name"], "emoji": ch["emoji"], "points": ch["points"]}
                            st.rerun()


# ======================== GARDEN / SCORE TAB ========================
with tab_garden:
    mon = get_monday(now)
    sun = get_sunday(now)
    st.markdown(
        f'<div class="g-week">🌿 Week of {mon.strftime("%b %d")} – {sun.strftime("%b %d")}</div>',
        unsafe_allow_html=True,
    )

    p_tot = scores["Pınar"]["total"]
    c_tot = scores["Cris"]["total"]
    top = None
    if p_tot > c_tot:
        top = "Pınar"
    elif c_tot > p_tot:
        top = "Cris"

    BG_GRAD = {
        "pinar": "linear-gradient(135deg, #D4764E, #E8A87C)",
        "cris": "linear-gradient(135deg, #5B8C5A, #8BBF88)",
    }
    c1, c2 = st.columns(2)
    for i, p in enumerate(PLAYERS):
        is_top = top == p["name"]
        crown = "<div style='font-size:28px;margin-bottom:-4px;'>👑</div>" if is_top else ""
        scale = "transform:scale(1.03);" if is_top else ""
        with [c1, c2][i]:
            st.markdown(f"""
            <div style="border-radius:22px;padding:22px 16px;text-align:center;color:white;
                background:{BG_GRAD[p['cls']]};box-shadow:0 8px 30px rgba(0,0,0,0.12);
                position:relative;{scale}">
                {crown}
                <div style="font-size:34px;">{p['icon']}</div>
                <div style="font-family:'Nunito',sans-serif;font-weight:800;font-size:18px;">{p['name']}</div>
                <div style="font-family:'Playfair Display',serif;font-size:50px;line-height:1.1;text-shadow:0 2px 10px rgba(0,0,0,0.15);">{scores[p['name']]['total']}</div>
                <div style="font-size:12px;opacity:0.85;font-weight:600;font-family:'Nunito',sans-serif;">{scores[p['name']]['count']} chores planted</div>
            </div>
            """, unsafe_allow_html=True)

    if top:
        tcls = "pinar" if top == "Pınar" else "cris"
        st.markdown(
            f'<div class="bloom-banner {tcls}">🌻 <strong>{top}</strong> has the most blooms this week!</div>',
            unsafe_allow_html=True,
        )
    elif wlog:
        st.markdown('<div class="bloom-banner tie">🌸 Beautiful — you\'re growing equally!</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="bloom-banner tie">🌱 Your garden is waiting! Plant your first chore.</div>', unsafe_allow_html=True)

    if wlog:
        st.markdown('<div class="sec-title">This week\'s garden</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="garden-viz">{blooms_for_log(wlog)}</div>', unsafe_allow_html=True)

    if wlog:
        st.markdown('<div class="sec-title">Recent activity</div>', unsafe_allow_html=True)
        with st.expander("Show details"):
            for entry in reversed(wlog):
                pcls = "pinar" if entry["player"] == "Pınar" else "cris"
                dt = datetime.fromisoformat(entry["date"])
                dt_str = dt.strftime("%a, %b %d · %I:%M %p")
                bloom = BLOOM_MAP.get(min(entry["points"], 5), "🌱")
                pcolor = "#D4764E" if pcls == "pinar" else "#5B8C5A"
                st.markdown(
                    f'<div class="g-history {pcls}">'
                    f'<strong>{entry["choreEmoji"]} {entry["choreName"]}</strong>'
                    f'<span style="float:right;color:{pcolor};font-weight:800">{bloom} +{entry["points"]}</span><br>'
                    f'<span style="color:{pcolor};font-weight:700">{entry["player"]}</span> · '
                    f'<span style="color:#8B9B7A;font-size:12px">{dt_str}</span></div>',
                    unsafe_allow_html=True,
                )
            st.markdown("---")
            del_opts = {
                f'{e["choreEmoji"]} {e["choreName"]} — {e["player"]} ({datetime.fromisoformat(e["date"]).strftime("%b %d %I:%M%p")})': e["id"]
                for e in reversed(wlog)
            }
            to_del = st.selectbox("Remove an entry:", ["(select)"] + list(del_opts.keys()), key="del_sel")
            if to_del != "(select)":
                if st.button("🗑️ Remove", key="do_del"):
                    data["log"] = [e for e in data["log"] if e["id"] != del_opts[to_del]]
                    save_data(data)
                    st.rerun()


# ======================== CHARTS TAB ========================
with tab_charts:
    if not data["log"]:
        st.markdown(
            '<div class="empty-state" style="margin-top:20px">'
            '📊 No data yet! Plant chores to see your garden grow over time.</div>',
            unsafe_allow_html=True,
        )
    else:
        view = st.radio("View", ["Weekly", "Monthly"], horizontal=True, key="cv", label_visibility="collapsed")

        if view == "Weekly":
            weeks = {}
            for e in data["log"]:
                d = datetime.fromisoformat(e["date"])
                iso = d.isocalendar()
                key = f"{iso[0]}-W{iso[1]}"
                label = f"W{iso[1]}"
                if key not in weeks:
                    weeks[key] = {"Week": label, "Pınar": 0, "Cris": 0, "_sort": d.timestamp()}
                weeks[key][e["player"]] += e["points"]
            chart_data = sorted(weeks.values(), key=lambda x: x["_sort"])[-8:]
        else:
            months = {}
            for e in data["log"]:
                d = datetime.fromisoformat(e["date"])
                key = f"{d.year}-{d.month:02d}"
                label = d.strftime("%b '%y")
                if key not in months:
                    months[key] = {"Month": label, "Pınar": 0, "Cris": 0, "_sort": d.timestamp()}
                months[key][e["player"]] += e["points"]
            chart_data = sorted(months.values(), key=lambda x: x["_sort"])[-6:]

        if chart_data:
            df = pd.DataFrame(chart_data)
            x_col = "Week" if view == "Weekly" else "Month"
            df = df[[x_col, "Pınar", "Cris"]].set_index(x_col)

            st.markdown('<div class="chart-box">', unsafe_allow_html=True)
            st.bar_chart(df, color=["#D4764E", "#5B8C5A"], height=300)
            st.markdown('</div>', unsafe_allow_html=True)

        # Stats
        st.markdown('<div class="sec-title">All-time garden stats</div>', unsafe_allow_html=True)
        total = len(data["log"])
        total_pts = sum(e["points"] for e in data["log"])
        p_all = sum(e["points"] for e in data["log"] if e["player"] == "Pınar")
        c_all = sum(e["points"] for e in data["log"] if e["player"] == "Cris")

        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f'<div class="g-stat"><div class="s-num">{total}</div><div class="s-label">Total chores planted</div></div>', unsafe_allow_html=True)
        with c2:
            st.markdown(f'<div class="g-stat"><div class="s-num">{total_pts}</div><div class="s-label">Total seeds earned</div></div>', unsafe_allow_html=True)

        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f'<div class="g-stat pinar-top"><div class="s-num pinar">{p_all}</div><div class="s-label">🌸 Pınar\'s all-time</div></div>', unsafe_allow_html=True)
        with c2:
            st.markdown(f'<div class="g-stat cris-top"><div class="s-num cris">{c_all}</div><div class="s-label">🌿 Cris\'s all-time</div></div>', unsafe_allow_html=True)

        if data["log"]:
            st.markdown('<div class="sec-title">Your full garden 🌳</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="garden-viz">{blooms_for_log(data["log"])}</div>', unsafe_allow_html=True)


# ======================== CHORES TAB ========================
with tab_chores:
    st.markdown('<div class="sec-title">Your chore list</div>', unsafe_allow_html=True)
    st.caption("Tap a chore to edit its name, difficulty, and repeat schedule.")

    for ch in data["chores"]:
        bloom = BLOOM_MAP.get(min(ch["points"], 5), "🌱")
        freq_label = FREQ_MAP.get(ch.get("freq", "none"), {}).get("label", "No repeat")
        freq_tag = ""
        if ch.get("freq") and ch["freq"] != "none":
            freq_tag = f' <span class="freq-tag">{freq_label}</span>'

        with st.expander(f'{ch["emoji"]} {ch["name"]}  —  {bloom} {ch["points"]} seeds'):
            new_name = st.text_input("Name", ch["name"], key=f"en_{ch['id']}")
            nc1, nc2 = st.columns(2)
            with nc1:
                new_pts = st.slider("Seeds (difficulty)", 1, 5, ch["points"], key=f"ep_{ch['id']}")
            with nc2:
                freq_vals = [f["value"] for f in FREQ_OPTIONS]
                freq_labels = [f["label"] for f in FREQ_OPTIONS]
                curr_idx = freq_vals.index(ch.get("freq", "none")) if ch.get("freq", "none") in freq_vals else 0
                new_freq_label = st.selectbox("Repeats", freq_labels, index=curr_idx, key=f"ef_{ch['id']}")
                new_freq = freq_vals[freq_labels.index(new_freq_label)]

            sc1, sc2 = st.columns(2)
            with sc1:
                if st.button("💾 Save", key=f"es_{ch['id']}", use_container_width=True):
                    for c in data["chores"]:
                        if c["id"] == ch["id"]:
                            c["name"] = new_name.strip() if new_name.strip() else c["name"]
                            c["points"] = new_pts
                            c["freq"] = new_freq
                    save_data(data)
                    st.rerun()
            with sc2:
                if st.button("🗑️ Delete", key=f"ed_{ch['id']}", use_container_width=True):
                    data["chores"] = [c for c in data["chores"] if c["id"] != ch["id"]]
                    save_data(data)
                    st.rerun()

    # Add new chore
    st.markdown("---")
    st.markdown('<div class="sec-title">Plant a new chore type 🌱</div>', unsafe_allow_html=True)

    with st.container():
        ac1, ac2 = st.columns([1, 3])
        with ac1:
            new_emoji = st.selectbox("Icon", EMOJIS, key="new_em")
        with ac2:
            new_name = st.text_input("Chore name", key="new_name", placeholder="e.g. Water the plants")

        ac3, ac4 = st.columns(2)
        with ac3:
            new_pts = st.slider("Difficulty (seeds)", 1, 5, 3, key="new_pts")
        with ac4:
            freq_labels = [f["label"] for f in FREQ_OPTIONS]
            freq_vals = [f["value"] for f in FREQ_OPTIONS]
            new_freq_l = st.selectbox("Repeats", freq_labels, key="new_freq")
            new_freq_v = freq_vals[freq_labels.index(new_freq_l)]

        if st.button("🌱 Add to garden", use_container_width=True, key="add_ch"):
            if new_name and new_name.strip():
                data["chores"].append({
                    "id": str(int(datetime.now().timestamp() * 1000)),
                    "name": new_name.strip(),
                    "points": new_pts,
                    "emoji": new_emoji,
                    "freq": new_freq_v,
                })
                save_data(data)
                st.rerun()
            else:
                st.warning("Please enter a chore name!")

    # Danger zone
    st.markdown("""
    <div class="danger-box">
        <div class="danger-title">⚠️ Reset</div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("🗑️ Reset all history", key="reset_all"):
        if st.session_state.get("confirm_reset"):
            data["log"] = []
            data["todo"] = {}
            save_data(data)
            st.session_state.confirm_reset = False
            st.rerun()
        else:
            st.session_state.confirm_reset = True
            st.warning("Are you sure? Click the button again to confirm.")
