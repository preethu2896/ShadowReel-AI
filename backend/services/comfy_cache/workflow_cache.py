import logging
from typing import Dict, Any
import hashlib
import json

logger = logging.getLogger(__name__)

class WorkflowCacheSystem:
    """
    Caches reusable ComfyUI node graphs to optimize workflow validation and loading speed.
    """
    def __init__(self):
        self.workflow_cache: Dict[str, Dict[str, Any]] = {}

    def _generate_hash(self, workflow_data: Dict[str, Any]) -> str:
        """Generates a stable hash for a workflow dictionary."""
        workflow_str = json.dumps(workflow_data, sort_keys=True)
        return hashlib.md5(workflow_str.encode('utf-8')).hexdigest()

    def get_cached_workflow(self, workflow_data: Dict[str, Any]) -> str:
        """
        Checks if a workflow is cached. If it is, returns the cached graph ID.
        If not, caches it and returns the new ID.
        """
        workflow_hash = self._generate_hash(workflow_data)
        
        if workflow_hash in self.workflow_cache:
            logger.info(f"Cache hit for workflow {workflow_hash[:8]}")
            return self.workflow_cache[workflow_hash]["id"]
            
        workflow_id = f"graph_{workflow_hash[:8]}"
        self.workflow_cache[workflow_hash] = {
            "id": workflow_id,
            "data": workflow_data
        }
        logger.info(f"Cached new workflow graph: {workflow_id}")
        return workflow_id
        
    def validate_workflow(self, workflow_data: Dict[str, Any]) -> bool:
        """Validates a ComfyUI API-format workflow structure before attempting execution."""
        if not workflow_data or not isinstance(workflow_data, dict):
            logger.error("Invalid workflow data structure.")
            return False
            
        valid_nodes = 0
        for node_id, node_info in workflow_data.items():
            if isinstance(node_info, dict) and "class_type" in node_info and "inputs" in node_info:
                valid_nodes += 1
                
        if valid_nodes == 0:
             logger.error("Workflow does not contain any valid ComfyUI API node definitions.")
             return False
             
        logger.info(f"Workflow validated successfully with {valid_nodes} nodes.")
        return True

workflow_cache = WorkflowCacheSystem()
