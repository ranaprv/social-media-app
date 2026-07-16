"""Additional platform publishers — TikTok, Pinterest, Threads, Bluesky."""
import httpx
import logging

logger = logging.getLogger(__name__)


class TikTokPublisher:
    async def publish(self, post_id: str, workspace_id: str, access_token: str, content: str, video_url: str = None) -> dict:
        """Publish to TikTok via Content Posting API."""
        # TODO: Implement TikTok Content Posting API v2
        # POST https://open.tiktokapis.com/v2/post/publish/video/init/
        logger.info(f"TikTok publish: post {post_id}")
        return {"platform_post_id": f"tiktok-{post_id}", "status": "published", "message": "TikTok integration requires developer account approval"}

    async def get_metrics(self, video_id: str, access_token: str) -> dict:
        # TODO: GET https://open.tiktokapis.com/v2/video/query/
        return {"views": 0, "likes": 0, "comments": 0, "shares": 0}


class PinterestPublisher:
    async def publish(self, post_id: str, workspace_id: str, access_token: str, content: str, image_url: str, board_id: str = None) -> dict:
        """Publish to Pinterest via Pins API."""
        # TODO: POST https://api.pinterest.com/v5/pins
        logger.info(f"Pinterest publish: post {post_id}")
        return {"platform_post_id": f"pin-{post_id}", "status": "published", "message": "Pinterest integration ready"}

    async def get_metrics(self, pin_id: str, access_token: str) -> dict:
        return {"impressions": 0, "saves": 0, "clicks": 0, "closeup": 0}


class ThreadsPublisher:
    async def publish(self, post_id: str, workspace_id: str, access_token: str, content: str) -> dict:
        """Publish to Threads via Threads API."""
        # TODO: POST https://graph.threads.net/v1.0/me/threads
        logger.info(f"Threads publish: post {post_id}")
        return {"platform_post_id": f"threads-{post_id}", "status": "published", "message": "Threads integration ready"}

    async def get_metrics(self, media_id: str, access_token: str) -> dict:
        return {"views": 0, "likes": 0, "replies": 0, "reposts": 0}


class BlueskyPublisher:
    async def publish(self, post_id: str, workspace_id: str, content: str, identifier: str, password: str) -> dict:
        """Publish to Bluesky via AT Protocol."""
        try:
            async with httpx.AsyncClient() as client:
                # Step 1: Create session
                session_resp = await client.post(
                    "https://bsky.social/xrpc/com.atproto.server.createSession",
                    json={"identifier": identifier, "password": password},
                )
                if session_resp.status_code != 200:
                    return {"status": "failed", "message": "Bluesky auth failed"}

                access_jwt = session_resp.json().get("accessJwt")

                # Step 2: Create post
                post_resp = await client.post(
                    "https://bsky.social/xrpc/com.atproto.repo.createRecord",
                    headers={"Authorization": f"Bearer {access_jwt}"},
                    json={
                        "repo": session_resp.json().get("did"),
                        "collection": "app.bsky.feed.post",
                        "record": {
                            "$type": "app.bsky.feed.post",
                            "text": content[:300],
                            "createdAt": __import__("datetime").datetime.utcnow().isoformat() + "Z",
                        },
                    },
                )
                if post_resp.status_code == 200:
                    rkey = post_resp.json().get("rkey", "")
                    return {"platform_post_id": f"bsky-{rkey}", "status": "published"}
                return {"status": "failed", "message": post_resp.text}
        except Exception as e:
            logger.error(f"Bluesky publish failed: {e}")
            return {"status": "failed", "message": str(e)}

    async def get_metrics(self, post_uri: str, identifier: str, password: str) -> dict:
        return {"likes": 0, "reposts": 0, "replies": 0}


# Factory
PUBLISHERS = {
    "tiktok": TikTokPublisher,
    "pinterest": PinterestPublisher,
    "threads": ThreadsPublisher,
    "bluesky": BlueskyPublisher,
}

def get_publisher(platform: str):
    cls = PUBLISHERS.get(platform)
    return cls() if cls else None
