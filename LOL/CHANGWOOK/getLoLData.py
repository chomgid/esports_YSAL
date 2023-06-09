import requests
import json
import time
import pandas as pd
from tqdm import tqdm
import numpy as np


# SummonerId 가져오기
def getSumId(api_key, tier):
    '''
    return dict{summoner name : summonerId} 

    args:
        api_key(str) : your Riot api key 
        tier(int) : 0 for challenger, 1 for grandmaster, 2 for master
    '''
    print("downloading summonerID!")

    if tier == 0:
        url = "https://kr.api.riotgames.com/lol/league/v4/challengerleagues/by-queue/RANKED_SOLO_5x5?api_key="+api_key
    elif tier ==1:
        url="https://kr.api.riotgames.com/lol/league/v4/grandmasterleagues/by-queue/RANKED_SOLO_5x5?api_key="+api_key
    elif tier==2:
        url="https://kr.api.riotgames.com/lol/league/v4/masterleagues/by-queue/RANKED_SOLO_5x5?api_key="+api_key
    

    summonerId = {}

    r = requests.get(url)
    r = r.json()['entries']
    for i in r:
        summonerId[i['summonerName']] = i['summonerId']
    
    print("summonerId downloaded!")

    return summonerId


# SummonerId 이용해 puuid 가져오기
def getPuuid(api_key, tier):
    '''
    return dict{name : puuid}

    args:
        api_key(str) : your Riot api key 
        tier(int) : 0 for challenger, 1 for grandmaster, 2 for master
    '''
    summonerId = getSumId(api_key, tier)
    print("downloading puuid!")
    
    puuid = {}

    for i in tqdm(summonerId.values())  :
        url ='https://kr.api.riotgames.com/lol/summoner/v4/summoners/'+i+ '?api_key='+api_key
        r = requests.get (url)

        if r.status_code == 200:
            pass
        elif r.status_code == 429:
            print ('api cost full : infinite loop start')
            print ('loop location : ',i)
            start_time = time.time ()

            while True:
                if r.status_code == 429:
                    print('try 120 second wait time')
                    time.sleep (120)
                    
                    r = requests.get (url)
                    print(r.status_code)
                elif r.status_code == 200:
                    print('total wait time :' , time.time() - start_time)
                    print('recovery api cost')
                    break

        r = r.json()
        puuid[r['name']] = r['puuid']
    
    print("puuid downloaded!")
    return puuid



# puuid를 이용해 matchId 가져오기
def getMatchId(api_key, tier):
    '''
    return matchIds in list
    args:
        api_key(str) : your Riot api key 
        tier(int) : 0 for challenger, 1 for grandmaster, 2 for master
    '''
   
    puuid = getPuuid(api_key, tier)
    print("downloading matchId!")
    
    matchId =set()

    for i in tqdm(puuid.values()):
        url = "https://asia.api.riotgames.com/lol/match/v5/matches/by-puuid/"+i+"/ids?start=0&count=10&api_key=" + api_key
        r = requests.get(url)

        if r.status_code ==200:
            pass
        elif r.status_code==429:
            print('api cost full : infinite loop start')
            print('loop location: ' ,i)
            start_time=time.time()
        
            while True:
                if r.status_code == 429:
                    print('try 120 second wait time')
                    time.sleep (120)
                    
                    r = requests.get (url)
                    print(r.status_code)
                elif r.status_code == 200:
                    print('total wait time :' , time.time() - start_time)
                    print('recovery api cost')
                    break
        
        matchId.update(r.json())
    
    print("matchId downloaded!")
    return list(matchId)



# matchId를 이용해 timelinedata 가져오기
def getTimelineData(api_key, tier, min):
    '''
    return gameData on specific min in pandas.DataFrame

    args:
        api_key(str) : your Riot api key 
        tier(int) : 0 for challenger, 1 for grandmaster, 2 for master
        min : minutes
    '''

    matchId = getMatchId(api_key, tier)

    
    print("downloading TimelineData!")
    

    

    # use columns
    use_columns = ['gameId','blueWins','blueTotalGolds','blueCurrentGolds','blueTotalLevel'\
                        ,'blueAvgLevel','blueTotalMinionKills','blueTotalJungleMinionKills'
                        ,'blueFirstBlood','blueKill','blueDeath','blueAssist'\
                        ,'blueWardPlaced','blueWardKills','blueFirstTower','blueFirstInhibitor'\
                        ,'blueFirstTowerLane'\
                        ,'blueTowerKills','blueMidTowerKills','blueTopTowerKills','blueBotTowerKills'\
                        ,'blueInhibitor','blueFirstDragon','blueDragnoType','blueDragon','blueRiftHeralds'\
                        ,'redWins','redTotalGolds','redCurrentGolds','redTotalLevel'\
                        ,'redAvgLevel','redTotalMinionKills','redTotalJungleMinionKills'
                        ,'redFirstBlood','redKill','redDeath','redAssist'\
                        ,'redWardPlaced','redWardKills','redFirstTower','redFirstInhibitor'\
                        ,'redFirstTowerLane'\
                        ,'redTowerKills','redMidTowerKills','redTopTowerKills','redBotTowerKills'\
                        ,'redInhibitor','redFirstDragon','redDragnoType','redDragon','redRiftHeralds']

    chal_timeline_df = pd.DataFrame()
    chal_timeline_df1 = pd.DataFrame()

    for b in tqdm(range(len(matchId))):
        game_id = matchId[b]
        url = 'https://asia.api.riotgames.com/lol/match/v5/matches/' + game_id +'/timeline/?api_key=' + api_key
        req = requests.get(url)
        # print(req.status_code)

        # 응답 테스트 부분
        if req.status_code == 200:
                    pass

        elif req.status_code == 429:
            print('api cost full : infinite loop start')
            print('loop location : ', b)
            start_time = time.time()

            while True:
                if req.status_code == 429:

                    print('try 120 second wait time')
                    time.sleep(121)

                    req = requests.get(url)
                    print(req.status_code)

                elif req.status_code == 200:
                    print('total wait time : ', time.time() - start_time)
                    print('recovery api cost')
                    break

        elif req.status_code == 503:
            print('service available error')
            start_time = time.time()

            while True:
                if req.status_code == 503 or req.status_code == 429:

                    print('try 10 second wait time')
                    time.sleep(10)

                    req = requests.get(url)
                    print(req.status_code)

                elif req.status_code == 200:
                    print('total error wait time : ', time.time() - start_time)
                    print('recovery api cost')
                    break
        elif req.status_code == 403: # api갱신이 필요
            print('you need api renewal')
            print('break')
            break
        # 응답 테스트 끝

        # 필요부분만 가져오기
        if len(req.json()['info']['frames']) < min+1:
            continue
        else:
            frames = req.json()['info']['frames']

        # 승패 확인
        lastEvent = frames[-1]['events'][-1]
        if lastEvent['type']=="GAME_END":
            if lastEvent['winningTeam'] == 100:
                blueWins='True'
                redWins = 'False'
            else:
                blueWins="False"
                redWins = "True"
        else:
            pass
        

        participant = frames[min]['participantFrames']
        bluetotal_gold, bluecurrent_gold, bluetotal_level,bluetotal_minionkill,bluetotal_jungleminionkill = [],[],[],[],[]
        redtotal_gold, redcurrent_gold, redtotal_level,redtotal_minionkill, redtotal_jungleminionkill = [],[],[],[],[]
        

        for i in range(len(participant)):
            i = i+1
            if 1<=i<5:
                bluetotal_gold.append(participant[str(i)]['totalGold'])
                bluecurrent_gold.append(participant[str(i)]['currentGold'])
                bluetotal_level.append(participant[str(i)]['level'])
                bluetotal_minionkill.append(participant[str(i)]['minionsKilled'])
                bluetotal_jungleminionkill.append(participant[str(i)]['jungleMinionsKilled'])
            else:
                redtotal_gold.append(participant[str(i)]['totalGold'])
                redcurrent_gold.append(participant[str(i)]['currentGold'])
                redtotal_level.append(participant[str(i)]['level'])
                redtotal_minionkill.append(participant[str(i)]['minionsKilled'])
                redtotal_jungleminionkill.append(participant[str(i)]['jungleMinionsKilled'])


        #timestamp별로 독립적인 변수들을 나타내므로 n분까지의 데이터를 수집하기 위해서는 계속 중첩해서 더해줘야 함
        blue_kill, red_kill = 0,0
        blue_firstkill, red_firstkill = 0,0
        blue_assist, red_assist = 0,0
        red_death, blue_death = 0,0
        blue_wardplace, red_wardplace = 0,0
        blue_wardkill, red_wardkill = 0,0
        blue_elite, red_elite = 0,0
        blue_rift, red_rift = 0,0
        blue_dragon, red_dragon = 0,0
        blue_baron, red_baron = 0,0
        blue_firstdragon, red_firstdragon = 0,0
        blue_dragontype, red_dragontype = [],[]
        blue_firstbaron, red_firstbaron = 0,0
        blue_tower,red_tower = 0,0
        blue_firsttower, red_firsttower = 0,0
        blue_firsttowerlane, red_firsttowerlane = [],[]
        blue_midtower, red_midtower = 0,0
        blue_toptower, red_toptower = 0,0
        blue_bottower, red_bottower = 0,0
        blue_inhibitor, red_inhibitor = 0,0
        blue_firstinhibitor, red_firstinhibitor = 0,0


        for y in range(1, min+1):
            events = frames[y]['events']

            for x in range(len(events)):
            
                # 와드 제거
                if events[x]['type'] == 'WARD_KILL':
                    if 1 <= events[x]['killerId'] <= 5:
                        blue_wardkill += 1
                    else:
                        red_wardkill += 1
                
                # 와드 박기
                elif events[x]['type'] == 'WARD_PLACED':
                    if 1 <= events[x]['creatorId'] <= 5:
                        blue_wardplace += 1
                    else:
                        red_wardplace += 1
                
                # 킬
                elif events[x]['type'] == 'CHAMPION_KILL': 
                    if 1 <= events[x]['killerId'] <= 5:
                        if red_kill ==0 and blue_kill ==0:
                            blue_firstkill += 1
                        else:
                            pass
                        blue_kill += 1
                        red_death += 1

                        # 블루 어시스트
                        if 'assistingParticipantIds' in events[x]:
                            blue_assist += len(events[x]['assistingParticipantIds'])
                        else:
                            pass


                    else:
                        if red_kill ==0 and blue_kill ==0:
                            red_firstkill += 1
                        else:
                            pass
                        red_kill += 1
                        blue_death += 1

                        # 레드 어시스트
                        if 'assistingParticipantIds' in events[x]:
                            red_assist += len(events[x]['assistingParticipantIds'])
                        else:
                            pass

                
                # 중요 몹(드래곤, 전령, 바론) 킬
                elif events[x]['type'] == 'ELITE_MONSTER_KILL':
                    if 1 <= events[x]['killerId'] <= 5:
                        blue_elite += 1

                        if events[x]['monsterType']== 'DRAGON':
                            if red_dragon ==0 and blue_dragon == 0:
                                blue_firstdragon += 1
                            else:
                                pass

                            blue_dragontype.append(events[x]['monsterSubType'])
                            blue_dragon += 1



                        elif events[x]['monsterType']== 'RIFTHERALD':
                            blue_rift += 1

                        elif events[x]['monsterType']== 'BARON_NASHOR':
                            if red_baron ==0 and blue_dragon == 0:
                                blue_firstbaron += 1    
                            else:
                                pass

                            blue_baron += 1

                    else:
                        red_elite += 1

                        if events[x]['monsterType']== 'DRAGON':
                            if red_dragon ==0 and blue_dragon == 0:
                                red_firstdragon += 1
                            else:
                                pass

                            red_dragontype.append(events[x]['monsterSubType'])
                            red_dragon += 1



                        elif events[x]['monsterType']== 'RIFTHERALD':
                            red_rift += 1

                        elif events[x]['monsterType']== 'BARON_NASHOR':
                            if red_baron ==0 and blue_dragon == 0:
                                red_firstbaron += 1
                            else:
                                pass

                            red_baron += 1
                
                # 구조물 파괴
                elif events[x]['type'] == 'BUILDING_KILL':
                    if 1 <= events[x]['killerId'] <= 5:
                    
                        # 블루 타워 파괴
                        if events[x]['buildingType'] == 'TOWER_BUILDING':
                            if red_tower == 0 and blue_tower ==0:
                                blue_firsttower += 1
                                blue_firsttowerlane.append(events[x]['laneType'])

                            else:
                                pass

                            blue_tower += 1

                            if events[x]['laneType'] == 'MID_LANE':
                                blue_midtower += 1

                            elif events[x]['laneType'] == 'TOP_LANE':
                                blue_toptower += 1

                            elif events[x]['laneType'] == 'BOT_LANE':
                                blue_bottower += 1


                        # 블루 억제기 파괴
                        elif events[x]['buildingType'] == 'INHIBITOR_BUILDING':
                            if red_inhibitor == 0 and blue_inhibitor ==0:
                                blue_firstinhibitor += 1

                            else:
                                pass

                            blue_inhibitor += 1

                    else:

                        # 레드 타워 파괴
                        if events[x]['buildingType'] == 'TOWER_BUILDING':
                            if red_tower == 0 and blue_tower ==0:
                                red_firsttower += 1
                                red_firsttowerlane.append(events[x]['laneType'])

                            else:
                                pass

                            red_tower += 1

                            if events[x]['laneType'] == 'MID_LANE':
                                red_midtower += 1

                            elif events[x]['laneType'] == 'TOP_LANE':
                                red_toptower += 1

                            elif events[x]['laneType'] == 'BOT_LANE':
                                red_bottower += 1

                        # 레드 억제기 파괴
                        elif events[x]['buildingType'] == 'INHIBITOR_BUILDING':
                            if red_inhibitor == 0 and blue_inhibitor ==0:
                                red_firstinhibitor += 1

                            else:
                                pass

                            red_inhibitor += 1


    try:
        blue_firsttowerlane = blue_firsttowerlane[0]
    except:
        blue_firsttowerlane= None
    try: 
        blue_dragontype=blue_dragontype[0]
    except:
        blue_dragontype=None
    try:
        red_firsttowerlane = red_firsttowerlane[0]
    except:
        red_firsttowerlane = None
    try:
        red_dragontype=red_dragontype[0]
    except:
        red_dragontype =None
        
    data_list = [game_id,blueWins,np.sum(bluetotal_gold)\
                ,np.sum(bluecurrent_gold),np.sum(bluetotal_level),np.mean(bluetotal_level)\
                ,np.sum(bluetotal_minionkill),np.sum(bluetotal_jungleminionkill)\
                ,blue_firstkill,blue_kill,blue_death,blue_assist,blue_wardplace,blue_wardkill\
                ,blue_firsttower,blue_firstinhibitor,blue_firsttowerlane,blue_tower\
                ,blue_midtower,blue_toptower,blue_bottower,blue_inhibitor,blue_firstdragon\
                ,blue_dragontype,blue_dragon,blue_rift\
                ,redWins,np.sum(redtotal_gold)\
                ,np.sum(redcurrent_gold),np.sum(redtotal_level),np.mean(redtotal_level)\
                ,np.sum(redtotal_minionkill),np.sum(redtotal_jungleminionkill)\
                ,red_firstkill,red_kill,red_death,red_assist,red_wardplace,red_wardkill\
                ,red_firsttower,red_firstinhibitor,red_firsttowerlane,red_tower\
                ,red_midtower,red_toptower,red_bottower,red_inhibitor,red_firstdragon\
                ,red_dragontype,red_dragon,red_rift]     
    
    
    

    chal_timeline_df = pd.DataFrame(np.array([data_list]), columns=use_columns)
    chal_timeline_df1 = pd.concat([chal_timeline_df1, chal_timeline_df])


    print("TimelineData downloaded!")
    return chal_timeline_df1


