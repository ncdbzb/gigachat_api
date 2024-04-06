from langchain.prompts import PromptTemplate


template = """Ты помощник для задач по ответам на вопросы.
Запомни контекст указанный в квадратных скобках [{context}].
На основе данных полученных из контекста ответь на вопрос указанный в квадратных скобках [{question}].
Используй фрагменты из контекста, чтобы ответить на вопрос.
Твой ответ должен быть максимально развернутым.
Если у тебя нет ответа напиши: "Я не знаю."
"""
# custom_rag_prompt = PromptTemplate.from_template(template)
custom_rag_prompt = PromptTemplate(
    template=template,
    input_variables=["question", "context"]
)
