from django.db import models

class Tweet(models.Model):
    tweet_id = models.IntegerField()
    user = models.CharField(max_length=240)
    lat = models.DecimalField(decimal_places=20, max_digits=25)
    lng = models.DecimalField(decimal_places=20, max_digits=25)
    text = models.CharField(max_length=240)
    sentiment = models.CharField(max_length=100)
    retrieved = models.BooleanField(default=False)