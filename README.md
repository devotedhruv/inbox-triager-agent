# Personal Inbox Triager Agent (FL-07 Checkpoint 1 MVP)

An autonomous AI agent implementing the design specification from **FL-06** (`FL06_SPEC.md`). It triages incoming email into four ranked buckets, cross-references calendar availability, applies VIP rules, and safely generates drafts without human intervention.

## Deliverables
- **Working Agent**: [`agent.py`](agent.py)
- **Build Log**: [`BUILDLOG.md`](BUILDLOG.md)
- **Raw Run Capture**: [`run_capture.mp4`](run_capture.mp4) (Unedited 2-minute Full HD recording)
- **Output Triage Note**: [`outputs/triage_note_2026-10-10.md`](outputs/triage_note_2026-10-10.md)
- **Draft Output**: [`outputs/drafts/draft_email_02_routine_scheduling.txt`](outputs/drafts/draft_email_02_routine_scheduling.txt)

## How to Run
```bash
python3 agent.py
```
