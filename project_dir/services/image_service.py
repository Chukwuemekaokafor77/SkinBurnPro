from PIL import Image
import io
import numpy as np

async def process_upload(file):
    """
    Asynchronously reads the uploaded file and opens it as an image using PIL.

    Args:
        file: The uploaded file to be processed.

    Returns:
        image: A PIL image object.
    """
    contents = await file.read()  # Read the file contents asynchronously
    image = Image.open(io.BytesIO(contents))  # Open the image from the byte stream
    return image

def preprocess_image(image, target_size=(224, 224)):
    """
    Synchronously preprocesses the image: resizing, normalizing, and expanding dimensions.

    Args:
        image: A PIL image object to be preprocessed.
        target_size: A tuple indicating the target size for resizing the image.

    Returns:
        image_array: A preprocessed numpy array ready for model prediction.
    """
    image = image.resize(target_size)  # Resize the image to the target size
    image_array = np.array(image)  # Convert the image to a numpy array
    image_array = image_array.astype(np.float32) / 255.0  # Normalize the image
    image_array = np.expand_dims(image_array, axis=0)  # Expand dimensions to add batch size
    return image_array
