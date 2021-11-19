from flask import Flask, flash, render_template, request, session
import os
import urllib.request
import json
import pyodbc

app = Flask(__name__)

@app.route('/')
def home():
    if not session.get('logged_in'):
        global account
        account = True
        return render_template('login.html')
    else:
        return render_template('diagnostico.html')


@app.route('/login', methods=['GET', 'POST'])
def do_admin_login():

    login = request.form

    userNameLogin = login['username']
    passwordLogin = login['password']

    server = 'mysqlserver2710.database.windows.net'
    database = 'diagnosticoDatabase'
    username = 'azureuser'
    password = '27100804Ak'
    driver = '{ODBC Driver 17 for SQL Server}'

    usersLogin = {}
    with pyodbc.connect('DRIVER='+driver+';SERVER=tcp:'+server+';PORT=1433;DATABASE='+database+';UID='+username+';PWD=' + password) as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT TOP (1000) * FROM [dbo].[login]")
            row = cursor.fetchone()
            while row:
                usersLogin[row[0]] = row[1]
                row = cursor.fetchone()

    if userNameLogin in usersLogin and usersLogin[userNameLogin] == passwordLogin:
        account = True
    else:
        account = False

    if account:
        session['logged_in'] = True
    else:
  
    return home()


@app.route('/diagnostico', methods=['GET', 'POST'])
def diagnostico():
    diagnostico = request.form

    PatientID = diagnostico['PatientID']
    Pregnancies = diagnostico['Pregnancies']
    PlasmaGlucose = diagnostico['PlasmaGlucose']
    DiastolicBloodPressure = diagnostico['DiastolicBloodPressure']
    TricepsThickness = diagnostico['TricepsThickness']
    SerumInsulin = diagnostico['SerumInsulin']
    BMI = diagnostico['BMI']
    DiabetesPedigree = diagnostico['DiabetesPedigree']
    Age = diagnostico['Age']

    data = {
        "Inputs": {
            "input1":
            [
                {
                    'PatientID': PatientID,
                    'Pregnancies': Pregnancies,
                    'PlasmaGlucose': PlasmaGlucose,
                    'DiastolicBloodPressure': DiastolicBloodPressure,
                    'TricepsThickness': TricepsThickness,
                    'SerumInsulin': SerumInsulin,
                    'BMI': BMI,
                    'DiabetesPedigree': DiabetesPedigree,
                    'Age': Age,
                }
            ],
        },
        "GlobalParameters":  {
        }
    }

    body = str.encode(json.dumps(data))

    url = 'https://ussouthcentral.services.azureml.net/workspaces/62f645b22b90403199314f0129087cba/services/60a5a2bda19b4bca96110f28c63fdf3b/execute?api-version=2.0&format=swagger'
    api_key = 'tJz0ArHhhSr5SWw0REnoo6Smqeuc6aJO/LB4sXZcysjQv0M0socW2ZF7OA5wNrxJybcV7qvf5sWlTGHxrMjkmQ=='
    headers = {'Content-Type': 'application/json',
               'Authorization': ('Bearer ' + api_key)}

    req = urllib.request.Request(url, body, headers)

    try:
        response = urllib.request.urlopen(req)

        result = response.read()
        resultString = result.decode('UTF-8')
        resultString = resultString[23:]
        resultString = resultString[:-3]
        result = json.loads(resultString)

        server = 'mysqlserver2710.database.windows.net'
        database = 'diagnosticoDatabase'
        username = 'azureuser'
        password = '27100804Ak'
        driver = '{ODBC Driver 17 for SQL Server}'

        cnxn = pyodbc.connect('DRIVER='+driver+';SERVER=tcp:'+server+';PORT=1433;DATABASE='+database+';UID='+username+';PWD=' + password)
        cursor = cnxn.cursor()
        count = cursor.execute("""
        INSERT INTO pacientes VALUES (?,?,?,?,?,?,?,?,?,?,?)""", 
        PatientID, Pregnancies, PlasmaGlucose, DiastolicBloodPressure, TricepsThickness, SerumInsulin, BMI, DiabetesPedigree, Age, result['DiabetesPrediction'], result['Probability']).rowcount
        cnxn.commit()
        print('Rows inserted: ' + str(count))

    except urllib.error.HTTPError as error:
        print("The request failed with status code: " + str(error.code))
        print(error.info())
        print(json.loads(error.read().decode("utf8", 'ignore')))
    
    return render_template('response.html',PatientIDResult=result['PatientID'],DiabetesPredictionResult=result['DiabetesPrediction'],ProbabilityResult=result['Probability'])


@app.route('/logout')
def logout():
    session['logged_in'] = False
    return home()


if __name__ == "__main__":
    app.debug = True
    app.run()
