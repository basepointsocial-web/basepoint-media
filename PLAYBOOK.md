# Basepoint Social: posting playbook (for Claude)

Read this before making any Basepoint post. The calendar event for each day (Google Calendar `basepointsocial@gmail.com`) has the post's brief; this file has the rules and the pipeline. Plan source: "Basepoint growth and scaling plan" research report (Oct 16, 2026).

## Weekly schedule (from Oct 19, 2026)
| Day | Time ET | Format | Pillar |
|---|---|---|---|
| Mon | 11:00 AM | Reel 30-45 s | Pittsburgh Fix-It: praise-first look at a strong local page |
| Tue | 12:00 PM | Carousel 6-8 slides | Owner playbook: save-worthy education |
| Wed | 6:00 PM | Reel | Before/after proof: real sample recipient as Collab, else a labeled "concept" |
| Thu | 11:00 AM | Carousel / Collab | Local spotlight or client results |
| Fri | 10:00 AM | Reel or carousel (optional, skip in heavy weeks) | Behind the build: faceless, hands/desk/screen |
| Sat-Sun | none | none | Batch next week (exception: Small Business Saturday) |

## Content rules
- Brand-only: no Basepoint founder face. Show hands, desk, screen recordings, voiceover; feature client owners' faces only with consent.
- Original and Pittsburgh-specific in every post: real business names (public info), neighborhoods, local dates. No generic stock-only posts (the "More Time For This" series ended Oct 18).
- Real businesses: public info only, praise first, tag them, never call out a struggling business. Prefer strong pages NOT on the lead sheet unless the owner agreed.
- Style: navy #1F3B73, orange #EF7B3F / #D9591A, white; IBM Plex Mono (headlines) + IBM Plex Sans (body); faint grid; crosshair logo.
- Reels: 30-45 s, hook in the first 2 s, on-screen text. Voice = Kokoro "Nicole warm-bright" mix (default in `tools/reel.py`). Label `isAiGenerated: true` only when the AI voice is used.
- Carousels: 6-8 slides, 1080x1350 PNG; last slide "Comment SAMPLE - free post in 48 hours".
- Captions: "we" voice; Pittsburgh location tag and neighborhood named in the text; max 5 hashtags; end with: Comment or DM "SAMPLE" and we'll make one post for your business, free, within 48 hours.
- Never show prices on posts (prices stay in DMs/calls).

## Stories (do NOT schedule in Metricool: the free plan allows only 20 scheduled posts a month)
Make the Story image and tell the owner what sticker to add in the Instagram app:
Mon poll "Do you post on Instagram every week?" · Tue reshare carousel + question sticker "What's your biggest Instagram headache?" · Wed reshare Reel + "Reply SAMPLE" · Thu "DM SAMPLE for a free post in 48h" + link sticker · Fri behind-the-scenes or a small win.

## Pipeline
1. Setup in a fresh workspace: `bash tools/setup.sh` (installs Kokoro voice + models from GitHub releases; fonts are in `tools/fonts`).
2. Reels: write a scene spec JSON and run `python3 tools/reel.py spec.json out.mp4` (see the docstring). Real-footage Reels: `python3 tools/adbuild.py out.mp4 clip.mp4 sound.mp3 "Line"`.
3. Stock footage/sound: add `name url` lines to `jobs/fetch.txt` and push; the GitHub Action downloads them into `stock/` (Mixkit video/SFX = Mixkit License; BigSoundBank = CC0). Pull after ~90 s.
4. Check frames visually before publishing.
5. Upload finished files to `posts/YYYY-MM-DD/` and push. Public link: `https://raw.githubusercontent.com/basepointsocial-web/basepoint-media/main/posts/YYYY-MM-DD/<file>`.
6. Schedule with Metricool `createScheduledPost`, blogId `7299479`, timezone America/New_York, `autoPublish: true`, provider instagram, `instagramData.type` POST or REEL, media = the raw link(s), alt text, `videoCoverMilliseconds` for Reels. Metricool copies the file at scheduling time.
7. Send the owner the files and the caption.

Only finished post files go in this repository. Never put leads, prices, contracts or personal info here.
