from llm_helper import llm

def generate_post(length: str, language: str, topic: str) -> str:
    prompt = f"Write a {length} LinkedIn-style post in {language} about {topic}."
    response = llm.invoke(prompt)
    return response.content
