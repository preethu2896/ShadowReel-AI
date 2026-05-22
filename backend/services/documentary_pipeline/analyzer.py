import uuid
from typing import List, Dict

def generate_script_from_topic(topic: str, is_trailer: bool = False) -> str:
    """Mock AI generation of a documentary script from a topic."""
    if is_trailer:
        return f"""They thought they knew the truth about {topic}...
But some secrets... were never meant to be uncovered.
Discover the terrifying reality. Coming soon."""

    # In a real app, call OpenAI/Anthropic/LLM here
    return f"""The history of {topic} is filled with mystery and dramatic turns.
It began long ago, when the first pioneers set out to change the world.
Against all odds, they fought epic battles and overcame insurmountable challenges.
Today, the legacy of {topic} continues to inspire millions across the globe."""

def analyze_and_split_script(script: str, style: str) -> List[Dict]:
    """Analyzes a script and splits it into scenes with visual prompts."""
    # Simple heuristic: split by newlines or sentences
    paragraphs = [p.strip() for p in script.split("\n") if p.strip()]
    if not paragraphs:
        paragraphs = ["A cinematic scene showing a dark atmosphere."]
        
    scenes = []
    for i, p in enumerate(paragraphs):
        # Generate a visual prompt based on the script and style
        visual_prompt = f"Cinematic {style} shot. {p} High quality, detailed, 8k resolution, dramatic lighting."
        scenes.append({
            "order_index": i,
            "script_text": p,
            "image_prompt": visual_prompt
        })
    return scenes
