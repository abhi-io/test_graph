import csv
from datetime import datetime
from video_subtitle.models import NewsArticle  # Replace 'myapp' with your actual app name
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Load a list of news articles from a CSV file into the database'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str)

    def handle(self, *args, **options):
        with open(options['csv_file'], 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                NewsArticle.objects.create(
                    source=row['source'],
                    category=row['category'],
                    link=row['link'],
                    author=row['author'],
                    published_at=datetime.strptime(row['published_at'], '%Y-%m-%d %H:%M:%S'),  # Adjust date format as needed
                    header=row['header'],
                    subheader=row['subheader'],
                    content=row['content']
                )
