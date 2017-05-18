from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User

'''
Model Structure:

The team, variable, and entry objects are read in from the master data spreadsheet; they are the same across users
Each team has a name; the teams are the same across the users
Each variable has a name, standard difference, and mean difference; every user has access to all the variables and can adjust the coefficients
Every entry (data value) links to a team and variable; the data points are the same across users

The coefficient object is unique to the user;
Every user has unique STANDARDIZED coefficients for each variable; thus, the coefficient object has a value, links to a variable, and links to a user


'''

'''
Procedure:
First Upload the Master Spreadsheet (whoever the admin is can do this)
Create login/passwords for each MBHS team
Allow individual teams to adjust their coefficient values and obtain results
'''

#The variables available to all teams (i.e. the column headers in the csv sheet)
class Variable(models.Model):
    name = models.CharField(max_length = 50)
    stdev = models.FloatField(default = 0)
    mean = models.FloatField(default = 0)
    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name

#The STANDARDIZED coefficients for each user
class Coefficient(models.Model):
    value = models.FloatField(default = 0) #coefficient value
    variable = models.ForeignKey(Variable)
    user = models.ForeignKey(User)
    def __str__(self):
        return str(self.value)

    def __unicode__(self):
        return str(self.value)

#The teams
class Team(models.Model):
    name = models.CharField(max_length = 50)
    team_id = models.IntegerField(default = 0) #Kaggle ID
    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name

#The data points corresponding to a team and variable (i.e. the spreadsheet values)
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
