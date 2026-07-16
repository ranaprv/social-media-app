"""HTML sanitizer for user-generated content."""
import bleach

ALLOWED_TAGS = [
    "p", "br", "strong", "em", "u", "s", "a", "img",
    "ul", "ol", "li", "h1", "h2", "h3", "h4", "h5", "h6",
    "blockquote", "code", "pre", "hr", "table", "thead", "tbody",
    "tr", "th", "td", "span", "div", "br",
]

ALLOWED_ATTRIBUTES = {
    "a": ["href", "title", "target"],
    "img": ["src", "alt", "width", "height"],
    "span": ["class"],
    "div": ["class"],
}


def sanitize_html(content: str) -> str:
    """Sanitize HTML content to prevent XSS attacks."""
    if not content:
        return content
    return bleach.clean(
        content,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        strip=True,
    )


def sanitize_text(content: str) -> str:
    """Strip all HTML tags from text content."""
    if not content:
        return content
    return bleach.clean(content, tags=[], strip=True)
