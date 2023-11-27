from django.db import models

class NewsArticle(models.Model):
    source = models.CharField(max_length=255)
    category = models.CharField(max_length=255)
    link = models.URLField()
    author = models.CharField(max_length=255)
    published_at = models.DateTimeField()
    header = models.TextField()
    subheader = models.TextField()
    content = models.TextField()
