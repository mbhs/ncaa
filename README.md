NCAA Simulation for MBHS Sports Statistics

Procedure:
First Upload the Master Spreadsheet (whoever the admin is can do this)
Create login/passwords for each MBHS team
Allow individual teams to adjust their coefficient values and obtain results

Model Structure:

The team, variable, and entry objects are read in from the master data spreadsheet; they are the same across users
Each team has a name; the teams are the same across the users
Each variable has a name, standard difference, and mean difference; every user has access to all the variables and can adjust the coefficients
Every entry (data value) links to a team and variable; the data points are the same across users

The coefficient object is unique to the user;
Every user has unique STANDARDIZED coefficients for each variable; thus, the coefficient object has a value, links to a variable, and links to a user

