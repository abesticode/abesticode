"""
GitHub Profile README Auto-Updater
Automatically updates star counts and last PR dates for contributed repositories.

Author: abesticode
Usage: python update_readme.py
"""

import os
import re
from datetime import datetime
from github import Github
from github import Auth


# Configuration
GITHUB_USERNAME = "abesticode"
README_PATH = "README.md"
TOP_N_REPOS = 4  # Number of top repos to display
MIN_STARS = 100  # Minimum stars for a repo to be included

# GitHub Token - set via environment variable for security
# You can create a token at: https://github.com/settings/tokens
# Required scopes: public_repo (for reading public repo data)
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")


def format_stars(stars: int) -> str:
    """Format star count to human readable format (e.g., 124k+)"""
    if stars >= 1000000:
        return f"{stars / 1000000:.1f}M+"
    elif stars >= 1000:
        return f"{stars / 1000:.0f}k+"
    else:
        return f"{stars}+"


def get_contributed_repos(g: Github, username: str, top_n: int = 10) -> list:
    """
    Fetch repositories where the user has merged PRs.
    Returns list of dicts with repo info, star count, PR count, and last PR date.
    """
    print(f"🔍 Searching for merged PRs by {username}...")
    
    # Search for merged PRs by the user (excluding their own repos)
    query = f"is:pr author:{username} is:merged -user:{username}"
    
    try:
        prs = g.search_issues(query=query, sort="updated", order="desc")
    except Exception as e:
        print(f"❌ Error searching PRs: {e}")
        return []
    
    # Aggregate PR data by repository
    repo_data = {}
    
    for pr in prs:
        repo_full_name = pr.repository.full_name
        
        if repo_full_name not in repo_data:
            repo_data[repo_full_name] = {
                "repo": pr.repository,
                "pr_count": 0,
                "last_pr_date": None,
                "stars": 0
            }
        
        repo_data[repo_full_name]["pr_count"] += 1
        
        # Track the most recent PR date
        pr_date = pr.closed_at
        if pr_date:
            if repo_data[repo_full_name]["last_pr_date"] is None:
                repo_data[repo_full_name]["last_pr_date"] = pr_date
            elif pr_date > repo_data[repo_full_name]["last_pr_date"]:
                repo_data[repo_full_name]["last_pr_date"] = pr_date
    
    print(f"📦 Found PRs in {len(repo_data)} repositories")
    
    # Fetch star counts for each repository
    results = []
    for repo_full_name, data in repo_data.items():
        try:
            repo = g.get_repo(repo_full_name)
            stars = repo.stargazers_count
            
            results.append({
                "name": repo_full_name,
                "url": f"https://github.com/{repo_full_name}",
                "stars": stars,
                "stars_formatted": format_stars(stars),
                "pr_count": data["pr_count"],
                "last_pr_date": data["last_pr_date"].strftime("%Y-%m-%d") if data["last_pr_date"] else "N/A"
            })
            
            print(f"  ⭐ {repo_full_name}: {format_stars(stars)} stars, {data['pr_count']} PRs")
            
        except Exception as e:
            print(f"  ⚠️ Could not fetch {repo_full_name}: {e}")
    
    # Sort by star count (descending), filter by min stars, and take top N
    results.sort(key=lambda x: x["stars"], reverse=True)
    # Filter repos with minimum star requirement
    results = [r for r in results if r["stars"] >= MIN_STARS]
    return results[:top_n]


def generate_table(repos: list) -> str:
    """Generate markdown table for repository contributions"""
    lines = [
        "| Repository | ⭐ Stars | PRs | Last PR |",
        "|:---|:---:|:---:|:---:|"
    ]
    
    for repo in repos:
        name = repo["name"]
        url = repo["url"]
        stars = repo["stars_formatted"]
        pr_count = repo["pr_count"]
        last_pr = repo["last_pr_date"]
        
        lines.append(f"| [{name}]({url}) | {stars} | {pr_count} | {last_pr} |")
    
    return "\n".join(lines)


def update_readme(table_content: str, readme_path: str = README_PATH) -> bool:
    """Update the README.md file with new table content and timestamp"""
    
    try:
        with open(readme_path, "r", encoding="utf-8") as f:
            content = f.read()
    except FileNotFoundError:
        print(f"❌ README file not found: {readme_path}")
        return False
    
    # Pattern to find the contributions table
    # Matches from "| Repository |" to the line before "</div>" or "---"
    pattern = r"(\| Repository \| ⭐ Stars \| PRs \| Last PR \|\n\|:---\|:---:\|:---:\|:---:\|\n(?:\|.*\|\n?)+)"
    
    match = re.search(pattern, content)
    
    if match:
        # Replace old table with new table
        new_content = content[:match.start()] + table_content + "\n" + content[match.end():]
        
        # Update the "Last updated" timestamp
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
        timestamp_pattern = r"\*🔄 Last updated: .*\*"
        new_timestamp = f"*🔄 Last updated: {timestamp}*"
        new_content = re.sub(timestamp_pattern, new_timestamp, new_content)
        
        with open(readme_path, "w", encoding="utf-8") as f:
            f.write(new_content)
        
        print(f"✅ README updated successfully!")
        print(f"🕐 Timestamp: {timestamp}")
        return True
    else:
        print("❌ Could not find the contributions table in README")
        return False


def main():
    """Main function to run the update process"""
    print("=" * 50)
    print("🚀 GitHub Profile README Auto-Updater")
    print(f"📅 Running at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    # Check for GitHub token
    if not GITHUB_TOKEN:
        print("⚠️ Warning: GITHUB_TOKEN not set. API rate limits will be very low.")
        print("   Set it with: export GITHUB_TOKEN=your_token_here")
        g = Github()
    else:
        print("🔐 Using authenticated GitHub API")
        auth = Auth.Token(GITHUB_TOKEN)
        g = Github(auth=auth)
    
    # Check rate limit
    try:
        rate_limit = g.get_rate_limit()
        remaining = rate_limit.core.remaining
        limit = rate_limit.core.limit
        print(f"📊 API Rate Limit: {remaining}/{limit}")
        
        if remaining < 10:
            print("❌ Insufficient API quota. Please wait or use a token.")
            return
    except Exception as e:
        print(f"⚠️ Could not check rate limit: {e}")
        print("   Continuing anyway...")
    
    # Get contributed repositories
    repos = get_contributed_repos(g, GITHUB_USERNAME, top_n=TOP_N_REPOS)
    
    if not repos:
        print("❌ No repository data found")
        return
    
    # Generate new table
    print("\n📝 Generating new table...")
    table = generate_table(repos)
    print(table)
    
    # Update README
    print("\n📄 Updating README.md...")
    success = update_readme(table)
    
    if success:
        print("\n✨ Done! Your README has been updated with the latest data.")
        print("   Don't forget to commit and push the changes!")
    else:
        print("\n❌ Failed to update README")


if __name__ == "__main__":
    main()
