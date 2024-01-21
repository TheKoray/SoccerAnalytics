import pandas as pd 
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from scipy.stats import hmean
from getData import *

class eloRating(getData):

    def expectedResult(self, home_elo,away_elo):

        home_elo += 25 #home team
        dr= home_elo-away_elo
        we=(1/(10**(-dr/400)+1))

        return np.round(we,3),1-np.round(we,3)

    def actualResult(self,home_score,away_score):

        if home_score<away_score:
            wa=1
            wl=0
        elif home_score>away_score:
            wa=0
            wl=1
        elif home_score==away_score:
            wa=0.5
            wl=0.5
        return wl,wa

    def calculateElo(self,elo_home,elo_away,home_score,away_score):

        k = 40
        wl, wv = self.actualResult(home_score,away_score)
        we_h, we_a = self.expectedResult(elo_home,elo_away)

        elo_ln = elo_home + k*(wl-we_h)
        elo_vn = elo_away + k*(wv-we_a)

        return elo_ln,elo_vn
    
    def getEloRating(self, df, home_team, away_team):

        home = df.loc[home_team, 'EloRating']
        away = df.loc[away_team, 'EloRating']

        return home, away   

    def updateElo(self,df):

        """
        - Maç Sonuçlarına göre takımların 'Elo Rating Değerleri' güncellenir.
        """

        current_elo = {}
        for idx, row in df.iterrows():

            home = row['Home']
            away = row['Away']
            home_score = row['HomeScore']
            away_score = row['AwayScore']

            if home not in current_elo.keys():
                current_elo[home] = 1300

            if away not in current_elo.keys():
                current_elo[away] = 1300

            elo_home = current_elo[home]
            elo_away = current_elo[away]
            elo_ln,elo_vn = self.calculateElo(elo_home,elo_away,home_score,away_score)

            current_elo[home] = elo_ln
            current_elo[away] = elo_vn

            df.loc[idx,'Elo_h_before']=elo_home
            df.loc[idx,'Elo_a_before']=elo_away
            df.loc[idx,'Elo_h_after']=elo_ln
            df.loc[idx,'Elo_a_after']=elo_vn
            df.loc[idx,'EloHomeChange'] = elo_ln - elo_home 
            df.loc[idx,'EloAwayChange'] = elo_vn - elo_away

        df['HomePoint'] = [3 if h>a else 0 if h<a else 1 for h,a in zip(df['HomeScore'], df['AwayScore'])]
        df['AwayPoint'] = [3 if a>h else 0 if a<h else 1 for h,a in zip(df['HomeScore'], df['AwayScore'])]

        df['HomeForm'] = ['W' if h>a else 'L' if h<a else 'D' for h,a in zip(df['HomeScore'], df['AwayScore'])]
        df['AwayForm'] = ['W' if a>h else 'L' if a<h else 'D' for h,a in zip(df['HomeScore'], df['AwayScore'])]

        df["HomeWin"] = [1 if h == "W" else 0 for h,a in zip(df["HomeForm"], df['AwayForm'])]
        df["HomeLost"] = [1 if h == "L" else 0 for h,a in zip(df["HomeForm"], df['AwayForm'])]
        df["HomeDraw"] = [1 if h == "D" else 0 for h,a in zip(df["HomeForm"], df['AwayForm'])]

        df["AwayWin"] = [1 if a == "W" else 0 for h,a in zip(df["HomeForm"], df['AwayForm'])]
        df["AwayLost"] = [1 if a == "L" else 0 for h,a in zip(df["HomeForm"], df['AwayForm'])]
        df["AwayDraw"] = [1 if a == "D" else 0 for h,a in zip(df["HomeForm"], df['AwayForm'])]
        
        return df

    def updateEloRating(self, df : pd.DataFrame):
        
        """
        Takımların elo rating değerlerine göre 'Spı Rating' hesaplar
        """
        home_elo, away_elo,home_teams, away_teams, team, elo = [],[],[],[],[],[]
        wk_result = pd.DataFrame()

        for i,j in zip(df.loc[:,'Home'], df.loc[:,'Away']):

            home_teams.append(i)
            home_elo.append(list(df.groupby('Home')['Elo_h_after'].get_group(name = i))[::-1][0]) #en son değeri ilk değer yapıp 0.değeri(ilk değer) alıyoruz.
            away_teams.append(j)
            away_elo.append(list(df.groupby('Away')['Elo_a_after'].get_group(name = j))[::-1][0])

        wk_result['Teams'] = home_teams + away_teams
        wk_result['EloRating'] = home_elo + away_elo

        wk_result.set_index('Teams', inplace = True)
        wk_result.sort_values(by='EloRating', ascending = False, inplace = True)

        scaler = MinMaxScaler()
        wk_result['Rating'] = scaler.fit_transform(wk_result[['EloRating']]) * 100
        wk_result['Rating'] = wk_result['Rating'].apply(lambda x: round(x,2))

        return wk_result
    
    def uptadeEloRating_(self): #en günceli
        
        gData = getData()
        """- Takımların elo rating değerlerine göre 'Spi Rating' hesaplar.
           - Oynanan maçlara göre elo rating değerleri güncellenir ve ardından takımların en son güncel elo değerleri alınır.
           - Güncel elo rating değerlerine göre de spi rating hesaplanır.
        """
        df = self.updateElo(df = gData.getNewData(played = True)) #bu sezon sadece oynanan maçları alıyoruz.
        #df = self.updateElo(df = self.mergeData()) #history data alıyoruz

        data_home = df.rename(columns = {'Home':'Team', 'Elo_h_after':'EloRating'}).loc[:,["Date",'Team','EloRating']]
        data_away = df.rename(columns = {'Away':'Team', 'Elo_a_after':'EloRating'}).loc[:,["Date",'Team','EloRating']]
        wk = pd.concat([data_home, data_away], ignore_index = True).sort_values(by ='Date').reset_index(drop=True)\
                                                                .groupby("Team")['EloRating']\
                                                                .last()\
                                                                .to_frame()\
                                                                .sort_values(by='EloRating', ascending = False)
        scaler = MinMaxScaler()
        wk['Rating'] = scaler.fit_transform(wk[['EloRating']]) * 100
        wk['Rating'] = wk['Rating'].apply(lambda x: round(x,2))

        return wk
    
    def eloChange(self,df,table = False):

        data_home = df.rename(columns = {'Home':'Team','HomeScore':'AG','AwayScore':'YG','EloHomeChange':'Change','Elo_h_after':'Elo','HomePoint':'Point','HomeForm':'Form'})
        data_away = df.rename(columns = {'Away':'Team', 'AwayScore':'AG','HomeScore':'YG','EloAwayChange':'Change','Elo_a_after':'Elo', 'AwayPoint':'Point','AwayForm':'Form'})

        if table:
            data_avg= pd.concat([data_home, data_away], ignore_index = True).loc[:,['Date','Team','AG','YG','Point','Elo','Change','Form','Point','Form']]\
                                                    .assign(AV=lambda x: np.subtract(x['AG'],x['YG']))\
                                                    .assign(OM= data_avg.groupby('Team').size())\
                                                    .assign(Form = data_avg.groupby('Team')['Form'].sum().apply(lambda x: x[::-1]))\
                                                    .sort_values(by = 'Point', ascending = False)\
                                                    .reindex(['OM','AG','YG','AV','Point','Change','Form'], axis=1)
        else:
            data_avg = pd.concat([data_home, data_away], ignore_index = True).loc[:,['Date','Team','AG','YG','Point','Elo','Change','Form']]\
                                                    .sort_values(by='Date', ascending=True).reset_index(drop=True)\
                                                    .loc[:,['Team','Change','Form']].set_index('Team')\
                                                    .sort_values(by = 'Change', ascending=False)
                                                    
        data_avg['Change'] = data_avg['Change'].apply(lambda x: round(x,2))
    
        return data_avg

    def eloRank(self, df):

        elo_rat = {}
        #elo_df = self.updateElo(df = self.getNewData(played= True))
        team_rating = self.uptadeEloRating_()

        for idx in df.index:
            for ix,col in team_rating.iterrows():
                if idx == ix:
                    elo_rat[idx] = col['EloRating'] #takımların elo ratinglerini elo_rat dictionarysinde tutarız
                
        df['EloRating'] = [elo_rat[i] if i in tuple(elo_rat.keys()) else "-"
                                    for i in df.index ]
        return df



