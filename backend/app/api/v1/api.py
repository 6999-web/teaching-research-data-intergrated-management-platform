from fastapi import APIRouter
from app.api.v1.endpoints import auth, self_evaluation, attachments, scoring, review, president_office, publication, insight, logs, chunked_upload

api_router = APIRouter()

@api_router.get("/health")
def health_check():
    return {"status": "healthy"}

# Include authentication routes
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])

# Include teaching office routes
api_router.include_router(self_evaluation.router, prefix="/teaching-office", tags=["teaching-office"])

# Include attachment routes
api_router.include_router(attachments.router, prefix="/teaching-office", tags=["teaching-office"])

# Include chunked upload routes (任务 22.1: 文件上传断点续传)
api_router.include_router(chunked_upload.router, prefix="/chunked", tags=["chunked-upload"])

# Include scoring routes
api_router.include_router(scoring.router, prefix="/scoring", tags=["scoring"])

# Include review routes
api_router.include_router(review.router, prefix="/review", tags=["review"])

# Include president office routes
api_router.include_router(president_office.router, prefix="/president-office", tags=["president-office"])

# Include publication routes
api_router.include_router(publication.router, prefix="/publication", tags=["publication"])

# Include insight summary routes
api_router.include_router(insight.router, prefix="/insight", tags=["insight"])

# Include operation logs routes
api_router.include_router(logs.router, prefix="/logs", tags=["logs"])
