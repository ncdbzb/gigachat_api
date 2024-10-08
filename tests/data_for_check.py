import csv
import os
from datetime import datetime, timezone, timedelta


def get_data_from_csv(limit: int=0):
    
    questions = []
    ref_answers = []
    ref_dita = []

    scv_path = os.path.join('tests', 'data_for_check.csv')

    with open(scv_path, newline='', encoding='utf-8') as csvfile:
        csvreader = csv.DictReader(csvfile, delimiter=';', quoting=csv.QUOTE_MINIMAL)

        csvreader.fieldnames = [name.replace('\ufeff', '') for name in csvreader.fieldnames]

        for row_num, row in enumerate(csvreader, start=1):

            questions.append(row['questions'])
            ref_answers.append(row['ref_answers'])
            rf_dt = row['ref_dita'].replace('\\', '/')
            if not rf_dt.endswith('.dita'):
                rf_dt = f'{rf_dt}.dita'
            ref_dita.append(rf_dt)

            if row_num == limit:
                break

    return {
        "questions": questions,
        "ref_answers": ref_answers,
        "ref_dita": ref_dita
    }


def log_result_to_csv(*args):
    # Установка временной зоны UTC+5 (Екатеринбург)
    tz_offset = timedelta(hours=5)
    current_time = datetime.now(timezone.utc) + tz_offset
    timestamp = current_time.strftime('%Y-%m-%d %H:%M:%S')

    result_file = os.path.join('gigachatAPI', 'data', 'result.csv')

    file_is_new = not os.path.exists(result_file) or os.path.getsize(result_file) == 0

    with open(result_file, mode='a', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile, delimiter=';')

        if file_is_new:
            writer.writerow(
                ['timestamp', 'filename', 'question', 'similarity_score',
                 'dita_path', 'bleu_score', 'rouge_1_f1', 'rouge_2_f1',
                 'rouge_l_f1', 'answer'
                ]
            )

        writer.writerow([timestamp, *args])
