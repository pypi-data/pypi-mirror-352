"""The workflow for extracting the essence of an article and storing it in the database."""

from fabricatio_core.models.action import WorkFlow

from fabricatio.actions.article import ExtractArticleEssence
from fabricatio.actions.rag import InjectToDB

StoreArticle = WorkFlow(
    name="Extract Article Essence",
    description="Extract the essence of an article in the given path, and store it in the database.",
    steps=(ExtractArticleEssence(output_key="to_inject"), InjectToDB(output_key="task_output")),
)
