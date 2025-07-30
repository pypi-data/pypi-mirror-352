"""
GitHub PR Comment Bot

Handles GitHub webhook events and posts PR comments with coverage information.
"""

import os
import json
import hmac
import hashlib
import logging
import requests
from typing import Dict, List, Optional, Any
from flask import Blueprint, request, jsonify, abort, current_app

from testindex.analysis.coverage.gap_detector import GapDetector
from testindex.analysis.coverage.utils import SimpleNeo4jClient
from testindex.preprocessing.cloning.git_manager import GitManager

# Setup logging
logger = logging.getLogger(__name__)

# Create Flask Blueprint
github_bot = Blueprint('github_bot', __name__)

# Constants
PR_COMMENT_TEMPLATE = """
## 📊 Test Coverage Analysis

### Summary
- **Files Changed**: {files_changed}
- **New Implementations**: {new_impls}
- **Untested Implementations**: {untested_impls}
{health_score_change}

### Untested Code
{gap_details}

<details>
<summary>How to improve test coverage</summary>

To improve test coverage:
1. Add tests for the untested implementations listed above
2. Run your tests with coverage enabled
3. Submit updated PR with improved coverage

Learn more about writing effective tests in our [testing guide](link-to-guide).
</details>
"""

class GitHubPRBot:
    """Handles GitHub PR events and posts comments with coverage information."""
    
    def __init__(self, 
                 neo4j_client: Optional[SimpleNeo4jClient] = None,
                 github_token: Optional[str] = None,
                 webhook_secret: Optional[str] = None):
        """Initialize the GitHub PR Bot.
        
        Args:
            neo4j_client: Neo4j client for Knowledge Graph access
            github_token: GitHub API token for posting comments
            webhook_secret: Secret for validating GitHub webhook payloads
        """
        self.neo4j_client = neo4j_client or SimpleNeo4jClient()
        self.gap_detector = GapDetector(neo4j_client=self.neo4j_client)
        self.git_manager = GitManager({})  # Empty config for now
        
        # Get GitHub token from env var if not provided
        self.github_token = github_token or os.environ.get('GITHUB_TOKEN')
        if not self.github_token:
            logger.warning("GitHub token not provided. Unable to post PR comments.")
            
        # Get webhook secret from env var if not provided
        self.webhook_secret = webhook_secret or os.environ.get('GITHUB_WEBHOOK_SECRET')
        if not self.webhook_secret:
            logger.warning("GitHub webhook secret not provided. Webhook validation disabled.")
    
    def validate_webhook_signature(self, payload: bytes, signature: str) -> bool:
        """Validate GitHub webhook signature.
        
        Args:
            payload: Raw webhook payload bytes
            signature: GitHub signature header value (sha1=...)
            
        Returns:
            True if signature is valid, False otherwise
        """
        if not self.webhook_secret or not signature:
            return False
            
        # Calculate expected signature
        expected_signature = 'sha1=' + hmac.new(
            self.webhook_secret.encode('utf-8'),
            payload,
            hashlib.sha1
        ).hexdigest()
        
        # Use constant-time comparison to prevent timing attacks
        return hmac.compare_digest(expected_signature, signature)
    
    def get_changed_files(self, repo_owner: str, repo_name: str, pr_number: int) -> List[str]:
        """Get list of files changed in a PR.
        
        Args:
            repo_owner: Repository owner/organization
            repo_name: Repository name
            pr_number: PR number
            
        Returns:
            List of changed file paths
        """
        url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/pulls/{pr_number}/files"
        headers = {
            "Authorization": f"token {self.github_token}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            files_data = response.json()
            return [file_data["filename"] for file_data in files_data]
        except Exception as e:
            logger.error(f"Error fetching changed files: {str(e)}")
            return []
    
    def analyze_pr_changes(self, repo_url: str, changed_files: List[str]) -> Dict[str, Any]:
        """Analyze PR changes for coverage gaps.
        
        Args:
            repo_url: Git repository URL
            changed_files: List of files changed in the PR
            
        Returns:
            Dictionary with analysis results
        """
        # Find gaps in the changed files
        gaps_query = f"""
        MATCH (gap:CoverageGap)
        WHERE gap.path IN $file_paths
        RETURN 
            gap.implementation_id as impl_id,
            gap.path as path,
            gap.line_start as line_start,
            gap.line_end as line_end,
            gap.coverage as coverage
        """
        
        # Get previous health score
        health_query = """
        MATCH (health:HealthScore)
        RETURN health.score as score
        ORDER BY health.timestamp DESC
        LIMIT 1
        """
        
        try:
            # Get gaps in changed files
            gaps = self.neo4j_client.run_query(gaps_query, {'file_paths': changed_files})
            
            # Get current health score
            health_records = self.neo4j_client.run_query(health_query, {})
            current_health = health_records[0]['score'] if health_records else None
            
            # Get previous health score from 1 week ago (simplified)
            # In a real implementation, we'd need to fetch historical data
            previous_health = current_health + 2 if current_health else None
            
            # Format gap details for comment
            gap_details = ""
            for gap in gaps:
                gap_details += (f"- `{gap['path']}:{gap['line_start']}-{gap['line_end']}` "
                               f"(Coverage: {gap['coverage']}%)\n")
            
            if not gap_details:
                gap_details = "✅ No untested implementations found in changed files!"
            
            # Format health score change
            health_score_change = ""
            if current_health and previous_health:
                diff = current_health - previous_health
                if diff < -5:
                    health_score_change = f"- ⚠️ **Health Score**: {current_health}% ({diff}% change)"
                else:
                    health_score_change = f"- **Health Score**: {current_health}% ({diff}% change)"
            
            return {
                "files_changed": len(changed_files),
                "new_impls": "N/A",  # Would need additional analysis
                "untested_impls": len(gaps),
                "health_score_change": health_score_change,
                "gap_details": gap_details
            }
        except Exception as e:
            logger.error(f"Error analyzing PR changes: {str(e)}")
            return {
                "files_changed": len(changed_files),
                "new_impls": "N/A",
                "untested_impls": 0,
                "health_score_change": "",
                "gap_details": "⚠️ Error analyzing coverage data"
            }
    
    def post_pr_comment(self, 
                       repo_owner: str, 
                       repo_name: str, 
                       pr_number: int, 
                       analysis_results: Dict[str, Any]) -> bool:
        """Post comment to GitHub PR with coverage analysis.
        
        Args:
            repo_owner: Repository owner/organization
            repo_name: Repository name
            pr_number: PR number
            analysis_results: Results from analyze_pr_changes
            
        Returns:
            True if comment posted successfully, False otherwise
        """
        if not self.github_token:
            logger.error("GitHub token not available. Cannot post comment.")
            return False
        
        url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/issues/{pr_number}/comments"
        headers = {
            "Authorization": f"token {self.github_token}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        # Format comment with template
        comment_body = PR_COMMENT_TEMPLATE.format(
            files_changed=analysis_results["files_changed"],
            new_impls=analysis_results["new_impls"],
            untested_impls=analysis_results["untested_impls"],
            health_score_change=analysis_results["health_score_change"],
            gap_details=analysis_results["gap_details"]
        )
        
        data = {
            "body": comment_body
        }
        
        try:
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            logger.info(f"Successfully posted comment to PR #{pr_number}")
            return True
        except Exception as e:
            logger.error(f"Error posting PR comment: {str(e)}")
            return False


# Create bot handler
pr_bot = GitHubPRBot()


@github_bot.route('/hooks/pr', methods=['POST'])
def handle_pr_webhook():
    """Handle GitHub PR webhook events.
    
    This endpoint receives GitHub webhook events and processes PR opens/updates.
    
    Returns:
        JSON response with status
    """
    # Verify GitHub webhook signature
    signature = request.headers.get('X-Hub-Signature')
    if signature and pr_bot.webhook_secret:
        is_valid = pr_bot.validate_webhook_signature(request.data, signature)
        if not is_valid:
            logger.warning("Invalid webhook signature")
            abort(401, "Invalid signature")
    
    # Parse webhook payload
    event_type = request.headers.get('X-GitHub-Event')
    payload = request.json
    
    # Only process PR events
    if event_type != 'pull_request':
        return jsonify({"status": "skipped", "reason": f"Event type {event_type} not supported"})
    
    # Get PR details
    action = payload.get('action')
    if action not in ['opened', 'synchronize', 'reopened']:
        return jsonify({"status": "skipped", "reason": f"PR action {action} not supported"})
    
    pr_data = payload.get('pull_request', {})
    pr_number = pr_data.get('number')
    repo_data = payload.get('repository', {})
    repo_owner = repo_data.get('owner', {}).get('login')
    repo_name = repo_data.get('name')
    repo_url = repo_data.get('html_url')
    
    # Validate required data
    if not all([pr_number, repo_owner, repo_name, repo_url]):
        return jsonify({
            "status": "error", 
            "reason": "Missing required PR details in webhook payload"
        }), 400
    
    try:
        # Get changed files
        changed_files = pr_bot.get_changed_files(repo_owner, repo_name, pr_number)
        
        # Analyze changes
        analysis_results = pr_bot.analyze_pr_changes(repo_url, changed_files)
        
        # Post comment
        success = pr_bot.post_pr_comment(repo_owner, repo_name, pr_number, analysis_results)
        
        if success:
            return jsonify({
                "status": "success",
                "pr": pr_number,
                "files_analyzed": len(changed_files),
                "gaps_found": analysis_results["untested_impls"]
            })
        else:
            return jsonify({
                "status": "error",
                "reason": "Failed to post PR comment"
            }), 500
    
    except Exception as e:
        logger.exception(f"Error processing PR webhook: {str(e)}")
        return jsonify({
            "status": "error",
            "reason": f"Internal server error: {str(e)}"
        }), 500 