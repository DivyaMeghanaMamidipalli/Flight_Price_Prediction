# -*- coding: utf-8 -*-
"""Bonus Project-B20CS032.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/17dwWEahuiRKQiv0aPXXb4bneFTkYLjKw

#Prediction of Price of Flight ticket

###Importing  Required Libraries
"""

import gc
import math
import PIL 
import pandas as pd
import numpy as np
import seaborn as sns
import datetime
import random
import warnings
import holidays
import datetime
import xgboost as xgb
from scipy import stats
from pandas.tseries.holiday import USFederalHolidayCalendar as calendar
from sklearn.linear_model import LinearRegression,Ridge,Lasso
from sklearn.ensemble import RandomForestRegressor, AdaBoostRegressor, GradientBoostingRegressor
from sklearn.neighbors import KNeighborsRegressor
from sklearn.tree import DecisionTreeRegressor
import matplotlib.pyplot as plt
from sklearn.utils import shuffle
from sklearn.model_selection import train_test_split , GridSearchCV,cross_val_score,cross_val_predict,cross_validate,RandomizedSearchCV
from sklearn.metrics import mean_absolute_error,explained_variance_score,max_error,r2_score,median_absolute_error,mean_squared_log_error
from sklearn.feature_selection import VarianceThreshold,SelectKBest,f_regression
from sklearn.preprocessing import MinMaxScaler,normalize,StandardScaler,RobustScaler
from sklearn.preprocessing import OneHotEncoder,LabelEncoder
from sklearn.decomposition import PCA
from sklearn.svm import SVR
!pip install mlxtend
import joblib
import sys
sys.modules['sklearn.externals.joblib'] = joblib
from mlxtend.feature_selection import SequentialFeatureSelector,ExhaustiveFeatureSelector

import warnings
warnings.filterwarnings('ignore')

from sklearn.metrics import mean_squared_error as mse

"""###Importing the data"""

from google.colab import drive
drive.mount('/content/drive')

data= pd.read_csv("/content/drive/MyDrive/Colab Notebooks/Flight price prediction Datset.csv")
data.head()

"""###Data Analysis

"""

data.info()

data.duplicated().sum()

data = data.drop_duplicates()

data_1 = data.copy()

const_feature = []
uniq_val_count = []
unique_cols = dict()
for col in list(data.columns):
    uniq_val_count.append(data[col].nunique())
    if(data[col].nunique()==1):
        const_feature.append(col)
    
# Removing the constant feature
data=data.drop(columns=const_feature)

"""##Preprocessing

###Treating the Dates
"""

data.Date_of_Journey=data.Date_of_Journey.str.split('/')
data.Date_of_Journey

data['Date']=data.Date_of_Journey.str[0]
data['Month']=data.Date_of_Journey.str[1]
data['Year']=data.Date_of_Journey.str[2]

data.Route=data.Route.str.split('→')
data.Route

data['City1']=data.Route.str[0]
data['City2']=data.Route.str[1]
data['City3']=data.Route.str[2]
data['City4']=data.Route.str[3]
data['City5']=data.Route.str[4]
data['City6']=data.Route.str[5]

data.Dep_Time=data.Dep_Time.str.split(':')
data['Dep_Time_Hour']=data.Dep_Time.str[0]
data['Dep_Time_Min']=data.Dep_Time.str[1]

data.Arrival_Time=data.Arrival_Time.str.split(' ')
data['Arrival_date']=data.Arrival_Time.str[1]

data['Time_of_arrival']=data.Arrival_Time.str[0]
data['Time_of_arrival']=data.Time_of_arrival.str.split(':')

data['Arrival_Time_Hour']=data.Time_of_arrival.str[0]
data['Arrival_Time_Min']=data.Time_of_arrival.str[1]

data.Duration=data.Duration.str.split(' ')
data['Travel_hours']=data.Duration.str[0]
data['Travel_hours']=data['Travel_hours'].str.split('h')
data['Travel_hours']=data['Travel_hours'].str[0]
data.Travel_hours

data['Travel_mins']=data.Duration.str[1]
data.Travel_mins=data.Travel_mins.str.split('m')
data.Travel_mins=data.Travel_mins.str[0]
data.Travel_mins

data.Total_Stops.unique()

data.Total_Stops.replace('non-stop','0',inplace=True)
data.Total_Stops=data.Total_Stops.str.split(' ')
data.Total_Stops=data.Total_Stops.str[0]
data.Total_Stops

data.head()

#There are two values in Additional_Info with similar value, hence we merged both of them to a single value..
data.Additional_Info.replace('No info','No Info',inplace=True)

data.isnull().sum()

#Dropping all the unnecessary columns from which we created extra rows.
data=data.drop(columns=['Date_of_Journey','Route','Dep_Time','Arrival_Time','Duration','City4','City5','City6','Time_of_arrival'])
data.head()
#City4, City5,  City6 are also deleted as they contain many null values..

"""###Working with Missing values"""

data.isnull().sum()

data[data['Total_Stops'].isnull()]

data['Total_Stops'].fillna('0',inplace=True)
data['City1'].fillna('DEL',inplace=True)
data['City2'].fillna('COK',inplace=True)

data['City3'].fillna('None',inplace=True)
data['Arrival_date'].fillna(data['Date'],inplace=True)
data['Travel_mins'].fillna('0',inplace=True)

data.isnull().sum()

"""Found a string '5m' in the column 'Travel_hours'  which is invalid, hence we are deleting that row of values which contains it.  """

data[data['Travel_hours']=='5m']

data.drop(index=6474,inplace=True,axis=0)

"""##Visualising the Data"""

#Count Plots of Categorial Data
Categorial_Col=['Airline','Source','Destination','City1','City2','City3']

for col in Categorial_Col:
    plt.style.use('dark_background')
    plt.figure(figsize=(5,5))
    plt.bar(list(data[col].value_counts().index),list(data[col].value_counts()),color = random.sample(['maroon','yellow'],1))            
    plt.title('\nCount Plot of {}'.format(col))
    plt.show()

#Distribution of Price with Categorial Data
for col in Categorial_Col:
    plt.style.use('dark_background')
    plt.figure(figsize=(5,5))
    plt.scatter(data[col],data['Price'],color=random.sample(['yellow','maroon','blue','pink'],1),linewidth = .5)
    plt.title('{} V/S {}'.format(col,data.Price))
    plt.xlabel(col)
    plt.ylabel('Price')
    plt.show()

"""##Label Encoding the data"""

columns = ['Airline','Source','Destination','Total_Stops','Additional_Info','City1','City2','City3']

label_enc=LabelEncoder()


for col in range(len(columns)):
    label_enc.fit(data[columns[col]])
    data[columns[col]] = label_enc.transform(data[columns[col]])

data.head()

"""##Separating the Target and the Features"""

X=data.drop(columns=['Price'],axis=1)
Y=data['Price']

"""###Scaling the data"""

sc=StandardScaler()
x=sc.fit_transform(X)
X=pd.DataFrame(x,columns=X.columns)

X.head()

"""###Splitting the data into train and test data"""

X_train,X_test,Y_train,Y_test=train_test_split(X,Y,test_size=.2,random_state=4)

X_train.head()

"""##Training and Fitting with our models

###Decision Tree
"""

dt=DecisionTreeRegressor()
dt.fit(X_train,Y_train)
pred_dt=dt.predict(X_test)
r2_score_dt=r2_score(Y_test,pred_dt)*100
print(r2_score_dt)
mean_squared_error_dt=mse(Y_test,pred_dt)
mse_dt=mean_squared_error_dt*(-1)
mse_dt

"""###Gradient Boosting Regressor"""

gbr=GradientBoostingRegressor()
gbr.fit(X_train,Y_train)
pred_gbr=gbr.predict(X_test)
r2_score_gbr=r2_score(Y_test,pred_gbr)*100
print(r2_score_gbr)
mean_squared_error_gbr=mse(Y_test,pred_gbr)
mse_gbr=mean_squared_error_gbr*(-1)
mse_gbr

"""###KNN"""

knn=KNeighborsRegressor()
knn.fit(X_train,Y_train)
pred_knn=knn.predict(X_test)
r2_score_knn=r2_score(Y_test,pred_knn)*100
print(r2_score_knn)
mean_squared_error_knn=mse(Y_test,pred_knn)
mse_knn=mean_squared_error_knn*(-1)
mse_knn

"""###Random Forest Regressor"""

rfr=RandomForestRegressor()
rfr.fit(X_train,Y_train)
pred_rfr=rfr.predict(X_test)
r2_score_rfr=r2_score(Y_test,pred_rfr)*100
print(r2_score_rfr)
mean_squared_error_rfr=mse(Y_test,pred_rfr)
mse_rfr=mean_squared_error_rfr*(-1)
mse_rfr

"""###Comparision between Models"""

Models=pd.DataFrame({'Models':['Decision Tree Regressor','Gradient Boosting Regressor','KNN','Random Forest Regressor'],
                     'Score':[r2_score_dt,r2_score_gbr,r2_score_knn,r2_score_rfr]
                    })
Models

"""##Hyper Parameter Tuning

###Decision Tree Regressor
"""

params_dt={"splitter":["best","random"],
            "max_depth" : [1,3,5,7,9,11,12],
           "min_samples_leaf":[1,2,3,4,5,6,7,8,9,10],
           "min_weight_fraction_leaf":[0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9],
           "max_features":["auto","log2","sqrt",None],
           "max_leaf_nodes":[None,10,20,30,40,50,60,70,80,90] }

grid_search_dt=GridSearchCV(dt,param_grid=params_dt,scoring='neg_mean_squared_error',cv=3,verbose=3)
grid_search_dt.fit(X_train,Y_train)
mse_dt_2=grid_search_dt.best_score_
print(mse_dt_2)
grid_search_dt.best_params_

dt_2=DecisionTreeRegressor(max_depth=5,max_features='auto',max_leaf_nodes=None,min_samples_leaf=1,min_weight_fraction_leaf=0.1,splitter='best')
dt_2.fit(X_train,Y_train)
pred_dt_2=dt_2.predict(X_test)
r2_score_dt_2=r2_score(Y_test,pred_dt_2)*100
r2_score_dt_2

"""###Gradient Boosting"""

params_gbr = {'max_depth':range(5,16,2), 'min_samples_split':range(200,1001,200)}           
grid_search_gbr = GridSearchCV(estimator = GradientBoostingRegressor(learning_rate=0.1, n_estimators=60, max_features='sqrt', subsample=0.8, random_state=10),param_grid = params_gbr, scoring='neg_mean_squared_error',n_jobs=4, cv=5)
grid_search_gbr.fit(X_train, Y_train)
mse_gbr_2=grid_search_gbr.best_score_
print(mse_gbr_2)
grid_search_gbr.best_params_

gbr_2=GradientBoostingRegressor(max_depth=15,min_samples_split=200)
gbr_2.fit(X_train,Y_train)
pred_gbr_2=gbr_2.predict(X_test)
r2_score_gbr_2=r2_score(Y_test,pred_gbr_2)*100
r2_score_gbr_2

"""###KNN"""

params_knn = { 'n_neighbors' : [i for i in range(3,20)],
               'weights' : ['uniform','distance'],
               'metric' : ['minkowski','euclidean','manhattan']}
grid_search_knn = GridSearchCV(knn, params_knn, verbose = 1,scoring='neg_mean_squared_error',cv=7, n_jobs = -1)
grid_search_knn.fit(X_train, Y_train)
mse_knn_2=grid_search_knn.best_score_
print(mse_knn_2)
grid_search_knn.best_params_

knn_2=KNeighborsRegressor(n_neighbors=5,weights='distance')
knn_2.fit(X_train,Y_train)
pred_knn_2=knn_2.predict(X_test)
r2_score_knn_2=r2_score(Y_test,pred_knn_2)*100
r2_score_knn_2

"""###Random Forest Regressor"""

params_rfr={'n_estimators':[10,30,50,70,100],'max_depth':[None,1,2,3],'max_samples':[50,100,250,500,1000],'min_samples_split':[2,4,10]}
grid_search_rfr=GridSearchCV(rfr,params_rfr,scoring='neg_mean_squared_error',cv=3)
grid_search_rfr.fit(X_train,Y_train)
mse_rfr_2=grid_search_rfr.best_score_
print(mse_rfr_2)
grid_search_rfr.best_params_

rfr_2=RandomForestRegressor(max_depth=None,min_samples_split=2,n_estimators=70)
rfr_2.fit(X_train,Y_train)
pred_rfr_2=rfr_2.predict(X_test)
r2_score_rfr_2=r2_score(Y_test,pred_rfr_2)*100
r2_score_rfr_2

"""##Comparing the models after Hyper Paramater Tuning"""

plot = ["before","after"]

"""Decision Tree"""

dt=[r2_score_dt,r2_score_dt_2]
fig=plt.figure(figsize=(5,5))
sns.barplot(x=plot,y=dt)
plt.xticks(rotation=90)
fig.show()

"""Gradient Boosting Regressor"""

gb=[r2_score_gbr,r2_score_gbr_2]
fig=plt.figure(figsize=(5,5))
sns.barplot(x=plot,y=gb)
plt.xticks(rotation=90)
fig.show()

"""KNN"""

kn=[r2_score_knn,r2_score_knn_2]
fig=plt.figure(figsize=(5,5))
sns.barplot(x=plot,y=kn)
plt.xticks(rotation=90)
fig.show()

"""Random Forest Regressor"""

rf=[r2_score_rfr,r2_score_rfr_2]
fig=plt.figure(figsize=(5,5))
sns.barplot(x=plot,y=rf)
plt.xticks(rotation=90)
fig.show()

"""##Comparision"""

Models_2=pd.DataFrame({'Models':['Decision Tree Regressorr','Gradient Boosting Regressor','KNN','Random forest regressor'],
                     'Initial_Score':[r2_score_dt,r2_score_gbr,r2_score_knn,r2_score_rfr],
                     'Final_Score':[r2_score_dt_2,r2_score_gbr_2,r2_score_knn_2,r2_score_rfr_2]
                    })

Models_2

fig=plt.figure(figsize=(5,5))
sns.barplot(x=Models_2.Models,y=Models_2.Initial_Score)
plt.xticks(rotation=90)
fig.show()

fig=plt.figure(figsize=(5,5))
sns.barplot(x=Models_2.Models,y=Models_2.Final_Score)
plt.xticks(rotation=90)
fig.show()

"""##After hypertuning all our model Gradient Boosting gave the best score, hence creating a dataframe of the predicted prices that came from this model."""

model=GradientBoostingRegressor(learning_rate=0.1, n_estimators=60, max_features='sqrt', subsample=0.8, random_state=10,max_depth=15,min_samples_split=200)

import joblib
joblib.dump(model,'FlightPrice.obj')

model=joblib.load('FlightPrice.obj')
model.fit(X_train,Y_train)
Flight_Prices=model.predict(X_test)

predicted_values=pd.DataFrame({'Actual':Y_test,'Predicted':Flight_Prices})

Flight_Prices