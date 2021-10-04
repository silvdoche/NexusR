from bs4 import BeautifulSoup as soup  
from urllib.request import Request, urlopen
import sys
import func_
import py_sql
import time
import datetime
import py_sql
import pickle




#finds gameduration requires first(thats the row)
def game_duration(soup_row):
    gamedur = soup_row.find("span",{"class":"gameDuration"}).text.split()
    strtime = str(gamedur[0]).strip("()").split(":")
    match_time = str(datetime.timedelta(seconds=int(strtime[0])*60+int(strtime[1])))
    return match_time

#find game id requires first(thats the row)
def get_gameid(soup_row):
    linkhr = soup_row.find("th",{"class":"hide-for-small-down"})
    gameid = linkhr.find("a",href=True)
    gameid = gameid['href']
    gameid = gameid.split("/")
    gameid = gameid[3]
    return gameid




#finding which side won , requires alltr[0]
def get_winside(soupa):
    allspans = soupa.findAll("span")
    if allspans[0].text == "Victory":
        Winside = "blue"
    else:
        Winside = "red"
    return Winside

#find game download link , requires alltr[11]
def get_rlink(soupa):
    replaylink_raw = soupa.find("a",{"class":"poplight spectatePopupLink"})
    replaylink = "https://www.leagueofgraphs.com" + replaylink_raw['data-spectate-link']
    return replaylink

#kills per tr 
#pdata = alltr[5]
def get_kda(pdata):
    kills_raw = pdata.findAll("span",{"class":"kills"})
    deaths_raw = pdata.findAll("span",{"class":"deaths"})
    assists_raw = pdata.findAll("span",{"class":"assists"})
    kills_blue = float(kills_raw[0].text)
    kills_red = float(kills_raw[2].text)
    deaths_blue = float(deaths_raw[0].text)
    deaths_red = float(deaths_raw[2].text)
    assist_blue = float(assists_raw[0].text)
    assist_red = float(assists_raw[2].text)
    kda_blue = calc_kda(kills_blue,deaths_blue,assist_blue)
    kda_red = calc_kda(kills_red,deaths_red,assist_red)
    return [kda_blue,kda_red]

def calc_kda(kills,deaths,assist):
    kda = 0.0
    if deaths == 0 :
        kda = kills+assist
    else:
        kda = kills+assist/deaths
    return kda

#find their rank , requires pdata
def get_rank(soupa):
    rank = soupa.findAll("div",{"class":"subname"})
    left_elo = rank[0].text.rstrip().lstrip()
    right_elo = rank[1].text.rstrip().lstrip()
    left_filtered = filter_rank(left_elo)
    right_filtered = filter_rank(right_elo)
    return [left_filtered,right_filtered]

def filter_rank(rank_buffer):
    if rank_buffer != "Challenger" and rank_buffer != "GrandMaster" and rank_buffer != "Master":
        rank = "Master"
    else:
        rank = rank_buffer
    return rank

#find their names requires pdata
def get_names(soupa):
    names = soupa.findAll("div",{"class":"name"})
    left_name = names[0].text.rstrip().lstrip()
    right_name = names[1].text.rstrip().lstrip()
    return [left_name,right_name]

#find their champions requires pdata
def get_champions(soupa):
    blue_champ_raw = soupa.find("div",{"class":"img-align-block"})
    red_champ_raw = soupa.find("div",{"class":"img-align-block-right"})
    blue_champ = blue_champ_raw.find("img")['title']
    red_champ = red_champ_raw.find("img")['title']
    return [blue_champ,red_champ]

def get_lanepos(posit):
    if posit == 0:
        return "Top"
    if posit == 1:
        return "Jungle"
    if posit == 2:
        return "Mid"
    if posit == 3:
        return "ADC"
    if posit == 4:
        return "Support"

def games_arrays(soupa,soupa_tr,region):
    ia = []
    ib = []
    souped_tr = soupa_tr
    del souped_tr[0]
    generated = [[ia for i in range(12)] for ib in range(5)]
    winside = get_winside(soupa)
    game_dur = game_duration(soupa)
    game_id = get_gameid(soupa)
    game_link = get_rlink(soupa)
    if winside == "blue":
        ss = 0
        sz = 1
    else:
        ss = 1
        sz = 0
    for z in range(len(generated)):
        generated[z][0] = get_champions(souped_tr[z])[ss]
        generated[z][1] = get_names(souped_tr[z])[ss]
        generated[z][2] = region
        generated[z][3] = game_id
        generated[z][4] = game_link
        generated[z][5] = get_names(souped_tr[z])[sz]
        generated[z][6] = get_champions(souped_tr[z])[sz]
        generated[z][7] = game_dur
        generated[z][8] = get_lanepos(z)
        generated[z][9] = get_rank(souped_tr[z])[ss]
        generated[z][10] = winside
        generated[z][11] = get_kda(souped_tr[z])[ss]
    return generated

#############################################################
# game_duration (requires soup row)                         #
#first to get duration                                      #
#############################################################
# get_gameid (requires soup row)                            #
#second to get game id                                      #
#############################################################
# get_winside (requires soup row 0 {alltr[0]})              #
# third to get win side                                     #
#############################################################
# get_rlink ( requires soup row)                            #
#forth to get replay link                                   #
#############################################################
# get_kda ( requires alltr{this is from 1 to 5 rows})       #
#from 0 to 5 in itteration                                  #
#############################################################
# get_rank ( requires alltr{this is from 1 to 5 rows})      #
#from 0 to 5 in itteration                                  #
#############################################################                
# get_names ( requires alltr{this is from 1 to 5 rows})     #
#from 0 to 5 in itteration                                  #
#############################################################
# get_champions ( requires alltr{this is from 1 to 5 rows}) #
#from 0 to 5 in itteration                                  #                
#############################################################

#find all games and splits them in 5 array
def scrape(page_url,region):
#page_url = "https://www.leagueofgraphs.com/replays/all/kr/challenger/short"
    hdr = {'User-Agent': 'Mozilla/5.0'}
    # opens the connection and downloads html page from url
    uClient = Request(page_url,headers=hdr)
    page = urlopen(uClient)
    # parses html into a soup data structure to traverse html
    page_soup = soup(page.read())
    page.close()
    matchdata = page_soup.findAll("div",{"class":"box matchBox"})

    #finds all tr in the first game , first is matchdata[0]
    arr_games = []
    arr_games.append(matchdata[0])
    arr_games.append(matchdata[1])
    arr_games.append(matchdata[2])
    arr_games.append(matchdata[3])
    arr_games.append(matchdata[4])

    arr_trs = []
    arr_trs.append(matchdata[0].findAll("tr"))
    arr_trs.append(matchdata[1].findAll("tr"))
    arr_trs.append(matchdata[2].findAll("tr"))
    arr_trs.append(matchdata[3].findAll("tr"))
    arr_trs.append(matchdata[4].findAll("tr"))


    #region = "kr"

    xy = []
    for i in range(5):
        xy.extend(games_arrays(arr_games[i],arr_trs[i],region))
    return xy

def constructor_(bracket,region,offset,n_games):

    allg = []
    for i in range(8):
        try:
            print("Current Itteration Page : {} and Region : {}".format(str(i),region))
            allg.extend(scrape("https://www.leagueofgraphs.com/replays/all/{}/{}/short/page-{}".format(region,bracket,i+1),region))
            time.sleep(10)
        except:
            print("page scrapping exceeded at position : {}".format(i+1))

    tt_kda = []
    for x in range(len(allg)):
        tt_kda.append(allg[x][11])

    best_match = []


    #with open('outfileDG', 'wb') as fp:
        #pickle.dump(allg, fp)

    for y in range(50):
        best_match.append(tt_kda.index(max(tt_kda)))
        tt_kda[tt_kda.index(max(tt_kda))] = 0.0
        #with open('outfileDB', 'wb') as fp:
            #pickle.dump(best_match, fp)

    l_del = []

    try:
        for u in range(len(best_match)):
            if py_sql.quary_last_champ_second(allg[best_match[u]][0],py_sql.quary_tolerance_check(allg[best_match[u]][0])[0][0] + offset) == True or py_sql.quary_check_second(allg[best_match[u]][3],allg[best_match[u]][0]) == True:
                l_del.append(best_match[u])
    except:
        print('exceeded range limits on constructor for casual')
    dif = [ x for x in best_match if not x in l_del ]

    for q in range(n_games):
        try:
            py_sql.quary_que(allg[dif[q]][0],allg[dif[q]][1],allg[dif[q]][2],allg[dif[q]][3],allg[dif[q]][4],allg[dif[q]][5],allg[dif[q]][6],allg[dif[q]][7],allg[dif[q]][8],allg[dif[q]][9],"0",allg[dif[q]][10])
        except:
            "Limit constructor KR exceeded"