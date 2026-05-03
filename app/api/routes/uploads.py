from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from app.api import deps
from app.services.upload_service import upload_service
from app.utils.logger import logger

router = APIRouter()

@router.post("/meter-image/{customer_id}")
async def upload_meter_image(
    customer_id: int,
    file: UploadFile = File(...),
    current_user = Depends(deps.get_current_user)
):
    """
    Upload ảnh chụp đồng hồ nước cho một hộ dân.
    Worker gọi API này trước khi submit reading để lấy image_url.
    """
    if current_user.role not in ["admin", "worker"]:
        raise HTTPException(status_code=403, detail="Not enough privileges")

    # Validate file type
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")

    try:
        content = await file.read()
        object_name = upload_service.upload_image(
            file_data=content,
            filename=file.filename,
            customer_id=customer_id
        )
        
        logger.info(f"Image uploaded for customer {customer_id} by {current_user.username}")
        
        return {
            "image_url": object_name,
            "filename": file.filename
        }
    except Exception as e:
        logger.error(f"Upload failed: {e}")
        raise HTTPException(status_code=500, detail="Could not upload image")
