from __future__ import unicode_literals

from django.db import models

# Create your models here.
class Variable(models.Model):
    name = models.CharField(max_length = 50)
    coefficient = models.FloatField(default = 0)
    stdev = models.FloatField(default = 0)
    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name

class Team(models.Model):
    name = models.CharField(max_length = 50)
    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name

class Entry(models.Model):
    value = models.FloatField(default = 0)
    team = models.ForeignKey(Team)
    variable = models.ForeignKey(Variable)
    class Meta:
        verbose_name_plural = "Entries"
    def __str__(self):
        return ""+self.team.name+", "+self.variable.name+"," +str(self.value)

    def __unicode__(self):
        return ""+self.team.name+", "+self.variable.name+"," +str(self.value)
