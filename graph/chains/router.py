from typing import Literal

from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI


class RouteQuery(BaseModel):
    """Route a user query to the most relevant datasource."""

    datasource: Literal["vectorstore", "websearch", "out_of_domain"] = Field(
        ...,
        description="Given a user question choose to route it to web search, a vectorstore, or out_of_domain.",
    )


llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
structured_llm_router = llm.with_structured_output(RouteQuery)

system = """You are an expert at routing a user question to a vectorstore or web search.
The vectorstore contains documents about nutrition, diets, meal plans, and health guidelines.

Use the vectorstore for questions about nutrition, diet plans, calories, macronutrients, vitamins, minerals, and related health guidelines.
Use the websearch for questions related to diet, food, or health that are NOT in the vectorstore.

If the question is completely unrelated to nutrition, diet, health, or the calorie tracking application (for example: history, geography, python programming, cars, etc.), you MUST choose out_of_domain."""
route_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system),
        ("human", "{question}"),
    ]
)

question_router = route_prompt | structured_llm_router
