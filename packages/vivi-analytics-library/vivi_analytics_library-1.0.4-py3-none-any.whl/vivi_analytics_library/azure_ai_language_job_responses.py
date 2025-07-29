from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel


class KeyPhraseDocument(BaseModel):
    id: str
    keyPhrases: List[str]
    warnings: List[str]


class KeyPhraseResult(BaseModel):
    documents: List[KeyPhraseDocument]
    errors: List[str]
    modelVersion: str


class KeyPhraseTaskItem(BaseModel):
    kind: str
    status: str
    results: KeyPhraseResult


class KeyPhraseTasks(BaseModel):
    completed: int
    failed: int
    inProgress: int
    total: int
    items: List[KeyPhraseTaskItem]


class KeyPhraseJobResponse(BaseModel):
    createdDateTime: datetime
    displayName: Optional[str] = None
    expirationDateTime: datetime
    jobId: str
    lastUpdatedDateTime: datetime
    status: str
    tasks: KeyPhraseTasks
    errors: List[str] = []


class SentimentScores(BaseModel):
    positive: float
    neutral: float
    negative: float


class SentimentAnalysisDocument(BaseModel):
    id: str
    sentiment: str
    confidenceScores: SentimentScores


class SentimentAnalysisResult(BaseModel):
    documents: List[SentimentAnalysisDocument]
    errors: List[str]
    modelVersion: str


class SentimentAnalysisTaskItem(BaseModel):
    kind: str
    status: str
    results: SentimentAnalysisResult


class SentimentAnalysisTasks(BaseModel):
    completed: int
    failed: int
    inProgress: int
    total: int
    items: List[SentimentAnalysisTaskItem]


class SentimentAnalysisJobResponse(BaseModel):
    createdDateTime: datetime
    displayName: Optional[str] = None
    expirationDateTime: datetime
    jobId: str
    lastUpdatedDateTime: datetime
    status: str
    tasks: SentimentAnalysisTasks
    errors: List[str] = []
