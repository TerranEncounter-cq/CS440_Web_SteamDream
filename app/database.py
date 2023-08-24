from app import db

import spacy
from collections import defaultdict
import json

try:
    nlp = spacy.load("en_core_web_md")
except OSError:
    # If the model is not found, download it
    spacy.cli.download("en_core_web_md")
    nlp = spacy.load("en_core_web_md")


"""

+-------------------+
| Tables_in_main    |
+-------------------+
| Games             |
| Genre             |
| RecommendedGames  |
| UserInputGameList |
| UserLogin         |
+-------------------+


"""


def getUserId(username, password):
    conn = db.connect()
    
    query = conn.execute("SELECT UserId FROM UserLogin WHERE Email = %s AND Pass LIKE %s", (username, password + "%"))
    
    # get the UserId
    userId = query.fetchone()[0]
    
    conn.close()
    
    return userId


    
def login(username, password):
    conn = db.connect()
    
    query = conn.execute("SELECT * FROM UserLogin WHERE Email = %s AND Pass LIKE %s", (username, password + "%"))
    conn.close()
    data = []
    for row in query:
        d = dict(row.items())
        data.append(d)
    print(data)
    
    return data

def createAccount(username, password):
    print(username)
    conn = db.connect()
    
    # get the last id
    query = conn.execute("SELECT MAX(UserID) FROM UserLogin")
    # get the last id
    UserId = 0
    for row in query:
        d = dict(row.items())
        UserId = d['MAX(UserID)']
    # increment the last id
    UserId += 1
    print(UserId)
    # insert the new user
    query = conn.execute("INSERT INTO UserLogin (UserId, Email, Pass) VALUES (%s, %s, %s)", (UserId, username, password))
    conn.close()
    return "Account Created!"

def changePassword(username, currentPassword, newPassword):
    conn = db.connect()
    
    query = conn.execute("UPDATE UserLogin SET Pass = %s WHERE Email = %s AND Pass LIKE %s", (newPassword, username, currentPassword + "%"))
    
    conn.close()
    return "Password Changed!"

def randomGames():
    conn = db.connect()
    
    query = conn.execute("SELECT GameId, GameName FROM main.Games ORDER BY RAND() LIMIT 10;")
    
    # loop through the query and add the data to a list. each item in the list is a dictionary with "id" as GameId and "name" as GameName
    data = []
    for row in query:
        d = {}
        d['id'] = row[0]
        d['name'] = row[1]
        data.append(d)
    return data

def addGameToUserList(gameIdList, userId):
    conn = db.connect()
    
    for gameId in gameIdList:
        currentListId = conn.execute("SELECT MAX(ListId) FROM UserInputGameList")
        currentListId = currentListId.fetchone()[0]
        currentListId += 1
        conn.execute("DROP TRIGGER IF EXISTS prevent_duplicate_entries;")
        conn.execute("CREATE TRIGGER prevent_duplicate_entries BEFORE INSERT ON UserInputGameList FOR EACH ROW IF EXISTS(SELECT * FROM UserInputGameList WHERE GameId = NEW.GameId AND UserId = NEW.UserId) THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Duplicate entry not allowed'; END IF;")
        try:
            query = conn.execute("INSERT INTO UserInputGameList (ListId, UserId, GameId) VALUES (%s, %s, %s)", (currentListId, userId, gameId))
        # add trigger to prevent duplicate entries
        except Exception:
        # drop trigger after insert
            conn.execute("DROP TRIGGER IF EXISTS prevent_duplicate_entries;")
            conn.close()
            return "Game Already Added!"
        
        conn.execute("DROP TRIGGER IF EXISTS prevent_duplicate_entries;")
    conn.close()
    return "Game Added!"



def getCurrentGames(userId):
    conn = db.connect()
    
    query = conn.execute("SELECT GameId, GameName FROM Games WHERE GameId IN (SELECT GameID FROM UserInputGameList WHERE UserId = %s)", (userId))
    
    data = []
    for row in query:
        d = {}
        d['id'] = row[0]
        d['name'] = row[1]
        data.append(d)
    return data

def deleteGameFromUserGameList(gameIdList, userId):
    conn = db.connect()
    print(gameIdList)
    for gameId in gameIdList:
        query = conn.execute("DELETE FROM UserInputGameList WHERE UserId = %s AND GameID = %s", (userId, gameId))
    
    conn.close()
    return "Game Deleted!"

def filterGames(dict):
    
    conn = db.connect()
    
    queryList = []
    genres = ["Indie", "Action", "Adventure", "Casual", "Strategy", "RPG", "Simulation", "Sports", "Racing"]
    operating = ["PlatformWindows", "PlatformMac", "PlatformLinux"]
    for key, value in dict.items():
        if value == 1 and key in genres:
            queryList.append(f"SELECT GameId FROM Games NATURAL JOIN Genre WHERE {key} = {value}")
        if value == 1 and key in operating:
            queryList.append(f"SELECT GameId FROM Games NATURAL JOIN Genre WHERE {key} = {value}")
        if value == 1 and key == "IsFree":
            queryList.append(f"SELECT GameId FROM Games NATURAL JOIN Genre WHERE {key} = {value}")
        if value != "" and key == "Price":
            queryList.append((f"SELECT GameId FROM Games NATURAL JOIN Genre WHERE Price < {value}"))
        if value != "" and key == "GameName":
            queryList.append(f"SELECT GameId FROM Games NATURAL JOIN Genre WHERE GameName LIKE '%%{value}%%'")
    
    conn = db.connect()
    
    if len(queryList) == 0:
        return randomGames()
    
    final_query = ""
    
    for query in queryList:
        final_query += query + " UNION "
    
    # remove last " INTERSECT "
    final_query = final_query[:-7]
    
    #add LIMIT 10
    final_query += " ORDER BY RAND() LIMIT 10"
    
    print(final_query)
    
    query = conn.execute(final_query)
    
    print(query)
    
    data = []
    for gameId in query:
        print(gameId[0])
        new_query = conn.execute(f"SELECT GameId, GameName FROM Games WHERE GameId = {gameId[0]}")
        d = {}
        for row in new_query:
            d['id'] = row[0]
            d['name'] = row[1]
        data.append(d)
    print(data)
    conn.close()
    return data

def getAllGames():
    conn = db.connect()
    
    query = conn.execute("SELECT GameId, GameName, GameDescription FROM Games ORDER BY RAND() LIMIT 100;")
    
    data = []
    for row in query:
        d = {}
        d['id'] = row[0]
        d['name'] = row[1]
        d['description'] = row[2]
        data.append(d)
    conn.close()
    return data


def getUserGames(userId):
    conn = db.connect()
    
    query = conn.execute("SELECT GameId, GameName, GameDescription FROM Games WHERE GameId IN (SELECT GameID FROM UserInputGameList WHERE UserId = %s)", (userId))
    
    data = []
    for row in query:
        d = {}
        d['id'] = row[0]
        d['name'] = row[1]
        d['description'] = row[2]
        data.append(d)
    conn.close()
    return data


def preprocess_text(text):
    doc = nlp(text)
    return " ".join([token.lemma_.lower() for token in doc if not token.is_stop and not token.is_punct])


def find_similar_games_for_user_games(user_games_list, database_games_list, top_n):
    # Initialize a dictionary to store the sum of similarity scores and a count of similarity scores
    similarity_sum = defaultdict(float)
    similarity_count = defaultdict(int)

    for user_game_id, user_game_title, user_game_description in user_games_list:
        user_game_doc = nlp(preprocess_text(user_game_description))

        for db_game_id, db_game_title, db_game_doc in database_games_list:
            similarity_sum[db_game_id] += db_game_doc.similarity(user_game_doc)
            similarity_count[db_game_id] += 1

    # Calculate the average similarity scores
    avg_similarity = {game_id: total_similarity / similarity_count[game_id] for game_id, total_similarity in similarity_sum.items()}

    # Sort the games by average similarity score
    sorted_games = sorted(avg_similarity.items(), key=lambda x: x[1], reverse=True)

    # Get game titles for the top N games
    top_n_games_with_titles = [(game_id, title, similarity) for game_id, similarity in sorted_games[:top_n] for db_game_id, title, _ in database_games_list if game_id == db_game_id]

    # Return the top N games with game id, game name, and similarity score
    return top_n_games_with_titles



def addRecommendation(userId, topGames):
    conn = db.connect()
    
    for game in topGames:
        gameId = game[0]
        gameName = game[1]
        similarityScore = game[2]
        query = conn.execute("INSERT INTO RecommendedGames (UserID, GameId, GameName, SimilarityScore) VALUES (%s, %s, %s, %s)", (userId, gameId, gameName, similarityScore))
    
    conn.close()
    return "Recommendation Added!"

def GetRecommendedGamesStoredProcedure(userId):
    conn = db.connect()
    
    """
    
    DELIMITER $$

USE main$$

CREATE PROCEDURE GetRecommendedGames(IN pUserId INT)
BEGIN
    -- Declare the necessary variables
    DECLARE varGameID INT;
    DECLARE varGameName VARCHAR(255);
    DECLARE varSimilarityScore DOUBLE;
    
    DECLARE exit_loop BOOLEAN DEFAULT FALSE;
    
    -- Declare the cursor
    DECLARE RecommendedGamesCursor CURSOR FOR 
        SELECT 
            TopGames.GameID, 
            Games.GameName,
            TopGames.SimilarityScore
        FROM (
            SELECT 
                GameID, 
                SimilarityScore,
                UserId
            FROM 
                RecommendedGames
            WHERE 
                UserId = pUserId
            ORDER BY 
                SimilarityScore DESC
            LIMIT 10
        ) AS TopGames
    JOIN 
        Games 
    ON 
        TopGames.GameID = Games.GameID;

    -- Declare a handler for when the cursor is out of rows
    DECLARE CONTINUE HANDLER FOR NOT FOUND SET exit_loop = TRUE;
    
    DROP TABLE IF EXISTS NewTable;

    -- Create a temporary table to store the result
    CREATE TEMPORARY TABLE IF NOT EXISTS NewTable (
        GameID INT,
        GameName VARCHAR(255),
        SimilarityScore DOUBLE
    );

    -- Open the cursor
    OPEN RecommendedGamesCursor;

    -- Fetch the first row
    read_loop: LOOP
        FETCH RecommendedGamesCursor INTO varGameID, varGameName, varSimilarityScore;
        IF exit_loop THEN
            LEAVE read_loop;
        END IF;

        -- Check if the similarity score is greater than or equal to 90
        IF varSimilarityScore >= 90 THEN
            -- Insert the result into the result table
            INSERT INTO NewTable (GameID, GameName, SimilarityScore)
            VALUES (varGameID, varGameName, varSimilarityScore);
        END IF;
    END LOOP;

    -- Close and deallocate the cursor
    CLOSE RecommendedGamesCursor;

    -- Return the result
    SELECT * FROM NewTable;

    -- Drop the temporary table
    DROP TEMPORARY TABLE NewTable;
END$$

DELIMITER ;

    
    """
    
    query = conn.execute("CALL GetRecommendedGames(%s)", (userId))
    
    data = []
    for row in query:
        d = {}
        d['id'] = row[0]
        d['name'] = row[1]
        d['description'] = row[2]
        data.append(d)
    conn.close()
    return data

def getSimilarGames(userId):
    print("Getting User Games")
    user_games_list = getUserGames(userId)
    
    if len(user_games_list) == 0:
        return []
    
    print("Getting Database Games")
    database_games_list = getAllGames()

    # make a list of tuples with the game title and description
    user_games_list = [(game['id'], game['name'], game['description']) for game in user_games_list]
    database_games_list = [(game['id'], game['name'], nlp(preprocess_text(game['description']))) for game in database_games_list]
    
    print("Finding Similar Games")
    
    # call the stored procedure to get the current top games
    storedGames = GetRecommendedGamesStoredProcedure(userId)
    #convert the stored games to a list of tuples
    storedGames = [(game['id'], game['name'], game['description']) for game in storedGames]
    print("Stored Games: " + str(storedGames))
    storedGamesLength = len(storedGames)
    print("Stored Games Length: " + str(storedGamesLength))
    # if there are less than 10 get the difference and add that to the top n
    
    # storedGames = [{'id': game['id'], 'name': game['name'], 'similarity': game['description']} for game in storedGames]
    print("Stored Games: " + str(storedGames))
    if storedGamesLength < 10:
        amountToAdd = 10 - storedGamesLength
        
        print("Amount to add: " + str(amountToAdd))
        
        topGames = find_similar_games_for_user_games(user_games_list, database_games_list, top_n= amountToAdd)
        topGames = [(game_id, game_title, round(similarity * 100)) for game_id, game_title, similarity in topGames]
        print("Top Games: " + str(topGames))
        addRecommendation(userId, topGames)
        topGames = storedGames + topGames
        topGames = [{'id': game_id, 'name': game_title, 'similarity': similarity} for game_id, game_title, similarity in topGames]
        
        print("Top Games: " + str(topGames))
        
    else:
        topGames = storedGames
        topGames = [{'id': game_id, 'name': game_title, 'similarity': similarity} for game_id, game_title, similarity in topGames]
    
    return topGames


def deleteRecommendedGames(gameIdList, userId):
    


    conn = db.connect()
    
    for gameId in gameIdList:
        print("Deleting Game: " + str(gameId))
        conn.execute("DELETE FROM RecommendedGames WHERE UserId = %s AND GameID = %s", (userId, gameId))
    
    conn.close()
    
    return "Deleted!"
