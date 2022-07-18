from django.db import models
from datetime import datetime

# Create your models here.
class BlogRank(models.Model):
	blog_name = models.CharField(max_length=255)
	blog_rank = models.CharField(max_length=255)
	search_rank = models.CharField(max_length=255)
	blog_link = models.CharField(max_length=255,unique=True)
	created_at = models.DateTimeField(default=datetime.now)

	class Meta:
		managed = True
		db_table = 'blog_rank'