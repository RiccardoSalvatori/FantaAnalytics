# -*- coding: utf-8 -*-
"""_FantaAnalytics_.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1wcxau-m9LDFQnh7ALMMPrclRECnwc89E
"""
import numpy as np
import math
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import math as math
import os
import scipy.stats as stats

## UTILITY FUNCTIONS

def all_nans(y):
  for val in y:
    if(not math.isnan(val)): 
      return False
  return True

def count_nans(y):
  nans_count = 0
  for val in y:
    if(math.isnan(val)): 
      nans_count=nans_count+1
  return nans_count

def nan_helper(y):
    """Helper to handle indices and logical indices of NaNs.

    Input:
        - y, 1d numpy array with possible NaNs
    Output:
        - nans, logical indices of NaNs
        - index, a function, with signature indices= index(logical_indices),
          to convert logical indices of NaNs to 'equivalent' indices
    Example:
        >>> # linear interpolation of NaNs
        >>> nans, x= nan_helper(y)
        >>> y[nans]= np.interp(x(nans), x(~nans), y[~nans])
    """

    return np.isnan(y), lambda z: z.nonzero()[0]

def getPlayersBySeasons(dataset, seasons):
  all_seasons = dataset.copy()
  for s in seasons:
    all_seasons = all_seasons[all_seasons[s] == True]
  return  all_seasons

# Return a numpy array containing votes just for played seasons
def getRawPlayerValues(playerName, df):
  from itertools import compress
  row = df[df['Name'] == playerName]
  x = row.iloc[0, SEASON_COLUMN_START:SEASON_COLUMN_START+len(SEASONS)]
  ranges = compress(SEASONS, x.tolist())
  z = list()
  z = z + [list(r) for r in ranges]
  z = [item + DISCARD_COLUMNS for sublist in z for item in sublist] 
  
  return (row.iloc[:, z]).values.flatten()

# Return a numpy array containing votes just for played seasons
def getPlayerValues(playerName, df, window = 5, diff=False):
  from itertools import compress
  row = df[df['Name'] == playerName]
  x = row.iloc[0, SEASON_COLUMN_START:SEASON_COLUMN_START+len(SEASONS)]
  ranges = compress(SEASONS, x.tolist())
  z = list()
  z = z + [list(r) for r in ranges]
  z = [item + DISCARD_COLUMNS for sublist in z for item in sublist] 
  
  ma_size = int(window / 2)
  player_values = getRawPlayerValues(playerName, df)
  res = pd.Series(player_values).rolling(window).mean().shift(-ma_size)
  res[0 : ma_size] = player_values[0 : ma_size]
  res[-ma_size : ] = player_values[ -ma_size:]
  if(diff):
      res = res.diff()
      res[0] = res[1]
      
  return  np.array(res);

## DATASET CREATION

"""#Loading data

Download dataset from Dropbox
"""

raw_fantavoti = pd.read_csv("https://dl.dropbox.com/s/ltafmntqwlm4677/serie_storiche_fantavoti.csv?dl=1") 
raw_voti = pd.read_csv("https://dl.dropbox.com/s/bnvi5y3upaka6dw/serie_storiche_voti.csv?dl=1")

"""Create "bonus" dataframe"""

raw_bonus = raw_fantavoti.copy()
raw_bonus.iloc[:, 3:] =  raw_fantavoti.iloc[:, 3:] - raw_voti.iloc[:, 3:]
raw_bonus

"""Fix error in OKONKWOO role"""

idx = raw_fantavoti[raw_fantavoti['Name'] == 'OKONKWOO'].index
for df in [raw_fantavoti, raw_voti, raw_bonus]:
  df.at[idx,"Role"] = "C"

"""Define utility functions and constants"""

FILLING_METHOD=1    #linear interpolation 
#FILLING_METHOD=2  # placheolder

NAME_COLUMN = 0
ROLE_COLUMN = 2 
SEASON_COLUMN_START = 3
SEASON_LENGTH = 38
SEASONS_COUNT = 3
TOTAL_MATCHES = SEASON_LENGTH*SEASONS_COUNT
SEASONS = [range(0, SEASON_LENGTH), range(SEASON_LENGTH, SEASON_LENGTH * 2), range(SEASON_LENGTH * 2, SEASON_LENGTH * 3)] #define seasons indexes
MATCH_PLAYED_COLUMN = SEASON_COLUMN_START + SEASONS_COUNT
DISCARD_COLUMNS = MATCH_PLAYED_COLUMN + 1



"""Add columns to show seasons played by a player<br>
By default, the column is created with falue 'F', then it will be set correctly.
"""

raw_fantavoti_values = raw_fantavoti.iloc[:, 3:]
raw_voti_values = raw_voti.iloc[:, 3:]
#concat votes and fantavotes for each season
seasons_votes = [pd.concat([raw_fantavoti_values.iloc[:,s], raw_voti_values.iloc[:,s]]) for s in SEASONS] 

#add one column for each season. Contains true or false if the player has played that season
for i in range(0,len(SEASONS)):
  raw_fantavoti.insert(SEASON_COLUMN_START + i, "S{}".format(i+1), "False")
  raw_voti.insert(SEASON_COLUMN_START + i, "S{}".format(i+1), "False")
  raw_bonus.insert(SEASON_COLUMN_START + i, "S{}".format(i+1), "False")

"""Fill season columns with right values"""

for index, row  in raw_fantavoti.iterrows():
  #One bool for each season: True if exists one value in that season
  has_played_season = [not all_nans(s.iloc[index,:]) for s in seasons_votes] 
  for s, b in enumerate(has_played_season):
    (raw_fantavoti.iloc[index, SEASON_COLUMN_START + s]) = b
    (raw_voti.iloc[index, SEASON_COLUMN_START + s]) = b
    (raw_bonus.iloc[index, SEASON_COLUMN_START + s]) = b

"""Add column to show the number of matches played by a player
By default, the column is created with value 0, then it will be set rightly.
"""

raw_fantavoti.insert(MATCH_PLAYED_COLUMN, "Match_Played", 0)
raw_voti.insert(MATCH_PLAYED_COLUMN, "Match_Played", 0)
raw_bonus.insert(MATCH_PLAYED_COLUMN, "Match_Played", 0)

"""Fill "Match_Played" column by counting the number of values in each row. Start counting from the columns that contains player votes. (nan values are omitted by default)"""

raw_fantavoti["Match_Played"] = (raw_fantavoti.iloc[:, DISCARD_COLUMNS:]).apply(lambda x: x.count(), axis=1)
raw_voti["Match_Played"] = (raw_voti.iloc[:, DISCARD_COLUMNS:]).apply(lambda x: x.count(), axis=1)
raw_bonus["Match_Played"] = (raw_bonus.iloc[:, DISCARD_COLUMNS:]).apply(lambda x: x.count(), axis=1)

"""Drop players that didn't play any match (rows that contains all NaNs in votes and fantavotes both)"""

toDrop = raw_fantavoti[raw_fantavoti['Match_Played'] == 0].iloc[:,NAME_COLUMN].values

[raw_voti.drop(raw_voti[ raw_voti['Name'] == d ].index , inplace=True) for d in toDrop]
[raw_fantavoti.drop(raw_fantavoti[ raw_fantavoti['Name'] == d ].index , inplace=True) for d in toDrop]
[raw_bonus.drop(raw_bonus[raw_bonus['Name'] == d ].index , inplace=True) for d in toDrop]

print("Dropped %d" % len(toDrop))
print(toDrop)

## PREPROCESSING


"""#Data preprocessing

##Fill missing values

1\.Linear interpolation
"""

def interpolate(values):
  _min = np.nanmin(values.to_numpy().flatten()) #find minimum fantavote (ignore NaNs)
  nanReplacement = _min - 1 #values that will replace NaN
  interpolated = pd.DataFrame(data=[],columns=range(1,TOTAL_MATCHES+1))
  for index, row  in values.iterrows():
    rowValues = row.to_numpy().flatten()
    nans, x = nan_helper(rowValues)
    if (not all_nans(rowValues)):
      rowValues[nans] = np.interp(x(nans), x(~nans), rowValues[~nans])
    else:
      rowValues[nans] = nanReplacement
    interpolated.loc[index] = rowValues
  return interpolated

if(FILLING_METHOD == 1):
    fantavoti = raw_fantavoti.copy()
    interpolated_votes = interpolate((fantavoti.iloc[:, DISCARD_COLUMNS:]).copy())
    fantavoti.iloc[:, DISCARD_COLUMNS:] = interpolated_votes.values
    
    voti = raw_voti.copy()
    interpolated_votes = interpolate((voti.iloc[:, DISCARD_COLUMNS:]).copy())
    voti.iloc[:, DISCARD_COLUMNS:] = interpolated_votes.values
    
    bonus = raw_bonus.copy()
    interpolated_votes = interpolate((bonus.iloc[:, DISCARD_COLUMNS:]).copy())
    bonus.iloc[:, DISCARD_COLUMNS:] = interpolated_votes.values
    
    print(fantavoti)

"""2\. Placeholder: NaN = (min vote - 1)."""



def replace_nan(df, filling_strategy=None):
  df2 = df.copy()
  _votes = df2.iloc[:, DISCARD_COLUMNS:]
  if filling_strategy is None: 
    _min = np.nanmin(_votes.to_numpy().flatten()) #find minimum fantavote (ignore NaNs)
    nanReplacement = _min - 1 #values that will replace NaN
  else:
    nanReplacement = filling_strategy()
  _votes[np.isnan(_votes)] = nanReplacement
  df2.iloc[:,DISCARD_COLUMNS:] = _votes
  return (df2, nanReplacement)

if(FILLING_METHOD == 2):
    fantavoti, FANTAVOTI_NAN_PLACEHOLDER = replace_nan(raw_fantavoti)
    voti = replace_nan(raw_voti)[0]
    bonus = replace_nan(raw_bonus, lambda : 0)[0]
    
    print(fantavoti)

"""##Translation<br> 
Votes transposed coherently in order to keep all votes positive.<br>
E.g. useful when performing log operations.
"""

def min_vote(df):
  return np.min(df.iloc[:, DISCARD_COLUMNS:].to_numpy().flatten())

def translate(df):
  votes = df.iloc[:, DISCARD_COLUMNS:]
  min_vote = np.nanmin(votes.to_numpy().flatten())
  if (min_vote <= 0):
    df.iloc[:, DISCARD_COLUMNS:] = df.iloc[:, DISCARD_COLUMNS:] + abs(min_vote) + 1

min_before = min_vote(fantavoti)
print("Fantavoti min vote before transaltion: %.1f" % min_before)
translate(fantavoti)
min_after = min_vote(fantavoti)
print("Fantavoti min vote after translation: %.1f" % min_after)
# Update NaN placeholder
if (FILLING_METHOD == 2): #i.e fixed value
  FANTAVOTI_NAN_PLACEHOLDER = min_after

translate(voti)

"""# Normalization"""

def minmax_normalize(values):
    _max = max(values)
    _min = min(values)
    normalized = (values-_min)/(_max-_min)
    return normalized

def z_normalize(values):
    return stats.zscore(values)

"""#Analysis on players data

Count played matches for each player
"""

players = fantavoti
TOTAL_MATCHES = players.shape[1] - DISCARD_COLUMNS
players_match_played_count = pd.DataFrame(columns=["Player", "Role", "Match_Played"])
for player in players.values:
  name = player[NAME_COLUMN]
  role = player[ROLE_COLUMN]
  nPlayed = player[MATCH_PLAYED_COLUMN] 
  players_match_played_count = players_match_played_count.append({"Player": name, "Role": role, "Match_Played": nPlayed}, ignore_index=True)

"""##High-level analysis on players dataset

Count players group by #playedMatch
"""

plt.rcdefaults()

match_played_count_no_role = players_match_played_count.groupby('Match_Played').agg('count')
played_count = match_played_count_no_role.index
player_count = match_played_count_no_role["Player"]

plt.bar(played_count, player_count, align='center', alpha=0.5)
plt.show()

"""Avg match played"""

avg_match_played = players_match_played_count["Match_Played"].mean()
print("Average number of match played by a player {}".format(avg_match_played))

max_match_played = players_match_played_count["Match_Played"].max()
print("Max number of match played by a player {}".format(max_match_played))
print(players_match_played_count[players_match_played_count["Match_Played"] == max_match_played])
print("\n\n")

min_match_played = players_match_played_count["Match_Played"].min()
print("Min number of match played by a player {}".format(min_match_played))
print("\n\n")

"""##Fine-grained analysis on players per role

Count match played for role
"""

roles = ['P', 'D', 'C', 'A'] 
role_match_played_count = players_match_played_count.loc[:,"Role":]
box_plots = list()
match_played_count = players_match_played_count["Match_Played"]

for role in roles:
  filter = role_match_played_count["Role"] == role
  single_role_match_played_count = role_match_played_count[filter]

  single_role_match_played_count = single_role_match_played_count.groupby('Match_Played').agg('count')
  single_role_match_played_count.columns = ["Count"]
  played_count = single_role_match_played_count.index
  player_count = single_role_match_played_count["Count"]
  box_plots.append(players_match_played_count[players_match_played_count.Role == role].Match_Played)
  plt.title(role)
  plt.bar(played_count, player_count, align='center', alpha=0.5)
  plt.show()

box_plots.append(match_played_count)
plt.boxplot(box_plots)
plt.xticks([1, 2, 3,4,5], roles+['ALL'])

"""Avg match played for role"""

(fantavoti.groupby("Role").agg('mean')).Match_Played

(fantavoti.groupby("Role")).Match_Played.quantile([.25,.5,.75])

"""#Data correlation

Pearson correlation
"""

from statsmodels.graphics.tsaplots import plot_pacf
from statsmodels.graphics.tsaplots import plot_acf
from scipy.stats import linregress
import scipy.stats as stats

DEAFULT_PEARSON_VALUE = 0

def pearsonCorrelation(player, dataset):
  """ 
	Pearson correlation. 

	Return a list of pearsons auto-correlations of players votes in dataset (DEAFULT_PEARSON_VALUE if NaN). 

	Parameters: 
	player (str): player name
  dataset (DataFrame): datafrme containing player votes
	Returns: 
	l: list of pearsons auto-correlations  (DEAFULT_PEARSON_VALUE when pearson correlation cannot be computed)

	"""
  df = pd.DataFrame()

  # Set "votes" column values
  votes = getPlayerValues(player, dataset, diff=True)
  df['votes'] = votes

  #Set "period" column values 
  df["period"] = range(1, len(votes)+1) 
  df.set_index('period')
  nLags = SEASON_LENGTH+1
  return [ df['votes'].autocorr(lag=l) if not np.isnan(df['votes'].autocorr(lag=l)) else DEAFULT_PEARSON_VALUE 
          for l in range(0, nLags)] 


def allPearsonsCorrelations(players, dataset):
  """ 
	Returns: 
	l: list of tuples (player, pearson) 

	"""
  ret = []
  for player in players: 
    pearson = pearsonCorrelation(player, dataset)
    ret.append((player, pearson))
  return sorted(ret, key=lambda tup: tup[1])

def bestSeasonality(player, dataset):
  """ 
	Returns: 
	l: list of tuples (best_seasonality, pearson_value) 

	"""
  pearson = pearsonCorrelation(player, dataset)
  if(len(pearson) > 1): 
    pearson = pearson[1:] #exclude the first element (always 1)
    maxIdx = np.asarray(pearson).argmax()
    return (maxIdx + 1, pearson[maxIdx])
  else:
    return (DEAFULT_PEARSON_VALUE, DEAFULT_PEARSON_VALUE)

def bestSeasonalities(players, dataset):
  """ 
	Returns: 
	l: list of tuples (player, best_seasonality, pearson_value) 

	"""
  ret = []
  for player in players: 
    best, value = bestSeasonality(player, dataset)
    if(best != DEAFULT_PEARSON_VALUE):
      ret.append((player, best, value))
    else:
       ret.append((player, DEAFULT_PEARSON_VALUE, DEAFULT_PEARSON_VALUE))
  return ret

"""Calculate best seasonality for each player using Pearson correlation"""

#players that played all seasons and more then 100 matches
players_df = getPlayersBySeasons(fantavoti, ["S1", "S2", "S3"])
players_df = players_df[players_df.Match_Played > 100]

x = bestSeasonalities(players_df['Name'], players_df)
x = [(i, players_df[players_df['Name'] == i[0]].Match_Played.values[0]) for i in x if not math.isnan(i[2])]
sorted(x, key=lambda tup: (tup[0])[2], reverse=False)

"""Pearson correlation per role"""

pearson_per_role = pd.DataFrame(columns=["Player", "Role", "Pearson"])

for i, row in players_df.iterrows():
  player = row['Name']
  role = row['Role']
  pearson = bestSeasonality(player, players_df)[0]
  pearson_per_role =  pearson_per_role.append({"Player":player, 
                                             "Role":role ,
                                             "Pearson": pearson}, ignore_index=True)

pearson_per_role["Pearson"] = pearson_per_role["Pearson"].astype(float)

((pearson_per_role.groupby('Role'))['Pearson']).quantile([.25,.5,.75])

"""# Utilities for player infos"""

import matplotlib.colors as mcolors

plt.rcParams.update({'figure.figsize':(12,3), 'figure.dpi':120})

def plotPlayerInfo(playerName, dataset):
  fig, axs = plt.subplots(1, 2)
  fig.suptitle(playerName)

  player_values = getPlayerValues(playerName, dataset)
  axs[0].plot(player_values)
  axs[0].set_title('Valori')

  p1 = pearsonCorrelation(playerName, dataset)
  axs[1].bar(range(0, len(p1)), p1, color="lightblue")
  axs[1].set_title('Correlazione di Pearson')

def plotAllPlayerInfo(playerName):
  fig, axs = plt.subplots(2, 3)
  fig.suptitle(playerName)

  axs[0,0].plot([i for i in getPlayerValues(playerName, voti, diff=True) if i < 100], color = "orange")
  axs[0,0].set_title('Voti')

  axs[0,1].plot(getPlayerValues(playerName, bonus, diff=True), color = "blue")
  axs[0,1].set_title('Bonus')

  axs[0,2].plot(getPlayerValues(playerName, fantavoti, diff=True), color = "red" )
  axs[0,2].set_title('Fantavoti')

  p1 = pearsonCorrelation(playerName, voti)
  p2 = pearsonCorrelation(playerName, bonus)
  p3 = pearsonCorrelation(playerName, fantavoti)

  axs[1,0].bar(range(0, len(p1)), p1, color = "orange")
  axs[1,0].set_title('Voti')

  axs[1,1].bar(range(0, len(p2)), p2, color = "blue")
  axs[1,1].set_title('Bonus')

  axs[1,2].bar(range(0, len(p3)), p3, color = "red")
  axs[1,2].set_title('Fantavoti')

"""Plot player data"""
plt.rcParams.update({'figure.figsize':(12,6), 'figure.dpi':120})

plotAllPlayerInfo("DZEKOE")
plt.show()

"""#Normality test: Q-Q plot"""

#import statsmodels.api as sm
import pylab as py 
plt.rcParams.update({'figure.figsize':(12,4), 'figure.dpi':120})

def plotNormalityTest(values):
  plt.rcParams.update({'figure.figsize':(8,3), 'figure.dpi':120})
  unique_elements, counts_elements = np.unique(values, return_counts=True)
  plt.bar(unique_elements, counts_elements,width=0.5, color='#0504aa',alpha=0.7)
  #sm.qqplot(np.asarray(values), line='s')
  py.show()

"""1\.Not considering non played matches"""

votes = getPlayerValues("DZEKOE", raw_fantavoti)
votes = votes[~np.isnan(votes)]
roundV = [round(v * 2) / 2 for v in votes]
plotNormalityTest(roundV)

"""2\. Considering non played matches too"""

votes = getPlayerValues("DZEKOE", fantavoti)
roundV = [round(v * 2) / 2 for v in votes]
plotNormalityTest(roundV)


"""1\.Not considering non played matches"""

votes = getPlayerValues("DZEKOE", raw_voti)
votes = votes[~np.isnan(votes)]
roundV = [round(v * 2) / 2 for v in votes]
plotNormalityTest(roundV)

"""2\. Considering non played matches too"""

votes = getPlayerValues("DZEKOE", voti)
roundV = [round(v * 2) / 2 for v in votes]
plotNormalityTest(roundV)

"""#Forecast"""

forecast_dataset = fantavoti
playerName = 'DZEKOE'


"""Define accuracy metrics"""

def forecast_accuracy(forecast, actual):
  mape = np.mean(np.abs(forecast - actual)/np.abs(actual))  # MAPE
  me = np.mean(forecast - actual)             # ME
  mae = np.mean(np.abs(forecast - actual))    # MAE
  mpe = np.mean((forecast - actual)/actual)   # MPE
  rmse = np.mean((forecast - actual)**2)**.5  # RMSE
  #corr = np.corrcoef(forecast, actual)[0,1]   # corr
  mins = np.amin(np.hstack([forecast[:,None], 
                            actual[:,None]]), axis=1)
  maxs = np.amax(np.hstack([forecast[:,None], 
                            actual[:,None]]), axis=1)
  minmax = 1 - np.mean(mins/maxs)             # minmax
  return({'mape':mape, 'me':me, 'mae': mae, 
            'mpe': mpe, 'rmse':rmse, 
            'corr':0, 'minmax':minmax})

"""Create data frame with all players train set and test set"""

#x = players_match_played_count[players_match_played_count['Match_Played'] >= 110]
players = getPlayersBySeasons(forecast_dataset, ["S1", "S2", "S3"])
players = players[players.Match_Played > 100]


players = players[players.Name==playerName] ## delete this to forecast all players

players = players.Name
player_train_test = pd.DataFrame(columns=['Player', 'Votes', 'Train', 'Test'])

for player in players:
  df = pd.DataFrame()
  df['votes'] = getPlayerValues(player, forecast_dataset, diff=False)
  votes = df['votes']

  # Set "period" column values 
  df["period"] = range(1,len(votes)+1) 
  df.set_index('period')

  TEST_SET_SIZE = int(len(votes) * 30 / 100)
  train = votes[:-TEST_SET_SIZE]
  test = votes[-TEST_SET_SIZE:]
  #test.index = range(0,len(test))
  player_train_test = player_train_test.append(
      {'Player':player,
       'Votes':votes,
       'Train':train,
       'Test':test}, ignore_index=True)
  
print("Dataset size {}".format(len(player_train_test)))


"""## SARIMA

Setup
"""

from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
import pyramid.arima as pm
from statsmodels.tsa.arima_model import ARIMA
import pprint

plt.rcParams.update({'figure.figsize':(12,4), 'figure.dpi':120})

"""Define ARIMA workflow"""

def arima(player, dataset, train , test):

  _m = bestSeasonality(player, dataset)[0]
  #_m = 38
  #if(_m == 1): 
  #  _m = 38

  # Seasonal - fit stepwise auto-ARIMA, returns an ARIMA model
  smodel = pm.auto_arima(train, start_p=1, start_q=1,
                         test='adf',
                         max_p=3, max_q=3, m=_m,
                         start_P=0, seasonal=True,
                         d=0, D=1, trace=True,
                         error_action='ignore',  
                         suppress_warnings=True, 
                         stepwise=True)
  df = pd.DataFrame()
  df['votes'] = getPlayerValues(player, dataset)
  votes = df['votes']

  #Set "period" column values 
  df["period"] = range(1,len(votes)+1) 
  df.set_index('period')

  # Predictions of y values based on "model", aka fitted values
  yhat = smodel.predict_in_sample(start=0, end=len(train))
  forecasts, confint = smodel.predict(n_periods=len(test), return_conf_int=True)
  index_forecasts = pd.Series(range(df.index[-1]+1-len(test), df.index[-1]+1))
  metrics = forecast_accuracy(forecasts, df.votes[-len(test)-1:-1])
  return ({'model':smodel, 'rmse':metrics['rmse']})


"""Create ARIMA model for each player"""

players_models_arima = {}
playersLength = len(player_train_test)
for i, row in player_train_test.iterrows():
  player = row['Player']
  train = row['Train']
  test = row['Test']
  votes = row['Votes']
  print("{} {}/{}".format(player, i+1, playersLength))
  arimaDict = arima(player, forecast_dataset, train, test)
  players_models_arima[player] = arimaDict

"""Evaluate mean accuracy"""

rmse = np.array( [ p['rmse'] for p in players_models_arima.values()])
print("SARIMA mean RSME {}".format(rmse.mean()))

forecast_player = playerName

# Seasonal - fit stepwise auto-ARIMA, returns an ARIMA model
smodel = players_models_arima[forecast_player]['model']
train = player_train_test[player_train_test.Player == forecast_player].Train.values[0]
test = player_train_test[player_train_test.Player == forecast_player].Test.values[0]

# Predictions of y values based on "model", aka fitted values
yhat = smodel.predict_in_sample(start=1, end=len(train))
forecasts, confint = smodel.predict(n_periods=len(test), return_conf_int=True)
index_forecasts = pd.Series(range(len(train),len(train)+len(test)))
fitted_series = pd.Series(forecasts, index=index_forecasts)
lower_series = pd.Series(confint[:, 0], index=index_forecasts)
upper_series = pd.Series(confint[:, 1], index=index_forecasts)

# Plot
plt.plot(np.concatenate((train, test)))
plt.plot(yhat,color='brown')
plt.plot(fitted_series, color='darkgreen')
plt.fill_between(lower_series.index, 
                 lower_series, 
                 upper_series, 
                 color='k', alpha=.15)

plt.title("SARIMA - Final Forecast " + forecast_player)
plt.show()



"""##LSTM
"""
from keras.models import Sequential
from keras.layers import Dense
from keras.layers import LSTM
from keras.layers import Flatten
from keras.layers import GRU
from keras.preprocessing.sequence import TimeseriesGenerator


accuracies = {}
players_models_lstm = {}
n_input = 12; 
n_features = 1
for index, player in player_train_test.iterrows():
  print("Training n.{} ".format(index+1)+ "on " + player.Player)
  train = player.Train.to_numpy()
  train = train.reshape((len(train),1))
  train_generator =  TimeseriesGenerator(train, train, length=n_input, batch_size=1)
  lstm_model = Sequential()
  lstm_model.add(LSTM(32, activation='relu', input_shape=(n_input,n_features)))
  lstm_model.add(Dense(1))
  lstm_model.compile(optimizer='adam', loss='mse')
  #lstm_model.summary()
  lstm_model.fit_generator(train_generator,epochs=50)
  test = player.Test.to_numpy()
  test = test.reshape((len(test),1))
  test_generator =  TimeseriesGenerator(test, test, length=n_input, batch_size=1)
  predictions = lstm_model.predict_generator(test_generator).flatten()
  accuracies[player.Player] = forecast_accuracy(test[n_input:].flatten(), predictions)
  players_models_lstm[player.Player] = {
      'model': lstm_model,
      'rmse': accuracies[player.Player]['rmse']
  }

lstm_mean_rsme = np.mean([ players_models_lstm[x]['rmse'] for x in players_models_lstm ])
print("LSTM mean RSME {}".format(lstm_mean_rsme))




#print single player DEZEKO
plt.rcParams.update({'figure.figsize':(12,3), 'figure.dpi':120})


plt.title("LSTM Final Forecast - " + playerName)
player = player_train_test[player_train_test.Player==playerName]
train = player.Train.values[0].to_numpy()
train = train.reshape((len(train),1))
train_generator =  TimeseriesGenerator(train, train, length=n_input, batch_size=1)
test = player.Test.values[0].to_numpy()
test = test.reshape((len(test),1))
lstm_test = np.concatenate((train[-n_input:], test))

test_generator =  TimeseriesGenerator(lstm_test, lstm_test, length=n_input, batch_size=1)
predictions =  players_models_lstm[playerName]['model'].predict_generator(test_generator).flatten()
train_pred =  players_models_lstm[playerName]['model'].predict_generator(train_generator)

plt.plot([t for t in train] + [x for x in test], label='votes')
plt.plot([None for x in range(n_input)] +[x for x in train_pred],
          color='brown',label="train_prediction")
plt.plot([None for t in range(len(train))] + [x for x in predictions], 
          label="prediction", color='darkgreen')

plt.xticks(range(0,114,3))

plt.show()

"""## MLP

Setup
"""

import math
from keras.models import Sequential
from keras.layers import Dense
from keras.preprocessing.sequence import TimeseriesGenerator
from keras import optimizers

np.random.seed(550) # for reproducibility

"""Define MLP forecast workflow"""

def mlp(votes, train, test, n_past, n_hidden, batch_size, epochs):
  #logdata = np.log(votes) # log transform
  logdata = votes
  mlp_dataset = logdata#.to_numpy() # time series values
  mlp_dataset = mlp_dataset.astype('float32') # needed for MLP input
  train, test = train.astype('float32'), test.astype('float32')
  test = test.reset_index()["votes"]
  print("Len train={0}, len test={1}".format(len(train), len(test)))
  generator = TimeseriesGenerator(train, train, length=n_past, batch_size=batch_size)
  model = Sequential()
  n_output = 1

  model.add(Dense(n_hidden, input_dim=n_past, activation='relu')) # hidden neurons, 1 layer
  model.add(Dense(n_output)) # output neurons
  sgd = optimizers.Adam(lr=0.001, beta_1=0.9, beta_2=0.999, amsgrad=False)
  model.compile(loss='mean_squared_error', optimizer=sgd)
  model.fit_generator(generator, epochs=epochs)
  trainScore = model.evaluate_generator(generator, verbose=0)
  print('Score on train: MSE = {0:0.2f} '.format(trainScore))

  test_generator = TimeseriesGenerator(test, test, length=n_past, batch_size=batch_size)
  test_score_mse = model.evaluate_generator(test_generator, verbose=0)
  return ({'model':model, 'rmse': math.sqrt(test_score_mse)})


"""Create MLP model for each player"""

MLP_NPAST = 12
MLP_BATCH_SIZE = 1

players_models_mlp = {}
playersLength = len(player_train_test)
for i, row in player_train_test.iterrows():
  player = row['Player']
  train = row['Train']
  test = row['Test']
  votes = row['Votes']
  print("{} {}/{}".format(player, i+1, playersLength))
  npast = bestSeasonality(player, forecast_dataset)[0]
  players_models_mlp[player] =  mlp(votes, train, test, 
                                    n_past=MLP_NPAST, n_hidden=38, 
                                    batch_size=MLP_BATCH_SIZE, epochs=75)

rmse = np.array( [ p['rmse'] for p in players_models_mlp.values()])
print(rmse.mean())

 #mlp forecasts
train = player_train_test[player_train_test.Player == playerName].Train.values[0]
test = player_train_test[player_train_test.Player == playerName].Test.values[0]

mlp_test = pd.concat([train[-MLP_NPAST:], test], ignore_index=True)
train_generator = TimeseriesGenerator(train, train, length=MLP_NPAST, batch_size=MLP_BATCH_SIZE)
test_generator = TimeseriesGenerator(mlp_test, mlp_test, length=MLP_NPAST, batch_size=MLP_BATCH_SIZE)

model = players_models_mlp[playerName]['model']
mlp_forecasts = model.predict_generator(test_generator)
mlp_forecasts = mlp_forecasts.flatten()

mlp_train_fit = model.predict_generator(train_generator)
mlp_train_fit = mlp_train_fit.flatten()

plt.plot([x for x in train] + [x for x in test])
plt.plot([None for x in train] + [x for x in mlp_forecasts])
plt.plot([None for x in range(0,n_input-1)] + [x for x in mlp_train_fit])
plt.show()


"""# FINAL FORECAST

Merge LSTM and SARIMA models.
Final forecast is 
$$\alpha*LSTM + (1-\alpha)*SARIMA$$

Alpha parameter is chosen to minimize RMSE
"""

def best_weigth(test, lstm_forecasts, arima_forecasts):
  """
  Find weight (w) that minimize error in w*mlp_forecasts + (a-w)*arima_forecasts
  """
  errors = []
  for i in range(0, 100):
    alpha = i / 100
    beta = 1 - alpha
    weighted_forecasts = (alpha * lstm_forecasts + beta * arima_forecasts)
    meanError = ((test - weighted_forecasts)**2).mean() #mse
    errors.append(meanError)
  return np.array(errors).argmin() / 100

"""Create dataframe that contains LSTM model, SARIMA model and Weigth"""

player_model = pd.DataFrame()

rmse_list = []
for i, row in player_train_test.iterrows():
  player = row['Player']
  test = row['Test']
  train = row['Train']
  test.index = range(0, len(test))
  train.index = range(0, len(train))

  #arima foreacsts
  arima_forecasts = players_models_arima[player]['model'].predict(n_periods=len(test))
  
   #lstm forecats
  lstm_test = pd.concat([train[-12:], test], ignore_index=True)
  test_r = lstm_test.to_numpy().reshape((len(lstm_test),1))
  test_generator =  TimeseriesGenerator(test_r, test_r, length=n_input, batch_size=1)
  lstm_forecast =  players_models_lstm[player]['model'].predict_generator(test_generator).flatten()
  
  alpha = best_weigth(test , lstm_forecast, arima_forecasts)
  weighted_forecasts = (alpha * lstm_forecast + (1-alpha) * arima_forecasts)

  rmse_list.append(forecast_accuracy(test, weighted_forecasts)['rmse'])
  
  player_model =player_model.append({"Player": player,
                       "Arima": players_models_arima[player]['model'],
                       "Lstm": players_models_lstm[player]['model'],
                       "Alpha": alpha}, ignore_index=True)

rmse = np.array(rmse_list)
print("SARIMA+LSTM mean RSME {}".format(rmse.mean()))

## RESULTS

player = "DZEKOE"
test = player_train_test[player_train_test.Player == player]['Test'].values[0]
test.index = range(0,len(test))

train = player_train_test[player_train_test.Player == player]['Train'].values[0]
train.index = range(0,len(train))

#arima foreacsts
arima_forecasts = players_models_arima[player]['model'].predict(n_periods=len(test))
  
#lstm forecasts
lstm_test = pd.concat([train[-12:], test], ignore_index=True)
test_r = lstm_test.to_numpy().reshape((len(lstm_test),1))
test_generator =  TimeseriesGenerator(test_r, test_r, length=n_input, batch_size=1)
lstm_forecast =  players_models_lstm[player]['model'].predict_generator(test_generator).flatten()

#weighted forcast
alpha = player_model[player_model.Player == player]['Alpha'].values[0]
weighted_forecasts = (alpha * lstm_forecast + (1-alpha) * arima_forecasts)

plt.plot(test, label = "test",alpha=0.7)

plt.plot(lstm_forecast, label = "LSTM",alpha=0.4)
plt.plot(arima_forecasts, label = "SARIMA", alpha=0.4)
plt.plot(weighted_forecasts, label = "FINAL")

plt.title("SARIMA+LSTM Final Forecast " + player)
plt.legend(loc=1)
plt.show()
print(player_model[player_model.Player == player]['Alpha'])
