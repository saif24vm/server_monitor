"""State persistence management."""

import json
import logging
import os


logger = logging.getLogger(__name__)

# In-memory state store (can be extended to database in future)
_state_store = {}


class StateManager:
    """Manages resident state persistence."""
    
    def __init__(self, state_file: str = "data/state.json"):
        """
        Initialize state manager.
        
        Args:
            state_file: Path to state persistence file
        """
        self.state_file = state_file
        self._load_state()
    
    def _load_state(self):
        """Load state from file if exists."""
        global _state_store
        try:
            if os.path.exists(self.state_file):
                with open(self.state_file, 'r') as f:
                    _state_store = json.load(f)
                logger.info(f"Loaded state from {self.state_file}")
            else:
                _state_store = {}
        except Exception:
            logger.warning(f"Failed to load state file {self.state_file}")
            _state_store = {}
    
    def save_state(self, resident_id: str, status: str) -> bool:
        """
        Save resident state.
        
        Args:
            resident_id: Resident identifier
            status: Current status
        
        Returns:
            bool: True if saved successfully
        """
        global _state_store
        try:
            _state_store[resident_id] = {
                "status": status,
                "timestamp": os.popen("date /T").read().strip()
            }
            with open(self.state_file, 'w') as f:
                json.dump(_state_store, f, indent=2)
            return True
        except Exception:
            logger.exception(f"Failed to save state for {resident_id}")
            return False
    
    def get_latest_state(self, resident_id: str) -> str:
        """
        Get latest state for resident.
        Initialize with API status if not found.
        
        Args:
            resident_id: Resident identifier
        
        Returns:
            str: Latest status, or None if not found
        """
        global _state_store
        if resident_id not in _state_store:
            logger.info(f"State not found for {resident_id}, will initialize on next sync")
            return None
        return _state_store[resident_id].get("status")
    
    def get_all_states(self) -> dict:
        """Get all resident states."""
        global _state_store
        return _state_store.copy()
