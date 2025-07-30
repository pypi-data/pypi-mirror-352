import httpx
from fastmcp import FastMCP

HN_API_BASE = "https://hacker-news.firebaseio.com/v0"
mcp = FastMCP("MCP Hacker News Server")

@mcp.tool()
def hacker_news_trends(limit: int = 10) -> list:
    """Retrieve trending articles from Hacker News.

    Args:
        limit (int, optional): Number of articles to retrieve. Defaults to 10.

    Returns:
        list: List of article information
    """
    # Get top story IDs
    with httpx.Client() as client:
        response = client.get(f"{HN_API_BASE}/topstories.json")
        if response.status_code != 200:
            return []
        
        story_ids = response.json()[:limit]
        stories = []
        
        # Get details for each story
        for story_id in story_ids:
            response = client.get(f"{HN_API_BASE}/item/{story_id}.json")
            if response.status_code == 200:
                story = response.json()
                if story and story.get('title'):  # Add only valid stories
                    stories.append({
                        "id": str(story.get('id')),
                        "title": story.get('title'),
                        "url": story.get('url', ''),
                        "score": story.get('score', 0),
                        "by": story.get('by', ''),
                        "time": story.get('time', ''),
                        "descendants": story.get('descendants', 0)
                    })
    
    return stories

@mcp.tool()
def hacker_news_get_article(id: str) -> dict:
    """Retrieve detailed information about a specific article.

    Args:
        id (str): Article ID

    Returns:
        dict: Detailed article information including comments if available
    """
    with httpx.Client() as client:
        # Get the article
        response = client.get(f"{HN_API_BASE}/item/{id}.json")
        if response.status_code != 200:
            return {"error": "Article not found"}
        
        story = response.json()
        if not story:
            return {"error": "Article not found"}

        # Build article information
        article = {
            "id": str(story.get('id')),
            "title": story.get('title', ''),
            "url": story.get('url', ''),
            "text": story.get('text', ''),
            "score": story.get('score', 0),
            "by": story.get('by', ''),
            "time": story.get('time', ''),
            "descendants": story.get('descendants', 0)
        }

        # Get comments if available
        if story.get('kids'):
            comments = []
            for comment_id in story['kids']:
                response = client.get(f"{HN_API_BASE}/item/{comment_id}.json")
                if response.status_code == 200:
                    comment = response.json()
                    if comment and comment.get('text'):
                        comments.append({
                            "id": str(comment.get('id')),
                            "text": comment.get('text'),
                            "by": comment.get('by', ''),
                            "time": comment.get('time', '')
                        })
            article["comments"] = comments

        return article
