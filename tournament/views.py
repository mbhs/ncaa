from django.contrib.auth import authenticate, login, logout
from django.shortcuts import get_object_or_404, render, render_to_response
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.views import generic
from django import forms
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.template import RequestContext
from django.contrib.auth.models import User, Group
from django.contrib.auth import login as auth_login

from .models import Variable, Team, Entry
from .forms import CoefficientForm, UploadForm, TeamsForm
from .matchup import sim_matchup

import csv
import numpy
import math
import random

def login(request):
    message = ''
    if request.method == 'POST':
        user = authenticate(username = request.POST.get('username'), password = request.POST.get('password'))
        if user is not None:
            auth_login(request, user)
            return HttpResponseRedirect(reverse('tournament:index'))
        else:
            message = "Incorrect Username-Password Combination"

    return render(request, 'tournament/login.html', {'message':message})

@login_required
def index(request):
    #Choose Simulation to Run -- two buttons
    #Update CSV File (will override all variables)-- two buttons
    username = request.user.username
    variables = Variable.objects.all()
    if not variables:
        return HttpResponseRedirect(reverse('tournament:read_in_values'))

    return render(request, 'tournament/index.html', {'variables':variables, 'username':username})

@login_required
def read_in_values(request):
    if request.method == 'POST':
        form = UploadForm(request.POST, request.FILES)
        if form.is_valid():
            Entry.objects.all().delete()
            Variable.objects.all().delete()
            Team.objects.all().delete()
            data_file = request.FILES['uploaded_file']
            data_reader = csv.reader(data_file)
            data = list(data_reader)
            variables = data[0]
            variables.pop(0)
            variable_list = []
            for var in variables:
                v = Variable.objects.create(name = var)
                variable_list.append(v)
            data.pop(0)
            for team_row in data:
                t = Team.objects.create(name = team_row[0])
                for i in range(1, len(team_row)):
                    Entry.objects.create(team = t, variable = variable_list[i-1], value = team_row[i])

            #Standardize Differences

            for variable in variable_list:
                differences = []
                entries_query = variable.entry_set.all()
                entries = []
                for entry in entries_query:
                    entries.append(entry.value)

                for i in range(0, len(entries)):
                    for j in range(0, len(entries)):
                        if j <= i:
                            continue
                        differences.append(entries[i]-entries[j])
                variable.stdev = numpy.std(differences)
                variable.save()

            return HttpResponseRedirect(reverse('tournament:index'))

    else:
        form = UploadForm()
    return render(request, 'tournament/upload_csv.html', {'form': form, })

@login_required
def update_coefficient(request, variable_id):
    variable = get_object_or_404(Variable, pk = variable_id)
    if request.method == 'POST':
        form = CoefficientForm(request.POST, instance = variable)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('tournament:index'))
    else:
        form = CoefficientForm(instance = variable)

    return render(request, 'tournament/update_coefficient.html', {'form': form, 'variable':variable})


@login_required
def all_probs_Kaggle(request):
    teams_query = Team.objects.all().order_by('name')
    teams = []
    for team in teams_query:
        teams.append(team)

    variables_query = Variable.objects.all().order_by('name')
    variables = []
    for var in variables_query:
        variables.append(var)

    output = []
    for i in range(0, len(teams)):
        team1 = teams[i]
        for j in range(i+1, len(teams)):
            team2 = teams[j]
            p = sim_matchup(team1, team2, variables)
            team1id = 1100+i
            team2id = 1100+j
            output_string = str(team1id)+"_"+str(team2id)
            output.append([output_string, p])

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attatchment; filename="all_matchups_Kaggle.csv"'
    writer=csv.writer(response)
    for row in output:
        writer.writerow(row)

    return response

@login_required
def all_probs(request):
    teams_query = Team.objects.all().order_by('name')
    teams = []
    output = []
    output_row = []
    output_row.append("")
    for team in teams_query:
        teams.append(team)
        output_row.append(team.name)
    output.append(output_row)
    variables_query = Variable.objects.all().order_by('name')
    variables = []
    for var in variables_query:
        variables.append(var)

    for i in range(0, len(teams)):
        output_row = []
        team1 = teams[i]
        output_row.append(team1.name)
        for k in range(0, i):
            output_row.append("")

        for j in range(i, len(teams)):
            team2 = teams[j]
            p = sim_matchup(team1, team2, variables)
            output_row.append(p)
        output.append(output_row)

    for i in range(1, len(output)):
        for j in range(i+1, len(output)):
            output[j][i] = output[i][j]

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attatchment; filename="all_matchups.csv"'
    writer=csv.writer(response)
    for row in output:
        writer.writerow(row)

    return response

@login_required
def tournament_probs(request):
    message = ''
    if request.method == 'POST':
        form = UploadForm(request.POST, request.FILES)
        if form.is_valid():
            data_file = request.FILES['uploaded_file']
            data_reader = csv.reader(data_file)
            data = list(data_reader)
            num_teams = data[0][0]
            if not num_teams.isdigit() or not int(num_teams) % 4 == 0:
                message = "The first row must indicate the number of teams and must be a power of 2."
                return render(request, 'tournament/tournament_probs.html', {'form': form, 'message':message, })
            data.pop(0)
            num_teams = int(num_teams)
            if not len(data) == num_teams:
                message = "You have a mismatch between the number of teams you indicated and the actual number of teams."
                return render(request, 'tournament/tournament_probs.html', {'form': form, 'message':message, })
            teams = []
            for row in data:
                team_list = Team.objects.filter(name=row[0])
                if not team_list:
                    message = "Invalid Team Name: "+row[0]
                    return render(request, 'tournament/tournament_probs.html', {'form': form, 'message':message, })
                team = team_list.first()
                teams.append(team)

            #Output Format
            #   16 8 4 2 1
            #T1
            #T2
            #T3
            #T4
            variables_query = Variable.objects.all().order_by('name')
            variables = []
            for var in variables_query:
                variables.append(var)

            output = []
            header = []
            count_row = []
            header.append("")
            num_rounds = int(math.log(num_teams)/math.log(2))
            for i in range(0, num_rounds):
                header.append(math.pow(2, num_rounds-i-1))
                count_row.append(0)

            output.append(header)

            for team in teams:
                row = list(count_row)
                row.insert(0, team.name)
                output.append(row)

            num_iterations = 1000
            for i in range(0, num_iterations):
                eliminated = []
                for c in range(0, num_teams):
                    eliminated.append(False)

                for r in range(1,num_rounds):
                    x = 0
                    while x < num_teams:
                        if not eliminated[x]:
                            y = x+1
                            while eliminated[y]:
                                y+=1

                            p = sim_matchup(teams[x], teams[y], variables)
                            if random.random() < p:
                                eliminated[y] = True
                                output[1+x][r] += 1
                            else:
                                eliminated[x] = True
                                output[1+y][r] += 1

                            x = y
                        x+=1

                for x in range(0, num_teams):
                    if not eliminated[x]:
                        output[1+x][num_rounds] += 1
                        break

            for i in range(1, len(output)):
                for j in range(1, len(row)):
                    output[i][j] = 1.0*output[i][j]/num_iterations

            request.session['output'] = output
            return HttpResponseRedirect(reverse('tournament:tournament_probs_download'))

    else:
        form = UploadForm()

    return render(request, 'tournament/tournament_probs.html', {'form': form, 'message':message, })

@login_required
def tournament_probs_download(request):
    output = request.session.get('output')
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attatchment; filename="tournament_probs.csv"'
    writer=csv.writer(response)
    for row in output:
        writer.writerow(row)
    return response


@login_required
def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse('tournament:index'))
