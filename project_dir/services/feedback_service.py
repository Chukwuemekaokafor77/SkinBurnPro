from .database import add_feedback
from .logging_service import log_info, log_error

async def save_feedback(user_id, classification_id, feedback_text):
    try:
        await add_feedback(user_id, classification_id, feedback_text)
        log_info(f"Feedback saved for user_id {user_id}, classification_id {classification_id}")
    except Exception as e:
        log_error(f"Failed to save feedback: {e}")
        raise
