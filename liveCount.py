import streamlit as st
import requests
import base64
import time
import regex as re
from datetime import datetime
from streamlit_autorefresh import st_autorefresh
import toml

# config = toml.load('secret.toml')
config = st.secrets

# ---------- CONFIG ----------
st.set_page_config(page_title="Addverb Live Emp Count", layout="wide", page_icon="https://addverb.com/wp-content/themes/onepress-child/assets/images/favicon.ico")

# ---------- API CALL ----------
def get_count_by_device_prefix():
    
    username = config["api"]["username"]
    password = config["api"]["password"]

    today_str = datetime.now().strftime("%d%m%Y")

    start_time = today_str + "000000"
    end_time = today_str + "235959"

    count_api = f"https://addverbacs.matrixvyom.com/api.svc/v2/event-ta?action=get;date-range={start_time}-{end_time};field-name=userid,edate,device_name,etime,entryexittype"

    # count_api = "https://addverbacs.matrixvyom.com/api.svc/v2/event-ta?action=get;date-range=11082025000000-11082025235959;field-name=userid,edate,device_name,etime,entryexittype"

    auth_string = f"{username}:{password}"
    base64_auth = base64.b64encode(auth_string.encode()).decode()
    headers = {"Authorization": f"Basic {base64_auth}"}

    response = requests.get(count_api, headers=headers, timeout=10)
    raw_res = response.text
    return parse_and_count_by_device_prefix(raw_res)

# ---------- PARSER ----------
def parse_and_count_by_device_prefix(raw_text):

    lines = raw_text.strip().split("\n")
    location_counts = {}

    for i in range(1, len(lines)):
        parts = lines[i].split("|")
        # parts = re.split(r"\|", lines[i])
        # print("[parts = ]", parts)
        if len(parts) < 6:
            continue

        user_id = parts[0]
        device_name = parts[2]
        entry_exit_type = parts[4]

        if device_name.startswith("Bot Valley"):
            if user_id.startswith("APP"):
                prefix = "Bot Valley APP"
            elif user_id.startswith("AD"):
                prefix = "Bot Valley AD"
            elif user_id.startswith("CN"):
                prefix = "Bot Valley CN"
            elif user_id[0].isdigit() or user_id.startswith("I"):
                prefix = "Bot Valley Emp"
            else:
                prefix = "Bot Valley"

        elif device_name.startswith("Pune"):
            prefix = "Pune"

        elif device_name.startswith("Bot Verse"):
            if user_id.startswith("APP"):
                prefix = "Bot Verse APP"
            elif user_id.startswith("AD"):
                prefix = "Bot Verse AD"
            elif user_id.startswith("CN") or user_id.startswith("Cn"):
                prefix = "Bot Verse CN"
            elif user_id[0].isdigit() or user_id.startswith("I"):
                prefix = "Bot Verse Emp"
            else:
                prefix = "Bot Verse"

        elif device_name.startswith("Skymark"):
            prefix = "Skymark"
        else:
            prefix = "Other"

        delta = 1 if entry_exit_type == "0" else -1
        location_counts[prefix] = location_counts.get(prefix, 0) + delta

    return location_counts


try:
    counts = get_count_by_device_prefix()
except Exception as e:
    st.error(f"Error fetching data: {e}")
    st.stop()

# Aggregate totals for main categories
bot_valley_total = sum(v for k, v in counts.items() if k.startswith("Bot Valley"))
bot_valley_app = sum(v for k, v in counts.items() if k.startswith("Bot Valley APP"))
bot_valley_ad = sum(v for k, v in counts.items() if k.startswith("Bot Valley AD"))
bot_valley_cn = sum(v for k, v in counts.items() if k.startswith("Bot Valley CN"))
bot_valley_contractual = bot_valley_cn + bot_valley_ad + bot_valley_app
bot_valley_emp = sum(v for k, v in counts.items() if k.startswith("Bot Valley Emp"))
bot_verse_total = sum(v for k, v in counts.items() if k.startswith("Bot Verse"))
bot_verse_app = sum(v for k, v in counts.items() if k.startswith("Bot Verse APP"))
bot_verse_ad = sum(v for k, v in counts.items() if k.startswith("Bot Verse AD"))
bot_verse_cn = sum(v for k, v in counts.items() if k.startswith("Bot Verse CN"))
bot_verse_contractual = bot_verse_cn + bot_verse_ad + bot_verse_app
bot_verse_emp = sum(v for k, v in counts.items() if k.startswith("Bot Verse Emp"))
skymark_total = counts.get("Skymark", 0)
pune_total = counts.get("Pune", 0)

# Card data
cards = [
    {"title": "Bot Valley", "count": bot_valley_total, "img": "https://addverb.com/wp-content/uploads/2023/05/Noida-Headquaters.jpg"},
    {"title": "Bot Verse", "count": bot_verse_total, "img": "https://addverb.com/wp-content/uploads/2024/02/bot-verse-building-photo-1-1-1024x567.jpg"},
    # {"title": "Skymark", "count": skymark_total, "img": "https://cdn-icons-png.flaticon.com/512/619/619034.png"},
    # {"title": "Pune", "count": pune_total, "img": "https://cdn-icons-png.flaticon.com/512/684/684908.png"},
]



st_autorefresh(interval=5000)


st.markdown(
    f"""
    <div style="width:100%; background:#ee3124;margin-top:-4%; margin-bottom:3%;display:flex; height:10vh;">
        <img style="width:15vw; margin:auto; filter: brightness(0) invert(1);" src="https://addverb.com/wp-content/uploads/2024/07/Addverb-Logo-small.png">
    </div>
    """,
    unsafe_allow_html=True
)


st.markdown(
            f"""
            <div style="
                display: flex;
                align-items: center;
                background: white;
                padding: 15px;
                border-radius: 12px;
                background: white;
                box-shadow: 0 5px 20px rgba(255, 153, 139, 0.4);
                text-align: center;
                width:80%;
                margin:auto;
                margin-bottom:3%;
                justify-content:space-between;
            ">
                <img src="{cards[0]['img']}" style="width:40%; height:30vh; object-fit:cover; border-radius: 8px;">
                <div style="width:60%;">
                    <div style="display:flex; flex-direction:column; justify-content:center; align-items:center; margin-bottom:3vh" >
                        <p style="color: #343434; font-weight:bold; font-size: 1.2vw; margin:0; text-transform: uppercase; letter-spacing: 0.5px;">Bot Valley Total</p>
                        <p style="font-size: 2vw; font-weight: bold; color: #ee3124; margin:5px 0 0 0;">{bot_valley_total}</p>
                    </div>
                    <div style="display:flex; flex-direction:row; justify-content:space-evenly; align-items:center;" >
                        <div style="display:flex; flex-direction:column; justify-content:center; align-items:center;" >
                            <p style="color: #343434;font-weight:650; line-height:1vw; font-size: 1vw; margin:0; text-transform: uppercase; letter-spacing: 0.5px;">Bot Valley <br> Employees</p>
                            <p style="font-size: 2vw; font-weight: bold; color: #ee3124; margin:5px 0 0 0;">{bot_valley_emp}</p>
                        </div>
                        <div style="display:flex; flex-direction:column; justify-content:center; align-items:center;" >
                            <p style="color: #343434;font-weight:650; line-height:1vw; font-size: 1vw; margin:0; text-transform: uppercase; letter-spacing: 0.5px;">Bot Valley <br> Apprentice</p>
                            <p style="font-size: 2vw; font-weight: bold; color: #ee3124; margin:5px 0 0 0;">{bot_valley_app}</p>
                        </div>  
                        <div style="display:flex; flex-direction:column; justify-content:center; align-items:center;" >
                            <p style="color: #343434;font-weight:650; line-height:1vw; font-size: 1vw; margin:0; text-transform: uppercase; letter-spacing: 0.5px;">Bot Valley <br> Admin</p>
                            <p style="font-size: 2vw; font-weight: bold; color: #ee3124; margin:5px 0 0 0;">{bot_valley_ad}</p>
                        </div>  
                        <div style="display:flex; flex-direction:column; justify-content:center; align-items:center;" >
                            <p style="color: #343434;font-weight:650; line-height:1vw; font-size: 1vw; margin:0; text-transform: uppercase; letter-spacing: 0.5px;">Bot Valley <br> Contractual</p>
                            <p style="font-size: 2vw; font-weight: bold; color: #ee3124; margin:5px 0 0 0;">{bot_valley_cn}</p>
                        </div>  
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )


st.markdown(
            f"""
            <div style="
                display: flex;
                align-items: center;
                background: white;
                padding: 15px;
                border-radius: 12px;
                background: white;
                box-shadow: 0 5px 20px rgba(255, 153, 139, 0.4);
                text-align: center;
                width:80%;
                margin:auto;
                margin-bottom:3%;
                justify-content:space-between;
            ">
                <img src="{cards[1]['img']}" style="width:40%; height:30vh; object-fit:cover; border-radius: 8px;">
                <div style="width:60%;">
                    <div style="display:flex; flex-direction:column; justify-content:center; align-items:center; margin-bottom:3vh" >
                        <p style="color: #343434; font-weight:bold; font-size: 1.2vw; margin:0; text-transform: uppercase; letter-spacing: 0.5px;">Bot Verse Total</p>
                        <p style="font-size: 2vw; font-weight: bold; color: #ee3124; margin:5px 0 0 0;">{bot_verse_total}</p>
                    </div>
                    <div style="display:flex; flex-direction:row; justify-content:space-evenly; align-items:center;" >
                        <div style="display:flex; flex-direction:column; justify-content:center; align-items:center;" >
                            <p style="color: #343434;font-weight:650; line-height:1vw; font-size: 1vw; margin:0; text-transform: uppercase; letter-spacing: 0.5px;">Bot Verse <br> Employees</p>
                            <p style="font-size: 2vw; font-weight: bold; color: #ee3124; margin:5px 0 0 0;">{bot_verse_emp}</p>
                        </div>
                        <div style="display:flex; flex-direction:column; justify-content:center; align-items:center;" >
                            <p style="color: #343434;font-weight:650; line-height:1vw; font-size: 1vw; margin:0; text-transform: uppercase; letter-spacing: 0.5px;">Bot Verse <br> Apprentice</p>
                            <p style="font-size: 2vw; font-weight: bold; color: #ee3124; margin:5px 0 0 0;">{bot_verse_app}</p>
                        </div> 
                        <div style="display:flex; flex-direction:column; justify-content:center; align-items:center;" >
                            <p style="color: #343434;font-weight:650; line-height:1vw; font-size: 1vw; margin:0; text-transform: uppercase; letter-spacing: 0.5px;">Bot Verse <br> Admin</p>
                            <p style="font-size: 2vw; font-weight: bold; color: #ee3124; margin:5px 0 0 0;">{bot_verse_ad}</p>
                        </div>
                        <div style="display:flex; flex-direction:column; justify-content:center; align-items:center;" >
                            <p style="color: #343434;font-weight:650; line-height:1vw; font-size: 1vw; margin:0; text-transform: uppercase; letter-spacing: 0.5px;">Bot Verse <br> Contractual</p>
                            <p style="font-size: 2vw; font-weight: bold; color: #ee3124; margin:5px 0 0 0;">{bot_verse_cn}</p>
                        </div>   
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
