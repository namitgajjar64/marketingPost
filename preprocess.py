import json
from llm_helper import llm
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.exceptions import OutputParserException

def process_posts(raw_file_path, processed_file_path=None):
    with open(raw_file_path, encoding="utf-8") as file:
        posts = json.load(file)
        enriched_posts = []
        for post in posts:
            metadata = extract_metadata(post["text"])
            post_with_metadata = post | metadata
            enriched_posts.append(post_with_metadata)

    unified_tags = get_unified_tags(enriched_posts)
    for post in enriched_posts:
        current_tags = post["tags"]
        new_tags = {unified_tags.get(tag, tag) for tag in current_tags}
        post["tags"] = list(new_tags)

    if processed_file_path:
        with open(processed_file_path, "w", encoding="utf-8") as outfile:
            json.dump(enriched_posts, outfile, indent=4)

def extract_metadata(post):
    template = """
    You are given a LinkedIn post. You need to extract number of lines, language of the post and tags.
    1. Return a valid JSON. No preamble. 
    2. JSON object should have exactly three keys: line_count, language and tags. 
    3. tags is an array of text tags. Extract maximum two tags.
    4. Language should be English or Hinglish (Hinglish means hindi + english)

    Here is the actual post on which you need to perform this task:  
    {post}
    """
    pt = PromptTemplate.from_template(template)
    prompt = pt.format(post=post)
    response = llm.invoke(prompt)

    try:
        parser = JsonOutputParser()
        return parser.parse(response.content)
    except OutputParserException:
        raise OutputParserException("Context too big. Unable to parse response.")

def get_unified_tags(posts_with_metadata):
    unique_tags = set()
    for post in posts_with_metadata:
        unique_tags.update(post["tags"])

    tag_string = ", ".join(unique_tags)

    template = """
    I will give you a list of tags. You need to unify tags with the following requirements:
    1. Tags are unified and merged to create a shorter list. 
       Example 1: "Jobseekers", "Job Hunting" → "Job Search" 
       Example 2: "Motivation", "Inspiration", "Drive" → "Motivation"
       Example 3: "Personal Growth", "Personal Development", "Self Improvement" → "Self Improvement"
       Example 4: "Scam Alert", "Job Scam" → "Scams"
    2. Each tag should follow Title Case. Example: "Job Search"
    3. Output a JSON object with original tag as key and unified tag as value. No preamble.

    Here is the list of tags:
    {tags}
    """
    pt = PromptTemplate.from_template(template)
    prompt = pt.format(tags=tag_string)
    response = llm.invoke(prompt)

    try:
        parser = JsonOutputParser()
        return parser.parse(response.content)
    except OutputParserException:
        raise OutputParserException("Context too big. Unable to parse response.")

if __name__ == "__main__":
    process_posts("data/raw_posts.json", "data/processed_posts.json")
