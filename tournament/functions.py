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
        #x_vec[i] = (x_vec[i]-variables[i].mean)/variables[i].stdev #Standardize the differences
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

def result(a,b,k):
    if type(a) != int:
        a = k[0].index(a)
    if type(b) != int:
        b = k[0].index(b)
    if a > b:
        return 1 - float(k[b][a])
    else:
        return float(k[a][b])

def reduce(teams, mini,k, rounds):
    if k[0] == '':
        k = k[1:]
    for stage in range(1,6):
        r = list(range(0,len(teams),2**stage))
        for n,i in enumerate(r):
            for you in range(2**stage):
                probability = mini[i+you][stage-1]
                multiplier = 0
                for opponent in range(2**stage):
                    multiplier += mini[(i + 2**stage - 2 * 2**stage * (n%2 == 1) + opponent)%len(teams)][stage-1] * result(teams[i+ you], teams[(i+2**stage + opponent - 2 * 2**stage * (n%2 == 1))%len(teams)], k)
                if len(rounds[stage]) > 0:
                    if teams[i+you] in rounds[stage]:
                        mini[i+you].append(1)
                    else:
                        mini[i+you].append(0)
                else:
                    mini[i+you].append(probability*multiplier)

    return mini
