from pydantic import BaseModel, HttpUrl
from datetime import date

class UploadReportSchema(BaseModel):
    url: HttpUrl


class AnalyzeRequestSchema(BaseModel):
    id: int
    status: str
    report_url: HttpUrl
    report_date: date | None
    llm_result: str | None
