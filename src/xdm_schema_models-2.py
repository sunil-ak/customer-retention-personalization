from typing import Literal, Optional
from pydantic import BaseModel, Field


class ChurnAnalytics(BaseModel):
  churnRiskLevel: [Literal["LOW", "MEDIUM", "HIGH"]] = Field(
      default=None,
      description=(
          "Evaluated churn risk level based on input signals:\n"
          "- HIGH: Customer explicitly shares an extremely harsh review, OR has an"
          " unresolved support ticket open >7 days, or expresses severe"
          " anger/frustration in reviews/surveys.\n"
          "- MEDIUM: Customer reports recurring issues, expresses mild"
          " disappointment with pricing/features/product, or has a ticket open 3-7"
          " days without resolution.\n"
          "- LOW: Transactional queries, routine feature requests, or general"
          " satisfaction despite minor issues."
      )
  )

  sentimentLabel: [Literal["POSITIVE", "NEUTRAL", "NEGATIVE"]] = Field(
      default=None,
      description="Overall emotional tone across survey comments and support ticket text."
  )

  primaryDriver: [str] = Field(
      default=None,
      description=(
          "Root cause category driving the risk level. Examples:"
          " 'UNRESOLVED_SUPPORT_TICKET', 'PRICING_DISSATISFACTION',"
          " 'PRODUCT_DEFECT', 'DELIVERY_DELAY', 'NONE'."
      )
  )

  llmReasoningSummary: [str] = Field(
      default=None,
      description=(
          "A 2-3 line summary citing explicit evidence from profile, event, ticket/survey excerpts that justifies the chosen churnRiskLevel."
      )
  )
