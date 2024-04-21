from langchain.prompts import PromptTemplate
from gigachatAPI.prompts.prompt_templates.qna_new import template as qna_template
from gigachatAPI.prompts.prompt_templates.gen_que import template as gen_que_template


def create_prompt(template: str) -> PromptTemplate:
    prompt = PromptTemplate(
        template=template,
        input_variables=["question", "context"]
    )
    return prompt


qna_prompt = create_prompt(qna_template)

gen_que_prompt = create_prompt(gen_que_template)
