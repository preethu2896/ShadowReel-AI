import logging
from typing import Dict, Optional, List
import uuid
import json

logger = logging.getLogger(__name__)

class CreatorTemplateSystem:
    """
    Manages user-defined reusable workflows, templates, and styles for ShadowReel AI.
    Allows creators to save their favorite cinematic setups and duplicate projects.
    """
    def __init__(self):
        # In a real app, this would be a database. We use an in-memory mock for now.
        self.saved_templates: Dict[str, Dict] = {}
        self.saved_visual_styles: Dict[str, Dict] = {}
        self.saved_narration_profiles: Dict[str, Dict] = {}
        self.saved_soundtrack_presets: Dict[str, Dict] = {}
        self.projects_db: Dict[str, Dict] = {} # Mock DB for projects
        
    def save_as_template(self, creator_id: str, project_id: str, template_name: str) -> str:
        """Saves an existing project's structure as a reusable template."""
        if project_id not in self.projects_db:
            logger.warning(f"Project {project_id} not found to save as template.")
            # For demonstration, we'll create a dummy project state
            project_state = {
                "timeline_structure": ["scene_1", "scene_2", "scene_3"],
                "visual_style_id": "custom_style_1",
                "narration_profile_id": "custom_narration_1"
            }
        else:
            project_state = self.projects_db[project_id]
            
        template_id = f"tpl_{uuid.uuid4().hex[:8]}"
        self.saved_templates[template_id] = {
            "creator_id": creator_id,
            "name": template_name,
            "project_state": project_state
        }
        logger.info(f"Saved project {project_id} as template '{template_name}' ({template_id})")
        return template_id

    def duplicate_project(self, creator_id: str, project_id: str, new_name: str) -> str:
        """Duplicates an existing documentary project."""
        if project_id not in self.projects_db:
            logger.warning(f"Cannot duplicate project {project_id}, not found.")
            original_project = {"settings": {}, "scenes": []}
        else:
            original_project = self.projects_db[project_id]
            
        new_project_id = f"proj_{uuid.uuid4().hex[:8]}"
        # Deep copy imitation
        new_project = json.loads(json.dumps(original_project))
        new_project["name"] = new_name
        new_project["creator_id"] = creator_id
        
        self.projects_db[new_project_id] = new_project
        logger.info(f"Duplicated project {project_id} into {new_project_id} '{new_name}'")
        return new_project_id
        
    def save_visual_style(self, creator_id: str, style_name: str, config: Dict) -> str:
        style_id = f"vstyle_{uuid.uuid4().hex[:8]}"
        self.saved_visual_styles[style_id] = {"creator_id": creator_id, "name": style_name, "config": config}
        logger.info(f"Saved visual style '{style_name}' ({style_id})")
        return style_id

    def save_narration_profile(self, creator_id: str, profile_name: str, config: Dict) -> str:
        profile_id = f"nprof_{uuid.uuid4().hex[:8]}"
        self.saved_narration_profiles[profile_id] = {"creator_id": creator_id, "name": profile_name, "config": config}
        logger.info(f"Saved narration profile '{profile_name}' ({profile_id})")
        return profile_id
        
    def save_soundtrack_preset(self, creator_id: str, preset_name: str, config: Dict) -> str:
        preset_id = f"spres_{uuid.uuid4().hex[:8]}"
        self.saved_soundtrack_presets[preset_id] = {"creator_id": creator_id, "name": preset_name, "config": config}
        logger.info(f"Saved soundtrack preset '{preset_name}' ({preset_id})")
        return preset_id

    def apply_cinematic_preset(self, project_id: str, preset_id: str) -> bool:
        """Applies a golden preset or a saved template to a project."""
        logger.info(f"Applying cinematic preset {preset_id} to project {project_id}")
        # Implementation would merge preset configs into the project
        return True

creator_templates = CreatorTemplateSystem()
