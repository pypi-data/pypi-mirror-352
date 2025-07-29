import json
import os
from datetime import timedelta
from typing import Optional

summary_path = f'{os.environ.get("REPORTER_PATH")}/widgets/summary.json'


def generate_summary(
        project_name: str, version: str, url: Optional[str] = '',
) -> str:
    with open(summary_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
        statistic = data['statistic']
        duration = timedelta(milliseconds=data['time']['duration'])
        hours, remainder = divmod(duration.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        formatted_duration = f'{hours:02d}:{minutes:02d}:{seconds:02d}'

    print(os.environ.get('VERSION'))
    text = (
        f'Проект: {project_name}\n'
        f'Версия: {version}\n'
        f'Продолжительность: {formatted_duration}\n'
        f'Всего: {statistic["total"]}\n'
        f'Успешно: {statistic["passed"]}\n'
        f'Пропущено: {statistic["skipped"]}\n'
        f'Провалено: {statistic["failed"]}\n'
        f'Сломано: {statistic["broken"]}\n'
        f'[Report Link]({url})'
    )

    return text


if __name__ == '__main__':
    print(
        generate_summary(
            project_name=str(os.environ.get('REPORTER_PROJECT')),
            version=str(os.environ.get('REPORTER_VERSION')),
        ),
    )
