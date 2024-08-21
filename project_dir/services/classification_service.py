import os
import logging
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import load_model
from .database import add_classification, get_user_classifications as db_get_user_classifications
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
FEATURE_NAMES = os.getenv('FEATURE_NAMES', '1st degree burn,2nd degree burn,3rd degree burn').split(',')
IMG_SIZE = (224, 224)
NUM_CLASSES = len(FEATURE_NAMES)
MODEL_PATH = os.getenv('MODEL_PATH', '/project_dir/models/final_burn_classifier_model_saved')
EXPECTED_ACCURACY = float(os.getenv('EXPECTED_ACCURACY', '0.80'))

def load_pretrained_model(model_path):
    """Load a pre-trained model from the specified path."""
    try:
        model = tf.keras.models.load_model(model_path)
        logger.info(f"Model loaded successfully from {model_path}")
        return model
    except Exception as e:
        logger.error(f"Failed to load model from {model_path}: {e}")
        raise

# Load the pre-trained model
model = load_pretrained_model(MODEL_PATH)

async def classify_image(processed_image):
    """Classify the processed image using the loaded pre-trained model."""
    if model is None:
        logger.error("Model not loaded")
        raise ValueError("Model not loaded")
    
    try:
        if len(processed_image.shape) != 4:
            logger.error("Processed image does not have the correct batch dimension.")
            raise ValueError("Processed image must have a batch dimension.")
        
        predictions = model.predict(processed_image)
        predicted_class = np.argmax(predictions, axis=-1)
        confidence = np.max(predictions, axis=-1)
        
        predicted_class_name = FEATURE_NAMES[predicted_class[0]] if predicted_class[0] < len(FEATURE_NAMES) else "Unknown"
        logger.info(f"Predicted class: {predicted_class_name}, Confidence: {confidence[0]:.2f}")
        
        # Check if the confidence meets the expected accuracy
        if confidence[0] < EXPECTED_ACCURACY:
            logger.warning(f"Prediction confidence {confidence[0]:.2f} is below the expected accuracy threshold {EXPECTED_ACCURACY:.2f}")
        
        return predicted_class_name, float(confidence[0])
    except Exception as e:
        logger.error(f"Failed to classify image: {e}")
        raise

async def save_classification(classification):
    """Save the classification result to the database."""
    try:
        await add_classification(
            classification.user_id,
            classification.image_name,
            classification.predicted_class,
            classification.confidence
        )
        logger.info(f"Classification saved for user_id {classification.user_id}")
    except Exception as e:
        logger.error(f"Failed to save classification: {e}")
        raise

async def get_user_classifications(user_id):
    """Retrieve classification history for a user."""
    try:
        classifications = await db_get_user_classifications(user_id)
        logger.info(f"Retrieved {len(classifications)} classifications for user_id {user_id}")
        return classifications
    except Exception as e:
        logger.error(f"Failed to retrieve classifications: {e}")
        raise
