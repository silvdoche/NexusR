import py_sql
import scrapper
import time
import urllib.parse
import string


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


#check if best game meets criteria and executed a quary to record the game
#if ten_games[best_game][1] == "Soloqueue" and ten_games[best_game][3] == "Victory" and ten_games[best_game][9] != "":
#    py_sql.quary_que(ten_games[best_game][0],player[0][1],player[0][2],
#    ten_games[best_game][5],ten_games[best_game][9],ten_games[best_game][8][0],
#    ten_games[best_game][8][1],ten_games[best_game][4],ten_games[best_game][7],ten_games[best_game][10][0],ten_games[best_game][10][1])

def time_tosec(timestr):
    return sum(x * int(t) for x, t in zip([3600, 60, 1], timestr.split(":")))
def tag_gen(CHAMP_SKIN_FRIENDLY,CHAMP_SKIN_ENEMY,FRIENDLY_RUNE,ENEMY_RUNE,LANE_POS,PLAYER_NAME,kill_seq,f_champ,PvsP="Pro"):
    f = open('tags.txt','r')
    tag_content = f.read()
    f.close()
    new_content = tag_content.replace("CHAMP_SKIN_FRIENDLY",CHAMP_SKIN_FRIENDLY).replace("CHAMP_SKIN_ENEMY",CHAMP_SKIN_ENEMY).replace(
        "FRIENDLY_RUNE",FRIENDLY_RUNE).replace("ENEMY_RUNE",ENEMY_RUNE).replace("LANE_POS",LANE_POS).replace("PLAYER_NAME",PLAYER_NAME).replace("PvsP",PvsP).replace(
            "KILL_SEQ",kill_seq).replace("F__CHAMP",f_champ)
    return new_content

def desc_gen(CHAMP_SKIN_FRIENDLY,CHAMP_SKIN_ENEMY,FRIENDLY_RUNE,ENEMY_RUNE,LANE_POS,PLAYER_NAME_F,PLAYER_NAME_E,
CHAMPION_FRIENDLY,CHAMPION_ENEMY,ID_OFTHEGAME,PLAYER_REGION,PLAYER_NICKNAME,LEAGUE_PATCH,CHAMPION_LIST,PLAYER_LIST):
    f = open('desc.txt','r')
    desc_content = f.read()
    f.close()
    new_content = desc_content.replace("CHAMP_SKIN_FRIENDLY",CHAMP_SKIN_FRIENDLY).replace("CHAMP_SKIN_ENEMY",CHAMP_SKIN_ENEMY).replace(
        "RUNES_FRIENDLY",FRIENDLY_RUNE).replace("RUNES_ENEMY",ENEMY_RUNE).replace("LANE_POS",LANE_POS).replace(
            "PLAYER_NAME_F",PLAYER_NAME_F).replace("PLAYER_NAME_E",PLAYER_NAME_E).replace("CHAMPION_FRIENDLY",CHAMPION_FRIENDLY).replace(
                "CHAMPION_ENEMY",CHAMPION_ENEMY).replace("ID_OFTHEGAME",ID_OFTHEGAME).replace(
                    "OPGG_LINK","https://"+PLAYER_REGION+".op.gg/summoner/userName="+PLAYER_NICKNAME).replace(
                        "PLAYER_NICKNAME",PLAYER_NICKNAME).replace("LEAGUE_PATCH",LEAGUE_PATCH).replace("CHAMPION_PLAYLIST",CHAMPION_LIST)
    if PLAYER_LIST != "":
        new_content = new_content.replace("PRO_PLAYER_IF",PLAYER_LIST)
    else:
        new_content = new_content.replace("PRO_PLAYER_IF","")
                                       
    if PLAYER_REGION == "kr":
        new_content = new_content.replace("PLAYER_REGION","Korea")
    if PLAYER_REGION == "euw":
        new_content = new_content.replace("PLAYER_REGION","Europe West")
    if PLAYER_REGION == "eune":
        new_content = new_content.replace("PLAYER_REGION","Europe Nordic & East")
    if PLAYER_REGION == "br":
        new_content = new_content.replace("PLAYER_REGION","Brazil")
    if PLAYER_REGION == "lan": 
        new_content = new_content.replace("PLAYER_REGION","Latin America North")
    if PLAYER_REGION == "las":
        new_content = new_content.replace("PLAYER_REGION","Latin America South")
    if PLAYER_REGION == "na":
        new_content = new_content.replace("PLAYER_REGION","North America")
    if PLAYER_REGION == "oce":
        new_content = new_content.replace("PLAYER_REGION","Oceania")
    if PLAYER_REGION == "tr":
        new_content = new_content.replace("PLAYER_REGION","Turkey")
    if PLAYER_REGION == "jp":
        new_content = new_content.replace("PLAYER_REGION","Japan")
    if PLAYER_REGION == "ru":
        new_content = new_content.replace("PLAYER_REGION","Russia")
    if LANE_POS == "Mid":
        new_content = new_content.replace("LANE_PFORMAT","Middle position")
    if LANE_POS == "Top":
        new_content = new_content.replace("LANE_PFORMAT","Top position")
    if LANE_POS == "Jungle":
        new_content = new_content.replace("LANE_PFORMAT","Jungle")
    if LANE_POS == "ADC":
        new_content = new_content.replace("LANE_PFORMAT","Bottom lane as ADC")
    if LANE_POS == "Support":
        new_content = new_content.replace("LANE_PFORMAT","Bottom lane as Support")
    return new_content
                        
def data_filter_casual(nickname,region,champion_main):
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
            if ten_games[x][1] != "Soloqueue" or ten_games[x][3] != "Victory" or ten_games[x][9] == "" or ten_games[x][11] == "long" or py_sql.quary_check(ten_games[x][5]) == True or py_sql.quary_last_champ(ten_games[x][0],True) == True or time_tosec(ten_games[x][4]) >= 1980 or ten_games[x][0] != champion_main:
                games_d.append(x)
                print('NOT passed , GAME ID : ' + ten_games[x][5] + ' , Champion : '+ ten_games[x][0] + '  , KDA : ' + str(ten_games[x][2]) + ' , Game Lenght : ' + ten_games[x][4])
            else :
                print('Passed game ID : ' + ten_games[x][5] + ' , Champion : '+ ten_games[x][0] + '  , KDA : ' + str(ten_games[x][2]) + ' , Game Lenght : ' + ten_games[x][4])

        for x in sorted(games_d,reverse=True):
            del ten_games[x]
        return ten_games
    except:
        print('Player error , probably changed name.')
        py_sql.quary_insert_errors_players("HTTP error",region,urllib.parse.unquote(nickname,encoding='utf-8', errors='replace'),"Could not locate","Check it out","CASUAL","EROR FROM SCRAPPER")
