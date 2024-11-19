import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from schemas import UploadReportSchema, AnalyzeRequestSchema
from db import get_async_session, create_db_and_tables
from service import create_analyze_request
from config import config_logging
from tasks import analyze_report


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_db_and_tables()
    config_logging()
    yield


app = FastAPI(lifespan=lifespan)
logger = logging.getLogger('fastapi')


@app.post('/upload_report_url/', response_model=AnalyzeRequestSchema)
async def post_upload_report_by_url(schema: UploadReportSchema, s: AsyncSession = Depends(get_async_session)):
    request = await create_analyze_request(s, schema)
    logger.info(f"Analyze request created with {request.id=}")
    analyze_report.delay(request.id)
    logger.info(f"Task analyze_report started for {request.id=}")
    return request
