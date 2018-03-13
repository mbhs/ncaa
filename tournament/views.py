from django.contrib.auth import authenticate, login, logout
from django.shortcuts import get_object_or_404, render, render_to_response, redirect
from django.http import HttpResponseRedirect, HttpResponse
from django.views import generic
from django import forms
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.template import RequestContext
from django.contrib.auth.models import User, Group
from django.contrib.auth import login as auth_login

from .models import Variable, Team, Entry, Coefficient
from .forms import CoefficientForm, UploadForm
from .functions import sim_matchup, is_power2

import csv
import numpy
import math
import random
import io
import datetime

#Login page
def login(request):
    message = ''
    if request.method == 'POST':
        user = authenticate(username = request.POST.get('username'), password = request.POST.get('password'))
        if user is not None:
            auth_login(request, user)
            return redirect('tournament:index')
        else:
            message = "Incorrect Username-Password Combination"

    return render(request, 'tournament/login.html', {'message':message})

#Index Page: Welcomes the user, gets a list of all variables in table form, and provides links to the different simulations
@login_required
def index(request):
    variables = Variable.objects.all().order_by('pk') #Get a list of all variables
    if not variables:
        #If no variables are in the database, then redirect to a page to upload a master data file.
        #This will only be done once and the master data file will be updated only by superusers
        return redirect('tournament:read_in_values')

    coefficients = Coefficient.objects.filter(user = request.user).order_by('variable__pk') #Get a list of all coefficients for the user
    if not coefficients:
        #If this is the user's first time logging in, then default all the coefficient values to 0
        for var in variables:
            Coefficient.objects.create(value = 0, user = request.user, variable = var)

    #Order coefficients in the same way as the variables -- by variable pk
    coefficients = Coefficient.objects.filter(user = request.user).order_by('variable__pk')

    username = request.user.username

    return render(request, 'tournament/index.html', {'coefficients':coefficients, 'username':username, 'user':request.user})

@login_required
def read_in_values(request):
    if request.method == 'POST':
        form = UploadForm(request.POST, request.FILES)
        if form.is_valid():
            #Delete All Current Data
            Entry.objects.all().delete()
            Variable.objects.all().delete()
            Team.objects.all().delete()

            #Read the uploaded file
            data_file = io.TextIOWrapper(request.FILES['uploaded_file'].file, encoding=request.encoding)
            data_reader = csv.reader(data_file)
            data = list(data_reader)

            #The variables are in the first row of the file
            variables = data[0]
            variables.pop(0)
            variables.pop(0)
            variable_list = []

            #Create variable objects in database
            for var in variables:
                v = Variable.objects.create(name = var)
                variable_list.append(v)
            data.pop(0)

            #Create team objects and populate data grid with data
            for team_row in data:
                t = Team.objects.create(name = team_row[0], team_id = team_row[1])
                for i in range(2, len(team_row)):
                    Entry.objects.create(team = t, variable = variable_list[i-2], value = team_row[i])

            #Compute the standard difference for each variable
            for variable in variable_list:
                differences = []
                entries_query = variable.entry_set.all()
                entries = []
                for entry in entries_query:
                    entries.append(entry.value)

                count = 0
                #Go through each distinct pair of data points that correspond to a particular variable
                for i in range(0, len(entries)):
                    for j in range(i+1, len(entries)):
                        differences.append(entries[i]-entries[j])
                        count += 1

                variable.stdev = numpy.std(differences)
                variable.mean = numpy.mean(differences)
                variable.save()

            return redirect('tournament:index')

    else:
        form = UploadForm()
    return render(request, 'tournament/upload_csv.html', {'form': form})

#Update a coefficient
@login_required
def update_coefficient(request, coefficient_id):
    coefficient = get_object_or_404(Coefficient, pk = coefficient_id)
    if request.method == 'POST':
        form = CoefficientForm(request.POST, instance = coefficient)
        if form.is_valid():
            form.save()
            return redirect('tournament:index')
    else:
        form = CoefficientForm(instance = coefficient)

    return render(request, 'tournament/update_coefficient.html', {'form': form, 'coefficient':coefficient})

#Simulate All Probabilities for the Kaggle tournament
@login_required
def all_probs_Kaggle(request):
    teams_query = Team.objects.all().order_by('team_id') #Get an alphabetical listing of teams

    #Convert query into a list
    teams = []
    for team in teams_query:
        teams.append(team)

    #Obtain a list of variables
    variables_query = Variable.objects.all().order_by('pk')
    variables = []
    for var in variables_query:
        variables.append(var)

    #Obtain a list of user coefficients
    coefficients_query = Coefficient.objects.filter(user = request.user).order_by('variable__pk')
    coefficients = []
    for coef in coefficients_query:
        coefficients.append(coef)

    output = []
    output.append(['id','pred'])
    for i in range(0, len(teams)):
        team1 = teams[i] #Select a team and then go through all teams alphabetically above it
        for j in range(i+1, len(teams)):
            team2 = teams[j]
            p = sim_matchup(team1, team2, variables, coefficients) #Determine the probability of team 1 winning (sim_matchup is in the functions.py file)
            output_string = str(datetime.datetime.now().year)+"_"+str(team1.team_id)+"_"+str(team2.team_id)
            output.append([output_string, p])

    #Return a csv response
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attatchment; filename="all_matchups_Kaggle.csv"'
    writer=csv.writer(response)
    for row in output:
        writer.writerow(row)

    return response

#Simulate every matchup and reuturn probabilities in a CSV
'''
Output Format:

        Team 1  Team 2  Team 3  Team 4 ...
Team 1    p11     p12     p13     p14 ...
Team 2    ...     ...
Team 3    ...     ...     ...
Team 4    ...     ...     ...     ...
...

'''
@login_required
def all_probs(request):
    teams_query = Team.objects.all().order_by('name')
    teams = []

    output = []
    output_row = []
    output_row.append("")

    #Populate the first output row with team names
    for team in teams_query:
        teams.append(team)
        output_row.append(team.name)
    output.append(output_row)

    #Obtain a list of variables
    variables_query = Variable.objects.all().order_by('pk')
    variables = []
    for var in variables_query:
        variables.append(var)

    #Obtain a list of user coefficients
    coefficients_query = Coefficient.objects.filter(user = request.user).order_by('variable__pk')
    coefficients = []
    for coef in coefficients_query:
        coefficients.append(coef)

    #Simulate the matchups and populate the output grid
    for i in range(0, len(teams)):
        output_row = []
        team1 = teams[i]
        output_row.append(team1.name)
        for k in range(0, i):
            output_row.append("")
        output_row.append("-")
        for j in range(i+1, len(teams)):
            team2 = teams[j]
            p = sim_matchup(team1, team2, variables, coefficients)
            output_row.append(p)
        output.append(output_row)



    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attatchment; filename="all_matchups.csv"'
    writer=csv.writer(response)
    for row in output:
        writer.writerow(row)

    return response


#Simulate the tournament
'''
Suppose that we are currently in the round of 32, with teams 1-16 in the east/midwest, and 17-32 in the south/west.

The input will be:
Input Format

32
Team 1
Team 2
...
Team 32

The output will be:
Output Format

Round   16 8 4 2 1
Team 1
Team 2
Team 3
Team 4
...
Team 32
'''

@login_required
def tournament_probs(request):
    message = ''
    if request.method == 'POST':
        form = UploadForm(request.POST, request.FILES)
        if form.is_valid():
            #Read and process the input
            data_file = io.TextIOWrapper(request.FILES['uploaded_file'].file, encoding=request.encoding)
            data_reader = csv.reader(data_file)
            data = list(data_reader)
            num_teams = data[0][0]
            if not (num_teams.isdigit() and is_power2(int(num_teams))):
                message = "The first row must indicate the number of teams and must be a power of 2."
                return render(request, 'tournament/tournament_probs.html', {'form': form, 'message':message, })
            data.pop(0)
            num_teams = int(num_teams)
            if not len(data) == num_teams:
                message = "You have a mismatch between the number of teams you indicated and the number of teams in the file."
                return render(request, 'tournament/tournament_probs.html', {'form': form, 'message':message, })
            teams = []
            for row in data:
                team_list = Team.objects.filter(name=row[0])
                if not team_list:
                    message = "Invalid Team Name: "+row[0]
                    return render(request, 'tournament/tournament_probs.html', {'form': form, 'message':message, })
                team = team_list.first()
                teams.append(team)

            #Obtain a list of variables
            variables_query = Variable.objects.all().order_by('pk')
            variables = []
            for var in variables_query:
                variables.append(var)

            #Obtain a list of coefficients
            coefficients_query = Coefficient.objects.filter(user = request.user).order_by('variable__pk')
            coefficients = []
            for coef in coefficients_query:
                coefficients.append(coef)


            output = []
            header = []
            count_row = []
            header.append("Round")
            num_rounds = int(math.log(num_teams)/math.log(2))

            #The first row indicates the round of the tournament
            for i in range(0, num_rounds):
                header.append(math.pow(2, num_rounds-i-1))
                count_row.append(0)

            output.append(header)

            #Populate the rest of the rows.
            #For now, the first element of each non-header row is a team name, and the remainder of the cells count the number of appearances
            for team in teams:
                row = list(count_row)
                row.insert(0, team.name)
                output.append(row)


            num_iterations = 1000
            for i in range(0, num_iterations):
                eliminated = [] #In each iteration, keep track of who is still in the tournament

                for c in range(0, num_teams):
                    eliminated.append(False)
                for r in range(1,num_rounds+1):
                    x = 0
                    while x < num_teams:
                        #Teams will be eliminated from the top of each side of the bracket to the bottom
                        if not eliminated[x]:
                            y = x+1
                            while eliminated[y]:
                                y+=1

                            #Choose Alphabetically First Team to be Team 1 (Spread the errors)
                            if teams[x].name < teams[y].name:
                                p = sim_matchup(teams[x], teams[y], variables, coefficients)
                                if random.random() < p:
                                    eliminated[y] = True
                                    output[1+x][r] += 1
                                else:
                                    eliminated[x] = True
                                    output[1+y][r] += 1
                            else:
                                p = sim_matchup(teams[y], teams[x], variables, coefficients)
                                if random.random() < p:
                                    eliminated[x] = True
                                    output[1+y][r] += 1
                                else:
                                    eliminated[y] = True
                                    output[1+x][r] += 1

                            x = y

                        x+=1

            #Divide the counts by the number of iterations to yield the probabilities
            for a in range(1, len(output)):
                for b in range(1, len(row)):
                    output[a][b] = 1.0*output[a][b]/num_iterations

            request.session['output'] = output
            return redirect('tournament:tournament_probs_download')

    else:
        form = UploadForm()

    return render(request, 'tournament/tournament_probs.html', {'form': form, 'message':message, })

#Download the tournament probabilities
@login_required
def tournament_probs_download(request):
    output = request.session.get('output')
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attatchment; filename="tournament_probs.csv"'
    writer=csv.writer(response)
    for row in output:
        writer.writerow(row)
    return response

#Logout
@login_required
def logout_view(request):
    logout(request)
    return redirect('tournament:index')
