# GitHub Profile README Auto-Updater

Script untuk mengupdate README profile GitHub secara otomatis dengan data kontribusi terbaru.

## Fitur

- ✅ Auto-update star count dari setiap repository
- ✅ Update tanggal Last PR secara akurat dari GitHub API
- ✅ Sorting berdasarkan star count (tertinggi di atas)
- ✅ Rate limit handling
- ✅ Siap di-schedule dengan cron/Task Scheduler

## Setup

### 1. Install Dependencies

```bash
cd scripts
pip install -r requirements.txt
```

### 2. Generate GitHub Token

1. Buka https://github.com/settings/tokens
2. Klik "Generate new token (classic)"
3. Beri nama seperti "readme-updater"
4. Pilih scope: `public_repo`
5. Generate dan copy token

### 3. Set Environment Variable

**Windows (PowerShell):**
```powershell
$env:GITHUB_TOKEN = "ghp_your_token_here"
```

**Windows (Permanent via System):**
```
1. Buka System Properties > Environment Variables
2. Tambah variable baru: GITHUB_TOKEN = ghp_your_token_here
```

**Linux/Mac:**
```bash
export GITHUB_TOKEN="ghp_your_token_here"
```

## Penggunaan

### Manual Run

```bash
cd c:\Users\insig\abesticode\abesticode
python scripts/update_readme.py
```

### Scheduling

#### Windows Task Scheduler

1. Buka Task Scheduler
2. Create Basic Task
3. Set trigger: Daily atau Weekly
4. Action: Start a program
   - Program: `python`
   - Arguments: `scripts/update_readme.py`
   - Start in: `c:\Users\insig\abesticode\abesticode`

#### Linux Cron (Weekly - Setiap Senin jam 9 pagi)

```bash
crontab -e
# Tambahkan:
0 9 * * 1 cd /path/to/abesticode && GITHUB_TOKEN=your_token python scripts/update_readme.py
```

#### GitHub Actions (Jika mau auto-commit juga)

Buat file `.github/workflows/update-readme.yml`:

```yaml
name: Update README

on:
  schedule:
    - cron: '0 0 * * 1'  # Setiap Senin jam 00:00 UTC
  workflow_dispatch:  # Manual trigger

jobs:
  update:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: pip install -r scripts/requirements.txt
      
      - name: Update README
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: python scripts/update_readme.py
      
      - name: Commit changes
        run: |
          git config --local user.email "action@github.com"
          git config --local user.name "GitHub Action"
          git add README.md
          git diff --quiet && git diff --staged --quiet || git commit -m "📊 Auto-update contribution stats"
          git push
```

## Output Example

```
==================================================
🚀 GitHub Profile README Auto-Updater
📅 Running at: 2025-12-31 11:45:00
==================================================
🔐 Using authenticated GitHub API
📊 API Rate Limit: 4999/5000
🔍 Searching for merged PRs by abesticode...
📦 Found PRs in 4 repositories
  ⭐ n8n-io/n8n: 166k+ stars, 1 PRs
  ⭐ langgenius/dify: 124k+ stars, 3 PRs
  ⭐ ItzCrazyKns/Perplexica: 28k+ stars, 1 PRs
  ⭐ langgenius/dify-plugins: 417+ stars, 3 PRs

📝 Generating new table...
| Repository | ⭐ Stars | PRs | Last PR |
|:---|:---:|:---:|:---:|
| [n8n-io/n8n](https://github.com/n8n-io/n8n) | 166k+ | 1 | 2025-10-23 |
...

📄 Updating README.md...
✅ README updated successfully!

✨ Done! Your README has been updated with the latest data.
   Don't forget to commit and push the changes!
```
