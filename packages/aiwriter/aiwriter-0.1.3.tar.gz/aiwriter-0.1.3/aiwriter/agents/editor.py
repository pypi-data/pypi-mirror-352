import os
from aiwriter.agents.context_builder import build_context
from aiwriter.agents.writer import write_essay
from aiwriter.agents.ranker import rank_essay
from aiwriter.agents.thinker import extract_insights
from aiwriter.env import DRAFTS_DIR


def save_to_file(path, content):
    """Save content to a file."""
    with open(path, "w") as f:
        f.write(str(content))


def agent_loop(
    prompt: str,
    max_iters: int = 6,
    length: int = 1000,
    style: str = "informal and analytical",
    audience: str = "sophisticated readers",
):
    """Main agent loop that iteratively improves an essay based on scores and insights.
    
    Args:
        prompt (str): The topic or task for the essay
        max_iters (int): Maximum number of iterations to run
        length (int): Target length for the essay in words
        style (str): Writing style to use
        audience (str): Target audience for the essay
    """
    os.makedirs(DRAFTS_DIR, exist_ok=True)
    
    scores = None
    FULL_CONTEXT = build_context()
    curr_context = prompt + '\n\nCONTEXT\n' + FULL_CONTEXT
    for i in range(1, max_iters + 1):
        essay = write_essay(
            str(curr_context),
            length=length,
            style=style,
            audience=audience,
            rewrite=i != 1,
        )
        curr_context = essay
        
        draft_path = f"{DRAFTS_DIR}/draft_{i}.md"
        save_to_file(draft_path, str(essay))

        scores = rank_essay(str(essay))
        score_path = f"{DRAFTS_DIR}/draft_score_{i}.md"
        save_to_file(score_path, str(scores))

        print(f"Draft #{i} - {curr_context.title}")
        print(f"Scores:\n\n{scores}")

        if scores.all_scores_greater_than_threshold():
            print(f"All scores above score threshold at iteration {i}. Exiting loop.")
            break

        if i > 2:
            insights = extract_insights(
                f"SOURCE MATERIAL\n\n{FULL_CONTEXT}\n\n---\n\n"
                f"ESSAY TO BE REWRITTEN\n\n{str(curr_context)}\n\n{str(scores)}"
            )
            
            insights_path = f"{DRAFTS_DIR}/draft_insights_{i}.md"
            save_to_file(insights_path, insights)
            
            curr_context = f"INSIGHTS\n\n{str(insights)}\n\n---\n\n ESSAY TO BE REWRITTEN\n\n{str(curr_context)}"
