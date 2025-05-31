"""
GitHub Traffic Analyzer

This script fetches and summarizes traffic data (views, clones, referrers, and popular paths)
for all repositories owned by a specified GitHub user using the GitHub API.

Usage:
    - Set your GitHub personal access token in a .env file as GITHUB_TOKEN=your_token_here
    - Run the script to fetch and print a summary of traffic data for all repositories.
    - Detailed data is saved to a JSON file.
"""
import json
import os
import time

import requests
from dotenv import load_dotenv
from requests.exceptions import ConnectionError, ReadTimeout, RequestException


class GitHubTrafficFetcher:
    """
    A class to fetch and summarize GitHub repository traffic data for a user.

    Methods
    -------
    get_user_repos():
        Get all repositories for the authenticated user.
    get_repo_views(repo_name):
        Get view statistics for a specific repository.
    get_repo_clones(repo_name):
        Get clone statistics for a specific repository.
    get_repo_referrers(repo_name):
        Get referrer statistics for a specific repository.
    get_popular_paths(repo_name):
        Get popular paths for a specific repository.
    get_all_traffic_data():
        Get comprehensive traffic data for all repositories.
    print_summary(traffic_data):
        Print a summary of traffic data.
    """

    def __init__(self, token, username):
        """
        Initialize the GitHubTrafficFetcher.

        Parameters
        ----------
        token : str
            GitHub personal access token for authentication.
        username : str
            GitHub username whose repositories will be analyzed.
        """
        self.token = token
        self.username = username
        self.headers = {
            'Authorization': f'token {token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        self.base_url = 'https://api.github.com'
        self.timeout = 30
        self.max_retries = 3
        self.retry_delay = 2
        self.repo_delay = 2  # Increased delay between repos
        self.api_call_delay = 0.5  # Delay between API calls within same repo

        self.session = requests.Session()
        self.session.headers.update(self.headers)

        # Configure connection pooling
        adapter = requests.adapters.HTTPAdapter(
            pool_connections=1,
            pool_maxsize=1
        )
        self.session.mount('https://', adapter)

    def check_rate_limit(self, response):
        """Check GitHub rate limit headers and sleep if necessary."""
        if not response:
            return

        remaining = response.headers.get('X-RateLimit-Remaining')
        reset_time = response.headers.get('X-RateLimit-Reset')

        if remaining and int(remaining) < 50:  # Conservative threshold
            if reset_time:
                reset_timestamp = int(reset_time)
                sleep_time = max(reset_timestamp - time.time(), 0) + 5
                print(
                    f"Rate limit low ({remaining} remaining). Sleeping {sleep_time:.1f}s")
                time.sleep(sleep_time)
            else:
                print(f"Rate limit low ({remaining} remaining). Sleeping 60s")
                time.sleep(60)

    def make_request(self, url, params=None):
        """
        Make a GET request with retry logic and timeout handling.

        Parameters
        ----------
        url : str
            The URL to send the GET request to.
        params : dict, optional
            Query parameters for the request.

        Returns
        -------
        requests.Response or None
            The response object if successful, None otherwise.
        """
        for attempt in range(self.max_retries):
            try:
                response = self.session.get(
                    url, params=params, timeout=self.timeout)

                # Handle rate limiting specifically
                if response.status_code == 429:
                    retry_after = int(response.headers.get('Retry-After', 60))
                    print(
                        f"Rate limited (429). Waiting {retry_after} seconds...")
                    time.sleep(retry_after)
                    continue  # Retry without counting against max_retries

                # Check rate limit headers for proactive throttling
                self.check_rate_limit(response)

                # Reset retry delay after successful request
                self.retry_delay = 2
                return response

            except (ReadTimeout, ConnectionError) as e:
                print(f"Network error on attempt {attempt + 1}: {str(e)}")
                if attempt < self.max_retries - 1:
                    print(f"Retrying in {self.retry_delay} seconds...")
                    time.sleep(self.retry_delay)
                    self.retry_delay *= 2  # Exponential backoff
                else:
                    print("Max retries reached for network errors.")
                    return None

            except RequestException as e:
                print(f"Request failed: {str(e)}")
                return None

        return None

    def get_repo_traffic_data(self, repo_name):
        """Get all traffic data for a single repository with proper delays."""
        print(f"Fetching traffic data for: {repo_name}")

        traffic_data = {}

        # Get views
        traffic_data['views'] = self.get_repo_views(repo_name)
        time.sleep(self.api_call_delay)

        # Get clones
        traffic_data['clones'] = self.get_repo_clones(repo_name)
        time.sleep(self.api_call_delay)

        # Get referrers
        traffic_data['referrers'] = self.get_repo_referrers(repo_name)
        time.sleep(self.api_call_delay)

        # Get popular paths
        traffic_data['popular_paths'] = self.get_popular_paths(repo_name)

        return traffic_data

    def get_user_repos(self):
        """
        Get all repositories for the authenticated user.

        Returns
        -------
        list
            A list of repository objects (dicts) owned by the user.
        """
        url = f'{self.base_url}/user/repos'
        params = {'per_page': 100, 'type': 'owner'}

        repos = []
        page = 1

        while True:
            params['page'] = page
            response = self.make_request(url, params)

            if response is None:
                print("Failed to fetch repositories after retries")
                break

            if response.status_code != 200:
                print(
                    f"Error fetching repos: {response.status_code} - {response.text}")
                break

            page_repos = response.json()
            if not page_repos:
                break

            repos.extend(page_repos)
            page += 1
            time.sleep(0.5)  # Small delay between requests

        return repos

    def get_repo_views(self, repo_name):
        """
        Get view statistics for a specific repository.

        Parameters
        ----------
        repo_name : str
            The name of the repository.

        Returns
        -------
        dict or None
            View statistics for the repository, or None if an error occurs.
        """
        # Fetch view statistics for a specific repository using the GitHub API
        # Returns a dictionary with view data or None if an error occurs
        url = f'{self.base_url}/repos/{self.username}/{repo_name}/traffic/views'
        response = self.make_request(url)

        if response and response.status_code == 200:
            return response.json()
        elif response:
            print(
                f"Error fetching views for {repo_name}: {response.status_code}")
        return None

    def get_repo_clones(self, repo_name):
        """
        Get clone statistics for a specific repository.

        Parameters
        ----------
        repo_name : str
            The name of the repository.

        Returns
        -------
        dict or None
            Clone statistics for the repository, or None if an error occurs.
        """
        # Fetch clone statistics for a specific repository using the GitHub API
        # Returns a dictionary with clone data or None if an error occurs
        url = f'{self.base_url}/repos/{self.username}/{repo_name}/traffic/clones'
        response = self.make_request(url)

        if response and response.status_code == 200:
            return response.json()

        print(
            f"Error fetching clones for {repo_name}: {response.status_code}")
        return None

    def get_repo_referrers(self, repo_name):
        """
        Get referrer statistics for a specific repository.

        Parameters
        ----------
        repo_name : str
            The name of the repository.

        Returns
        -------
        list or None
            List of referrer statistics, or None if an error occurs.
        """
        # Fetch referrer statistics for a specific repository using the GitHub API
        # Returns a list of referrer data or None if an error occurs
        url = f'{self.base_url}/repos/{self.username}/{repo_name}/traffic/popular/referrers'
        response = self.make_request(url)

        if response and response.status_code == 200:
            return response.json()

        print(
            f"Error fetching referrers for {repo_name}: {response.status_code}")
        return None

    def get_popular_paths(self, repo_name):
        """
        Get popular paths for a specific repository.

        Parameters
        ----------
        repo_name : str
            The name of the repository.

        Returns
        -------
        list or None
            List of popular paths, or None if an error occurs.
        """
        # Fetch popular paths for a specific repository using the GitHub API
        # Returns a list of popular paths or None if an error occurs
        url = f'{self.base_url}/repos/{self.username}/{repo_name}/traffic/popular/paths'
        response = self.make_request(url)

        if response and response.status_code == 200:
            return response.json()

        print(
            f"Error fetching popular paths for {repo_name}: {response.status_code}")
        return None

    def get_all_traffic_data(self):
        """
        Get comprehensive traffic data for all repositories owned by the user.

        Returns
        -------
        dict
            A dictionary containing traffic data for each repository.
        """
        # Collect traffic data for all repositories owned by the user
        # Returns a dictionary with traffic data for each repository
        repos = self.get_user_repos()
        if not repos:
            print("No repositories found or failed to fetch repositories")
            return {}

        all_traffic_data = {}
        total_repos = len(repos)

        print(f"Found {total_repos} repositories. Fetching traffic data...")
        print("This may take a while due to API rate limiting...")

        for i, repo in enumerate(repos, 1):
            repo_name = repo['name']

            print(f"\n[{i}/{total_repos}] Processing: {repo_name}")

            # Store repository info
            all_traffic_data[repo_name] = {
                'repository_info': {
                    'name': repo_name,
                    'full_name': repo['full_name'],
                    'description': repo['description'],
                    'stars': repo['stargazers_count'],
                    'forks': repo['forks_count'],
                    'language': repo['language'],
                    'created_at': repo['created_at'],
                    'updated_at': repo['updated_at']
                }
            }

            # Get traffic data for this repository
            traffic_data = self.get_repo_traffic_data(repo_name)
            all_traffic_data[repo_name].update(traffic_data)

            # Progress indicator
            progress = (i / total_repos) * 100
            print(f"Progress: {progress:.1f}% complete")

            # Delay between repositories (except for the last one)
            if i < total_repos:
                print(f"Waiting {self.repo_delay}s before next repository...")
                time.sleep(self.repo_delay)

        return all_traffic_data

    def print_summary(self, all_traffic_data):
        """
        Print a summary of traffic data for all repositories.

        Parameters
        ----------
        all_traffic_data : dict
            The traffic data dictionary as returned by get_all_traffic_data().
        """
        # Initialize counters for total views, unique visitors, and clones
        total_views = 0
        total_unique_views = 0
        total_clones = 0

        # Print header for the summary
        print("\n" + "="*60)
        print("GITHUB TRAFFIC SUMMARY")
        print("="*60)

        # Iterate through each repository's data
        for repo_name, data in all_traffic_data.items():
            # Extract view and clone data for each repository
            views_data = data.get('views')
            clones_data = data.get('clones')

            # If view data is available, add to totals and print per-repo stats
            if views_data:
                repo_views = views_data.get('count', 0)
                repo_unique_views = views_data.get('uniques', 0)
                total_views += repo_views
                total_unique_views += repo_unique_views

                print(f"\n{repo_name}:")
                print(f"  Views (14 days): {repo_views}")
                print(f"  Unique visitors: {repo_unique_views}")

            # If clone data is available, add to totals and print per-repo stats
            if clones_data:
                repo_clones = clones_data.get('count', 0)
                total_clones += repo_clones
                print(f"  Clones (14 days): {repo_clones}")

        # Print overall totals for all repositories
        print("\n" + "-"*40)
        print("TOTALS:")
        print(f"Total Views: {total_views}")
        print(f"Total Unique Visitors: {total_unique_views}")
        print(f"Total Clones: {total_clones}")
        print("-"*40)


# Usage example
if __name__ == "__main__":
    # Main execution block.
    # Loads environment variables, fetches traffic data, prints a summary, and saves detailed data to a JSON file.
    load_dotenv()

    # Get token from environment variable
    TOKEN = os.getenv("GITHUB_TOKEN")
    USERNAME = "LiteObject"

    # Check if the GitHub token is available
    if not TOKEN:
        print("Error: GITHUB_TOKEN not found in .env file")
        print("Please create a .env file with: GITHUB_TOKEN=your_token_here")
        exit(1)

    # Initialize the fetcher with the token and username
    fetcher = GitHubTrafficFetcher(TOKEN, USERNAME)
    # Get traffic data for all repositories (may take a while for many repos)
    traffic_data = fetcher.get_all_traffic_data()
    # Print a summary of the traffic data
    fetcher.print_summary(traffic_data)
    # Save detailed data to a JSON file for further analysis
    with open(f'{USERNAME}_traffic_data.json', 'w', encoding='utf-8') as f:
        json.dump(traffic_data, f, indent=2)
    print(f"\nDetailed data saved to {USERNAME}_traffic_data.json")
    # Close the session to release network resources
    fetcher.session.close()
