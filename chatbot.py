from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableBranch, RunnableParallel, RunnableLambda

from prompts import (
    classifier_prompt,
    programming_prompt,
    math_prompt,
    general_prompt,
    summary_prompt,
)
from schemas import ChatResponse, SummaryResponse, FinalChatOutput

load_dotenv()

model = ChatGroq(model="openai/gpt-oss-120b")
parser = StrOutputParser()

classifier_chain = classifier_prompt | model | parser

structured_model = model.with_structured_output(
    ChatResponse,
    method="json_mode",
)

programming_chain = programming_prompt | structured_model
math_chain = math_prompt | structured_model
general_chain = general_prompt | structured_model

answer_branch = RunnableBranch(
    (lambda x: x["category"].strip().lower() == "programming", programming_chain),
    (lambda x: x["category"].strip().lower() == "mathematics", math_chain),
    general_chain,
)

structured_summary_model = model.with_structured_output(
    SummaryResponse,
    method="json_mode",
)


def _build_summary_input(inputs: dict) -> dict:
    """Reshapes the branch's ChatResponse into input for the summary prompt."""
    return {"question": inputs["question"], "answer": inputs["chat_response"].answer}


summary_chain = RunnableLambda(_build_summary_input) | summary_prompt | structured_summary_model

parallel_chain = RunnableParallel(
    chat_response=lambda x: x["chat_response"],
    summary_response=summary_chain,
)


def run_chatbot(question: str) -> FinalChatOutput:
    """
    Full pipeline entry point used by app.py:
      1. classifier_chain          -> category string ("programming"/"mathematics"/"general")
      2. answer_branch (RunnableBranch)    -> ChatResponse
      3. parallel_chain (RunnableParallel) -> {chat_response, summary_response}
      4. merge into FinalChatOutput (Pydantic) for the UI
    """
    category = classifier_chain.invoke({"question": question})
    print("predicted category:", category)

    chat_response: ChatResponse = answer_branch.invoke(
        {"question": question, "category": category}
    )

    parallel_result = parallel_chain.invoke(
        {"question": question, "chat_response": chat_response}
    )

    summary_response: SummaryResponse = parallel_result["summary_response"]

    return FinalChatOutput(
        answer=chat_response.answer,
        category=chat_response.category,
        confidence=chat_response.confidence,
        keywords=chat_response.keywords,
        summary=summary_response.summary,
        difficulty_level=summary_response.difficulty_level,
        follow_up_questions=summary_response.follow_up_questions,
    )