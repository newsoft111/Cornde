from django.db import models

# Create your models here.
class SupportFaq(models.Model):
	subject = models.CharField(max_length=255)
	content = models.TextField()
	category = models.CharField(max_length=255)
	target = models.IntegerField()
	hit = models.IntegerField(default=0)
	
	class Meta:
		managed = True
		db_table = 'support_faq'