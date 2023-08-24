from flask import Flask, request, jsonify, render_template, redirect, flash
from app import app
from app import database as db_helper
import json


userId = -1
def getUserId():
    global userId
    return userId

def setUserId(id):
    global userId
    userId = id
    
games = []

def getGames():
    global games
    return games

def resetGames():
    global games
    games = []

def setGames(gameList):
    global games
    games = gameList
    
@app.route("/", methods = ['GET'])
def index():
    return render_template("login.html")

@app.route("/login", methods = ['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    
    # Check if the username and password exist in the database
    data = db_helper.login(username, password)
    print(data)
    if len(data) == 0:
        # Set an error message variable to display on the login page
        error_message = 'Invalid username or password'
        return render_template('login.html', error_message=error_message)
    else:
        # Set a success message variable to display on the login page
        success_message = 'Login successful!'
        
        userID = db_helper.getUserId(username, password)
        setUserId(userID)
        
        # Go to the games page and 
        return redirect('/addGames')
    
@app.route("/createAccount", methods = ['POST'])
def createAccount():
    print("hi")
    username = request.form['username']
    password = request.form['password']
    
    print("bye")
    # Check if the username and password exist in the database
    message = db_helper.createAccount(username, password)
    # should return a success message'
    print(message)
    return render_template('login.html', success_message=message)

@app.route('/addGames', methods=['GET', 'POST'])
def addGames():
    # Handle search query
    print("hi")
    render_template('games.html')
    if (getGames() == []):
        games = db_helper.randomGames()
    else :
        games = getGames()
        resetGames()
    
    if request.method == 'POST':
        
        #get game ids from the checkboxes
        gameIds = request.form.getlist('game_ids[]')
        print(gameIds)
        UserId = getUserId()

        result = db_helper.addGameToUserList(gameIds, UserId)

        if result == "Game Added!":
            return redirect('/currentGameList')
        else:
            error_message = result
            return render_template('games.html', games=games, error_message=error_message)
        
    else:
        
        
        return render_template('games.html', games=games)
    
    
@app.route('/changePassword', methods=['GET', 'POST'])
def changePassword():
    print("hi")
    render_template('change_password.html')
    print("bye")
    #get the username, current password, and new password
    
    if (request.method == 'POST'):
        username = request.form['username']
        currentPassword = request.form['current_password']
        newPassword = request.form['new_password']
        print("e")
        message = db_helper.changePassword(username, currentPassword, newPassword)
        
        return render_template('change_password.html', success_message=message)
    else:
        return render_template('change_password.html')
    
    

@app.route('/currentGameList', methods=['GET', 'POST'])
def currentGameList():
    list = db_helper.getCurrentGames(getUserId())
    
    return render_template('currentGameList.html', games=list)
    
@app.route('/deleteGame', methods=['GET', 'POST'])
def deleteGame():
    # get the game id of checkbox
    gameId = request.form.getlist('game_ids[]')
    
    message = db_helper.deleteGameFromUserGameList(gameId, getUserId())
    
    return redirect('/currentGameList')

@app.route('/searchGames', methods=['GET', 'POST'])
def searchGames():
    
    if request.method == 'POST':
        Indie = -1
        Action = -1
        Adventure = -1
        Casual = -1
        Strategy = -1
        RPG = -1
        Simulation = -1
        Sports = -1
        Racing = -1

        Price = ""

        PlatformWindows = -1
        PlatformMac = -1
        PlatformLinux = -1

        GameName = ""

        IsFree = -1

        #if Indie is checked set Indie to 1
        if 'indie' in request.form:
            Indie = 1
        if 'action' in request.form:
            Action = 1
        if 'adventure' in request.form:
            Adventure = 1
        if 'casual' in request.form:
            Casual = 1
        if 'strategy' in request.form:
            Strategy = 1
        if 'rpg' in request.form:
            RPG = 1
        if 'simulation' in request.form:
            Simulation = 1
        if 'sports' in request.form:
            Sports = 1
        if 'racing' in request.form:
            Racing = 1
        if 'platform' in request.form and request.form['platform'] == 'pc':
            PlatformLinux = 1
        if 'platform' in request.form and request.form['platform'] == 'mac':
            PlatformMac = 1
        if 'platform' in request.form and request.form['platform'] == 'windows':
            PlatformWindows = 1
        if 'price' in request.form and request.form['price'] == 'free':
            IsFree = 1
        if 'game-name' in request.form:
            GameName = request.form['game-name']
        if 'max-price' in request.form:
            Price = request.form['max-price']



        # add each to a dictionary
        dict = {'Indie': Indie, 'Action': Action, 'Adventure': Adventure, 'Casual': Casual, 'Strategy': Strategy, 'RPG': RPG, 'Simulation': Simulation, 'Sports': Sports, 'Racing': Racing, 'PlatformLinux': PlatformLinux, 'PlatformMac': PlatformMac, 'PlatformWindows': PlatformWindows, 'IsFree': IsFree, 'GameName': GameName, 'Price': Price}
        
        print("THIS IS THE DICT: ", dict)
        
        
        data = db_helper.filterGames(dict)

        setGames(data)
        
        
        return redirect('/addGames')
    else:
        return render_template('filter.html')


@app.route('/recommendedGames', methods=['GET', 'POST'])
def recommendedGames():
    games = db_helper.getSimilarGames(getUserId())
    print("GAMES: ", games)
    if not games:
        return render_template('games.html', games=getGames(), error_message="No Games in User Profile")
    
    return render_template('recommended_games.html', games=games)

@app.route('/deleteRecommendedGames', methods=['GET', 'POST'])
def deleteRecommendedGames():
    
    # get the game id of checkbox
    gameId = request.form.getlist('game_ids[]')
    print("DELETING GAMES")
    
    message = db_helper.deleteRecommendedGames(gameId, getUserId())
    
    return redirect('/recommendedGames')

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    return redirect('/')

    