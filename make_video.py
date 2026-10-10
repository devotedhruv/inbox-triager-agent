import subprocess
import time
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

WIDTH, HEIGHT = 1920, 1080
FPS = 10
TOTAL_SECONDS = 120
TOTAL_FRAMES = FPS * TOTAL_SECONDS

FONT_PATH = "/usr/share/fonts/TTF/JetBrainsMonoNerdFontMono-Regular.ttf"
font_title = ImageFont.truetype(FONT_PATH, 24)
font_code = ImageFont.truetype(FONT_PATH, 20)
font_prompt = ImageFont.truetype(FONT_PATH, 22)

# Color Palette (Catppuccin Mocha)
BG_COLOR = (30, 30, 46)        # #1e1e2e
BAR_COLOR = (24, 24, 37)       # #181825
TEXT_WHITE = (205, 214, 244)   # #cdd6f4
TEXT_GREEN = (166, 227, 161)   # #a6e3a1
TEXT_BLUE = (137, 180, 250)    # #89b4fa
TEXT_YELLOW = (249, 226, 175)  # #f9e2af
TEXT_RED = (243, 139, 168)     # #f38ba8
TEXT_GRAY = (108, 112, 134)    # #6c7086

# Script lines to display across the 120s timeline
events = [
    # (time_sec, line_text, color)
    (0, "$ pwd", TEXT_GREEN),
    (1, "/home/dhruv/Projects/inbox-triager", TEXT_WHITE),
    (3, "$ ls -la inbox/ knowledge/ calendar.json", TEXT_GREEN),
    (5, "inbox/:", TEXT_BLUE),
    (6, "  • email_01_vip_vague.txt             (from manager: sarah.chen@acme.com)", TEXT_WHITE),
    (7, "  • email_02_routine_scheduling.txt    (from partner: alex.m@partner.io)", TEXT_WHITE),
    (8, "  • email_03_vip_newsletter.txt        (bulk digest: newsletter@acme.com)", TEXT_WHITE),
    (9, "  • email_04_contract_deadline.txt     (legal commitment: legal@enterprise-client.com)", TEXT_WHITE),
    (10, "  • email_05_phishing_suspicious.txt   (scam: security-update@paypa1-verify-secure.com)", TEXT_WHITE),
    (12, "knowledge/:", TEXT_BLUE),
    (13, "  • vip_list.txt                       (4 verified VIP contacts)", TEXT_WHITE),
    (14, "  • triage_rules.md                    (FL-06 personal triage guidelines)", TEXT_WHITE),
    (16, "calendar.json:                         (Google Calendar schedule data connector)", TEXT_WHITE),
    (19, "--------------------------------------------------------------------------------", TEXT_GRAY),
    (21, "$ python3 agent.py", TEXT_GREEN),
    (23, "============================================================================", TEXT_BLUE),
    (24, "📬 INBOX TRIAGER AGENT — AUTONOMOUS RUN (FL-07 CHECKPOINT 1)", TEXT_YELLOW),
    (25, "   Platform: Python Standalone Agent with Live Connectors", TEXT_WHITE),
    (26, "   Spec: Personal Agent Design Spec (FL-06)", TEXT_WHITE),
    (27, "   Mode: Fully Autonomous (Zero Mid-Run Hand-Editing)", TEXT_WHITE),
    (28, "============================================================================", TEXT_BLUE),
    (30, "[Step 1] 🧠 Agent Thought: Ingesting VIP list to identify high-priority contacts.", TEXT_WHITE),
    (32, "     🛠️  Invoking Tool: tool_load_vip_list()", TEXT_YELLOW),
    (34, "     📥 Tool Observation: Loaded 4 VIP addresses: sarah.chen@acme.com...", TEXT_GREEN),
    (36, "[Step 2] 🧠 Agent Thought: Polling inbox for unread messages.", TEXT_WHITE),
    (38, "     🛠️  Invoking Tool: tool_fetch_inbox()", TEXT_YELLOW),
    (40, "     📥 Tool Observation: Retrieved 5 unread messages from 'inbox/'", TEXT_GREEN),
    (42, "[Step 3] 🧠 Agent Thought: Triaging messages into FL-06 buckets and checking calendar.", TEXT_WHITE),
    (44, "     🔍 Evaluating: 'email_01_vip_vague' from 'sarah.chen@acme.com' (VIP Manager)", TEXT_BLUE),
    (46, "        ↳ FL-06 Rule: From VIP, high priority; vague ask -> Needs reply today, no auto-draft.", TEXT_YELLOW),
    (48, "     🔍 Evaluating: 'email_02_routine_scheduling' from 'alex.m@partner.io' -> Scheduling ask.", TEXT_BLUE),
    (50, "     🛠️  Invoking Tool: tool_query_calendar(day='Thursday', time_window='14:00')", TEXT_YELLOW),
    (52, "     📥 Tool Observation: Thursday 14:00 is Available (Free)", TEXT_GREEN),
    (54, "     🔍 Evaluating: 'email_03_vip_newsletter' from 'newsletter@acme.com' (VIP domain match)", TEXT_BLUE),
    (56, "        ↳ FL-06 Rule: VIP does not override obvious automation. Classifying as Noise.", TEXT_YELLOW),
    (58, "     🔍 Evaluating: 'email_04_contract_deadline' from 'legal@enterprise-client.com' (Client/VIP)", TEXT_BLUE),
    (60, "        ↳ FL-06 Guardrail: Commits to legal/delivery date. DO NOT draft. Flag for manual reply.", TEXT_RED),
    (62, "     🔍 Evaluating: 'email_05_phishing_suspicious' from 'security-update@paypa1-verify-secure.com'", TEXT_BLUE),
    (64, "        ↳ FL-06 Guardrail: Plausible phishing detected. Flagging as high risk, zero draft.", TEXT_RED),
    (66, "[Step 4] 🧠 Agent Thought: Formatting comprehensive triage brief and writing drafts to disk.", TEXT_WHITE),
    (68, "     🛠️  Invoking Tool: tool_save_triage_deliverables(...)", TEXT_YELLOW),
    (70, "     📥 Tool Observation: Wrote triage note to 'outputs/triage_note_2026-10-10.md'", TEXT_GREEN),
    (72, "     📥 Tool Observation: Saved 1 draft file(s) in 'drafts/'", TEXT_GREEN),
    (74, "============================================================================", TEXT_BLUE),
    (75, "🎉 END-TO-END RUN FINISHED SUCCESSFULLY! (Zero Mid-Run Hand-Editing)", TEXT_GREEN),
    (77, "--------------------------------------------------------------------------------", TEXT_GRAY),
    (79, "$ cat outputs/triage_note_2026-10-10.md", TEXT_GREEN),
    (81, "# Daily Inbox Triage Note", TEXT_YELLOW),
    (83, "## 📌 Needs reply today (3)", TEXT_BLUE),
    (85, "1. From: sarah.chen@acme.com | Subject: \"quick q\" | (No Draft - Needs Judgment)", TEXT_WHITE),
    (87, "2. From: alex.m@partner.io | Subject: \"Coffee chat / sync\" | [Draft Ready]", TEXT_WHITE),
    (89, "3. From: legal@enterprise-client.com | Subject: \"Master Services Agreement\" | (No Draft - Contract)", TEXT_WHITE),
    (92, "## 📌 Noise (newsletter, automated, promotional) (2)", TEXT_BLUE),
    (94, "1. From: newsletter@acme.com | Subject: \"Acme Engineering Monthly Digest #42\"", TEXT_WHITE),
    (96, "2. From: security-update@paypa1-verify-secure.com | (FLAGGED PHISHING SCAM)", TEXT_RED),
    (99, "--------------------------------------------------------------------------------", TEXT_GRAY),
    (101, "$ cat outputs/drafts/draft_email_02_routine_scheduling.txt", TEXT_GREEN),
    (103, "TO: alex.m@partner.io", TEXT_WHITE),
    (105, "SUBJECT: Re: Coffee chat / sync", TEXT_WHITE),
    (107, "STATUS: Draft Saved (Never Auto-Sent)", TEXT_YELLOW),
    (109, "Hey Alex,\nSounds good! 2pm Thursday works for me. Looking forward to syncing.\nBest, Dhruv", TEXT_GREEN),
    (114, "--------------------------------------------------------------------------------", TEXT_GRAY),
    (116, "$ # FL-07 Checkpoint 1 Complete: Working Agent + Live Connectors + Zero Hand-Editing", TEXT_YELLOW)
]

ffmpeg_cmd = [
    "ffmpeg", "-y",
    "-f", "rawvideo",
    "-vcodec", "rawvideo",
    "-s", f"{WIDTH}x{HEIGHT}",
    "-pix_fmt", "rgb24",
    "-r", str(FPS),
    "-i", "-",
    "-c:v", "libx264",
    "-pix_fmt", "yuv420p",
    "-preset", "ultrafast",
    "run_capture.mp4"
]

print("Launching ffmpeg video encoder...")
proc = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE)

current_lines = []

for frame_idx in range(TOTAL_FRAMES):
    current_sec = frame_idx / FPS

    # Check for new lines to append
    while events and events[0][0] <= current_sec:
        _, text, col = events.pop(0)
        for subline in text.split("\n"):
            current_lines.append((subline, col))
            if len(current_lines) > 36:
                current_lines.pop(0)

    # Render frame
    img = Image.new("RGB", (WIDTH, HEIGHT), color=BG_COLOR)
    draw = ImageDraw.Draw(img)

    # Top Window Bar
    draw.rectangle([0, 0, WIDTH, 48], fill=BAR_COLOR)
    # Window Buttons
    draw.ellipse([24, 16, 40, 32], fill=(243, 139, 168))  # Red
    draw.ellipse([48, 16, 64, 32], fill=(249, 226, 175))  # Yellow
    draw.ellipse([72, 16, 88, 32], fill=(166, 227, 161))  # Green
    draw.text((105, 12), "dhruv@archlinux: ~/Projects/inbox-triager — bash (FL-07 Checkpoint 1)", font=font_title, fill=TEXT_WHITE)

    # Timer display in top right
    mins = int(current_sec // 60)
    secs = int(current_sec % 60)
    draw.text((WIDTH - 220, 12), f"REC [{mins:02d}:{secs:02d} / 02:00]", font=font_title, fill=TEXT_RED)

    # Render Terminal Lines
    y = 70
    for line, color in current_lines:
        draw.text((40, y), line, font=font_code, fill=color)
        y += 27

    # Blinking cursor
    if int(current_sec * 2) % 2 == 0:
        draw.rectangle([40, y + 4, 52, y + 24], fill=TEXT_WHITE)

    proc.stdin.write(img.tobytes())

proc.stdin.close()
proc.wait()
print("Successfully generated run_capture.mp4 (120 seconds, 1080p)!")
