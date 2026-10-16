# Basepoint Social: posting playbook (for Claude)

Read this before making any Basepoint post. The calendar event for each day (Google Calendar `basepointsocial@gmail.com`) has the post's brief; this file has the rules and the pipeline. Plan source: "Basepoint growth and scaling plan" research report (Oct 16, 2026).

## Weekly schedule (from Oct 19, 2026)
| Day | Time ET | Format | Pillar |
|---|---|---|---|
| Mon | 11:00 AM | Reel 30-45 s | Quick Fix: general advice for salons/gyms/spas, shown on made-up 'concept' examples |
| Tue | 12:00 PM | Carousel 6-8 slides | Owner playbook: save-worthy education |
| Wed | 6:00 PM | Reel | Before/after proof: a labeled "concept" business (a real one only with written permission) |
| Thu | 11:00 AM | Carousel | Local tips / results: Pittsburgh-flavored general tips; client results only with written permission |
| Fri | 10:00 AM | Reel or carousel (optional, skip in heavy weeks) | Behind the build: faceless, hands/desk/screen |
| Sat-Sun | none | none | Batch next week (exception: Small Business Saturday) |

## Content rules
- Brand-only: no Basepoint founder face. Show hands, desk, screen recordings, voiceover; feature client owners' faces only with consent.
- NO REAL BUSINESSES WITHOUT PERMISSION (owner's rule, Oct 16): never name, tag, screenshot, describe or use info from a real business unless that business has given written permission. Use general advice and made-up examples clearly labeled "concept".
- Keep it Pittsburgh-flavored: neighborhoods, local seasons and dates are fine. No generic stock-only posts (the "More Time For This" series ended Oct 18).
- Style: navy #1F3B73, orange #EF7B3F / #D9591A, white; IBM Plex Mono (headlines) + IBM Plex Sans (body); faint grid; crosshair logo.
- Reels: 30-45 s, hook in the first 2 s, on-screen text. Voice = Kokoro "Nicole warm-bright" mix (default in `tools/reel.py`). Label `isAiGenerated: true` only when the AI voice is used.
- Carousels: 6-8 slides, 1080x1350 PNG; last slide "Comment SAMPLE - free post in 48 hours".
- Captions: "we" voice; Pittsburgh location tag and neighborhood named in the text; max 5 hashtags; end with: Comment or DM "SAMPLE" and we'll make one post for your business, free, within 48 hours.
- Never show prices on posts (prices stay in DMs/calls).

## Owner approval for posts that name a real business (overrides the calendar prompt)
By default no post names a real business. If one ever does (a client or sample recipient who gave written permission, or a Collab), it is NOT scheduled automatically. Make it, then send the owner the video/slides + caption + the facts used and their sources, and WAIT for an explicit OK before uploading to `posts/` or scheduling in Metricool. Before sending, check every line against this list:
- Praise only. No "mistakes", "fixes", ratings below 8/10, or comparisons that make anyone look worse.
- Every claim is verifiable from their own public website, Instagram, or reviews; give the source. No guesses about their page, numbers that will go stale, or "only/best" claims we can't prove.
- The "tip" is general ("any salon can..."), never aimed at the featured business.
- No reuse of their photos, logo, or videos; recreate as Basepoint graphics.
- Confirm their Instagram handle before tagging.
- Recommend the owner DM the business before posting ("we'd love to feature you"); if they say no, swap in another business.

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
