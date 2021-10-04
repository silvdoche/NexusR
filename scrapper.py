from bs4 import BeautifulSoup as soup  
from urllib.request import Request, urlopen
import sys
import func_
import py_sql
import time
import datetime


#get player soup data
def get_player_soup(player_name,player_region):
    page_url = "https://www.leagueofgraphs.com/summoner/"+player_region+"/"+player_name+""
    hdr = {'User-Agent': 'Mozilla/5.0'}
    # opens the connection and downloads html page from url
    uClient = Request(page_url,headers=hdr)
    page = urlopen(uClient)
    # parses html into a soup data structure to traverse html
    page_soup = soup(page.read())
    page.close()
    return page_soup

#get the table data for recent games ,ALWAYS START AT 1 , 0 is trash data
def get_player_tr(soupdataT):
    matchdata = soupdataT.findAll("table",{"class":"data_table relative recentGamesTable"})
    #get all rows , note [0] is always game types so skip
    matchdatatr = matchdata[0].findAll("tr")
    return matchdatatr

#get player ELO
def get_player_elo(soupdataK):
    getRank = soupdataK.findAll("div",{"class" : "leagueTier"})
    ELO = getRank[0].text.split()
    # Tier = ELO[0]
    # LP = ELO[1]
    # print(Tier + " LP : " + LP)
    return ELO

def get_player_recent_time(soupdataRC):
    match_time_data_recent = soupdataRC.find("div",{"class":"gameDate requireTooltip"}).text.split()
    if match_time_data_recent[1] == "hour" or match_time_data_recent[1] == "hours":
        return "hour"
    else:
        return "long"

    


#get player champion
def get_player_champion(soupdataC):
    matchdatatr = soupdataC
    #get champion data
    champ_data = matchdatatr.findAll("td",{"class":"championCellLight"})
    champion = champ_data[0].img['title']
    return champion

#get the game mode data
def get_player_gamemode(soupdataM):
    gameModeData = soupdataM.findAll("div",{"class":"gameMode requireTooltip"})
    #strip the game mode
    gamem_mode = gameModeData[0].text.strip()
    return gamem_mode


#get the KDA data
def get_player_KDA(soupdataKD):
    KDA_Data = soupdataKD.findAll("div",{"class":"kda"})
    KDA_Parse = KDA_Data[0].findAll("span",{"class":["kills","deaths","assists"]})
    kills = float(KDA_Parse[0].text)
    deaths = float(KDA_Parse[1].text)
    assist = float(KDA_Parse[2].text)
    kda = 0.0
    #calculate KDA rating
    if deaths == 0 :
        kda = kills+assist
    else:
        kda = kills+assist/deaths
    return kda

#get game result
def get_player_gameresult(soupdataGR):
    match_result = soupdataGR.findAll("div",{"class":"victoryDefeatText victory"})
    #match_result_split = match_result[1].text
    match_result_end = ""
    if not match_result:
        match_result_end = "Defeat"
    else:
        match_result_end = "Victory"
    return match_result_end

#get game lenght  match_time[0]=minutes match_time[1]=seconds
def get_player_gamelenght(soupdataL):
    match_time_data = soupdataL.find("div",{"class":"gameDuration"}).text.split()
    match_time_calc = [int(match_time_data[0].replace("min","")),int(match_time_data[1].replace("s",""))]
    match_time = str(datetime.timedelta(seconds=match_time_calc[0]*60+match_time_calc[1]))
    return match_time

#get game id
def get_player_gameid(soupdataID):
    match_id_data = soupdataID.find("div",{"class":"gameDate"})
    match_id = match_id_data["tooltip-var"]
    match_id = match_id.replace("match-","")
    return match_id

#get all participents  data
def get_player_matchplayers(soupdataMP):
    participents_data = soupdataMP.findAll("td",{"class":"summonersTdLight"})
    #get all participents names
    participents_names = participents_data[0].findAll("div",{"class":"txt"})
    #get all participents champions
    participents_champs = participents_data[0].findAll('img')
                            
    #loop thro all data
    #for x in range(len(participents_names)):
    #    print (participents_names[x].text.rstrip().lstrip() + " Champions : " + participents_champs[x]['alt'])

    summoner_name = []
    for x in range(len(participents_names)):
        summoner_name.append(participents_names[x].text.rstrip().lstrip())

    summoner_champ = []
    for x in range(len(participents_names)):
        summoner_champ.append(participents_champs[x]['alt'])
    return [summoner_name,summoner_champ]

#get player lane position
def get_player_lanePOS(soupdataPOS,champion):
    lane_position = ""
    position = soupdataPOS.index(champion)
    if position == 0 or position == 5:
        lane_position = "Top"
    elif position == 1 or position == 6:
        lane_position = "Jungle"
    elif position == 2 or position == 7:
        lane_position = "Mid"
    elif position == 3 or position == 8:
        lane_position = "ADC"
    elif position == 4 or position == 9:
        lane_position = "Support"
    return lane_position

#get enemy laner
def get_player_enemylaner(summoner_name,summoner_champ,position):
    enemy_laner = [summoner_name[func_.getenemypos(position)],summoner_champ[func_.getenemypos(position)]]
    #print(lane_position + " VS : " + enemy_laner[0] + enemy_laner[1])
    return enemy_laner

#get replay url
def get_player_replayurl(soupdataRE):
    has_replay = None
    replay_url = ""
    replay_url_data = soupdataRE.findAll("button",{"class":"replay_button_super_small poplight spectatePopupLink hide-for-small-down-custom"})
    #check if there is replay
    if replay_url_data == []:
        has_replay = False
    else:
        has_replay = True
        replay_url = "https://www.leagueofgraphs.com" + replay_url_data[0]["data-spectate-link"]
    return replay_url


def get_player_side(soupdataSD,champion):
    side = soupdataSD.index(champion)
    if side <= 4:
        return "blue"
    else:
        return "red"

    #py_sql.quary_que(champion,player_name,player_region,match_id,replay_url,enemy_laner[0],enemy_laner[1],match_time,lane_position,Tier,LP)
    #text_file = open("Output.txt", "w")
    #text_file.write(str(matchdata[0]))
    #text_file.close()
    #print(page_soup)

