---
type: community
cohesion: 0.16
members: 21
---

# Media

**Cohesion:** 0.16 - loosely connected
**Members:** 21 nodes

## Members
- [[AsyncSession_20]] - code
- [[Create a new media folder.]] - rationale - backend/app/api/media.py
- [[Create dummy media assets with real playable URLs for testing.]] - rationale - backend/app/api/media.py
- [[Delete a media asset.]] - rationale - backend/app/api/media.py
- [[Get all platform directories with asset counts.      Returns the full directory]] - rationale - backend/app/api/media.py
- [[Get all unique tags across assets.]] - rationale - backend/app/api/media.py
- [[Get media assets with filtering. Supports platform and content_type filters.]] - rationale - backend/app/api/media.py
- [[Media library API with platform-specific directories.]] - rationale - backend/app/api/media.py
- [[Update asset metadata (tags, name, folder, platform, content_type).]] - rationale - backend/app/api/media.py
- [[Upload a new media asset. Optionally assign to a platform directory.]] - rationale - backend/app/api/media.py
- [[User_19]] - code
- [[_seed_dummy_assets()]] - code - backend/app/api/media.py
- [[create_folder()]] - code - backend/app/api/media.py
- [[delete_asset()]] - code - backend/app/api/media.py
- [[get_folders()]] - code - backend/app/api/media.py
- [[get_media_assets()]] - code - backend/app/api/media.py
- [[get_platform_directories()]] - code - backend/app/api/media.py
- [[get_tags()]] - code - backend/app/api/media.py
- [[media.py]] - code - backend/app/api/media.py
- [[update_asset()]] - code - backend/app/api/media.py
- [[upload_asset()]] - code - backend/app/api/media.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Media
SORT file.name ASC
```

## Connections to other communities
- 7 edges to [[_COMMUNITY_Asyncsession]]
- 2 edges to [[_COMMUNITY_Asyncsession_1]]
- 1 edge to [[_COMMUNITY_Any]]

## Top bridge nodes
- [[get_media_assets()]] - degree 6, connects to 2 communities
- [[upload_asset()]] - degree 6, connects to 2 communities
- [[delete_asset()]] - degree 5, connects to 1 community
- [[get_platform_directories()]] - degree 5, connects to 1 community
- [[get_tags()]] - degree 5, connects to 1 community