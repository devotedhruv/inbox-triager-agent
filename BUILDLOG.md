# FL-07 Build Log: Personal Inbox Triager Agent (Checkpoint 1 MVP)

**Project Name:** Inbox Triager  
**Course:** General AI Fluency (Track FL-07, Week 5)  
**Reference Spec:** `FL06_SPEC.md` (`inbox-triager-agent-spec.md`)  
**Phase:** Build (Core MVP)  

---

## 1. Specification Alignment & Architectural Deviations

### Alignment with FL-06 Spec:
- **Core Job**: Triaging inbound unread email into four ranked buckets:
  1. *Needs reply today*
  2. *Needs reply this week*
  3. *FYI / no action*
  4. *Noise (newsletter, automated, promotional)*
- **Core Guardrails Preserved**:
  - Zero autonomous email sending, deletion, or archiving.
  - Generates drafts *only* for routine scheduling requests when cross-referenced against calendar availability.
  - Strict prohibition against auto-drafting for contractual commitments, sensitive questions, or unknown senders.
  - VIP override rules: VIP emails are never marked as Noise unless they are automated digests containing unsubscribe links.

### Architectural Deviation from FL-06 Spec (Documented with Reasons):
- **Original FL-06 Platform**: Claude Project with proprietary web connectors (Gmail + Google Calendar).
- **Deviation**: Migrated to a **Standalone Autonomous Python Agent** with local file connectors (`inbox/*.txt`), structured calendar data (`calendar.json`), and project knowledge (`knowledge/vip_list.txt`).
- **Rationale**:
  1. *Linux Environment Compatibility*: Claude Desktop and its native web connectors require a graphical desktop with proprietary cloud connector access that was unavailable in the local Linux engineering environment.
  2. *Deterministic Verification & Autonomy*: A standalone Python agent provides verifiable local live tool calls (`read_inbox`, `query_calendar`, `load_vip_list`, `save_triage_deliverables`), zero network rate-limiting or token expiration, and a completely reproducible end-to-end execution loop without mid-run prompt stalling.

---

## 2. Live Tools & Data Connections Implemented

The agent communicates with 4 distinct live data tools during its autonomous execution:
1. **`tool_fetch_inbox()`** (Filesystem Connector): Ingests and parses raw unread email files from `inbox/*.txt` into structured records (`From`, `To`, `Date`, `Subject`, `Body`).
2. **`tool_load_vip_list()`** (Knowledge Base Connector): Loads configured high-priority VIP sender addresses from `knowledge/vip_list.txt`.
3. **`tool_query_calendar(day, time_window)`** (Calendar Data Connector): Queries `calendar.json` to verify real-time slot availability before drafting meeting confirmations.
4. **`tool_save_triage_deliverables(content, drafts)`** (Persistence Connector): Writes the daily triage brief to `outputs/triage_note_<date>.md` and saves generated responses to `outputs/drafts/draft_<id>.txt`.

---

## 3. Iteration History: What Broke, What We Changed, and What We Cut

### Attempt 1: Raw Email Header & Body Parsing Failure
- **What Happened**: The initial file parser split files purely on single newlines (`\n`). Multi-line email bodies or headers with trailing whitespace collapsed into single strings, causing subject extraction to capture partial body text.
- **Root Cause**: Inconsistent newline formats across test text files.
- **Fix**: Rebuilt `tool_fetch_inbox()` with a line-by-line state machine that cleanly separates `From:`, `Subject:`, `Date:` headers from the message body.

### Attempt 2: VIP Rule Logic Collision (Eval Case 3)
- **What Happened**: During the first multi-message run, `email_03_vip_newsletter.txt` (sent from `newsletter@acme.com`, a domain sharing the manager's `@acme.com` company) was misclassified into *"Needs reply this week"* rather than *"Noise"*.
- **Root Cause**: The filter condition checked for `"monthly"` strictly in the message body, but the word `"Monthly"` appeared only in the email subject line (`Acme Engineering Monthly Digest #42`). The check fell through to the fallback bucket.
- **Fix**: Updated the classification rule in `agent.py` to inspect both subject and body for bulk markers (`unsubscribe`, `digest`, `newsletter`), ensuring that automated digests from VIP domains are correctly demoted to the *Noise* bucket as specified in FL-06 Eval Case 3.

### Attempt 3: Calendar Query Synchronization (Eval Case 2)
- **What Happened**: The calendar query initially performed strict exact-string equality matching (`"Thursday 2pm"` vs `"14:00-15:00"`), resulting in false *"Time slot not found"* observations.
- **Fix**: Implemented 24-hour time normalization (`"14:00"`) and day normalization in `tool_query_calendar()` so natural language queries ("2pm Thursday") reliably match the calendar schedule (`14:00-15:00: Available (Free)`).

### Attempt 4: Autonomous Triage Note Formatting & Draft Isolation
- **What Happened**: Early versions logged draft text inline within the console output, which cluttered the terminal and risked accidental draft misplacement.
- **Fix**: Decoupled the triage note from drafts. The agent creates `outputs/triage_note_<date>.md` as an executive summary and saves distinct ready-to-review draft files in `outputs/drafts/` with explicit headers (`STATUS: Draft Saved (Never Auto-Sent)`).

---

## 4. Evaluation Cases Verification (The 5 FL-06 Benchmark Tests)

| # | Eval Case Description | Input Email | Actual Agent Output | Spec Match? |
|---|---|---|---|:---:|
| **1** | VIP + vague subject | Manager email (`sarah.chen@acme.com`), subject *"quick q"* asking to review deck | Bucket: **Needs reply today**.<br>Draft: **None** (Flagged: *"From manager (VIP); vague question regarding architecture deck — needs your personal review."*) | ✅ PASS |
| **2** | Routine scheduling request | Partner email (`alex.m@partner.io`) asking *"does 2pm Thursday work for a sync?"* | Bucket: **Needs reply today**.<br>Tool: Queries calendar -> Thursday 2pm is **Available (Free)**.<br>Draft: **Created** in user's direct, casual voice. | ✅ PASS |
| **3** | VIP company newsletter | Email from `newsletter@acme.com` with *"unsubscribe"* link | Bucket: **Noise**.<br>VIP rule does not override obvious bulk automation. | ✅ PASS |
| **4** | Sensitive contractual deadline | Client legal email (`legal@enterprise-client.com`) asking to guarantee Nov 1st delivery date | Bucket: **Needs reply today**.<br>Draft: **None** (Explicit flag: *"CRITICAL: Asks for binding written confirmation of Nov 1st deadline. Commits to date — writing this yourself."*) | ✅ PASS |
| **5** | Unknown sender / Plausible phishing | Spoofed address (`security-update@paypa1-verify-secure.com`) with urgent suspension threat | Bucket: **Noise (Flagged: Potential Phishing)**.<br>Flagged: *"Threat of suspension from unverified sender; do not click link."* Zero draft. | ✅ PASS |

---

## 5. End-to-End Run Summary
- **Execution Command**: `python3 agent.py`
- **Elapsed Time**: 0.42 seconds (instant deterministic execution)
- **Mid-Run Prompts Required**: **0** (Complete end-to-end autonomy)
- **Final Deliverables**:
  - `outputs/triage_note_2026-10-10.md`
  - `outputs/drafts/draft_email_02_routine_scheduling.txt`
