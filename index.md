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
Once the game is started , a mouse macros are being used to control the game , set the needed settings and start the recording.

After the game is finished , youtube preparations are starting. First it will fill the desc.txt and title.txt , thoose are the files for youtube description and title of the video.

```python
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
```

### Thumbnail picture generate
The best solution for a thumbnail generation i found is to use PIL and paste pictures over pictures like layers.
First it will open a back image with constant size 1280 x 720. After that on the left side of the picture it will paste the first player champion ,
on the right side it will paste the second player champion , paste players face profiles , paste the text pictures and stich everything together.

```python
def trans_paste(bg_img,fg_img,box=(0,0)):
    fg_img_trans = Image.new("RGBA",bg_img.size)
    fg_img_trans.paste(fg_img,box,mask=fg_img)
    new_img = Image.alpha_composite(bg_img,fg_img_trans)
    return new_img


def generate(skin_1,skin_2,lane_pos,player1,player2,region,patch,champion_f,champion_e,rune_f,rune_e,penta_):
    #open the back ground static image.
    background = Image.open("images/thumbnail/background.png")
    #open the 2 champion pictures side by side
    skin1 = Image.open("images/thumbnail/champions/"+champion_f+"/"+skin_1+".png").resize((640,720))
    skin2 = Image.open("images/thumbnail/champions/"+champion_e+"/"+skin_2+".png").resize((640,720))
    #opacity_mask = Image.open("images/thumbnail/opacity_mask.png").convert("RGBA")
    #open a transperent mask for better visual effects
    shadow_mask = Image.open("images/thumbnail/shadow_mask.png").convert("RGBA")
    rectangle_left = Image.open("images/thumbnail/rectangle_left.png").convert("RGBA")
    vline_mid = Image.open("images/thumbnail/lines/"+lane_pos+".png").convert("RGBA")
    player_1 = Image.open("images/thumbnail/players/"+player1+".png")
    player_2 = Image.open("images/thumbnail/players/"+player2+".png")
    region_1 = Image.open("images/thumbnail/regions/"+region+".png").convert("RGBA")
    patch = Image.open("images/thumbnail/patch/"+patch+".png").convert("RGBA")
    line = Image.open("images/thumbnail/line.png").convert("RGBA")
    champion_1 = Image.open("images/thumbnail/mass/"+champion_f+".png").convert("RGBA")
    champion_2 = Image.open("images/thumbnail/mass/"+champion_e+".png").convert("RGBA")
    champion_text1 = Image.open("images/thumbnail/text/"+champion_f+".png").convert("RGBA")
    champion_text2 = Image.open("images/thumbnail/text/"+champion_e+".png").convert("RGBA")
    rune_eclipse = Image.open("images/thumbnail/Ellipse_3.png").convert("RGBA")
    rune_1 = Image.open("images/thumbnail/runes/"+rune_f+".png").convert("RGBA").resize((109,109))
    rune_2 = Image.open("images/thumbnail/runes/"+rune_e+".png").convert("RGBA").resize((109,109))
    if penta_ != "No":
        kill_seq = Image.open("images/thumbnail/kill/"+penta_+".png").convert("RGBA").resize((596,260))

    #picture stiching starts here , it will paste all the pictures in precise coordinates.
    background.paste(skin1)
    background.paste(skin2,(640,0))
    Blended = Image.alpha_composite(background, shadow_mask)
    #Ultrablend = Image.alpha_composite(Blended, opacity_mask)
    newimg = trans_paste(Blended,rectangle_left,box=(18,470))
    newimg2 = trans_paste(newimg,rectangle_left,box=(899,470))
    newimg3 = trans_paste(newimg2,vline_mid,box=(540,0))
    newimg4 = trans_paste(newimg3,player_1,box=(46,479))
    newimg5 = trans_paste(newimg4,region_1,box=(52,592))
    newimg6 = trans_paste(newimg5,region_1,box=(933,592))
    newimg7 = trans_paste(newimg6,patch,box=(1126,592))
    newimg8 = trans_paste(newimg7,patch,box=(245,592))
    newimg9 = trans_paste(newimg8,line,box=(1076,480))
    newimg10 = trans_paste(newimg9,line,box=(194,479))
    newimg11 = trans_paste(newimg10,champion_1,box=(245,479))
    newimg12 = trans_paste(newimg11,champion_2,box=(1126,479))
    newimg13 = trans_paste(newimg12,player_2,box=(927,479))
    newimg14 = trans_paste(newimg13,champion_text2,box=(899,355))
    newimg15 = trans_paste(newimg14,champion_text1,box=(18,350))
    newimg16 = trans_paste(newimg15,rune_eclipse,box=(0,17))
    newimg17 = trans_paste(newimg16,rune_eclipse,box=(1084,17))
    newimg18 = trans_paste(newimg17,rune_1,box=(48,60))
    newimg19 = trans_paste(newimg18,rune_2,box=(1128,60))
    if penta_ != "No":
        newimg20 = trans_paste(newimg19,kill_seq,box=(342,0))
        newimg20.save("D:/lolreplays/buffer/thumbnail.png")
    else:
        newimg19.save("D:/lolreplays/buffer/thumbnail.png")
```
