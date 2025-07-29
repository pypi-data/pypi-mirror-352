import os
from pathlib import Path

from dotenv import load_dotenv

from ecss_chat_client import Client

from .diagram import create_diagram
from .summary import generate_summary

load_dotenv()


def send_report():
    current_dir = Path(__file__).parent
    output_path = current_dir / str(os.getenv('REPORT_DIAGRAM_NAME'))
    create_diagram(output_path)
    client = Client(
        server=os.getenv('REPORT_ELPH_SERVER'),
        username=os.getenv('REPORT_ELPH_USER'),
        password=os.getenv('REPORT_ELPH_PASSWORD'),
    )

    version = client.different.version()
    version = version.json()

    summary = generate_summary(
        project_name=os.getenv('REPORT_PROJECT_NAME'),
        version=version.get('version'),
        url=os.getenv('REPORT_LINK', 'default_url'),
    )

    client.rooms.upload_file(
        os.getenv('REPORT_ELPH_ROOM_ID'),
        summary,
        output_path,
    )


if __name__ == '__main__':
    send_report()


__all__ = ['send_report']
