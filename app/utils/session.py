# app/utils/session.py

from dataclasses import dataclass
from typing import Optional
from app.model.user import User

@dataclass
class Session:

    """
    Runtime session state for the currently authenticated user.
    Not persisted; used by controllers and services.
    """

    current_user: Optional[User] = None
    reset_email: Optional[str] = None
    selected_community_id: Optional[int] = None # For ADMIN users ONLY

    @property
    def is_authenticated(self) -> bool:
        return self.current_user is not None
    
    # Community management
    def set_selected_community(self, cid: int):
        self.selected_community_id = cid

    def get_effective_community(self) -> Optional[int]:
        """
        Returns:
        - selected community for admin
        - user community for technician/neighbor
        """
        if self.selected_community_id is not None:
            return self.selected_community_id
        if self.current_user:
            return self.current_user.community_id
        return None
       

    # User management
    def get_current_user(self):
        return self.current_user
    
    def set_current_user(self, user: User):
        self.current_user = user
        # Reset selected community on user change if any
        self.selected_community_id = None


    # Reset flow
    def start_reset(self, email: str):
        self.reset_email = email

    def clear_reset(self):
        self.reset_email = None     

    # Logout / clear session
    def clear(self):
        self.current_user = None
        self.reset_email = None
        self.selected_community_id = None


    def logout(self): # Alias for clear
        self.clear()
