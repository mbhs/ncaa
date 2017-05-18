import numpy
import math
from .models import Entry

#Return probability that team1 beats team 2
def sim_matchup(team1, team2, variables, coefficients):

    #Populate vectors of the relevant team-variable values
    x_1 = Entry.objects.filter(team = team1).order_by('variable__pk')

    x1_vec = []
    for e in x_1:
        x1_vec.append(e.value)

    x_2 = Entry.objects.filter(team = team2).order_by('variable__pk')
    x2_vec = []
    for e in x_2:
        x2_vec.append(e.value)

    x_vec = numpy.subtract(x1_vec,x2_vec) #Vector of differences

    #Get the coefficients for the given user
    coefficients_vec = []
    for i in range(0, len(variables)):
        x_vec[i] = (x_vec[i]-variables[i].mean)/variables[i].stdev #Standardize the differences
        coefficients_vec.append(coefficients[i].value) #Develop the vector of user coefficients

    parameter = numpy.dot(coefficients_vec, x_vec) #Compute the logit parameter

    #To prevent overflow
    if parameter > 10:
        return .999

    if parameter < -10:
        return 0.001

    #Compute probability
    p = math.exp(parameter)/(1+math.exp(parameter))
    return p

#Determine whether or a number is a power of 2
def is_power2(num):
	return num != 0 and ((num & (num - 1)) == 0)
