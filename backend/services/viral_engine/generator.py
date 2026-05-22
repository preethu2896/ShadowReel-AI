import random

def generate_viral_metadata(topic: str, is_short: bool) -> dict:
    """
    Mock AI engine to generate viral titles, hooks, and SEO metadata.
    In production, this would use GPT-4 or Anthropic to analyze current YouTube trends.
    """
    
    titles_long = [
        f"The TRUTH About {topic} (They Lied To You)",
        f"Why {topic} is Terrifyingly Important",
        f"I Investigated {topic} - Here's What I Found",
        f"The Dark History of {topic}",
        f"We Were Wrong About {topic}"
    ]
    
    titles_short = [
        f"The SECRETS of {topic} 🤫",
        f"You won't believe this about {topic}!",
        f"{topic} EXPLAINED in 60 seconds 🤯",
        f"The crazy history of {topic} #shorts",
    ]
    
    tags_base = [topic.lower().replace(" ", ""), "documentary", "history", "mystery", "explained", "educational"]
    
    if is_short:
        title = random.choice(titles_short)
        tags = tags_base + ["shorts", "tiktok", "viral"]
    else:
        title = random.choice(titles_long)
        tags = tags_base + ["full documentary", "video essay"]
        
    description = f"Dive deep into the mysteries of {topic}. In this AI-generated cinematic documentary, we explore the hidden truths, the dramatic history, and the shocking reality behind it all.\n\nSubscribe for more cinematic stories."
    
    chapters = "0:00 - The Hook\n1:20 - The Discovery\n4:00 - The Dark Truth\n8:30 - The Conclusion" if not is_short else ""
    
    return {
        "seo_title": title,
        "seo_description": description,
        "seo_tags": ", ".join(tags),
        "chapters": chapters
    }
