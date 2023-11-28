from django.db import models

class NewsArticle(models.Model):
    source          = models.CharField(max_length=255)
    category        = models.CharField(max_length=255)
    link            = models.URLField()
    author          = models.CharField(max_length=255)
    published_at    = models.DateTimeField()
    header          = models.TextField()
    subheader       = models.TextField()
    content         = models.TextField()

    @property
    def published_date(self):
        return self.published_at.date()

class GraphQuery(models.Model):
    query_id        = models.AutoField(primary_key=True)
    dict_query_x    = models.TextField()
    dict_query_y    = models.TextField()
    description     = models.TextField()
    graph_type      = models.CharField(max_length=255)
    data            = models.TextField()
    do_refresh      = models.BooleanField(default=False)
    is_deleted      = models.BooleanField(default=False)
    updated_at      = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title
    
# # Create your models here.


# class Language(models.Model):
    
#     language_id = models.AutoField(primary_key=True,null=False)
#     language_code = models.CharField(max_length=20, null=False, blank=True)
#     language = models.CharField(max_length=250, null=False, blank=True)
#     is_deleted = models.BooleanField(default=False)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
#     def __str__(self):
#         return self.language


# class Video(models.Model):
#     video_number = models.AutoField(primary_key=True,null=False)
#     video_url = models.TextField(blank=True, null=True)
#     video_name = models.CharField(max_length=400, blank=True, null=True)
    
#     video_year = models.IntegerField(blank=True, null=True)
#     video_session = models.IntegerField(blank=True, null=True)
#     video_date = models.DateField(blank=True, null=True)
#     video_event = models.CharField(max_length=200, blank=True, null=True)
#     video_description = models.TextField(blank=True, null=True)

#     video_members = models.TextField(blank=True, null=True)
#     video_minister = models.TextField(blank=True, null=True)
#     video_sequence_number = models.IntegerField(blank=True, null=True)
#     video_tags = models.TextField(blank=True, null=True)
#     video_uploaded_user_id = models.IntegerField(blank=True, null=True)
#     thumbnail = models.FileField(null=True, blank=True, upload_to="thumbnails/")

#     is_deleted = models.BooleanField(default=False)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     def __str__(self):
#         return self.video_name


# class VideoSubTitle(models.Model):
#     video_id = models.ForeignKey(Video, on_delete=models.CASCADE, null=True, blank=True)
#     srt_sequence_number = models.IntegerField(default=0)
#     start_time = models.DurationField(blank=True, null=True)
#     end_time = models.DurationField(blank=True, null=True)
#     sub_title = models.CharField(max_length=400, blank=True, null=True)
#     language = models.ForeignKey(Language, on_delete=models.CASCADE, null=True, blank=True)
#     is_deleted = models.BooleanField(default=False)
#     uploded_user_id = models.IntegerField(blank=True, null=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     def __str__(self):
#         return self.video_id
    

# class HomeHighlights(models.Model):
#     id                      = models.AutoField(primary_key=True,null=False)
#     video_id                = models.ForeignKey(Video, on_delete=models.CASCADE, null=True, blank=True)
#     highlight_title         = models.CharField(max_length=400, blank=True, null=True)
#     highlight_description   = models.TextField(blank=True, null=True)
#     highlight_priority      = models.IntegerField(blank=True, null=True)
#     uploded_user_id         = models.IntegerField(blank=True, null=True)
#     created_at              = models.DateTimeField(auto_now_add=True)
#     updated_at              = models.DateTimeField(auto_now=True)

#     def __str__(self):
#         return self.video_id