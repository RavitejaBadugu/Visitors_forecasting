import os
import pickle
import numpy as np
import pandas as pd
import pandasql as ps
from tqdm import tqdm
from inference_functions import *
from sklearn.preprocessing import MultiLabelBinarizer,LabelEncoder
from get_data_from_s3 import get_bucket,get_model
from insert_into_tables import insert_predictions

AREA_SPLIT=False
if not os.path.isdir("code_outputs"):
    os.mkdir("code_outputs")
get_model("code_outputs")

with open(f"code_outputs/predictive_features,.pkl","rb") as f:
    PREDICTIVE_FEATURES=pickle.load(f)

with open("code_outputs/scaler_lstm_0.001_2.pkl","rb") as f:
    scaler=pickle.load(f)


MODEL_PATH="code_outputs/lstm_2_dense_1.h5"
categorical_columns=['air_store_id','visit_month','visit_dow','visit_day','air_genre_name','air_area_name']
embedding_dims={'air_store_id': {'input_dim': 829, 'out_dim': 69},
 'visit_month': {'input_dim': 13, 'out_dim': 7},
 'visit_dow': {'input_dim': 7, 'out_dim': 5},
 'visit_day': {'input_dim': 32, 'out_dim': 11},
 'air_genre_name': {'input_dim': 36, 'out_dim': 12},
 'air_area_name': {'input_dim': 135, 'out_dim': 25}}
parameters={"window_size":19,"lstm_n_layers":2,"lstm_units":[30,30],"dense_layers":1,"dense_units":[30]}
numerical_columns=list(col for col in PREDICTIVE_FEATURES if col not in categorical_columns)



##################################################################################
air_res=pd.read_csv("air_reserve.csv")
air_info=pd.read_csv("air_store_info.csv")
##########################################
hpg_res=pd.read_csv('hpg_reserve.csv')
hpg_info=pd.read_csv('hpg_store_info.csv')
##########################################
date_info=pd.read_csv("date_info.csv")
stores_map=pd.read_csv('store_id_relation.csv')
###########################################
test=pd.read_csv("sample_submission.csv")
##################################
air_visit=pd.read_csv("air_visit_data.csv")
##################################################################################



test['air_store_id']=test['id'].apply(lambda x: "_".join(x.split("_")[:-1]))
test['visit_date']=test['id'].apply(lambda x: x.split("_")[-1])
hpg_res=pd.merge(left=hpg_res,right=stores_map,left_on="hpg_store_id",right_on='hpg_store_id',how='inner')
hpg_res.drop("hpg_store_id",axis=1,inplace=True)
reservations=pd.concat([air_res,hpg_res],ignore_index=True)
reservations=make_datetime_to_date(reservations)
hpg_info=pd.merge(left=hpg_info,right=stores_map,left_on="hpg_store_id",right_on='hpg_store_id',how='inner')
hpg_info.rename(columns={"hpg_genre_name":"air_genre_name","hpg_area_name":"air_area_name"},inplace=True)
hpg_info.drop("hpg_store_id",axis=1,inplace=True)
information=pd.concat([air_info,hpg_info],ignore_index=True)
new_cols=["air_store_id","visit_date"]
for col in ['reserve_visitors','n_hrs_gap','n_days_gap']:
    for agg in ['mean','max','min','sum']:
        new_cols.append(col+"_"+agg)
reservations=reservations.groupby(["air_store_id","visit_date"]).agg({"reserve_visitors":["mean","max","min","sum"],
                                                        "n_hrs_gap":["mean","max","min","sum"],
                                                        "n_days_gap":["mean","max","min","sum"]}).reset_index()

reservations.columns=new_cols
reservations['visit_date']=pd.to_datetime(reservations['visit_date'])
reservations.sort_values(by=['air_store_id','visit_date'],ignore_index=True,inplace=True)
cols=['reserve_visitors_sum',"n_hrs_gap_sum","n_days_gap_sum"]
for col in cols:
    for window in [7,14,30]:
        reservations[f"{col}_rolling_{window}_mean"]=reservations.groupby("air_store_id")[col].transform(lambda x: x.rolling(window).mean())
        reservations[f"{col}_rolling_{window}_std"] =reservations.groupby("air_store_id")[col].transform(lambda x: x.rolling(window).std())
        reservations[f"{col}_rolling_{window}_max"] =reservations.groupby("air_store_id")[col].transform(lambda x: x.rolling(window).max())
        reservations[f"{col}_rolling_{window}_min"] =reservations.groupby("air_store_id")[col].transform(lambda x: x.rolling(window).min())
reservations.sort_values(by=['air_store_id','visit_date'],ignore_index=True,inplace=True)
cols=['reserve_visitors_sum',"n_hrs_gap_sum","n_days_gap_sum"]
for col in cols:
    for lag in range(1,8):
        reservations[f"{col}_lag_{lag}"]=reservations.groupby("air_store_id")[col].transform(lambda x: x.shift(lag))        
information=information.groupby("air_store_id").agg({"air_genre_name":"unique","air_area_name":"unique"}).reset_index()
information['n_areas']=information['air_area_name'].apply(lambda x: len(x))
if AREA_SPLIT:
    information['first_area'] =information['air_area_name'].apply(lambda x: x[0])
    information['second_area']=information['air_area_name'].apply(lambda x: x[1] if len(x)>1 else "only at one area")
else:
    information['air_area_name']=information['air_area_name'].apply(lambda x: ",".join(x))

information['air_genre_name']=information['air_genre_name'].apply(get_cuisines)

if AREA_SPLIT:
    information.drop(['air_area_name'],axis=1,inplace=True)

if AREA_SPLIT:
    areas=information['first_area'].unique().tolist()
    areas.extend(information['second_area'].unique().tolist())
else:
    areas=information['air_area_name'].unique().tolist()

area_encoder=LabelEncoder()
area_encoder.fit(areas)
if AREA_SPLIT:
    information['first_area']=area_encoder.transform(information['first_area'])
    information['second_area']=area_encoder.transform(information['second_area'])
else:
    information['air_area_name']=area_encoder.transform(information['air_area_name'])
##########################################
if AREA_SPLIT:
    cuisine_encoder=MultiLabelBinarizer()
    cuisine_encoder.fit(information['air_genre_name'])
    temp=pd.DataFrame(cuisine_encoder.transform(information['air_genre_name']),columns=list(cuisine_encoder.classes_))
    information=information.join(temp)
    information.drop("air_genre_name",axis=1,inplace=True)
else:
    cuisine_encoder=LabelEncoder()
    information['air_genre_name']=information['air_genre_name'].apply(lambda x: ",".join(x))
    information['air_genre_name']=cuisine_encoder.fit_transform(information['air_genre_name'])

if AREA_SPLIT:
    information['Asian'].value_counts()
    information.loc[information['Asian']==1,"first_area"].unique(),information.loc[information['Asian']==1,"second_area"].unique()

if AREA_SPLIT:
    for c in list(cuisine_encoder.classes_):
        sec={c:information.groupby('second_area')[c].transform("sum").values,"sec":information['second_area'].values}
        sec=pd.DataFrame(sec)
        sec.loc[sec['sec']==119,c]=0
        information[f"n_rest_of_{c}_per_area"]=information.groupby('first_area')[c].transform("sum")+sec[c]
else:
    information['count_res_per_genre_area']=information.groupby(['air_area_name','air_genre_name'])['air_store_id'].transform("count")
    information['count_genres_per_area']=information.groupby(['air_area_name'])['air_genre_name'].transform("count")


if AREA_SPLIT:
    sec=pd.DataFrame({"n_res":information.groupby("second_area")['air_store_id'].transform("count").values,
                  "sec":information['second_area'].values})
    sec.loc[sec['sec']==119,'n_res']=0
    information["n_restaurants_per_area"]=information.groupby("first_area")['air_store_id'].transform("count")+sec['n_res']


date_info['calendar_date']=pd.to_datetime(date_info['calendar_date'])
date_info.loc[date_info['day_of_week'].isin(['Saturday','Sunday']),"holiday_flg"]=1
date_info['month']=date_info['calendar_date'].dt.month
date_info['day']=date_info['calendar_date'].dt.day
for i in date_info.loc[((date_info['month']==4) & (date_info['day']>=29)) | ((date_info['month']==5) & (date_info['day']<=7))].index:
    day=date_info.loc[i,'day']
    if day not in [6,7]:
        date_info.loc[i,'holiday_flg']=1
    else:
        if day==6:
            if date_info.loc[i+1,'day']==7 and date_info.loc[i+1,'holiday_flg']==1:
                date_info.loc[i,'holiday_flg']=1

q='''
with f_cte as
(
select a.calendar_date,b.calendar_date as sec,b.holiday_flg,a.day_of_week,a.month,a.day
from date_info a
inner join
date_info b
on b.calendar_date>=a.calendar_date and (a.holiday_flg=1 and b.holiday_flg=1)
),final_cte as
(
select *,row_number() over(partition by calendar_date order by sec) as row_id
from
(
select *,julianday(sec)-julianday(calendar_date) as diff
from f_cte
) a
)
select *,sum(holiday_flg) as n_holidays
from final_cte
where row_id-diff=1
group by calendar_date


'''
a=ps.sqldf(q)
a['calendar_date']=pd.to_datetime(a['calendar_date'])
a.drop(['sec','holiday_flg','day_of_week','month','day','diff','row_id'],axis=1,inplace=True)
date_info=pd.merge(left=date_info,right=a,left_on='calendar_date',right_on='calendar_date',how='left')
date_info['n_holidays'].fillna(0,inplace=True)
date_info.drop(['day_of_week','month','day'],axis=1,inplace=True)

q='''
with f_cte as
(
select *,(select min(b.calendar_date)
          from date_info b
          where b.calendar_date>=a.calendar_date and b.holiday_flg!=a.holiday_flg) as max_date
from date_info a
),final_cte as
(
select a.calendar_date,a.holiday_flg,a.n_holidays,a.max_date,b.calendar_date as temp_date
from f_cte a
left join
f_cte b
on a.max_date=b.max_date
),last_cte as
(
select calendar_date,holiday_flg,n_holidays,max_date,julianday(max_date)-julianday(min(temp_date)) as temp_vacation_length
from final_cte
group by calendar_date,holiday_flg,n_holidays,max_date
)
select calendar_date,holiday_flg,n_holidays,
       (case when holiday_flg=1 then temp_vacation_length
       else 0
       end) as vacation_length
from last_cte
'''
date_info=ps.sqldf(q)
date_info['calendar_date']=pd.to_datetime(date_info['calendar_date'])
date_info['month']=date_info['calendar_date'].dt.month
date_info['day']=date_info['calendar_date'].dt.day
date_info.drop(['month','day'],axis=1,inplace=True)
test['visit_date']=pd.to_datetime(test['visit_date'])
air_visit['visit_date']=pd.to_datetime(air_visit['visit_date'])
air_visit=pd.merge(left=air_visit,right=date_info,left_on="visit_date",right_on='calendar_date',how='left')
air_visit.drop(['calendar_date'],axis=1,inplace=True)
###########################################
test=pd.merge(left=test,right=date_info,left_on="visit_date",right_on='calendar_date',how='left')
test.drop(['calendar_date'],axis=1,inplace=True)
air_visit['visit_month']=air_visit['visit_date'].dt.month
air_visit['visit_dow']=air_visit['visit_date'].dt.dayofweek
air_visit['visit_day']=air_visit['visit_date'].dt.day
########################################
test['visit_month']=test['visit_date'].dt.month
test['visit_dow']=test['visit_date'].dt.dayofweek
test['visit_day']=test['visit_date'].dt.day
air_visit=pd.merge(left=air_visit,right=reservations,left_on=['air_store_id','visit_date'],right_on=['air_store_id','visit_date'],how='left')
air_visit=pd.merge(left=air_visit,right=information,left_on='air_store_id',right_on='air_store_id',how='left')
##########################
test=pd.merge(left=test,right=reservations,left_on=['air_store_id','visit_date'],right_on=['air_store_id','visit_date'],how='left')
test=pd.merge(left=test,right=information,left_on='air_store_id',right_on='air_store_id',how='left')
air_visit.sort_values(by=['air_store_id','visit_date'],ignore_index=True,inplace=True)
########################
test.sort_values(by=['air_store_id','visit_date'],ignore_index=True,inplace=True)
cols=["visitors"]
for col in cols:
    for lag in range(1,8):
        air_visit[f"{col}_lag_{lag}"]=air_visit.groupby("air_store_id")[col].transform(lambda x: x.shift(lag))  
test.fillna(-1,inplace=True)
air_visit.fillna(-1,inplace=True)
restaurant_encoder=LabelEncoder()
air_visit['air_store_id']=restaurant_encoder.fit_transform(air_visit['air_store_id'])
test['air_store_id']=restaurant_encoder.transform(test['air_store_id'])
air_visit=air_visit.loc[air_visit['air_store_id'].isin(test['air_store_id'].unique())].reset_index(drop=True)
air_visit.sort_values(by=['air_store_id','visit_date'],ignore_index=True,inplace=True)
test.sort_values(by=['air_store_id','visit_date'],ignore_index=True,inplace=True)
model=Make_LSTM_Model(parameters,embedding_dims,numerical_columns)
model.load_weights(MODEL_PATH)
submissions=[]
stores=air_visit['air_store_id'].unique().tolist()
for store_id in tqdm(stores):
    train_store_data=air_visit.loc[air_visit['air_store_id']==store_id].reset_index(drop=True)
    train_store_data=train_store_data.iloc[-19:].reset_index(drop=True)
    test_store_data=test.loc[test['air_store_id']==store_id].reset_index(drop=True)
    length=test_store_data.shape[0]
    for i in range(length):
        train_store_data=pd.concat([train_store_data,test_store_data.iloc[i:i+1].reset_index(drop=True)],ignore_index=True)
        train_store_data=MAKE_LAG_FEATURES(train_store_data)
        train_store_data.fillna(-1,inplace=True)
        prediction_data=train_store_data.iloc[-20:-1].reset_index(drop=True)
        data=scaler.transform(prediction_data.loc[:,numerical_columns])
        data=pd.DataFrame(data,columns=scaler.feature_names_in_)
        prediction_data=prediction_data.loc[:,categorical_columns+['visit_date','visitors']].join(data)
        window_data=create_window(prediction_data,numerical_columns,categorical_columns)
        del data,prediction_data
        import gc
        gc.collect()
        train_store_data.loc[train_store_data.shape[0]-1,'visitors']=np.squeeze(model.predict(window_data))
    final_sub_data=train_store_data.iloc[-length:].reset_index(drop=True)
    submissions.append(final_sub_data)

submissions=pd.concat(submissions,ignore_index=True)
submissions['air_store_id']=submissions['id'].apply(lambda x: "_".join(x.split("_")[:2]))
submission=submissions[['id',"air_store_id","visit_date",'visitors']]
submission.to_csv("submission.csv",index=False)

bucket=get_bucket()
bucket.upload_file("submission.csv","predictions.csv")
insert_predictions(submission)