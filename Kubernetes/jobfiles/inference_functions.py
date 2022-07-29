import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input,Embedding,BatchNormalization,Dense,ReLU

def make_datetime_to_date(dataframe):
    dataframe['visit_datetime']=pd.to_datetime(dataframe['visit_datetime'])
    dataframe['reserve_datetime']=pd.to_datetime(dataframe['reserve_datetime'])
    dataframe['n_days_gap']=dataframe.apply(lambda x: (x['visit_datetime']-x['reserve_datetime']).days,axis=1)
    dataframe["n_hrs_gap"]=dataframe.apply(lambda x: (x['visit_datetime']-x['reserve_datetime']).total_seconds()/3600.0,axis=1)
    dataframe["visit_date"]=dataframe['visit_datetime'].dt.date
    dataframe.drop(['visit_datetime',"reserve_datetime"],axis=1,inplace=True)
    return dataframe


def get_cuisines(genres):
    l=[]
    for g in genres:
        gs=g.split("/")
        l.extend(gs)
    return list(set(l))

def Embedding_out_dim(n_cat):
    return min(600, round(1.6 * n_cat ** .56))

def RMSLE(y_true,y_pred):
    y_true=tf.cast(y_true,dtype=y_pred.dtype)
    log_1p_y_true=tf.keras.backend.log(1.0+y_true)
    log_1p_y_pred=tf.keras.backend.log(1.0+y_pred)
    sq_diff=tf.reduce_mean(tf.keras.backend.square(log_1p_y_true-log_1p_y_pred),axis=-1)
    mean_value=tf.reduce_mean(sq_diff,axis=-1)
    return mean_value**0.5


def create_window(window_data,numerical_columns,categorical_columns):
    X={}
    X['numeric']=np.empty((1,19,len(numerical_columns)))
    for col in categorical_columns:
        X[col]=np.empty((1,19))
    assert window_data['air_store_id'].nunique()==1,"arrange data by air_store_id"
    X['numeric'][0,]=window_data.loc[:,numerical_columns].values
    for col in categorical_columns:
        X[col][0,]=window_data[col].values
    return X




def Make_LSTM_Model(parameters,embedding_dims,numerical_columns):
    window_size=parameters['window_size']
    lstm_n_layers=parameters['lstm_n_layers']
    dense_layers=parameters['dense_layers']
    lstm_units=parameters['lstm_units']
    dense_units=parameters['dense_units']
    ins_dict={}
    embed_layers={}
    ins_dict['numeric']=Input((window_size,len(numerical_columns)),name='numerical')
    for col,dims in embedding_dims.items():
        ins_dict[col]=Input((window_size,),name=f"ins_{col}")
        embed_layers[col]=Embedding(input_dim=dims['input_dim'],output_dim=dims['out_dim'],
                                    input_length=window_size,name=f"embedding_{col}")(ins_dict[col])
    concat_layer=tf.keras.layers.Concatenate()
    l=[ins_dict['numeric']]
    for col,layer in embed_layers.items():
        l.append(layer)
    x=concat_layer(l)
    for layer in range(lstm_n_layers):
        if layer!=lstm_n_layers-1:
            x=tf.keras.layers.Bidirectional(tf.keras.layers.LSTM(lstm_units[layer],return_sequences=True))(x)
            #x=tf.keras.layers.SpatialDropout1D(0.1)(x)
        else:
            x=tf.keras.layers.Bidirectional(tf.keras.layers.LSTM(lstm_units[layer]))(x)
    #x=tf.keras.layers.Dropout(0.1)(x)
    if dense_layers>0:
        for layer in range(dense_layers):
            x=Dense(dense_units[layer])(x)
            x=BatchNormalization()(x)
            x=ReLU()(x)
            #x=tf.keras.layers.Dropout(0.1)(x)
    outs=Dense(1,activation="relu")(x)
    model=Model(inputs=ins_dict,outputs=outs)
    return model

def MAKE_LAG_FEATURES(data):
    col='visitors'
    for lag in range(1,8):
        data[f"{col}_lag_{lag}"]=data.groupby("air_store_id")["visitors"].transform(lambda x: x.shift(lag))  
    return data
    
def MAKE_ROLLING_FEATURES(data):
    col='visitors'
    for window in [7,14,30]:
        data[f"{col}_rolling_{window}_mean"]=data.groupby("air_store_id")[col].transform(lambda x: x.rolling(window).mean())
        data[f"{col}_rolling_{window}_std"] =data.groupby("air_store_id")[col].transform(lambda x: x.rolling(window).std())
        data[f"{col}_rolling_{window}_max"] =data.groupby("air_store_id")[col].transform(lambda x: x.rolling(window).max())
        data[f"{col}_rolling_{window}_min"] =data.groupby("air_store_id")[col].transform(lambda x: x.rolling(window).min())
    return data
