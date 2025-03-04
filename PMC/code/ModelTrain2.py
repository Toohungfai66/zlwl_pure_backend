import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.model_selection import train_test_split
from bayes_opt import BayesianOptimization
from sklearn.model_selection import cross_val_score
from functools import partial
import joblib, re, os

class modeltrain:
    def xgb_evaluate(self, eta, max_depth, min_child_weight, gamma, subsample, colsample_bytree, colsample_bylevel, reg_lambda, alpha, X_train, X_test, y_train, y_test):
        params = {
            'objective':'reg:tweedie',
            'eta': eta,
            'max_depth': int(max_depth),
            'gamma': gamma,
            'subsample': subsample,
            'colsample_bytree': colsample_bytree,
            'colsample_bylevel': colsample_bylevel,
            'lambda': reg_lambda,
            'alpha': alpha,
            'min_child_weight': min_child_weight
        }
        model = xgb.XGBRegressor(**params)
        # 使用交叉验证评估模型
        cv_scores = cross_val_score(model, X_train, y_train, cv=5, scoring='r2')
        return cv_scores.mean()
    
    def main(self):
        for _data in os.listdir("C:\\Project\\zlwl_pure_backend\\PMC\\static\\msku_files"):
            if _data[:-5] + ".pkl" in os.listdir("C:\\Project\\zlwl_pure_backend\\PMC\\static\\msku_fiels_model"):
                continue
            df = pd.read_excel(f"C:\\Project\\zlwl_pure_backend\\PMC\\static\\msku_files\\{_data}")
            df['日期'] = pd.to_datetime(df['日期'])
            df['年'] = df['日期'].dt.year
            df['月'] = df['日期'].dt.month
            df['日'] = df['日期'].dt.day
            df['星期几'] = df['日期'].dt.dayofweek

            # 定义季节映射
            season_mapping = {1: '冬季', 2: '冬季', 3: '春季', 4: '春季', 5: '春季', 6: '夏季', 
                            7: '夏季', 8: '夏季', 9: '秋季', 10: '秋季', 11: '秋季', 12: '冬季'}
            df['季节'] = df['月'].map(season_mapping)

            # 对季节进行独热编码
            df = pd.get_dummies(df, columns=['季节'])

            df['大类排名'] = df['大类排名'].apply(lambda x : int(re.findall("\d+", str(x))[0]) if re.findall("\d+", str(x)) else 0)
            df['广告花费'] = -df['广告花费']

            # 1. 生成模拟回归数据集
            X = df.drop(columns=['日期','销量'])
            y = df['销量']

            try:
                # 2. 划分训练集和测试集
                X_train, X_test, y_train, y_test = train_test_split(X.values, y.values, test_size=0.1, random_state=42)
            except:
                continue

            pbounds = {
                'eta': (0.01, 0.2),  # 扩大 eta 范围
                'max_depth': (3, 10),  # 扩大 max_depth 范围
                'min_child_weight': (1, 30),  # 扩大 min_child_weight 范围
                'gamma': (0.1, 5),  # 扩大 gamma 范围
                'subsample': (0.5, 1),  # 扩大 subsample 范围
                'colsample_bytree': (0.5, 1),  # 扩大 colsample_bytree 范围
                'colsample_bylevel': (0.5, 1),  # 扩大 colsample_bylevel 范围
                'reg_lambda': (5, 50),  # 扩大 reg_lambda 范围
                'alpha': (5, 50)  # 扩大 alpha 范围
            }
            xgb_eval_partial = partial(self.xgb_evaluate, X_train=X_train, X_test=X_test, y_train=y_train, y_test=y_test)
            optimizer = BayesianOptimization(
                f=xgb_eval_partial,
                pbounds=pbounds,
                random_state=42
            )
            optimizer.maximize(init_points=10, n_iter=20)

            # 3. 将数据转换为XGBoost所需的DMatrix格式
            dtrain = xgb.DMatrix(X_train, label=y_train)
            dval = xgb.DMatrix(X_test, label=y_test)
            dtest = xgb.DMatrix(X_test)

            # 4. 设置XGBoost模型参数
            params = optimizer.max['params']
            params['max_depth'] = int(params['max_depth'])
            params['objective'] = 'reg:squarederror'

            # 训练模型并使用 early_stopping_rounds 确定最优迭代次数
            model = xgb.train(params, dtrain, num_boost_round=1000, evals=[(dval, 'val')], early_stopping_rounds=10, verbose_eval=False)
            best_iteration = model.best_iteration
            # 使用最优迭代次数重新训练模型
            model = xgb.train(params, dtrain, num_boost_round=best_iteration)
            joblib.dump(model, f'C:\\Project\\zlwl_pure_backend\\PMC\\static\\msku_fiels_model\\{_data[:-5]}.pkl')