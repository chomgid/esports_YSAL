import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from sklearn.metrics import f1_score
from lightgbm import LGBMClassifier
from bayes_opt import BayesianOptimization

# 데이터 전처리
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
                 'redWins', 'redCurrentGolds', 'redAvgLevel', 'redFirstTowerLane', 'redDragonType', 'redKill',
                 'redDeath', 'matchMin'])

    print("lol_df dataframe created!")
    return lol_df


# LGBM 모델링 후 예측열, 예측성공열 생성
def LGBMmodeling(df):
    global x_valid, y_valid, valid_pred

    def train_test(df):
        x_train = df.drop(['blueWins'], axis=1)
        y_train = df['blueWins']
        return x_train, y_train

    x_train, y_train = train_test(df)
    val_size = 0.3

    x_train, x_valid, y_train, y_valid = train_test_split(x_train, y_train, test_size=val_size, random_state=42)

    model = LGBMClassifier()
    model.fit(x_train, y_train)
    valid_pred = model.predict(x_valid)
    accuracy = accuracy_score(y_valid, valid_pred)
    print("LGBM Accuracy: ", accuracy * 100)

    # 탐색 대상 함수 (XGBRegressor)
    def LGBM_cv(max_depth, learning_rate, n_estimators,
                min_child_weight, subsample
                , colsample_bytree, silent=True):
        # 모델 정의
        model = LGBMClassifier(max_depth=int(max_depth),
                               learning_rate=learning_rate,
                               n_estimators=int(n_estimators),
                               min_child_weight=min_child_weight,
                               subsample=subsample,
                               colsample_bytree=colsample_bytree
                               )
        # 모델 훈련
        model.fit(x_train, y_train)

        # 예측값 출력
        y_pred = model.predict(x_valid)

        return f1_score(y_valid, y_pred)

    pbounds = {'max_depth': (3, 7),
               'learning_rate': (0.01, 0.3),
               'n_estimators': (20, 100),
               'min_child_weight': (0, 3),
               'subsample': (0.5, 1),
               'colsample_bytree': (0.2, 1)
               }

    lm_bo = BayesianOptimization(f=LGBM_cv, pbounds=pbounds, verbose=2, random_state=1)

    lm_bo.maximize(init_points=2, n_iter=100)

    param = lm_bo.max['params']
    param['max_depth'] = int(param['max_depth'])
    param['n_estimators'] = int(param['n_estimators'])

    model = LGBMClassifier(**param)
    model.fit(x_train, y_train)
    valid_pred = model.predict(x_valid)
    accuracy = accuracy_score(y_valid, valid_pred)
    print("Bayesian LGBM Accuracy: ", accuracy * 100)

    y_valid_idx = y_valid.tolist()
    x_valid['predSuccess'] = 1
    for i in range(len(y_valid_idx)):
        if y_valid_idx[i] != valid_pred[i]:
            index_num = y_valid.index[i]
            x_valid['predSuccess'][index_num] = 0

    x_valid["blueWins"] = y_valid.tolist()
    x_valid["pred"] = valid_pred

    return model, x_valid
