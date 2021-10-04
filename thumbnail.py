from PIL import Image

def trans_paste(bg_img,fg_img,box=(0,0)):
    fg_img_trans = Image.new("RGBA",bg_img.size)
    fg_img_trans.paste(fg_img,box,mask=fg_img)
    new_img = Image.alpha_composite(bg_img,fg_img_trans)
    return new_img


def generate(skin_1,skin_2,lane_pos,player1,player2,region,patch,champion_f,champion_e,rune_f,rune_e,penta_):
    background = Image.open("images/thumbnail/background.png")
    skin1 = Image.open("images/thumbnail/champions/"+champion_f+"/"+skin_1+".png").resize((640,720))
    skin2 = Image.open("images/thumbnail/champions/"+champion_e+"/"+skin_2+".png").resize((640,720))
    #opacity_mask = Image.open("images/thumbnail/opacity_mask.png").convert("RGBA")
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
    

#thumbnail.generate("High Noon Lucian","Enduring Sword Talon","mid","doinb","Master","kr","10.1","Lucian","Talon","Press the Attack","Electrocute","1025205")