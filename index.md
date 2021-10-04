## What is Nexus replay automated system ?

Its a fully automated replay recording system for League of Legends ( Riot Games, Inc. ) 

First its going to render and record all the games in real time using OBS , then upload the videos with Selenium chrome webdriver to youtube.

All of the recorded games are published at : [Nexus Replays](https://www.youtube.com/channel/UCbcrpME8Gf0Swwrk4IupVow/featured)

### How does it work

1. Scrape data using BS4 (Beautiful Soup 4) from [leagueofgraphs](https://www.leagueofgraphs.com/) 



```python
def scrape_pro():
    #get pro player names from SQL database
    player = py_sql.quary_players()
    da = []
    dy = []
    datasett = [[da for i in range(12)] for dy in range(1)]

    for i in range(len(player)):
        print('Current player : '+ player[i][2] + '  , Region : ' + player[i][1])
        records_ = engine.data_filter(urllib.parse.quote(player[i][0]),player[i][1])
        if records_ != None:
            datasett.extend(records_)
            time.sleep(5)
        else:
            print('Player Missing.')
        print('Slept for 5 sec')
        
```
Using the **data_filter** function its going to store all the 100+ possible games and prepare them for the filter



```python
def data_filter(nickname,region):
#get players from mysql
    try:
        #select the first player , name and region and then soup
        getsoup = scrapper.get_player_soup(nickname,region)
        #all 10 games into a tr
        player_tr = scrapper.get_player_tr(getsoup)
        player_rank = scrapper.get_player_elo(getsoup)
        #build the matrix 10x10
        xy = []
        yx = []
        ten_games = [[xy for i in range(15)] for yx in range(10)]
        #fill the matrix with all last 10 games data :
        #  [Champion, GameMode, KDA, GameResult, GameLenght, GameID, MatchPlayers, LanePos, EnemyLaner, ReplayURL,Player Rank,Time ago,player,region]
        for x in range(len(ten_games)):
            ten_games[x][0] = scrapper.get_player_champion(player_tr[x+1])
            ten_games[x][1] = scrapper.get_player_gamemode(player_tr[x+1])
            ten_games[x][2] = scrapper.get_player_KDA(player_tr[x+1])
            ten_games[x][3] = scrapper.get_player_gameresult(player_tr[x+1])
            ten_games[x][4] = scrapper.get_player_gamelenght(player_tr[x+1])
            ten_games[x][5] = scrapper.get_player_gameid(player_tr[x+1])
            ten_games[x][6] = scrapper.get_player_matchplayers(player_tr[x+1])
            ten_games[x][7] = scrapper.get_player_lanePOS(ten_games[x][6][1],ten_games[x][0])
            ten_games[x][8] = scrapper.get_player_enemylaner(ten_games[x][6][0],ten_games[x][6][1],ten_games[x][6][1].index(ten_games[x][0]))
            ten_games[x][9] = scrapper.get_player_replayurl(player_tr[x+1])
            ten_games[x][10] = player_rank
            ten_games[x][11] = scrapper.get_player_recent_time(player_tr[x+1])
            ten_games[x][12] = urllib.parse.unquote(nickname)
            ten_games[x][13] = region
            ten_games[x][14] = scrapper.get_player_side(ten_games[x][6][1],ten_games[x][0])
        #determine the best kda of all 10 games
        t_kda = []
        for x in range(10):
            t_kda.append(ten_games[x][2])

        #best_game = t_kda.index(max(t_kda))
        games_d = []
        #filter the 10 games  
        for x in range(10):
            if ten_games[x][1] != "Soloqueue" or ten_games[x][3] != "Victory" or ten_games[x][9] == "" or py_sql.quary_check_second(ten_games[x][5],ten_games[x][0]) == True or py_sql.quary_last_champ_second(ten_games[x][0],py_sql.quary_tolerance_check(ten_games[x][0])[0][0]) == True or time_tosec(ten_games[x][4]) >= 1600:
                games_d.append(x)
                print('NOT passed , GAME ID : ' + ten_games[x][5] + ' , Champion : '+ ten_games[x][0] + '  , KDA : ' + str(ten_games[x][2]) + ' , Game Lenght : ' + ten_games[x][4])
            else :
                print('Passed game ID : ' + ten_games[x][5] + ' , Champion : '+ ten_games[x][0] + '  , KDA : ' + str(ten_games[x][2]) + ' , Game Lenght : ' + ten_games[x][4])

        for x in sorted(games_d,reverse=True):
            del ten_games[x]
        return ten_games
    except:
        print('Player error , probably changed name.')
        py_sql.quary_insert_errors_players("HTTP error",region,urllib.parse.unquote(nickname,encoding='utf-8', errors='replace'),"Could not locate","Check it out","PRO SCRAPPER","EROR FROM SCRAPPER")

```



Now that we have the data , we have to find the best KDA (Kill/Death/Assist) games and insert them into the SQL database to be recorder.KDA is the best metric to measure a quality of the game , having a higher score means the game is more interesting to watch, nobody wants to watch a loosing game or a game that is too stale.
```python
    del datasett[0]
    tt_kda = []
    for x in range(len(datasett)):
        tt_kda.append(datasett[x][2])

    best_match = []
    try:
        for y in range(2):
            best_match.append(tt_kda.index(max(tt_kda)))
            tt_kda[tt_kda.index(max(tt_kda))] = 0.0
    except:
            with open('outfile', 'wb') as fp:
                pickle.dump(datasett, fp)
    for z in range(2):
        try:
            #prepares and insert the best games data , ready to be recorder.
            py_sql.quary_que(datasett[best_match[z]][0],datasett[best_match[z]][12],datasett[best_match[z]][13],
            datasett[best_match[z]][5],datasett[best_match[z]][9],datasett[best_match[z]][8][0],datasett[best_match[z]][8][1],datasett[best_match[z]][4],
            datasett[best_match[z]][7],datasett[best_match[z]][10][0],'0',datasett[z][14])
        except:
            print('couldnt find 2 games , proceeding')
```


The script then creates a folder where it will store the game replay data , empty video description and title text files. OBS is being started at the same time , and being controlled with keyboard macros. I couldnt find a way to control it with API or wincom , so im using a virtual keyboard inputs.

