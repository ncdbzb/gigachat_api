import re


async def parse_output(text: str, current_que_number: int = 0, total_que_number: int = 0) -> tuple[str, int]:
    pattern = re.compile(r"(\d+\. .*?\n(a\) .*?\n|b\) .*?\n|c\) .*?\n|d\) .*?\n)+)")

    matches = pattern.findall(text)[:total_que_number] if total_que_number else pattern.findall(text)

    result = ''
    for num, i in enumerate(matches, start=1):
        result += f'{num}{i[0][i[0].index("."):]}'
        if i != matches[-1]:
            result += '\n'
    if current_que_number:
        return result, total_que_number - len(matches)
    else:
        return result, 0


async def get_questions_dict(test: str) -> dict[str: str]:
    splittt = list(filter(None, test.split('\n')))
    splitt = list(filter(None, map(lambda x: x.strip(), splittt)))
    result = {}
    try:
        if splitt[1] == 'Варианты:':
            splitt.pop(1)
        if splitt[0].startswith('Вопрос:'):
            result["question"] = splitt[0].split(": ")[1]
        else:
            raise ValueError("Invalid format: 'Вопрос:' not found")
        if splitt[1].startswith('1.'):
            result["1 option"] = splitt[1].split(". ")[1]
        else:
            raise ValueError("Invalid format: '1.' not found")
        if splitt[2].startswith('2.'):
            result["2 option"] = splitt[2].split(". ")[1]
        else:
            raise ValueError("Invalid format: '2.' not found")
        if splitt[3].startswith('3.'):
            result["3 option"] = splitt[3].split(". ")[1]
        else:
            raise ValueError("Invalid format: '3.' not found")
        if splitt[4].startswith('4.'):
            result["4 option"] = splitt[4].split(". ")[1]
        else:
            raise ValueError("Invalid format: '4.' not found")
        if splitt[5].startswith('Ответ:'):
            answer = splitt[5].split(": ")[1]
            if answer[0].isdigit():
                answer = answer.split('. ')[1]
            result["right answer"] = answer
        else:
            raise ValueError("Invalid format: 'Ответ:' not found")
        if len(set([result["1 option"], result['2 option'], result['3 option'], result['4 option']])) != 4:
            raise ValueError("Not all values unique")
        return {f'result': result}     
    except ValueError as e:
        print(e)
        return {f'error': test}
