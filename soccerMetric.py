import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
import statsmodels.api as sm
import statsmodels.formula.api as smf
from scipy.stats import poisson,skellam
from getData import *
from eloRating import *

class soccerMetric(eloRating):

    def teamStrength(self,df):

        data_home = df[['Home','HomeScore','AwayScore']]
        data_away = df[['Away','AwayScore','HomeScore']]

        data_home = data_home.rename(columns = {'Home':'Team', 'HomeScore':'GoalScore','AwayScore':'GoalCancel'})
        data_away = data_away.rename(columns = {'Away':'Team', 'AwayScore':'GoalScore','HomeScore':'GoalCancel'})

        data_avg = pd.concat([data_home, data_away], ignore_index = True).groupby('Team').mean()

        data_avg['Attack'] = data_avg['GoalScore'].apply(lambda x: x / data_avg['GoalScore'].mean())
        data_avg['Defense'] = data_avg['GoalCancel'].apply(lambda x: x / data_avg['GoalCancel'].mean())

        teams = self.getTeams

        return data_avg.loc[teams,:]
        #return data_avg
    
    def attackRank(self,df):
    
        attack_rank,at_rank = {}, []
        for cnt, team in enumerate(df.sort_values(by='Attack',ascending=False).index):
            attack_rank[team] = cnt+1

        for team, _ in df.iterrows():
            for k,v in  attack_rank.items():
                if team == k:
                    at_rank.append(v)
        df['Attack_Rank'] = at_rank

        return df

    def defenseRank(self,df):

        def_rank,d_rank = {}, []
        for cnt, team in enumerate(df.sort_values(by='Defense',ascending=True).index):
            def_rank[team] = cnt+1
        
        for team, _ in df.iterrows():
            for k,v in  def_rank.items():
                if team == k:
                    d_rank.append(v)
                    
        df['Defense_Rank'] = d_rank

        return df

    def poissonPredict(self, df: pd.DataFrame, home_team : str, away_team: str):

        play_df = self.getNewData(played = True) #bu sezon sadece oynanan maçları alıyoruz.

        if home_team in df.index and away_team in df.index:

            lamb_home = df.loc[home_team, 'Attack'] * df.loc[away_team, 'Defense']
            lamb_away = df.loc[away_team, 'Attack'] * df.loc[home_team, 'Defense']

            prob_home, prob_away, prob_draw = 0,0,0

            for home in range(0,10): #10 tane gol kez döner

                for away in range(0,10):

                    p = poisson.pmf(home, lamb_home) * poisson.pmf(away, lamb_away)

                    if home == away:
                        prob_draw += p

                    elif home > away:
                        prob_home += p
                    else:
                        prob_away += p

            point_home = 3 * prob_home + prob_draw
            point_away = 3 * prob_away + prob_draw

            return round(prob_home*100,2),round(prob_draw *100,2),round(prob_away *100,2)
            
        else:
            return (0,0)
        
    def _uptadeRating(self,df):

        team_data = self.teamStrength(df = df)
        team_data = self.attackRank(df = team_data)
        team_data = self.defenseRank(df = team_data)
        team_data = self.eloRank(df = team_data)
        team_data = team_data.sort_values('EloRating', ascending = False).loc[:,['EloRating','Attack','Defense']]

        scaler = MinMaxScaler()
        team_data['Rating'] = scaler.fit_transform(team_data[['EloRating']]) * 100
        #team_data['Rating'] = team_data['Rating'].apply(lambda x: round(x,2))
        team_data = team_data.applymap(lambda x: round(x,2))

        return team_data.loc[:,['Rating','Attack','Defense']]

    def getProba(self, week):

        data = self.mergeData() #history data ile bu sezon oynanan maçlardaki dataları birleştirir
        team_data = self.teamStrength(df = data) #attack defense güçlerini hesaplar ve kolon olarak ekler
        team_data = self.attackRank(df = team_data) #takımların attack ranklarını ekler
        team_data = self.defenseRank(df = team_data) #takımların defense ranklarını ekler
        team_data = self.eloRank(df = team_data) #takımların güncel elo ratinglerini ekler
        wk = self.getNewData(played=False, weekColumn = True) #weekColumn True old. bu sezon datasına hafta kolonu ekler
        wk = wk.loc[wk['Hafta'].isin([int(week)])].reset_index(drop=True)

        result = pd.DataFrame()
        home,away,h_w,drw,a_w = [],[],[],[],[]
        for idx, col in wk.iterrows():

            h,d,a = self.poissonPredict(df = team_data,
                    home_team = col['Home'], away_team = col['Away'])

            home.append(col['Home'])
            away.append(col['Away'])
            h_w.append(h)
            drw.append(d)
            a_w.append(a)

        result['Home'] = home
        result['Home_Prob'] = h_w
        result['Draw'] = drw
        result['Away_Prob'] = a_w
        result['Away'] = away

        return result