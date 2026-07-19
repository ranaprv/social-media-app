# How to: Generate AI Content

Use the AI Content Generator to create platform-specific posts, threads, captions, and scripts.

---

## Prerequisites

- A running instance with at least one LLM API key configured (OpenAI, Anthropic, or Google AI)
- (Optional) Brand voice configured for consistent style

---

## Basic Content Generation

1. Navigate to **Content Studio** in the sidebar
2. Enter a topic or brief description in the text area
3. Select the target platform (LinkedIn, X, Instagram, Facebook, YouTube)
4. Choose a tone (Professional, Casual, Witty, Inspirational, Educational)
5. Click **Generate**

The AI produces a post tailored to the platform's format:
- **LinkedIn**: Long-form post with hook, body paragraphs, and CTA
- **X (Twitter)**: Thread-ready format with numbered points
- **Instagram**: Caption with emoji and hashtags
- **YouTube**: Video description or script outline

---

## Writing Tools

After generation, use the writing tools panel to refine:

| Tool | What it does |
|------|-------------|
| **Rewrite** | Restyle the content while keeping the message |
| **Expand** | Add more detail and depth |
| **Summarize** | Condense to a shorter version |
| **Translate** | Convert to another language |
| **Grammar Check** | Fix grammar and punctuation |
| **Generate Hooks** | Create attention-grabbing opening lines |
| **Generate CTAs** | Add call-to-action endings |
| **Generate Hashtags** | Suggest relevant hashtags |
| **SEO Optimize** | Optimize for search visibility |
| **Tone Adjust** | Change the tone without rewriting |

---

## AI Idea Generator

Not sure what to write about? Use the Idea Generator:

1. Go to **Content Studio** → **Ideas** tab
2. Enter your industry and keywords
3. Select an audience and content category (educational, tutorials, case studies, tips)
4. Click **Generate Ideas**

The AI returns 5-10 content ideas with suggested angles and formats.

---

## Content Score

Every generated piece gets a score (0-100) across 6 dimensions:

- **Readability** — How easy it is to read
- **Emotional Impact** — How much it resonates
- **Specificity** — Concrete vs vague language
- **Originality** — Fresh angle vs generic
- **CTA Strength** — How compelling the call to action is
- **Hook Power** — How well it grabs attention

Click **Improve** on any low-scoring dimension to get specific suggestions.

---

## Content Repurposing

Turn one piece of content into multiple formats:

1. Go to **Repurpose** in the sidebar
2. Paste your source content (blog post, video transcript, article URL)
3. Select which formats to generate:
   - LinkedIn post
   - X thread
   - Facebook post
   - Instagram caption
   - Carousel copy
   - Newsletter section
   - YouTube Shorts script
   - Reel script
   - Email
4. Click **Repurpose**

Each output is formatted for its target platform.

---

## Provider Selection

The app supports multiple AI providers. You can configure which provider to use per platform:

1. Go to **Settings** → **AI Models**
2. Set your preferred provider for each platform:
   - **OpenAI** — GPT-4, GPT-4o
   - **Anthropic** — Claude 3.5 Sonnet, Claude 3 Opus
   - **Google AI** — Gemini 1.5 Pro, Gemini 1.5 Flash

Each provider has different strengths — Anthropic for nuanced writing, OpenAI for structured content, Google for fast iterations.

---

## Troubleshooting

**"No API key configured":**
- Check your `.env` file has at least one of: `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `GOOGLE_AI_API_KEY`

**Content looks generic:**
- Configure your [Brand Voice](configure-brand-voice.md) to train the AI on your style
- Be more specific in your topic description

**Rate limit errors:**
- The app uses circuit breakers for external APIs. Wait 60 seconds and try again
- Consider using a different provider if one is rate-limited
