from functools import lru_cache
import json
from pathlib import Path
from typing import Any

from mcp.server.fastmcp import FastMCP
from pydantic import ValidationError

from prime_mcp.operations import CaseModel, IssueID, IssueSummaryAttributesModel
from pydantic_ai import format_as_xml

RESOURCES = Path(__file__).parent / "data"
RECOMMENDATIONS = RESOURCES / "recommendation.json"
SUMMARY = RESOURCES / "summary.json"
CODE_GUIDELINE = RESOURCES / "code_guideline.xml"
INSTRUCTIONS = RESOURCES / "instructions.txt"


@lru_cache(maxsize=1)
def load_code_guideline() -> str:
    with open(CODE_GUIDELINE) as f:
        return f.read()


@lru_cache(maxsize=1)
def load_recommendations() -> dict[str, Any]:
    with open(RECOMMENDATIONS) as f:
        try:
            data = json.load(f)
            model = CaseModel.model_validate(data)
            return model.model_dump()
            # return format_as_xml(model, include_root_tag=False, indent=None, item_tag="item", root_tag="data")
        except ValidationError as e:
            raise ValueError(f"Invalid JSON: {e}") from e


@lru_cache(maxsize=1)
def load_summary() -> dict[str, Any]:
    with open(SUMMARY) as f:
        data = json.load(f)
        model = IssueSummaryAttributesModel.model_validate(data)
        return model.model_dump()
        # return format_as_xml(model, include_root_tag=False, indent=None, item_tag="item", root_tag="data")


async def main():
    mcp = FastMCP(
        "Prime-MCP",
        instructions=INSTRUCTIONS.read_text(),
    )

    @mcp.tool()
    def issue_summary() -> dict[str, Any]:
        """Summarize an issue or ticket.
        Use this tool to summarize an issue when you need to provide a high-level overview of the issue.
        """
        issue_id = "JIRA-123"
        print(f"Loading issue summary for {issue_id}")
        return load_summary()

    @mcp.tool()
    def recommendations() -> dict[str, Any]:
        """Security Concerns and Recommendations for an issue or ticket.
        Use this tool when you need to:
        - Identify concerns and recommendations for an issue
        - Provide a detailed description of the issue and the recommendations to address it
        - verify implementation are aligned with the recommendations
        - when you generate code and you need to consider security
        Example response structure:
        {
            "issue_id": "JIRA-123",
            "fire_summary": "Critical feature to prevent unintended duplicate charges",
            "recommendations": [
                {
                    "concern": {
                        "short_description": "Idempotency keys could be guessed or brute-forced",
                        "long_description": "If idempotency keys are predictable or follow a pattern, malicious actors could attempt to guess valid keys and replay transactions, potentially leading to transaction confusion or denial of service.",
                        "methodology": {
                            "category": "Authentication",
                            "type": "Linddun"
                        }
                    },
                    "recommendation": "Ensure idempotency keys use cryptographically secure random generation with sufficient entropy (UUID v4 or similar) and validate the format server-side."
                }
            ]
        }
        """
        issue_id = "JIRA-123"
        print(f"Loading recommendations for {issue_id}")
        return load_recommendations()

    @mcp.tool()
    def code_guideline() -> str:
        """Code Guideline for an issue or ticket.
        Use this tool when you need to:
        - Provide a detailed description of code guideline for an issue or ticket in secure coding practices
        - when you generate code and you need to consider security
        """
        issue_id = "JIRA-123"
        print(f"Loading code guideline for {issue_id}")
        return load_code_guideline()

    await mcp.run_stdio_async()
