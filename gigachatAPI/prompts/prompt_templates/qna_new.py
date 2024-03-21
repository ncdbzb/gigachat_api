from langchain.prompts import PromptTemplate


template = """Ты помощник для задач по ответам на вопросы.
Запомни контекст указанный в квадратных скобках [{context}].
На основе данных полученных из контекста ответь на вопрос указанный в квадратных скобках [{question}].
Используй фрагменты из контекста, чтобы ответить на вопрос. 
Если ты не нашел ответ в контексте, напиши: "Я не знаю".
Твой ответ должен быть максимально развернутым, но содержать не более 150 слов.
Ответ:
"""
# custom_rag_prompt = PromptTemplate.from_template(template)
custom_rag_prompt = PromptTemplate(
    template=template,
    input_variables=["question", "context"]
)
