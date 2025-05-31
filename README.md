# GitHub Traffic Data Fetcher

A Python script to programmatically fetch traffic analytics for all your GitHub repositories using the GitHub API.

## Features

- Fetch view statistics for all your repositories
- Get clone data and referrer information
- Display comprehensive traffic summaries
- Export detailed data to JSON format
- Secure token management via environment variables

## Prerequisites

- Python 3.6 or higher
- GitHub account with repositories
- GitHub Personal Access Token

## Installation

1. **Clone or download this repository**

2. **Install required Python packages:**
   ```bash
   pip install requests python-dotenv
   ```

3. **Create a GitHub Personal Access Token** (see instructions below)

4. **Set up environment variables** (see configuration section)

## GitHub Personal Access Token Setup

### Step 1: Navigate to Token Settings
1. Go to [GitHub.com](https://github.com) and sign in
2. Click your profile picture (top right) → **Settings**
3. Scroll down and click **Developer settings** (left sidebar)
4. Click **Personal access tokens** → **Tokens (classic)**

### Step 2: Generate New Token
1. Click **Generate new token (classic)**
2. You may need to confirm your password

### Step 3: Configure Token
1. **Note/Description:** Enter a descriptive name like "Traffic Analytics" or "Repository Stats"
2. **Expiration:** Choose an appropriate expiration date (30-90 days recommended)

### Step 4: Select Required Scopes

Choose one of the following options based on your needs:

#### Option A: Public Repositories Only
If you only want to track traffic for your public repositories:
- ✅ **public_repo** - Access public repositories

#### Option B: All Repositories (Public + Private)
If you want to track traffic for all your repositories:
- ✅ **repo** - Full control of private repositories

> **Note:** The `repo` scope includes access to public repositories as well.

### Step 5: Generate and Save Token
1. Click **Generate token**
2. **IMPORTANT:** Copy the token immediately - you won't be able to see it again!
3. Store it securely (you'll need it for the next step)

## Configuration

### Create Environment File
Create a `.env` file in the same directory as the Python script:

```env
GITHUB_TOKEN=your_personal_access_token_here
```

Replace `your_personal_access_token_here` with the token you generated above.

### Security Best Practices
- Add `.env` to your `.gitignore` file to prevent committing your token
- Never share your token or commit it to version control
- Use token expiration dates and rotate tokens regularly
- Only grant the minimum required scopes

Example `.gitignore` entry:
```gitignore
.env
*.env
```

## Usage

### Basic Usage
```bash
python github_traffic_fetcher.py
```

### What the Script Does
1. Loads your GitHub token from the `.env` file
2. Fetches all repositories associated with your account
3. Retrieves traffic data for each repository including:
   - Page views and unique visitors
   - Repository clones
   - Top referrer sources
   - Most popular content paths
4. Displays a summary in the terminal
5. Saves detailed data to `{USERNAME}_traffic_data.json`

### Sample Output
```
============================================================
GITHUB TRAFFIC SUMMARY
============================================================

my-awesome-project:
  Views (14 days): 1,234
  Unique visitors: 567
  Clones (14 days): 89

another-repository:
  Views (14 days): 456
  Unique visitors: 234
  Clones (14 days): 23

----------------------------------------
TOTALS:
Total Views: 1,690
Total Unique Visitors: 801
Total Clones: 112
----------------------------------------

Detailed data saved to LiteObject_traffic_data.json
```

## Understanding the Data

### Traffic Metrics
- **Views:** Total number of page views in the last 14 days
- **Unique Visitors:** Number of unique users who viewed the repository
- **Clones:** Number of times the repository was cloned
- **Referrers:** External sites that directed traffic to your repository

### Data Limitations
- Traffic data is only available for the **last 14 days**
- Data is only accessible for repositories you **own or have admin access to**
- GitHub updates traffic data **once per day**
- API rate limits apply (5,000 requests/hour for authenticated users)

## Troubleshooting

### Common Issues

**"GITHUB_TOKEN not found in .env file"**
- Ensure you created a `.env` file in the correct directory
- Verify the token is formatted correctly: `GITHUB_TOKEN=your_token`
- Check that there are no extra spaces around the equals sign

**"Error fetching repos: 401"**
- Your token may be expired or invalid
- Verify you selected the correct scopes when creating the token
- Try generating a new token

**"Error fetching views for [repo]: 403"**
- You may not have the required permissions for that repository
- Ensure you selected the appropriate scope (`public_repo` or `repo`)
- Some repositories may not have traffic data available

**Rate Limit Exceeded**
- GitHub API limits requests to 5,000 per hour
- Wait before making additional requests
- The script includes basic rate limit handling

### Getting Help
If you encounter issues:
1. Check that your token has the correct scopes
2. Verify your `.env` file is properly formatted
3. Ensure you have owner/admin access to the repositories
4. Check GitHub's API status at [status.github.com](https://status.github.com)

## API Reference

This script uses the following GitHub API endpoints:
- `/user/repos` - List user repositories
- `/repos/{owner}/{repo}/traffic/views` - Repository view statistics
- `/repos/{owner}/{repo}/traffic/clones` - Repository clone statistics
- `/repos/{owner}/{repo}/traffic/popular/referrers` - Top referrers
- `/repos/{owner}/{repo}/traffic/popular/paths` - Popular content paths

For more information, see the [GitHub REST API documentation](https://docs.github.com/en/rest/metrics/traffic).

## License

This project is open source and available under the MIT License.