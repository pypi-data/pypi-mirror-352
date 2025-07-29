import instructor
from pydantic import Field, BaseModel
from aiwriter.env import MODEL, CRITERIA


SCORE_THRESHOLD = 8


class ScoreModel(BaseModel):
    clarity: int = Field(default=5, ge=0, le=10)
    conciseness: int = Field(default=5, ge=0, le=10)
    relevance: int = Field(default=5, ge=0, le=10)
    engagement: int = Field(default=5, ge=0, le=10)
    accuracy: int = Field(default=5, ge=0, le=10)

    def all_scores_greater_than_threshold(self, threshold=SCORE_THRESHOLD):
        """Check if all scores are greater than the threshold."""
        return all(getattr(self, c, 6) > threshold for c in CRITERIA)


def rank_essay(essay: str):
    """This function takes an essay and returns a score based on the criteria."""
    from typing import cast

    RANKER_PROMPT = (
        "Score the essay based on the following criteria: "
        + ", ".join(CRITERIA)
        + ".\n\nEach criteria should be scored from 0 to 10.\n\nEssay:\n\n"
    )

    llm = instructor.from_provider(MODEL)
    response = cast(ScoreModel, llm.chat.completions.create(
        messages=[{"role": "user", "content": RANKER_PROMPT + essay}],
        response_model=ScoreModel,
    ))

    return response
