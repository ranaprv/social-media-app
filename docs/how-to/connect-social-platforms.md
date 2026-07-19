# How to: Connect Social Platforms

Connect LinkedIn, X (Twitter), Instagram, Facebook, or YouTube to publish and schedule content directly from the app.

---

## Prerequisites

- A running instance of Social Media Manager
- A registered account with a workspace
- OAuth credentials for the platform you want to connect (see below)

---

## Connecting via OAuth

1. Navigate to **Accounts** in the sidebar (`/dashboard/connections`)
2. Find the platform you want to connect
3. Click **Connect**
4. You'll be redirected to the platform's authorization page
5. Grant the requested permissions
6. You'll be redirected back — the connection shows "Connected"

The app stores an access token and refresh token. Tokens refresh automatically.

---

## Platform-Specific Setup

### LinkedIn

1. Go to [LinkedIn Developer Portal](https://www.linkedin.com/developers/apps)
2. Create an app and request the **Share on LinkedIn** and **Sign In with LinkedIn** products
3. Set the redirect URI to `http://localhost:8000/api/connections/linkedin/callback`
4. Copy Client ID and Client Secret to your `.env`:

```env
LINKEDIN_CLIENT_ID=your-client-id
LINKEDIN_CLIENT_SECRET=your-client-secret
LINKEDIN_REDIRECT_URI=http://localhost:8000/api/connections/linkedin/callback
```

### X (Twitter)

1. Go to [Twitter Developer Portal](https://developer.twitter.com/en/portal)
2. Create a project and app with **OAuth 2.0** enabled
3. Set callback URL to `http://localhost:8000/api/connections/twitter/callback`
4. Copy credentials to `.env`:

```env
TWITTER_CLIENT_ID=your-client-id
TWITTER_CLIENT_SECRET=your-client-secret
```

### Instagram / Facebook

1. Go to [Facebook Developers](https://developers.facebook.com/)
2. Create an app with **Instagram Graph API** product
3. Set redirect URI to `http://localhost:8000/api/connections/facebook/callback`
4. Copy credentials to `.env`:

```env
FACEBOOK_APP_ID=your-app-id
FACEBOOK_APP_SECRET=your-app-secret
FACEBOOK_REDIRECT_URI=http://localhost:8000/api/connections/facebook/callback
```

### YouTube

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Enable the **YouTube Data API v3**
3. Create OAuth 2.0 credentials
4. Set redirect URI to `http://localhost:8000/api/connections/youtube/callback`
5. Copy credentials to `.env`:

```env
GOOGLE_CLIENT_ID=your-client-id
GOOGLE_CLIENT_SECRET=your-client-secret
```

---

## Disconnecting a Platform

1. Go to **Accounts** in the sidebar
2. Find the connected platform
3. Click **Disconnect**
4. Confirm — the app revokes the stored token

---

## Troubleshooting

**"Connection failed" after OAuth redirect:**
- Check that the redirect URI in your developer portal exactly matches what's in your `.env`
- Ensure the platform app is in "Live" mode (not sandbox/development) for Facebook/Instagram
- Verify your API keys are correct

**Token expired:**
- The app auto-refreshes tokens. If it fails, disconnect and reconnect.

**Multiple accounts per platform:**
- Currently supports one account per platform per workspace. To manage multiple accounts, create additional workspaces.
