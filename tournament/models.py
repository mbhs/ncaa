from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User

'''
Model Structure:

The team, variable, and entry objects are read in from the master data spreadsheet.
Each team has a name; the teams are the same across the users
Each variable has a name, standard difference, and mean difference; every user has access to all the variables
Every entry (data value) links to a team and variable; the data points are the same across users

The coefficient object is unique to the user.
Every user has unique coefficients for each variable; thus, the coefficient object has a value, links to a variable, and links to a user


'''



# Create your models here.
class Variable(models.Model):
    name = models.CharField(max_length = 50)
    stdev = models.FloatField(default = 0)
    mean = models.FloatField(default = 0)
    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name

class Coefficient(models.Model):
    value = models.FloatField(default = 0)
    variable = models.ForeignKey(Variable)
    user = models.ForeignKey(User)
    def __str__(self):
        return str(self.value)

    def __unicode__(self):
        return str(self.value)

class Team(models.Model):
    name = models.CharField(max_length = 50)
    team_id = models.IntegerField(default = 0)
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
