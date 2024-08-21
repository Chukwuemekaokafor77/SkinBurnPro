from project_dir.services.logging_service import log_info, log_error
from project_dir.services.classification_service import classify_image, save_classification
from project_dir.services.feedback_service import save_feedback

async def run_classification_pipeline(image, user_id):
    try:
        # Step 1: Classification
        predicted_class, confidence = await classify_image(image)

        # Step 2: Save classification results
        classification_id = await save_classification(user_id, image.filename, predicted_class, confidence)
        
        # Step 3: Gather feedback (optional)
        feedback_text = "This was accurate"  # Example feedback
        await save_feedback(user_id, classification_id, feedback_text)

        log_info(f"Pipeline successful: {predicted_class} with confidence {confidence}")
        return predicted_class, confidence
    except Exception as e:
        log_error(f"Error in classification pipeline: {str(e)}")
        raise
