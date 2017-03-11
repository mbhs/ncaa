import numpy
import math
from .models import Entry

#Return probability that team1 beats team 2
def sim_matchup(team1, team2, variables, coefficients):
    x_1 = Entry.objects.filter(team = team1).order_by('variable__pk')

    x1_vec = []
    for e in x_1:
        x1_vec.append(e.value)

    x_2 = Entry.objects.filter(team = team2).order_by('variable__pk')
    x2_vec = []
    for e in x_2:
        x2_vec.append(e.value)

    x_vec = numpy.subtract(x1_vec,x2_vec) #Vector of differences

    coefficients_vec = []
    for i in range(0, len(variables)):
        x_vec[i] = (x_vec[i]-variables[i].mean)/variables[i].stdev #Standardize the differences
        coefficients_vec.append(coefficients[i].value)

    logit = numpy.dot(coefficients_vec, x_vec)

    #To prevent overflow
    if logit > 10:
        return 1

    if logit < -10:
        return 0

    p = math.exp(logit)/(1+math.exp(logit))
    return p

def is_power2(num):

	'states if a number is a power of two'

	return num != 0 and ((num & (num - 1)) == 0)
