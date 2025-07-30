from typing import Annotated, Optional

from pydantic import BaseModel, Field

IssueID = Annotated[str, Field(..., description="The issue id", examples=["JIRA-234"], pattern=r"^[A-Z]+-\d+$")]


class QuoteModel(BaseModel):
    quote_text: str = Field(..., description="The quoted text")
    source: str = Field(..., description="The source of the quote")


class QuotesModel(BaseModel):
    quote: list[QuoteModel] = Field(..., description="A list of quote objects")


class TextQuotesModel(BaseModel):
    text: Optional[str] = Field(None, description="The main text content")
    quotes: Optional[QuotesModel] = Field(None, description="Associated quotes for the text")


class WhatModel(BaseModel):
    summary: TextQuotesModel = Field(..., description="Summary of what is to be done")
    description: TextQuotesModel = Field(..., description="Detailed description of what is to be done")


class WhoModel(BaseModel):
    stakeholders: TextQuotesModel = Field(..., description="Stakeholders involved")
    affected: TextQuotesModel = Field(..., description="Entities affected by the issue or feature")


class WhereModel(BaseModel):
    environment: TextQuotesModel = Field(..., description="Target environment for the implementation")
    components: TextQuotesModel = Field(..., description="System components involved")
    products: TextQuotesModel = Field(..., description="Products impacted or involved")


class WhyModel(BaseModel):
    purpose: TextQuotesModel = Field(..., description="Purpose of the issue or feature")
    impact: TextQuotesModel = Field(..., description="Impact of the issue or feature")


class HowModel(BaseModel):
    approach: TextQuotesModel = Field(..., description="Implementation approach")
    acceptance: TextQuotesModel = Field(..., description="Acceptance criteria")


class QuestionsModel(BaseModel):
    what: WhatModel = Field(..., description="What is being addressed")
    who: WhoModel = Field(..., description="Who is involved or affected")
    where: WhereModel = Field(..., description="Where the change applies")
    why: WhyModel = Field(..., description="Why the change is needed")
    how: HowModel = Field(..., description="How the change will be implemented")


class IssueSummaryAttributesModel(BaseModel):
    issue_id: IssueID
    summary: str = Field(..., description="High-level summary of the issue or feature")
    short: str = Field(..., description="Short summary of the issue or feature")


class SummaryRootModel(BaseModel):
    issue_summary_attributes: list[IssueSummaryAttributesModel] = Field(
        ..., description="List of issue summary attributes"
    )


class MethodologyModel(BaseModel):
    category: str = Field(..., description="Category of the methodology (e.g., Data Protection, TA0005)")
    type: str = Field(..., description="Type of methodology (e.g., Linddun, Mitre)")


class ConcernModel(BaseModel):
    short_description: str = Field(..., description="Short description of the concern")
    long_description: str = Field(..., description="Detailed description of the concern")
    methodology: MethodologyModel = Field(..., description="Methodology used for the concern")


class ControlsModel(BaseModel):
    NIST: Optional[list[str]] = Field(default=None, description="List of relevant NIST controls")
    HITRUST: Optional[list[str]] = Field(default=None, description="List of relevant HITRUST controls")
    PCI: Optional[list[str]] = Field(default=None, description="List of relevant PCI controls")
    CIS: Optional[list[str]] = Field(default=None, description="List of relevant CIS controls")


class RecommendationModel(BaseModel):
    concern: Optional[ConcernModel] = Field(None, description="Concern object, if applicable")
    recommendation: str = Field(..., description="Recommendation to address the concern")
    controls: Optional[ControlsModel] = Field(None, description="Relevant compliance controls for this recommendation")


class CaseModel(BaseModel):
    issue_id: IssueID
    fire_summary: str = Field(..., description="Summary of the case or task")
    recommendations: list[RecommendationModel] = Field(..., description="List of recommendations for the case")
