import pandas as pd
import numpy as np 
import requests
from bs4 import BeautifulSoup as bs
import re
import matplotlib.pyplot as plt
import seaborn as sns
from plottable import ColumnDefinition, Table
from plottable.plots import circled_image # image
from matplotlib.colors import LinearSegmentedColormap
from plottable.cmap import normed_cmap
from plottable.formatters import decimal_to_percent
from plottable.plots import circled_image # image
import matplotlib
import matplotlib.patches as patches

class getData:

    def historyData(self):

        df = pd.read_csv(r"C:\Users\koray\OneDrive\Masaüstü\SuperLig\süperligAI\süperligHistory.csv")
        df.drop('Unnamed: 0', axis=1, inplace=True)

        return df
    
    def addWeek(self,df):

        """Hafta Kolonu ekler
        Keyword arguments:
        df : Hafta kolonu ekleyeceğimiz dataFrame
        Return: dataFrame
        """
        for i in range(int(len(df) / 10)): #Hafta kolonu ekliyoruz
            x,y = i*10, i*10+9
            df.loc[x:y,'Hafta'] = i+1
        df['Hafta'] = df['Hafta'].astype('int')

        return df
    
    def getPlayedMatches(self,df):

        """
        - Oynanmiş maçlari alir
        """
        ix = []
        for idx, col in df.iterrows():
            try:
                if ",".join(col['Score'].split("-")[0])[0].isnumeric():
                    ix.append(idx)
            except IndexError:
                break
        df = df.loc[ix]
        df['HomeScore'] = df['Score'].apply(lambda x: re.findall('[0-9]',x)[0]).astype('int')
        df['AwayScore'] = df['Score'].apply(lambda x: re.findall('[0-9]',x)[1]).astype('int')

        return df
    
    def getNewData(self, played=False, weekColumn = False):

        r = requests.get("https://fbref.com/en/comps/26/schedule/Super-Lig-Scores-and-Fixtures")
        soup = bs(r.content, 'html.parser')
        table = soup.find('table', class_ = 'stats_table') #fikstür, maç ve sonuçları bizim tablelarımız

        result = pd.DataFrame()
        day,date,time,home,score,away = [],[],[],[],[],[]
        for row in table.tbody.find_all('tr'):

            columns = row.find_all('td')
            day.append(columns[0].text)
            date.append(columns[1].text)
            time.append(columns[2].text)
            home.append(columns[3].text)
            score.append(columns[4].text)
            away.append(columns[5].text)

        result['Day'] = day
        result['Date'] = date
        #result['Time'] = time
        result['Home'] = home
        result['Score'] = score
        result['Away'] = away

        result['Date'] = pd.to_datetime(result['Date'])
        result.drop(result.loc[result['Date'].isnull()].index, axis=0, inplace=True) #date sütunlarında gelen boş satırları siliyoruz.
        result.reset_index(drop=True, inplace=True)

        if played:
            result.drop([23,27,29], axis=0, inplace=True) #ertelenen maçları datadan çıkarttık. O maçlar oynanınca bu satırı sil!
            result.reset_index(drop=True,inplace = True)
            result = self.getPlayedMatches(df = result)

        if weekColumn:
            result = self.addWeek(df = result)

        return result
  
    def mergeData(self):
        """
        - History Data ile 2023/2024 maç datasını birleştirir.
        """
        return pd.concat(
            [self.historyData(),self.getNewData(played=True)], ignore_index=True)
    
    @property
    def getTeams(self):
        """
        get Team names
        """

        df = self.getNewData(played=True)

        return set(list(df['Home']) + list(df['Away']))
    
    def imgAdd(self,result_df, team_img):
        """
        Haftalık sonuçların bulunduğu dataya takımların logolarını ekler.
        - Home ve Away kolonunda ki takımların isimlerinin takımların logoları ile değişir.
        """
        for idx, col in result_df.iterrows():
            for i,j in team_img.iterrows():
                if col['Home'] == j['Home']:
                    result_df.loc[idx,'Home'] = j['Img']
                if col['Away'] == j['Away']:
                    result_df.loc[idx,'Away'] = j['Img']
        return result_df
    
    def formTeam(self,df):

        team_form = {}
        teams = self.getTeams

        for t in list(teams):
            form_l = [] # liste her takım için yenilenecek ve ilgili takımın form değerleri alınacak bu listeye eklenecek.
            for idx, col in df.iterrows():
                if t == df.loc[idx,'Home']:
                    form_l.append(df.loc[idx,'HomeForm'])
                elif t == df.loc[idx,'Away']:
                    form_l.append(df.loc[idx,'AwayForm'])

            team_form[t] = form_l # her takım için oluşturulan form değerlerinin bulunduğu liste team_form dictionarysinde ilgili takım değerine eklenir.

        return {k:v[::-1] for k,v in team_form.items()}
    
    def teamTable(self,df):
        """
        - Puan Tablosunu veren fonksiyon
        """

        team_form = self.formTeam(df =df) # takımların form değerlerini alırız.

        data_home = df.rename(columns = {'Home':'Team','HomeScore':'AG','AwayScore':'YG','EloHomeChange':'Change','Elo_h_after':'Elo','HomePoint':'Point','HomeForm':'Form',
                                 'HomeWin':'Win','HomeDraw':'Draw','HomeLost':'Lost'})
        data_away = df.rename(columns = {'Away':'Team', 'AwayScore':'AG','HomeScore':'YG','EloAwayChange':'Change','Elo_a_after':'Elo', 'AwayPoint':'Point','AwayForm':'Form',
                                'AwayWin':'Win','AwayDraw':'Draw','AwayLost':'Lost'})

        data_avg = pd.concat([data_home, data_away], ignore_index = True)\
                                                    .groupby('Team').sum().loc[:,['AG','YG','Point','Elo','Change']]\
                                                    .assign(WeeklyChange = pd.concat([data_home,data_away], ignore_index=True).groupby(['Date','Team'])['Change'].last().to_frame()\
                                                            .reset_index("Team").groupby("Team")['Change'].last())\
                                                    .assign(OM = pd.concat([data_home, data_away], ignore_index = True).groupby("Team").size())\
                                                    .assign(W = pd.concat([data_home, data_away], ignore_index = True).groupby("Team")['Win'].sum())\
                                                    .assign(D = pd.concat([data_home, data_away], ignore_index = True).groupby("Team")['Draw'].sum())\
                                                    .assign(L = pd.concat([data_home, data_away], ignore_index = True).groupby("Team")['Lost'].sum())\
                                                    .assign(AV=lambda x: np.subtract(x['AG'],x['YG']))\
                                                    .assign(MBP = lambda x: round(np.divide(x["Point"], x['OM']),2))\
                
        data_avg = data_avg.assign(Form = [form[:5] for idx in data_avg.index for team, form in self.formTeam(df = df).items() if idx == team])
        data_avg = data_avg.assign(Form = [''.join(data_avg.loc[idx,'Form']) for idx in data_avg.index])\
                    .reindex(['OM','W','D','L','AG','YG','AV','Point','WeeklyChange','Change','MBP','Form'], axis=1)\
                    .sort_values(by = 'Point', ascending = False)

        data_avg['Change'] = data_avg['Change'].apply(lambda x: round(x,2))
        data_avg['WeeklyChange'] = data_avg['WeeklyChange'].apply(lambda x: round(x,2))

        return data_avg
    
