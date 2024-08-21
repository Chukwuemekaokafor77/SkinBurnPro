from fastapi import FastAPI, File, UploadFile, HTTPException, Depends, BackgroundTasks
from fastapi.security import OAuth2PasswordBearer
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import logging
from dotenv import load_dotenv
from services.auth_service import login, register, get_user_id_from_token, validate_user_access
from services.image_service import process_upload
from services.report_service import generate_report
from services.database import get_user_classifications as db_get_user_classifications
from services.classification_service import classify_image, save_classification

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, filename='app.log', filemode='a', format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = FastAPI(title="Burn Classification API", version="1.0.0")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class User(BaseModel):
    username: str
    password: str

class Classification(BaseModel):
    user_id: int
    image_name: str
    predicted_class: str
    confidence: float

@app.on_event("startup")
async def startup_event():
    logger.info("Application is starting up")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Application is shutting down")

@app.post("/login")
async def login_endpoint(user: User):
    try:
        token, user_id = await login(user.username, user.password)
        return JSONResponse(content={"access_token": token, "token_type": "bearer", "user_id": user_id})
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        raise HTTPException(status_code=401, detail="Invalid credentials")

@app.post("/register")
async def register_endpoint(user: User):
    try:
        user_id = await register(user.username, user.password)
        return JSONResponse(content={"message": "User registered successfully", "user_id": user_id})
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/predict")
async def predict(background_tasks: BackgroundTasks, token: str = Depends(oauth2_scheme), file: UploadFile = File(...)):
    try:
        user_id = await get_user_id_from_token(token)
        image = await process_upload(file)
        predicted_class, confidence = await classify_image(image)
        classification = Classification(
            user_id=user_id,
            image_name=file.filename,
            predicted_class=predicted_class,
            confidence=confidence
        )
        background_tasks.add_task(save_classification, classification)
        return JSONResponse(content={"classification": classification.dict()})
    except Exception as e:
        logger.error(f"Prediction error: {str(e)}")
        raise HTTPException(status_code=500, detail="Prediction failed")

@app.get("/classifications/{user_id}")
async def get_classifications(user_id: int, token: str = Depends(oauth2_scheme)):
    try:
        await validate_user_access(token, user_id)
        classifications = await db_get_user_classifications(user_id)
        return JSONResponse(content=classifications)
    except Exception as e:
        logger.error(f"Get classifications error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve classifications")

@app.post("/feedback")
async def feedback_endpoint(user_id: int, classification_id: int, feedback_text: str, token: str = Depends(oauth2_scheme)):
    try:
        await save_feedback(user_id, classification_id, feedback_text)
        return JSONResponse(content={"message": "Feedback submitted successfully"})
    except Exception as e:
        logger.error(f"Feedback error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to submit feedback")
