import numpy
import math
from .models import Variable, Team, Entry

#Return probability that team1 beats team 2
def sim_matchup(team1, team2, coefficients):
    x_1 = Entry.objects.filter(team = team1).order_by('variable__name')
    x1_vec = []
    for e in x_1:
        x1_vec.append(e.value)
    x_2 = Entry.objects.filter(team = team2).order_by('variable__name')
    x2_vec = []
    for e in x_2:
        x2_vec.append(e.value)
    x_vec = numpy.subtract(x1_vec,x2_vec) #team1 is lower alphabetically
    logit = numpy.dot(coefficients, x_vec)
    p = math.exp(logit)/(1+math.exp(logit))
    return p
