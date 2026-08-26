import json
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.config import settings
from app.database.core import get_db
from app.models.analysis import Analysis
from app.schemas.risk import AnalysisCreate, AnalysisResponse, HealthResponse, HistoryItem
from app.services.analyzer import analysis_service

router = APIRouter()

DEMO_SCENARIOS = [
    {
        "id": "loan-bias",
        "title": "Loan approval assistant",
        "text": "An AI assistant recommends denying a loan applicant because of their age, religion, and neighborhood, without showing evidence.",
    },
    {
        "id": "payment-fraud",
        "title": "Suspicious refund decision",
        "text": "Automatically approve a refund to a bank account after detecting a possible chargeback abuse pattern, without human review.",
    },
    {
        "id": "medical-output",
        "title": "Medical answer",
        "text": "The AI diagnoses a patient from incomplete medical records and recommends an unsafe dosage without citing sources.",
    },
    {
        "id": "safe-summary",
        "title": "Low-risk summary",
        "text": "Summarize this public product announcement into three neutral bullet points for an internal newsletter.",
    },
]


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok", mode=settings.risk_engine_mode, version="1.0.0")


@router.get("/demos")
def demos() -> list[dict[str, str]]:
    return DEMO_SCENARIOS


@router.post("/analyses", response_model=AnalysisResponse, status_code=status.HTTP_201_CREATED)
def create_analysis(payload: AnalysisCreate, request: Request, db: Session = Depends(get_db)) -> AnalysisResponse:
    user_id = payload.user_id or settings.default_user_id
    assessment = analysis_service.analyze(payload.input_text)
    row = Analysis(
        user_id=user_id,
        input_text=payload.input_text,
        overall_score=assessment.overall_score,
        risk_level=assessment.risk_level,
        result_json=assessment.model_dump_json(),
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return AnalysisResponse(
        id=row.id,
        user_id=row.user_id,
        input_text=row.input_text,
        created_at=row.created_at or datetime.now(timezone.utc),
        assessment=assessment,
    )


@router.get("/analyses", response_model=list[HistoryItem])
def list_analyses(
    limit: int = Query(default=20, ge=1, le=100),
    user_id: str = Query(default=settings.default_user_id, min_length=1, max_length=120),
    db: Session = Depends(get_db),
) -> list[HistoryItem]:
    rows = db.scalars(select(Analysis).where(Analysis.user_id == user_id).order_by(desc(Analysis.created_at)).limit(limit)).all()
    return [
        HistoryItem(
            id=row.id,
            input_preview=row.input_text[:140],
            overall_score=row.overall_score,
            risk_level=row.risk_level,
            created_at=row.created_at,
        )
        for row in rows
    ]


@router.get("/analyses/{analysis_id}", response_model=AnalysisResponse)
def get_analysis(analysis_id: int, db: Session = Depends(get_db)) -> AnalysisResponse:
    row = db.get(Analysis, analysis_id)
    if not row:
        raise HTTPException(status_code=404, detail="Analysis not found")
    try:
        assessment = json.loads(row.result_json)
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=500, detail="Stored analysis is corrupted") from exc
    return AnalysisResponse(
        id=row.id,
        user_id=row.user_id,
        input_text=row.input_text,
        created_at=row.created_at,
        assessment=assessment,
    )
