# VicCouncilBot Setup

## 1. Create Bot BlueSky Account

Go to https://bsky.app and create account:
- Handle: @viccouncilbot.bsky.social
- Display Name: Victorian Council Bot
- Bio: "🏛️ Automated transparency for Victorian councils. Posting meeting agendas & minutes as they're published. Community-run, open source. Not affiliated with any government."

## 2. Create Bot GitHub Account

Create new GitHub account:
- Username: VicCouncilBot
- Email: viccouncilbot@protonmail.com (or similar)
- Bio: Link to main repo

## 3. Transfer/Fork Repository

Options:
1. Fork your current repo to bot account
2. Create new repo under bot account
3. Keep under your account but make it clear it's the bot's project

## 4. Update Repository

- Add ATTRIBUTION.md
- Update README to focus on the bot, not personal
- Add clear documentation
- Include contribution guidelines

## 5. Environment Setup

```bash
# .env file for bot
BLUESKY_HANDLE=viccouncilbot.bsky.social
BLUESKY_PASSWORD=<bot_password>
```

## 6. Initial Posts

First post from bot:
"🏛️ Victorian Council Bot is now active! I'll be posting meeting agendas and minutes from Victorian councils to improve government transparency. Starting with Melbourne and Darebin councils. Open source: [github link] #VicCouncils #OpenGov"

## 7. Deployment Options

- GitHub Actions (free, already set up)
- Small VPS under bot identity
- Free tier cloud service

This keeps everything under the bot's identity, not yours.
