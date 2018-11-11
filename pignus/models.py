from django.db import models

# Create your models here.

class User(models.Model):
  login = models.CharField(max_length=100)

  def __str__(self):
    return "login: %s" % self.login


class XGBoostModel(models.Model):
  user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
  file_path = models.CharField(max_length=100, default='')


class Session(models.Model):
  user = models.ForeignKey(User, on_delete=models.CASCADE)
  last_updated = models.DateTimeField('Last updated at')

class Probability(models.Model):
  session = models.ForeignKey(Session, on_delete=models.CASCADE)
  value = models.FloatField()
  time_stamp = models.DateTimeField('Timestamp')