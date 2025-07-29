import pandas as pd
from os.path import dirname, join

TIME_NAME = "time"
CENS_NAME = "cens"


def get_y(cens, time):
    cens, time = np.array(cens), np.array(time) 
    y = np.empty(dtype=[(CENS_NAME, bool), 
                        (TIME_NAME, np.float64)], 
                 shape=cens.shape[0])
    y[CENS_NAME] = cens
    y[TIME_NAME] = time
    return y


def str_to_categ(df_col):
    uniq = df_col.unique()
    return df_col.map(dict(zip(uniq, range(len(uniq)))))


def load_backblaze_2016_2018(threshold=0.99):
    df = pd.read_csv('./backblaze_drop_truncated_2016_2018.csv')
    df['time'] = pd.to_timedelta(df['time']).dt.days
    df = df.rename({"time": TIME_NAME, "event": CENS_NAME}, axis=1)
    nan_percentage = df.isna().mean()
    columns_with_high_nan = nan_percentage[nan_percentage >= threshold].index.tolist()
    df = df.drop(columns=['serial_number', 'date', 'time_row'] + columns_with_high_nan)
    categ = ['model']
    df['model'] = str_to_categ(df['model'])
    sign = sorted(list(set(df.columns) - {CENS_NAME, TIME_NAME}))
    y = get_y(df[CENS_NAME], df[TIME_NAME] + 1)
    X = df.loc[:, sign]
    return X, y, sign, categ