# FandomGames Clips — GTA 6 clip channel

Context for any agent working on this project. Owner: Farrah Karls (Kenosha, WI, America/Chicago). She approves every post personally — nothing is ever published without her yes on the exact clip.

## The channel

- **Name:** FandomGames Clips — a new, faceless clip page, separate from her plant channel.
- **Platforms:** TikTok, plus a NEW YouTube Shorts channel. Do NOT use Pixel & Sprout (@pixelandsprout) — that channel is plants-only.
- **Niche:** funny moments from GTA 6 streams. One lane, kept consistent.
- **Timezone for scheduling/reporting:** America/Chicago.

## What this project does

Find GTA 6 streams and VODs, detect clip-worthy moments, and cut finished vertical clips (1080×1920, 30 fps, word-by-word burned captions with slurs/swears masked, a hook line in the opening seconds, audio normalized to −14 LUFS). The human reviews every clip, joins campaigns, and posts. The tooling prepares; the human publishes.

Pipeline: streams/trends (find what's live and what's rising) → moments (loudness spikes + hype words in the transcript, 15–40 s candidates) → cut (finished clip + metadata) → human review → human posts → payouts logged locally (numbers only as the human provides them — never invent a rate, a view count, or a payout).

Live mode: record a live YouTube/Twitch stream in segments while reading chat anonymously (Twitch IRC, no login); auto-cut around chat spikes (roughly 15 s before to 20 s after). Confirm the stream is public and legitimate first — never record leaks, pirated copies, or "play early" content.

## Origin and audit status

This is Farrah's own version of the idea behind the open-source `gtavi-claudecode` plugin by Bodila51 (MIT license). Her assistant Juno audited that plugin's code on 2026-11-19 before anything was run: network calls go only to Twitch, Kick, YouTube, and Reddit (plus one OpenCV face-detection model file from GitHub); it handles no credentials and no payments; the human approves every post. The audited version is pinned at commit `dd95d393c6f74fe2ac14b0239f8826691e5dcb0e` — do not pull updates to it without re-auditing.

Verified end-to-end on 2026-11-19: the pipeline ran on a Jynxzi "playing GTA 6 for the first time" VOD, produced 5 ranked moment candidates from a 15-minute section, and cut a finished, correctly formatted captioned clip. Output quality is postable.

`SPEC.md` in this repo is the full build spec for Farrah's standalone toolkit (FandomGames Clip Desk): same pipeline as scripts she owns, no plugin runtime needed.

## Campaigns and money rules

- Campaign sources: Whop Content Rewards (whop.com/discover, contentrewards.com) and clip.tech/clippers. Read rates and budgets from the live pages at the time — they change daily. If a number is not visible, write "unknown". Never estimate earnings.
- clip.tech pays Net 30 after a campaign ends and only if the client pays — say so plainly when reporting a campaign.
- The human joins campaigns and submits clips herself. Never sign up, accept terms, or submit on her behalf.
- Skip any campaign that asks for leaks, piracy, GTA Online money/AFK bots, or fake engagement, and say why in one line.
- Credit the streamer in every clip's caption/description.

## Working rules (Farrah's, non-negotiable)

- Nothing posts, ever, without Farrah approving the exact clip and caption.
- Copy must sound like Farrah wrote it: plain language first. Never use the phrase "Long story short".
- No credential handling: no logins, no API keys, no account passwords anywhere in this project.
- Report failures immediately and plainly — a stalled download or a crashed run gets flagged the moment it's known, never smoothed over.
- Footage sources are other creators' streams: campaign rules and streamer credit govern what may be clipped; when a campaign's rules are behind a login, ask Farrah to paste them rather than trying to sign in.
