# Personal Agent Design Spec: Inbox Triager

**Course:** General AI Fluency — FL-06, Week 5
**Platform:** Claude Project with Gmail + Google Calendar connectors, custom skill

---

## 1. Job to Be Done

Every morning and again in the early evening, I open Gmail to a mixed pile of newsletters, automated notifications, real requests from people, and a handful of things that actually need a reply today. The job: **triage my inbox into a short, ranked action list** — what needs a reply now, what can wait, what's pure noise — and draft replies for the easy, low-stakes ones so I only have to review and send.

The agent does **not** send email on its own, delete anything, or manage my calendar beyond reading it for context. It is a sorting and drafting assistant, not an autonomous responder.

**Definition of done for the job:** I open a single triage note, spend under 5 minutes reading it, and know exactly which 3–5 emails need my personal attention today, with drafts ready for anything routine.

## 2. User and Usage Frequency

- **User:** me, sole user, personal Gmail account.
- **Frequency:** twice daily — a morning run (processes overnight mail) and an early-evening run (processes the day's mail). Roughly 10–20 emails per run on average, more on Mondays.
- **Trigger:** manual for now ("run my inbox triage") — not on an automated schedule, since Claude Projects don't currently support cron-style triggers without an external scheduler. I may move the schedule piece to n8n later, but that's out of scope for this 10-hour build.

## 3. Tools, Data, and Access Plan

| Tool/Data | Purpose | Access Plan |
|---|---|---|
| Gmail connector | Read recent/unread emails, thread context, sender history | Connect via Claude's native Gmail connector under my Google account; read + draft-creation scopes only, no send scope if Claude's connector permissions allow that granularity — if not, I accept send scope exists but the agent is instructed never to use it |
| Google Calendar connector | Check today's/this week's meetings so the agent can flag emails tied to upcoming events (e.g., "confirm the 3pm call") | Connect via Claude's native Calendar connector, read-only |
| A short **VIP list** (text file in the Project's knowledge) | Tells the agent which senders (boss, key clients, family) always count as high priority regardless of content | I maintain this manually, update as needed |
| A short **triage rules doc** (Project instructions/skill) | Encodes my personal rules: what counts as noise, what tone to use in drafts, which categories exist | Written once as part of this spec, refined after the first week of use |

No tool here requires anything beyond what Claude Projects natively supports (connectors + project knowledge files), so there's no custom API work.

## 4. Draft Instructions (Project System Prompt)

> You are my inbox triage assistant. Each run, pull unread and recent emails from Gmail (last 24 hours, or since last run) and today's calendar events. Sort every email into one of four buckets: **Needs reply today**, **Needs reply this week**, **FYI / no action**, **Noise (newsletter, automated, promotional)**. Use my VIP list — anything from a VIP is never "Noise" even if it looks automated. Cross-reference calendar: if an email relates to a meeting today, flag it under "Needs reply today" regardless of tone.
>
> For everything in "Needs reply today" that is routine (scheduling confirmations, simple yes/no, acknowledgments), draft a short reply in my voice (casual, direct, no corporate filler) and save it as a Gmail draft — do not send. For anything ambiguous, sensitive, or from someone I don't recognize, do not draft; flag it for me to write myself and say why.
>
> Output a single ranked summary: bucket headers, one line per email (sender, subject, why it's in that bucket), and a note on which ones have a draft ready. Never send an email. Never delete or archive anything. Never draft a reply that commits me to a date, a price, or a decision — flag those instead.

## 5. Five Eval Cases (defined before building)

1. **VIP + vague subject:** email from my manager, subject "quick q," one-line question. Expect: bucket = Needs reply today, no auto-draft (ambiguous ask), flagged with reason "from VIP, needs your judgment."
2. **Routine scheduling:** email asking "does 2pm Thursday work?" with my calendar free then. Expect: bucket = Needs reply today, draft created confirming 2pm, correctly cross-referenced against calendar.
3. **Newsletter from a VIP's company (edge case):** a marketing email that happens to come from a VIP's domain but is clearly automated (unsubscribe link, "no-reply" sender). Expect: bucket = Noise, VIP rule does not override obvious automation — tests that the agent isn't naively pattern-matching on domain alone.
4. **Sensitive/high-stakes ask:** email involving a contract term or a commitment ("can you confit to the Nov 1 deadline?"). Expect: bucket = Needs reply today, no draft, explicit flag: "commits you to a date — writing this yourself."
5. **Unknown sender, plausible phishing:** email with urgent tone, generic greeting, a link, from an unrecognized address. Expect: bucket = Noise or explicitly flagged as "possible phishing — do not click," never drafted, never treated as VIP.

## 6. Risks and Guardrails

**Must always confirm with me before:**
- Sending any email (agent has no send capability by design; if the connector's scope doesn't allow separating draft from send, I will treat "send" as a hard forbidden action stated in the instructions and verify manually each run for the first two weeks).
- Drafting a reply that includes a commitment (date, price, agreement, decision).

**Must never do:**
- Send, delete, or archive email.
- Modify calendar events.
- Draft a reply to an unrecognized/unverified sender.
- Treat marketing or automated mail as high priority just because of sender domain.
- Infer or fabricate context not present in the email/calendar data (e.g., don't guess at deadlines not stated).

**Known risks:**
- **False negative on urgency:** something genuinely important gets bucketed as noise. Mitigation: weekly spot-check of the "Noise" bucket for the first month.
- **Draft tone mismatch:** auto-drafts don't sound like me. Mitigation: I review every draft before sending regardless; the agent never sends unsupervised.
- **Connector over-scoping:** Gmail connector may grant send access I don't want the agent to use. Mitigation: instruction-level prohibition plus manual audit until I confirm Claude's connector permissions are read/draft-only.

## 7. Platform Choice and Justification

**Chosen: Claude Project with Gmail + Calendar connectors and a custom triage skill.**

**Alternative considered: n8n workflow.** n8n would give me a real cron trigger (no manual "run triage" step) and more granular API scoping (e.g., true read-only Gmail access, no send scope at all). I'm not choosing it now because it adds real build time — OAuth setup, node wiring, error handling — that pushes this past the ~10-hour budget for what's meant to be a scoping exercise first. A Claude Project gets me a working triager in a couple of hours using connectors I already have, so I can validate the eval cases and refine the rules doc before investing in automation. If the triage rules prove solid after a few weeks of manual runs, migrating the same instructions into an n8n agent with a schedule trigger is a natural next step — the spec (rules, buckets, guardrails) transfers directly; only the trigger and execution layer changes.
