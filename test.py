import app.database as db_helper

def printGames():
    print("hi")
    games = db_helper.getSimilarGames(305)
    print(games)
    
printGames()