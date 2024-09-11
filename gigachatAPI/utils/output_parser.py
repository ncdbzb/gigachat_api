from gigachatAPI.logs.logs import error_test_logger


async def get_questions_dict(test: str) -> dict[str: str]:
    splittt = list(filter(None, test.split('\n')))
    splitt = list(filter(None, map(lambda x: x.strip(), splittt)))
    result = {}
    try:
        if splitt[1].lower() == 'варианты:':
            splitt.pop(1)
        if splitt[0].lower().startswith('вопрос:'):
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
        if splitt[5].lower().startswith('ответ:'):
            answer = splitt[5].split(": ")[1]
            if answer[0].isdigit():
                answer = answer.split('. ')[1]
            if answer not in result.values():
                raise ValueError("Invalid format: Answer does not mathc any of the options")
            result["right answer"] = answer
        else:
            raise ValueError("Invalid format: 'Ответ:' not found")
        if len({result["1 option"], result['2 option'], result['3 option'], result['4 option']}) != 4:
            raise ValueError("Not all values unique")
        return {f'result': result}     
    except Exception as e:
        error_test_logger.warning(f'Test failed by reason: {e}')
        error_test_logger.info(f'{test}\n')
        return {f'error': test}
