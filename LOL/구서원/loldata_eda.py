import pandas as pd
import numpy as np


def lolDataEda(csv_name):
    lol_df = pd.read_csv(f'./{csv_name}.csv', encoding='CP949')

    # 승패 변환
    wl_mapping = {True: 1, False: 0}
    lol_df['blueWins'] = lol_df['blueWins'].map(wl_mapping)
    lol_df['redWins'] = lol_df['redWins'].map(wl_mapping)

    # dragon_type 변환
    dragontype = ['WATER_DRAGON', 'FIRE_DRAGON', 'AIR_DRAGON', 'EARTH_DRAGON', 'CHEMTECH_DRAGON', 'HEXTECH_DRAGON']
    n_dragontype = 6

    for i in dragontype:  # 리스트형태 없애기
        lol_df = lol_df.replace(f"['{i}']", i)

    bDT = lol_df['blueDragonType'].tolist()  # ','를 기준으로 데이터값 구분하기(리스트로 변환)
    rDT = lol_df['redDragonType'].tolist()
    for i in range(len(bDT)):
        try:
            bDT[i] = bDT[i].split(',')
        except:
            bDT[i] = 'NO_DRAGON'
    for i in range(len(rDT)):
        try:
            rDT[i] = rDT[i].split(',')
        except:
            rDT[i] = 'NO_DRAGON'

    one_hot_mat = list()  # 리스트 원핫인코딩 후 다시 데이터프레임에 집어넣기(blue)
    for _ in range(len(bDT)):
        one_hot_vec = list()
        for _ in range(n_dragontype):
            one_hot_vec.append(0)
        one_hot_mat.append(one_hot_vec)

    for bDT_idx, bDTs in enumerate(bDT):
        one_hot_vec = one_hot_mat[bDT_idx]
        for i in bDTs:
            if i == 'WATER_DRAGON':
                one_hot_vec[0] = 1
            elif i == 'FIRE_DRAGON':
                one_hot_vec[1] = 1
            elif i == 'AIR_DRAGON':
                one_hot_vec[2] = 1
            elif i == 'EARTH_DRAGON':
                one_hot_vec[3] = 1
            elif i == 'CHEMTECH_DRAGON':
                one_hot_vec[4] = 1
            elif i == 'HEXTECH_DRAGON':
                one_hot_vec[5] = 1
    dragon_df = np.array(one_hot_mat)
    dragon_df = pd.DataFrame(dragon_df, columns=[f'blue{i}' for i in dragontype])
    lol_df = pd.concat([lol_df, dragon_df], axis=1)

    one_hot_mat = list()  # (red)
    for _ in range(len(bDT)):
        one_hot_vec = list()
        for _ in range(n_dragontype):
            one_hot_vec.append(0)
        one_hot_mat.append(one_hot_vec)

    for rDT_idx, rDTs in enumerate(rDT):
        one_hot_vec = one_hot_mat[rDT_idx]
        for i in rDTs:
            if i == 'WATER_DRAGON':
                one_hot_vec[0] = 1
            elif i == 'FIRE_DRAGON':
                one_hot_vec[1] = 1
            elif i == 'AIR_DRAGON':
                one_hot_vec[2] = 1
            elif i == 'EARTH_DRAGON':
                one_hot_vec[3] = 1
            elif i == 'CHEMTECH_DRAGON':
                one_hot_vec[4] = 1
            elif i == 'HEXTECH_DRAGON':
                one_hot_vec[5] = 1
    dragon_df = np.array(one_hot_mat)
    dragon_df = pd.DataFrame(dragon_df, columns=[f'red{i}' for i in dragontype])
    lol_df = pd.concat([lol_df, dragon_df], axis=1)

    lol_df = lol_df.drop(
        columns=['gameId', 'Unnamed: 0', 'blueCurrentGolds', 'blueAvgLevel', 'blueFirstTowerLane', 'blueDragonType',
                 'redWins', 'redCurrentGolds', 'redAvgLevel', 'redFirstTowerLane', 'redDragonType'])

    lol_df.to_csv(f'{csv_name}_fix.csv', index=False, encoding='cp949')


lolDataEda("GM15")
