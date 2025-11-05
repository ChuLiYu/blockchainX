# 🚀 Complete Setup Guide

This guide walks you through setting up the Blockchain News Daily Collector from scratch.

## Prerequisites

- A GitHub account
- Basic familiarity with Git and GitHub
- Python 3.11+ (for local testing only)

## Step-by-Step Setup

### 1️⃣ Create Your Repository

**Option A: Use This as a Template**
1. Click the "Use this template" button on GitHub
2. Name your repository (e.g., `blockchainX` or `blockchain-news-daily`)
3. Choose public or private
4. Click "Create repository from template"

**Option B: Fork This Repository**
1. Click "Fork" at the top right
2. Your fork will appear in your repositories

**Option C: Manual Setup**
1. Create a new repository on GitHub
2. Clone it locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/YOUR_REPO.git
   cd YOUR_REPO
   ```
3. Copy all files from this project into your repository

### 2️⃣ Local Testing (Optional but Recommended)

Before deploying, test the scraper locally:

```bash
# Create a virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the scraper
python scraper.py

# Check the output
ls -la data/$(date +%Y-%m-%d)/
cat data/$(date +%Y-%m-%d)/coindesk.md
```

If successful, you should see a new Markdown file with today's headlines!

### 3️⃣ Configure GitHub Secrets (Critical!)

GitHub Actions needs credentials to commit changes. Here's how to set them up:

#### A. Create a Personal Access Token (PAT)

1. Go to GitHub → **Settings** (your profile, not the repository)
2. Scroll to **Developer settings** (bottom left)
3. Click **Personal access tokens** → **Tokens (classic)**
4. Click **Generate new token** → **Generate new token (classic)**
4. Configure the token:
   - **Note**: `blockchainX-collector-token`
   - **Expiration**: 90 days or No expiration (for long-term projects)
   - **Scopes**: Check `repo` (all sub-items will be checked automatically)
6. Click **Generate token**
7. **⚠️ IMPORTANT**: Copy the token immediately! You won't see it again.

#### B. Add Secrets to Your Repository

1. Go to your repository on GitHub
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**

Add these three secrets:

| Name | Value | Example |
|------|-------|---------|
| `PAT_TOKEN` | The token you just created | `ghp_xxxxxxxxxxxxxxxxxxxx` |
| `COMMITTER_NAME` | Your name (how you want commits to appear) | `John Doe` |
| `COMMITTER_EMAIL` | Your email | `john.doe@example.com` |

**Screenshot Guide:**
```
Settings Tab
└── Secrets and variables
    └── Actions
        └── New repository secret
            ├── Name: PAT_TOKEN
            ├── Secret: ghp_xxxxxxxxxxxxx
            └── [Add secret]
```

### 4️⃣ Enable GitHub Actions

1. Go to the **Actions** tab in your repository
2. If you see a prompt "Workflows aren't being run", click **I understand, enable them**
3. You should see "Daily Blockchain News Collection" workflow listed

### 5️⃣ Test the Workflow Manually

Before waiting for the scheduled run, test it manually:

1. Go to **Actions** tab
2. Click **Daily Blockchain News Collection** workflow
3. Click **Run workflow** dropdown (top right)
4. Leave defaults and click **Run workflow**
5. Wait 30-60 seconds, refresh the page
6. Click on the running workflow to see logs
7. Check if it completes successfully ✅

### 6️⃣ Verify the Results

After the workflow completes:

1. Go to your repository's main page
2. You should see a new commit: "📰 Daily news update: YYYY-MM-DD HH:MM:SS"
3. Navigate to `data/` folder
4. You'll see a folder named with today's date
5. Inside, you'll find `coindesk.md` with the collected headlines

### 7️⃣ Check Your Contribution Graph

1. Go to your GitHub profile
2. Scroll to the contribution graph
3. You should see a green square for today! 🟩

## Advanced Configuration

### Customize Collection Schedule

Edit `.github/workflows/daily-news.yml`:

```yaml
schedule:
  # Change these times (in UTC)
  - cron: '0 0 * * *'   # Midnight
  - cron: '0 12 * * *'  # Noon
```

**Cron Format**: `minute hour day month weekday`
- `0 0 * * *` = Every day at midnight
- `0 */6 * * *` = Every 6 hours
- `0 9 * * 1-5` = Weekdays at 9 AM

Use [crontab.guru](https://crontab.guru/) to create custom schedules.

### Multiple Commits Per Day

For a richer contribution graph:

1. **Automatic**: The workflow already runs 3 times daily (00:00, 08:00, 16:00 UTC)
2. **Manual trigger**: Go to Actions → Run workflow → Enable "multiple commits" option

**⚠️ Warning**: Don't abuse this. GitHub can flag suspicious patterns. 3-4 commits per day is plenty.

### Add More News Sources

Edit `scraper.py` and add new source classes:

```python
class CoinTelegraphSource(NewsSource):
    def __init__(self):
        super().__init__("CoinTelegraph", "https://cointelegraph.com")
    
    def extract_headlines(self) -> List[Dict[str, str]]:
        # Your extraction logic here
        html = self.fetch_page(self.url)
        # ... parse HTML and return headlines
        return headlines

# Add to sources list in main()
sources = [
    CoinDeskSource(),
    CoinTelegraphSource(),  # New!
]
```

## Troubleshooting

### ❌ Workflow Fails: "Failed to push"

**Problem**: Git credentials not configured correctly.

**Solution**:
1. Check that `PAT_TOKEN` secret exists and is correct
2. Verify token has `repo` scope
3. Token hasn't expired

### ❌ "No changes to commit"

**Problem**: Scraper didn't collect any data.

**Solution**:
1. Check workflow logs for errors
2. Test locally: `python scraper.py`
3. CoinDesk website structure may have changed
4. Try again later (could be temporary network issue)

### ❌ Workflow Doesn't Run on Schedule

**Problem**: GitHub Actions might be disabled or schedule isn't triggering.

**Solution**:
1. Actions must be enabled: Settings → Actions → General → Allow all actions
2. Workflows in forks require manual enabling
3. Scheduled workflows may have 10-15 minute delay (normal)
4. Test with manual trigger first

### ❌ Python Import Errors

**Problem**: Missing dependencies.

**Solution**:
```bash
pip install -r requirements.txt
```

### ❌ Rate Limiting / 403 Errors

**Problem**: Too many requests to website.

**Solution**:
1. Reduce frequency in workflow schedule
2. Add delays in scraper: `time.sleep(5)`
3. Check website's robots.txt

## Maintenance

### Monthly Checkup

1. **Review workflow runs**: Actions tab → check recent runs for failures
2. **Test scraper locally**: `python scraper.py` to ensure still working
3. **Update dependencies**: `pip install --upgrade -r requirements.txt`
4. **Rotate tokens**: If using expiring tokens, regenerate every 90 days

### When Website Structure Changes

If headlines stop appearing:

1. Run locally to see errors: `python scraper.py`
2. Inspect the website's HTML:
   - Right-click → Inspect Element
   - Find article container classes
3. Update `CoinDeskSource.extract_headlines()` method
4. Test locally, then push changes

### Backup Your Data

The `data/` folder contains all historical collections. To backup:

```bash
# Clone your repo
git clone https://github.com/YOUR_USERNAME/YOUR_REPO.git
cd YOUR_REPO

# Data is in data/ folder
tar -czf blockchain-news-backup.tar.gz data/
```

## Best Practices

✅ **DO**:
- Test locally before deploying
- Keep schedules reasonable (2-3 times/day)
- Monitor workflow runs periodically
- Update dependencies regularly
- Document any custom changes

❌ **DON'T**:
- Run workflow every 5 minutes (wastes resources, may get flagged)
- Use unlimited commits for graph manipulation (suspicious)
- Ignore errors in workflow logs
- Hard-code credentials in code
- Scrape too aggressively (respect rate limits)

## Security Notes

🔒 **Secrets Management**:
- Never commit tokens to repository
- Use GitHub Secrets for all sensitive data
- Rotate tokens periodically
- Use minimal required permissions

🔒 **Token Permissions**:
- Only `repo` scope is needed
- Don't grant admin or delete permissions
- Create separate tokens for different projects

## Next Steps

After setup is complete:

1. ⭐ **Star this repository** if you found it useful!
2. 📊 **Watch your contribution graph** fill up over time
3. 🔧 **Customize** to add more news sources
4. 🤝 **Share** with the community
5. 🐛 **Report issues** if you find bugs

## Support & Community

- **Issues**: Report bugs or request features in [Issues](../../issues)
- **Discussions**: Share ideas in [Discussions](../../discussions)
- **Pull Requests**: Contributions welcome!

---

**Happy news collecting! 📰✨**

*If you have questions, open an issue or check existing ones first.*
