import pandas as pd


def make_datetime_to_date(dataframe):
    dataframe['visit_datetime']=pd.to_datetime(dataframe['visit_datetime'])
    dataframe['reserve_datetime']=pd.to_datetime(dataframe['reserve_datetime'])
    dataframe['n_days_gap']=dataframe.apply(lambda x: (x['visit_datetime']-x['reserve_datetime']).days,axis=1)
    dataframe["n_hrs_gap"]=dataframe.apply(lambda x: (x['visit_datetime']-x['reserve_datetime']).total_seconds()/3600.0,axis=1)
    dataframe["visit_date"]=dataframe['visit_datetime'].dt.date
    dataframe.drop(['visit_datetime',"reserve_datetime"],axis=1,inplace=True)
    return dataframe

def create_reservations_table(air_res_path,hpg_res_path,mapper_path):
    air_res=pd.read_csv(air_res_path)
    hpg_res=pd.read_csv(hpg_res_path)
    stores_map=pd.read_csv(mapper_path)
    hpg_res=pd.merge(left=hpg_res,right=stores_map,left_on="hpg_store_id",right_on='hpg_store_id',how='inner')
    hpg_res.drop("hpg_store_id",axis=1,inplace=True)
    reservations=pd.concat([air_res,hpg_res],ignore_index=True)
    reservations=make_datetime_to_date(reservations)
    new_cols=["air_store_id","visit_date"]
    for col in ['reserve_visitors','n_hrs_gap','n_days_gap']:
        for agg in ['mean']:
            new_cols.append(col+"_"+agg)
    reservations=reservations.groupby(["air_store_id","visit_date"]).agg({"reserve_visitors":["mean"],
                                                        "n_hrs_gap":["mean"],
                                                        "n_days_gap":["mean"]}).reset_index()
    reservations.columns=new_cols
    reservations['visit_date']=pd.to_datetime(reservations['visit_date'])
    reservations.sort_values(by=['air_store_id','visit_date'],ignore_index=True,inplace=True)
    reservations.to_csv("reservations.csv",index=False)

def create_cuisine_geo_tables(air_info_path,hpg_info_path,mapper_path):
    air_info=pd.read_csv(air_info_path)
    hpg_info=pd.read_csv(hpg_info_path)
    stores_map=pd.read_csv(mapper_path)
    hpg_info=pd.merge(left=hpg_info,right=stores_map,left_on="hpg_store_id",right_on='hpg_store_id',how='inner')
    hpg_info.rename(columns={"hpg_genre_name":"air_genre_name","hpg_area_name":"air_area_name"},inplace=True)
    hpg_info.drop("hpg_store_id",axis=1,inplace=True)
    information=pd.concat([air_info,hpg_info],ignore_index=True)
    cuisine=information[['air_store_id','air_genre_name']]
    cuisine['air_genre_name']=cuisine['air_genre_name'].apply(lambda x: x.split("/"))
    cuisine=cuisine.explode("air_genre_name").reset_index(drop=True)
    cuisine.to_csv("cuisine.csv",index=False)
    geo=information[['air_store_id','air_area_name','latitude','longitude']]
    geo.to_csv("geo.csv",index=False)
    
    