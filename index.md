## What is Nexus replay automated system ?

It's a fully automated replay recording system for League of Legends ( Riot Games, Inc. ) 

First it's going to render and record all the games in real time using OBS , then upload the videos with Selenium chrome webdriver to youtube.

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



2.Now that we have the data , we have to find the best KDA (Kill/Death/Assist) games and insert them into the SQL database to be recorder.KDA is the best metric to measure a quality of the game , having a higher score means the game is more interesting to watch, nobody wants to watch a loosing game or a game that is too stale.
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


3.The script then creates a folder where it will store the game replay data , empty video description and title text files. OBS is being started at the same time , and being controlled with keyboard macros. I couldnt find a way to control it with API or wincom , so i'm using a virtual keyboard inputs.
Once the game is started , a mouse macros are being used to control the game , set the needed settings and start the recording.

4.After the game is finished , youtube preparations are starting. First it will fill the desc.txt and title.txt , those are the files for youtube description and title of the video.

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
First it will open a background black image with constant size 1280 x 720. After that on the left side of the picture it will paste the first player champion ,
on the right side it will paste the second player champion , paste players face profiles , paste the text pictures and stitch everything together.

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
#### Samples
 Here are some generated thumbnail pictures , the possibilities are almost endless , there are 150 champions , over 80 pro players and about 10 skins of each champion.

![thumbnail one](https://i.imgur.com/XaNQCME.png)
![thumbnail two](https://i.imgur.com/p3CthQm.png)
![thumbnail three](https://i.imgur.com/hbSUx8z.png)
![thumbnail four](https://i.imgur.com/zgjMBW4.png)

### Youtube upload

Now that we have a video , thumbnail picture , video title and description file , we are ready to upload to Youtube. I decided to use python Selenium instead of youtube api becuase
the API have some hard limitations , like a maximum upload traffic per day , limited edition on the video and some other problems. 

For some reason Chrome webdriver works better than mozila web driver for youtube , i saw an improvement of 20% better upload speed using chrome over mozila , which doesnt sound like
a lot but when you upload 50GB + of data per day it adds up quickly , the upload is done simultaneously while a new game is being recorded.

```python
def upload_video():
    #initialize chrome webdriver and get my chrome user data so i dont have to sign up to youtube everytime i start the webdriver 
    options = webdriver.ChromeOptions() 
    options.add_argument("user-data-dir=C:\\Users\\zeros\\AppData\\Local\\Google\\Chrome\\User Data")
    driver = webdriver.Chrome(executable_path="chromedriver.exe", chrome_options=options)
    while True:
        #endless loop waiting for a video to pop up in the SQL database.
        try:
            getbreaker = py_sql.quary_switch()
            if getbreaker[0][0] == 1 :
                sys.exit('Switch triggered ! Maintenance mode...')
            #vid_name = input('Enter Video : ')
            get_res = py_sql.quary_get_video()
            
            if len(get_res) != 0:
                vid_name = str(get_res[0][1])
                notify_check = str(get_res[0][2])
                py_sql.quary_delete_video(get_res[0][0])
                driver.get("https://youtube.com/upload")
                champion = vid_name.split("_")
                #uploads the file
                champion_playlis = py_sql.quary_champ_playlist(champion[1])
                champion_playlis = champion_playlis[0][0]
                is_it_apro = False
                if len(champion) == 3:
                    is_it_apro = True
                    player_plali = py_sql.quary_player_playlist(champion[2])
                    player_plali = player_plali[0][0]
                print("Started upload for video ID : %s and Champion : %s"%(champion[0],champion[1]))
                while True:
                    try:
                        elem = driver.find_element_by_xpath("//input[@type='file']")
                        print("ELEMENT FOUND! BREAKING OUT!!!")
                        break
                    except:
                        print("Element not found,sleeping for 2 seconds.")
                        time.sleep(2)
                elem.send_keys("D:\\lolreplays\\replays\\%s\\%s.mp4"%(vid_name,champion[1]))
                time.sleep(10)
                #gets the upload status
                print("slept for 10 seconds after first loop")
                text = driver.find_element_by_css_selector('#dialog > div > ytcp-animatable.button-area.metadata-fade-in-section.style-scope.ytcp-uploads-dialog > div > div.left-button-area.style-scope.ytcp-uploads-dialog > ytcp-video-upload-progress > span').text
                switch_var = True
                while switch_var:
                    if text == 'Processing HD version' or text == "Finished processing" or text == "Checks complete. No issues found.":
                        switch_var = False
                    else:
                        time.sleep(5)
                        text = driver.find_element_by_css_selector('#dialog > div > ytcp-animatable.button-area.metadata-fade-in-section.style-scope.ytcp-uploads-dialog > div > div.left-button-area.style-scope.ytcp-uploads-dialog > ytcp-video-upload-progress > span').text
                        print("Uploading not done yet! Status : %s"%text)

                #read title , desc and tag
                f = open("D:\\lolreplays\\replays\\%s\\description.txt"%vid_name,"r",encoding="utf8")
                desc_content = f.read()
                f.close()
                f = open("D:\\lolreplays\\replays\\%s\\tags.txt"%vid_name,"r",encoding="utf8")
                tag_content = f.read()
                f.close()
                f = open("D:\\lolreplays\\replays\\%s\\name.txt"%vid_name,"r")
                name_title = f.read()
                f.close()
                #fill title
                time.sleep(2)
                title_driv = driver.find_element_by_xpath('/html/body/ytcp-uploads-dialog/tp-yt-paper-dialog/div/ytcp-animatable[1]/ytcp-video-metadata-editor/div/ytcp-video-metadata-editor-basics/div[1]/ytcp-mention-textbox/ytcp-form-input-container/div[1]/div[2]/ytcp-mention-input/div')
                title_driv.clear()
                time.sleep(2)
                title_driv.send_keys(name_title)
                #fill desc
                print("Filled video Title!")
                time.sleep(3)
                driver.find_element_by_xpath('/html/body/ytcp-uploads-dialog/tp-yt-paper-dialog/div/ytcp-animatable[1]/ytcp-video-metadata-editor/div/ytcp-video-metadata-editor-basics/div[2]/ytcp-mention-textbox/ytcp-form-input-container/div[1]/div[2]/ytcp-mention-input/div').send_keys(desc_content)
                print("Filled video Description!")
                time.sleep(3)
                #fill thumbnail
                elem_thumb = driver.find_element_by_xpath('//input[@type="file"]')
                elem_thumb.send_keys("D:\\lolreplays\\replays\\%s\\thumbnail.png"%vid_name)
                print("Thumbnail changed!")
                time.sleep(9)
                #clicks the playlist
                playlist = driver.find_element_by_xpath('//*[@id="scrollable-content"]/ytcp-video-metadata-editor/div/ytcp-video-metadata-editor-basics/div[4]/div[3]/div[1]/ytcp-video-metadata-playlists/ytcp-text-dropdown-trigger/ytcp-dropdown-trigger/div/div[2]/span')
                print("Clicking Playlist")
                playlist.click()
                time.sleep(10)
                #searchs for champion
                playlist_search = driver.find_element_by_xpath('//*[@id="search-input"]')
                try : 
                    playlist_search.send_keys(champion[1])
                except :
                    playlist_search = driver.find_element_by_xpath('/html/body/ytcp-playlist-dialog/paper-dialog/div[1]/input')
                    playlist_search.send_keys(champion[1])
                print("Typed champion name!")
                time.sleep(5)
                #click the checkbox
                try:
                    playlist_checkbox = driver.find_element_by_xpath('//*[@id="checkbox-0"]')
                    playlist_checkbox.click()
                    print("clicked champion checkbox")
                except:
                    #clicks X on playlist
                    driver.find_element_by_css_selector('ytcp-icon-button.ytcp-playlist-dialog > iron-icon:nth-child(1)').click()
                    time.sleep(4)
                    #clicks add new
                    driver.find_element_by_css_selector('.new-playlist-button').click()
                    time.sleep(5)
                    #searc for text area
                    playlist_add_text = driver.find_element_by_css_selector('textarea.style-scope')
                    #sends the text
                    time.sleep(1)
                    playlist_add_text.send_keys(champion[1])
                    time.sleep(4)
                    #creates the new playlist
                    driver.find_element_by_css_selector('.create-playlist-button > div:nth-child(2)').click()
                time.sleep(5)
                #clicks done
                driver.find_element_by_css_selector('.done-button > div:nth-child(2)').click()
                print("clicked save button for playlist!")
                time.sleep(3)
                #clicks more options
                driver.find_element_by_xpath('//*[@id="toggle-button"]').click()
                print("Clicked more options!")
                time.sleep(3)
                #fills tag
                taglist = driver.find_element_by_xpath('/html/body/ytcp-uploads-dialog/tp-yt-paper-dialog/div/ytcp-animatable[1]/ytcp-video-metadata-editor/div/ytcp-video-metadata-editor-advanced/div[2]/ytcp-form-input-container/div[1]/div[2]/ytcp-free-text-chip-bar/ytcp-chip-bar/div/input')
                taglist.send_keys(tag_content)
                print("Filled TAG content!")
                time.sleep(6)
                #check if notify is selected ,default is false
                if notify_check == "False":
                    driver.find_element_by_xpath('//*[@id="notify-subscribers"]').click()
                time.sleep(7)
                #game name
                game_name = driver.find_element_by_css_selector(".ytcp-form-gaming > ytcp-dropdown-trigger:nth-child(1) > div:nth-child(2) > div:nth-child(3) > input:nth-child(3)")
                game_name.send_keys('League of Legends 2009')
                print("Filled Game Name!")
                time.sleep(8)
                driver.find_element_by_css_selector('#text-item-2 > ytcp-ve:nth-child(1) > div:nth-child(3)').click()
                print("Clicked game League of Legends 2009 to save it!")
                time.sleep(8)

                #next page

                driver.find_element_by_xpath('//*[@id="next-button"]').click()
                print("Clicked Next Page , Waiting for 10 seconds now.!")

                time.sleep(10)
                driver.find_element_by_css_selector('#endscreens-button').click()
                time.sleep(5)
                driver.find_element_by_css_selector('#import-endscreen-from-video-button').click()
                print("Clicked import end video cards ! sleeping for 10")
                time.sleep(25)
                #add from previous video
                try:                              
                    driver.find_element_by_xpath('//*[@id="dialog"]/div[2]/div/ytcp-entity-card[2]').click()
                except:
                    time.sleep(15)
                    driver.find_element_by_xpath('//*[@id="dialog"]/div[2]/div/ytcp-entity-card[5]').click()
                print("Clicked add from previous video! Sleeping for 7 seconds !")
                time.sleep(13)
                #click latest

                #bellow is code for clicking champion playlist to bring it into view
                driver.find_element_by_css_selector('#decorations > ytve-endscreen-marker:nth-child(8)').click()
                time.sleep(5)

                #edits the playlist link
                driver.find_element_by_css_selector('#label-container > tp-yt-iron-icon').click()
                time.sleep(5)
                cham_pla = driver.find_element_by_xpath('/html/body/ytcp-playlist-pick-dialog/tp-yt-paper-dialog/div[2]/tp-yt-paper-tabs/div/div/tp-yt-paper-tab[2]/div/input')
                cham_pla.clear()
                cham_pla.send_keys(champion_playlis)
                time.sleep(2)
                print("Clicked importing for champion list , sleeping 5 sec!")
                driver.find_element_by_xpath('//*[@id="inner-dialog"]/div[3]/ytcp-entity-card[1]').click()
                time.sleep(8)
                if is_it_apro == True:
                    driver.find_element_by_css_selector('#decorations > ytve-endscreen-marker:nth-child(11)').click()
                    time.sleep(5)
                    driver.find_element_by_css_selector('#label-container > tp-yt-iron-icon').click()
                    time.sleep(2)
                    pro_plax = driver.find_element_by_xpath('/html/body/ytcp-playlist-pick-dialog/tp-yt-paper-dialog/div[2]/tp-yt-paper-tabs/div/div/tp-yt-paper-tab[2]/div/input')
                    pro_plax.clear()
                    pro_plax.send_keys(player_plali)
                    time.sleep(2)
                    print("Clicked All pro player done , sleeping 7 sec!")
                    driver.find_element_by_xpath('//*[@id="inner-dialog"]/div[3]/ytcp-entity-card[1]').click()
                time.sleep(7)
                driver.find_element_by_xpath('//*[@id="save-button"]').click()
                print("Clicked save button , sleeping for 5")
                time.sleep(9)
                #return button 

                #starts the cards page
                driver.find_element_by_xpath('//*[@id="cards-button"]').click()
                time.sleep(15)
                driver.find_element_by_css_selector('#panel-container > ytve-info-cards-editor-options-panel > div > ytve-info-cards-editor-default-options > div:nth-child(3) > ytcp-icon-button').click()
                time.sleep(3)
                cards_champ = driver.find_element_by_css_selector('#search-any')
                time.sleep(6)
                
                cards_champ.send_keys(champion_playlis)
                time.sleep(7)
                driver.find_element_by_xpath('//*[@id="inner-dialog"]/div[3]/ytcp-entity-card[1]').click()
                
                time.sleep(2)
                cards_champ_text_one = driver.find_element_by_css_selector('#textarea-container > textarea')
                card_text_len_one = champion[1] + ' Playlist'
                if len(card_text_len_one) >= 30:
                    range_trim = len(card_text_len_one) - 30
                    card_text_len_one = card_text_len_one[:-range_trim]
                cards_champ_text_one.send_keys(card_text_len_one)
                time.sleep(1)
                card_text_len_two_text = 'Watch ' + champion[1] + ' Playlist'
                if len(card_text_len_two_text) >= 30:
                    range_trima = len(card_text_len_two_text) - 30
                    card_text_len_two_text = card_text_len_two_text[:-range_trima]
                try:
                    card_text_len_two = driver.find_element_by_xpath('/html/body/ytve-info-cards-modal/ytve-modal-host/ytcp-dialog/paper-dialog/div[2]/div/ytve-editor/div[1]/div/ytve-info-cards-editor-options-panel/div[3]/div[2]/ytve-info-cards-editor-playlist-card-options/ytve-info-cards-editor-teaser-options/div/ytve-lightweight-textarea/div/div[2]/textarea')
                    card_text_len_two.send_keys(card_text_len_two_text)
                    time.sleep(3)
                except:
                    print('not fgound')

                
                time.sleep(5)
                #slide the slider
                print('sliding slider')
                driver.execute_script("document.querySelector('#markers > ytve-point-marker').style['left']='50px';")
                time.sleep(1)
                slide = driver.find_element_by_css_selector('#markers > ytve-point-marker')
                actionChains = ActionChains(driver)
                move = ActionChains(driver)
                move.click_and_hold(slide).move_by_offset(10, 0).release().perform()
                #adds the player if he pro
                if is_it_apro == True:
                    driver.find_element_by_css_selector('#add-card-button').click()
                    time.sleep(3)
                    driver.find_element_by_css_selector('#text-item-1 > ytcp-ve > div > div > yt-formatted-string').click()
                    time.sleep(6)
                    cards_player = driver.find_element_by_css_selector('#tabs')
                    cards_player.send_keys(player_plali)
                    time.sleep(2)
                    driver.find_element_by_xpath('//*[@id="inner-dialog"]/div[3]/ytcp-entity-card[1]').click()
                    time.sleep(2)
                    cards_player_text_one = driver.find_element_by_css_selector('#textarea-container > textarea')
                    player_text_len_one = champion[2] + ' Playlist'
                    if len(player_text_len_one) >= 30:
                        range_trim = len(player_text_len_one) - 30
                        player_text_len_one = player_text_len_one[:-range_trim]
                    cards_player_text_one.send_keys(player_text_len_one)
                    time.sleep(1)
                    card_text_len_two_text = 'Watch ' + champion[2] + ' Playlist'
                    if len(card_text_len_two_text) >= 30:
                        range_trima = len(card_text_len_two_text) - 30
                        card_text_len_two_text = card_text_len_two_text[:-range_trima]
                    try:

                        card_text_len_two = driver.find_element_by_css_selector('/html/body/ytve-info-cards-modal/ytve-modal-host/ytcp-dialog/paper-dialog/div[2]/div/ytve-editor/div[1]/div/ytve-info-cards-editor-options-panel/div[3]/div[2]/ytve-info-cards-editor-playlist-card-options/ytve-info-cards-editor-teaser-options/div/ytve-lightweight-textarea/div/div[2]/textarea')
                        card_text_len_two.send_keys(card_text_len_two_text)
                    except:
                        print('kostana')
                    time.sleep(3)
                    
                    time.sleep(5)
                    #slide the slider
                    print('sliding slider')
                    driver.execute_script("document.querySelector('#markers > ytve-point-marker:nth-child(2)').style['left']='70px';")
                    time.sleep(2)

                    slide = driver.find_element_by_css_selector('#markers > ytve-point-marker:nth-child(2)')
                    actionChains = ActionChains(driver)
                    move = ActionChains(driver)
                    move.click_and_hold(slide).move_by_offset(10, 0).release().perform()
                    time.sleep(4)




                time.sleep(4)
                driver.find_element_by_css_selector('#save-button').click()
                time.sleep(15)
                #next page
                driver.find_element_by_xpath('//*[@id="next-button"]').click()
                print("Clicked Next button! on copyright page now waiting for 7 seconds")
                time.sleep(25)
                driver.find_element_by_css_selector('#next-button').click()
                print("Clicked Next button! waiting for 7 seconds")
                time.sleep(9)
                #driver.find_element_by_css_selector('#first-container').click()
                print("clicked publish")
                time.sleep(6)

                print("Clicking done and we are almost done")
                driver.find_element_by_xpath('//*[@id="done-button"]').click()
                print("AND WE ARE DONE! Video uploaded.!")
                now = datetime.now()
                dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
                py_sql.quary_insert_uploaded(champion[0],champion[1],str(dt_string))
                shutil.move("D:/lolreplays/replays/%s"%vid_name,"D:/lolreplays/replays_uploaded/")
                time.sleep(random.randrange(10,25))
                time.sleep(1)
            else:
                print('No videos to upload! , waiting.....')
                time.sleep(random.randrange(10,25))
        except Exception as e:
            
            just_the_string = traceback.format_exc()
            py_sql.quary_insert_errors_videos(vid_name,str(e),str(just_the_string))



if __name__ == "__main__":
    upload_video()

```
### Final notes

And thats it , the video is uploaded. I know that time.sleep() is not ideal to use but in my case with youtube reactive UI it seems to work best. I've uploaded the source codes for engine.py , scrapper.py , thumbnail.py here : https://github.com/silvdoche/NexusR

That is just a small part of the whole project source code , but the other parts are unedited without comments and it's a huge mess. Took me about a month to finish the whole project from scratch and another month to fix all the bugs and calibrate it correctly. The project is put on hold and have not been active for 3 months.