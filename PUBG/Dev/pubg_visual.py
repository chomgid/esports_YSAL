# api 요청
import requests
import json
# 이미지 다운
import os
import time
from PIL import Image
# 데이터 자료형 및 분석도구
import pandas as pd
import numpy as np
# 시각화 패키지
import matplotlib as mlp
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.image as mpimg
import matplotlib.pyplot as plt
from matplotlib import patheffects

# 시간
import time
import datetime
# 스케일링
from sklearn.preprocessing import MinMaxScaler
import math
# 진행 사항 확인
from tqdm import tqdm
# PUBG 분석 도구
import chicken_dinner
from chicken_dinner.pubgapi import PUBG
from chicken_dinner.pubgapi import PUBGCore
from chicken_dinner.constants import COLORS
from chicken_dinner.constants import map_dimensions

def get_tours(api_key):
    url = "https://api.pubg.com/tournaments"
    headers = {'accept': 'application/vnd.api+json',
            'Authorization': f'Bearer {api_key}'}
    r = requests.get(url, headers=headers)
    tour_json = r.json()
    tourID_list = []
    for data in tour_json["data"]:
        tourID_list.append(data["id"])

    return tourID_list


def get_matchID(api_key, tournamentID ="as-pgs1gf" ):
    pubg = PUBG(api_key)
    tour = pubg.tournament(tournamentID)
    matchId = tour.match_ids
    return matchId


def track(api_key, match_id, teamName,tournmentID = "as-pgs1gf"):
    api_key = api_key
    pubg = PUBG(api_key)

    # pgs1 토너먼트만 가져오기
    tour = pubg.tournament(tournmentID)
    matchId = tour.match_ids

    # Erangel, Miramar 구분
    ErangelId = []
    MiramarId = []
    for id in matchId:
        match = pubg.match(id, shard="tournament")
        if match.map_name == 'Erangel (Remastered)':
            ErangelId.append(id)
        elif match.map_name == 'Miramar':
            MiramarId.append(id)
    
    # map 이미지 다운
    Erangel_url = "https://i.namu.wiki/i/F_NInQG03981Yy0k8Le59R5Ey-CA2oFsikXQCcctk1qLZxz3HpSiYGQseibzFRV7ZsB8GBRHd4U5BQRZCyWaLw.webp"
    Miramar_url = "https://i.namu.wiki/i/cpjvLRGACQfciwKyBWFi4EOGCZUAniqNPsWXFunBbFP7FAxbFA0P_8U9-adzKj3nfhGl7G9igN3u1czGGBno-0614bSnNBaHQuylF3v59i5x9h8V0OFjsGnya70kewUKv_regMcnW8Mqw0a1NWXJ7w.webp"

    start = time.time()

    os.system("curl " + Miramar_url + " > Miramar.jpg")
    os.system("curl " + Erangel_url + " > Erangel.jpg")


    # track data 그리기
    current_match = pubg.match(match_id, shard="tournament")
    telemetry = current_match.get_telemetry()
    map_id = current_match.map_id
    mapx, mapy = map_dimensions[map_id]
    positions = telemetry.player_positions()
    circles = telemetry.circle_positions()
    whites = np.array(circles['white'])
    whites[:, 2] = mapy - whites[:, 2]
    phases = np.where(whites[1:, 4] - whites[:-1, 4] != 0)[0] + 1

    fig = plt.figure(figsize=(10, 10), dpi=100)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.axis("off")
    if map_id == "Desert_Main":
        path =  "./Miramar.jpg"
    else:
        path = "./Erangel.jpg"

    img = mpimg.imread(path)
    ax.imshow(img, extent=[0, mapx, 0, mapy])
    for phase in phases:
        white_circle = plt.Circle((whites[phase][1], whites[phase][2]), whites[phase][4],
                                    edgecolor="w", linewidth=0.7, fill=False, zorder=5)
        ax.add_patch(white_circle)

    startTime = pd.to_timedelta(telemetry.started()[telemetry.started().find('T')+1:-1])
    unequips = telemetry.filter_by('log_item_unequip')
    landing_locations = {unequip['character']['name']:
                            (unequip['character']['location']['x'], mapy - unequip['character']['location']['y'],
                            (pd.to_timedelta(unequip.timestamp[unequip.timestamp.find('T')+1:-1]) - startTime).total_seconds(),
                            unequip['character']['team_id'])
                            for unequip in unequips if unequip['item']['item_id'] == 'Item_Back_B_01_StartParachutePack_C'}
    landing_locations = pd.DataFrame(landing_locations).T.reset_index()
    landing_locations.columns = ['name', 'x', 'y', 'time', 'teamId']
    landing_locations['teamId'] = landing_locations['teamId'].astype('int64')
    landing_locations['teamName'] = landing_locations['name'].str.extract(r'([0-9A-Za-z]+)\_')

    x_sum = 0
    y_sum = 0
    count = 0
    for player in positions.keys():
        if teamName not in player :continue
        curpos = np.array(positions[player])
        curpos[:, 2] = mapy - curpos[:, 2]
        curlanding = landing_locations[landing_locations['name'] == player]
        curpos = curpos[curpos[:, 0] > curlanding['time'].values[0]]
        x_sum += curpos[0,1]
        y_sum += curpos[0,2]
        count+=1
        ax.plot(curpos[:, 1], curpos[:, 2], '--', linewidth=2, color = 'w', zorder=20)
    
    label = ax.text(x_sum/count-500, y_sum/count+500, '{}'.format(teamName,fontsize = "medium", visible = True), color='w', size=10, zorder=22)
    label.set_path_effects([patheffects.withStroke(linewidth=1.5, foreground='k')])


def landing(api_key, match_id, tournmentID = "as-pgs1gf"):
    api_key = api_key
    pubg = PUBG(api_key)

    # pgs1 토너먼트만 가져오기
    tour = pubg.tournament("as-pgs1gf")
    matchId = tour.match_ids

    # Erangel, Miramar 구분
    ErangelId = []
    MiramarId = []
    for id in matchId:
        match = pubg.match(id, shard="tournament")
        if match.map_name == 'Erangel (Remastered)':
            ErangelId.append(id)
        elif match.map_name == 'Miramar':
            MiramarId.append(id)

    # map 이미지 다운
    Erangel_url = "https://i.namu.wiki/i/F_NInQG03981Yy0k8Le59R5Ey-CA2oFsikXQCcctk1qLZxz3HpSiYGQseibzFRV7ZsB8GBRHd4U5BQRZCyWaLw.webp"
    Miramar_url = "https://i.namu.wiki/i/cpjvLRGACQfciwKyBWFi4EOGCZUAniqNPsWXFunBbFP7FAxbFA0P_8U9-adzKj3nfhGl7G9igN3u1czGGBno-0614bSnNBaHQuylF3v59i5x9h8V0OFjsGnya70kewUKv_regMcnW8Mqw0a1NWXJ7w.webp"

    start = time.time()

    os.system("curl " + Miramar_url + " > Miramar.jpg")
    os.system("curl " + Erangel_url + " > Erangel.jpg")

    current_match = pubg.match(match_id, shard="tournament")
    telemetry = current_match.get_telemetry()
    positions = telemetry.player_positions()
    map_id = telemetry.map_id()
    mapx, mapy = map_dimensions[map_id]
    circles = telemetry.circle_positions()
    whites = np.array(circles['white'])
    whites[:, 2] = mapy - whites[:, 2]
    curpos = np.array(positions.popitem()[1])
    curpos[:, 2] = mapy - curpos[:, 2]

    unequips = telemetry.filter_by('log_item_unequip') # 아이템 제거한 이벤트
    landing_locations = {unequip['character']['name']:
                            (unequip['character']['location']['x'], mapy - unequip['character']['location']['y'],
                            unequip['character']['team_id'])
                            for unequip in unequips if unequip['item']['item_id'] == 'Item_Back_B_01_StartParachutePack_C'} # 낙하산 제거
    landing_locations = pd.DataFrame(landing_locations).T.reset_index()
    landing_locations.columns = ['name', 'x', 'y', 'teamId']
    landing_locations['teamId'] = landing_locations['teamId'].astype('int64')


    #비행기 라인 기울기 및 절편 계산 (수송선 내에 있는 경우의 플레이어 데이터 이용)
    slope1 = (curpos[0][2] - curpos[1][2]) / (curpos[0][1] - curpos[1][1])
    beta1 = curpos[1][2] - curpos[1][1]*slope1
    x = np.linspace(0, mapx, 100)
    y = slope1*x + beta1
    x = np.delete(x, np.where(y > mapy))
    y = np.delete(y, np.where(y > mapy))
    np.random.shuffle(COLORS)

    map_range = (0, mapy)
    map_range = np.array(map_range).astype('float64').reshape(-1, 1)
    scaler = MinMaxScaler(feature_range=(0, 8))
    scaler.fit(map_range)
    # 낙하산 거리 계산 (선과 직선 사이의 수직선 거리 계산 공식 이용)
    landing_locations['chuteDist'] = np.abs(slope1*landing_locations.x - landing_locations.y + beta1) / np.sqrt(slope1*slope1 + 1)
    landing_locations['chuteDist'] = scaler.transform(landing_locations['chuteDist'].values.reshape(-1, 1))
    landing_locations['teamName'] = landing_locations['name'].str.extract(r'([0-9A-Za-z]+)\_')

    landing_locations["circleDist"] = np.sqrt((landing_locations.x - whites[whites[:,4]>0][0][1])**2 + (landing_locations.y - whites[whites[:,4]>0][0][2])**2)
    landing_locations["circleDist"] = landing_locations["circleDist"]/100000
    team_dists = landing_locations.groupby('teamName').mean()
    team_dists['chuteDist'] = np.round(team_dists['chuteDist'], 2)
    team_dists['circleDist'] = np.round(team_dists['circleDist'], 2)

    fig = plt.figure(figsize=(10, 10), dpi=100)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.axis("off")
    if map_id == "Desert_Main":
        path =  "./Miramar.jpg"
    else:
        path = "./Erangel.jpg"
    img = mpimg.imread(path)
    ax.imshow(img, extent=[0, mapx, 0, mapy])


    # 화이트존 그리기
    white_circle = plt.Circle((whites[whites[:,4]>0][0][1], whites[whites[:,4]>0][0][2]), whites[whites[:,4]>0][0][4], edgecolor="w", linewidth=2, fill=False, zorder=5)
    ax.add_patch(white_circle)
    ax.plot(x, y, 'r--', linewidth=3, zorder=20) # 비행기 라인

    used_teamId = []
    for index, row in landing_locations.iterrows():
        # 직교하는 선 구하기
        slope2 = -1 / slope1
        beta2 = row.y - row.x*slope2
        x2 = -(beta1-beta2)/(slope1-slope2)
        y2 = x2*slope1 + beta1

        if not row['teamId'] in used_teamId:  # 각 팀의 첫 번째만 글자 그리기
            teamName = row["name"][:row['name'].find('_')]
            label = ax.text(team_dists['x'][teamName], team_dists['y'][teamName] + np.random.randint(-10000, 10000),
                            '{}: {}Km'.format(teamName, team_dists['circleDist'][teamName],fontsize = "small", visible = True),
                            color=COLORS[row['teamId']], size=10, zorder=22)
            label.set_path_effects([patheffects.withStroke(linewidth=1.5, foreground='k')])
            used_teamId.append(row['teamId'])
        # ax.plot([x2, row.x], [y2, row.y], c=COLORS[row['teamId']], linestyle='--', linewidth=0.5, zorder=15) # 선수와 비행기 간의 선
        ax.scatter(row.x, row.y, marker="o", c=COLORS[row['teamId']], edgecolor="k", s=60, linewidths=1, zorder=20); # 선수

    return landing_locations


def first_fight(api_key, match_id, teamName, tournmentID = "as-pgs1gf"):
    api_key = api_key
    pubg = PUBG(api_key)

    # pgs1 토너먼트만 가져오기
    tour = pubg.tournament(tournmentID)
    matchId = tour.match_ids

    # Erangel, Miramar 구분
    ErangelId = []
    MiramarId = []
    for id in matchId:
        match = pubg.match(id, shard="tournament")
        if match.map_name == 'Erangel (Remastered)':
            ErangelId.append(id)
        elif match.map_name == 'Miramar':
            MiramarId.append(id)

    # map 이미지 다운
    Erangel_url = "https://i.namu.wiki/i/F_NInQG03981Yy0k8Le59R5Ey-CA2oFsikXQCcctk1qLZxz3HpSiYGQseibzFRV7ZsB8GBRHd4U5BQRZCyWaLw.webp"
    Miramar_url = "https://i.namu.wiki/i/cpjvLRGACQfciwKyBWFi4EOGCZUAniqNPsWXFunBbFP7FAxbFA0P_8U9-adzKj3nfhGl7G9igN3u1czGGBno-0614bSnNBaHQuylF3v59i5x9h8V0OFjsGnya70kewUKv_regMcnW8Mqw0a1NWXJ7w.webp"

    start = time.time()

    os.system("curl " + Miramar_url + " > Miramar.jpg")
    os.system("curl " + Erangel_url + " > Erangel.jpg")



    current_match = pubg.match(match_id, shard="tournament")

    telemetry = current_match.get_telemetry()
    startTime = pd.to_timedelta(telemetry.started()[telemetry.started().find('T')+1:-1])
    positions = telemetry.player_positions()
    pl_names = telemetry.player_names()
    map_id = telemetry.map_id()
    mapx, mapy = map_dimensions[map_id]
    teams = pd.DataFrame(pl_names, columns=["player_name"])
    teams["team"] = teams["player_name"].str.extract(r'([0-9A-Za-z]+)\_')
    circles = telemetry.circle_positions()
    whites = np.array(circles['white'])
    whites[:, 2] = mapy - whites[:, 2]


    fig = plt.figure(figsize=(10, 10), dpi=100)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.axis("off")
    if map_id == "Desert_Main":
        path =  "./Miramar.jpg"
    else:
        path = "./Erangel.jpg"

    img = mpimg.imread(path)
    ax.imshow(img, extent=[0, mapx, 0, mapy])

    np.random.shuffle(COLORS)

    # 첫 교전 plot
    damage = telemetry.filter_by('log_player_take_damage')
    used_teamId = []

    for event in damage:
        if ((event.damage_type_category == 'Damage_Gun')&(event.damage_type_category != 'Damage_Groggy')&
            (event.damage_type_category != 'Damage_Explosion_Grenade')&(event.damage_type_category != "Damage_Molotov")):
            if not teams[teams["player_name"]==event.attacker.name]["team"][teams[teams["player_name"]==event.attacker.name].index.to_list()[0]] in used_teamId:
                pos_idx = int(math.ceil((pd.to_timedelta(event.timestamp[event.timestamp.find('T')+1:-1]) - startTime).total_seconds())/10)
                att_team = teams[teams["player_name"]==event.attacker.name]["team"][teams[teams["player_name"]==event.attacker.name].index.to_list()[0]]
                def_team  = teams[teams["player_name"]==event.victim.name]["team"][teams[teams["player_name"]==event.victim.name].index.to_list()[0]]
                
                if((teamName == att_team)|(teamName == att_team)):
                    x_sum = 0
                    y_sum = 0
                    count = 0
                    for player in teams[teams["team"]==att_team]["player_name"]:
                        try:
                            x = positions[player][pos_idx][1]
                            y = positions[player][pos_idx][2]
                            x_sum += x
                            y_sum += y
                            count+=1
                            ax.scatter(x,y, marker="o", c=COLORS[0], edgecolor="k", s=60, linewidths=1, zorder=20)
                        except:
                            continue
                    label = ax.text(x_sum/count-500, y_sum/count+500, '{}'.format(att_team,fontsize = "small", visible = True), color=COLORS[0], size=10, zorder=22)
                    label.set_path_effects([patheffects.withStroke(linewidth=1.5, foreground='k')])
                    used_teamId.append(att_team)

                    x_sum = 0
                    y_sum = 0
                    count = 0
                    for player in teams[teams["team"]==def_team]["player_name"]:
                        try:
                            x = positions[player][pos_idx][1]
                            y = positions[player][pos_idx][2]
                            x_sum += x
                            y_sum += y
                            count+=1
                            ax.scatter(x,y, marker="o", c=COLORS[1], edgecolor="k", s=60, linewidths=1, zorder=20)

                        except:
                            continue
                    label = ax.text(x_sum/count-500, y_sum/count+500, '{}'.format(def_team,fontsize = "small", visible = True), color=COLORS[1], size=10, zorder=22)
                    label.set_path_effects([patheffects.withStroke(linewidth=1.5, foreground='k')])
                    used_teamId.append(def_team)
        


def get_rank(api_key, match_id, tournmentID = "as-pgs1gf"):
    api_key = api_key
    pubg = PUBG(api_key)

    current_match = pubg.match(match_id, shard="tournament")
    ranking = current_match.get_telemetry().rankings()
    keys = list(ranking.keys())
    keys.sort()
    sorted_rank = {i:ranking[i] for i in keys}
    rank = pd.DataFrame((sorted_rank.keys(), sorted_rank.values())).T

    h = []
    for a in rank.iloc[:,1]:
        h.append(a[0][:a[0].find("_")])
    
    rank = pd.DataFrame(h, columns=["teamName"])
    rank["rank"] = pd.DataFrame(rank.index+1)
    return rank




def compare_rank_dist(api_key, match_id, par, tournmentID = "as-pgs1gf"):
    api_key = api_key
    pubg = PUBG(api_key)

    current_match = pubg.match(match_id, shard="tournament")
    telemetry = current_match.get_telemetry()
    positions = telemetry.player_positions()
    map_id = telemetry.map_id()
    mapx, mapy = map_dimensions[map_id]
    circles = telemetry.circle_positions()
    whites = np.array(circles['white'])
    whites[:, 2] = mapy - whites[:, 2]
    curpos = np.array(positions.popitem()[1])
    curpos[:, 2] = mapy - curpos[:, 2]

    unequips = telemetry.filter_by('log_item_unequip') # 아이템 제거한 이벤트
    landing_locations = {unequip['character']['name']:
                            (unequip['character']['location']['x'], mapy - unequip['character']['location']['y'],
                            unequip['character']['team_id'])
                            for unequip in unequips if unequip['item']['item_id'] == 'Item_Back_B_01_StartParachutePack_C'} # 낙하산 제거
    landing_locations = pd.DataFrame(landing_locations).T.reset_index()
    landing_locations.columns = ['name', 'x', 'y', 'teamId']
    landing_locations['teamId'] = landing_locations['teamId'].astype('int64')


    #비행기 라인 기울기 및 절편 계산 (수송선 내에 있는 경우의 플레이어 데이터 이용)
    slope1 = (curpos[0][2] - curpos[1][2]) / (curpos[0][1] - curpos[1][1])
    beta1 = curpos[1][2] - curpos[1][1]*slope1
    x = np.linspace(0, mapx, 100)
    y = slope1*x + beta1
    x = np.delete(x, np.where(y > mapy))
    y = np.delete(y, np.where(y > mapy))
    np.random.shuffle(COLORS)

    map_range = (0, mapy)
    map_range = np.array(map_range).astype('float64').reshape(-1, 1)
    scaler = MinMaxScaler(feature_range=(0, 8))
    scaler.fit(map_range)
    # 낙하산 거리 계산 (선과 직선 사이의 수직선 거리 계산 공식 이용)
    landing_locations['chuteDist'] = np.abs(slope1*landing_locations.x - landing_locations.y + beta1) / np.sqrt(slope1*slope1 + 1)
    landing_locations['chuteDist'] = scaler.transform(landing_locations['chuteDist'].values.reshape(-1, 1))
    landing_locations["circleDist"] = np.sqrt((landing_locations.x - whites[whites[:,4]>0][0][1])**2 + (landing_locations.y - whites[whites[:,4]>0][0][2])**2)
    landing_locations["circleDist"] = landing_locations["circleDist"]/100000
    landing_locations['teamName'] = landing_locations['name'].str.extract(r'([0-9A-Za-z]+)\_')

    if par == 0:
        data = pd.DataFrame((landing_locations.groupby("teamName").mean().sort_values(by="circleDist").index , 
                         landing_locations.groupby("teamName").mean().sort_values(by="circleDist")["circleDist"]), index=["teamName","mean_dist"]).T
    elif par==1:
        data = pd.DataFrame((landing_locations.groupby("teamName").mean().sort_values(by="chuteDist").index , 
                         landing_locations.groupby("teamName").mean().sort_values(by="chuteDist")["chuteDist"]), index=["teamName","mean_dist"]).T
        
    rank = get_rank(api_key, match_id, tournmentID = "as-pgs1gf")
    data["dist_rank"] = pd.DataFrame(rank.index+1)

    return pd.merge(data, rank, how = "inner", on="teamName")