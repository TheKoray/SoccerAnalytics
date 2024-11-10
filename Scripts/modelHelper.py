import pandas as pd 
import numpy as np 
from soccerMetric import * 
from getPlot import *
from getData import *
from eloRating import *
from helpers import save
from poissonmodel import * 
import pickle 
import os 

gData = getData()
soccer = soccerMetric()
elo = eloRating()
plot = getPlot()
poisson = poissonmodel()

class modelHelper():

    def teamPower(self, df,home_team,away_team):

        data_home = df.rename(columns = {'Home':'Team', 'HomeScore':'GoalScore','AwayScore':'GoalCancel'})
        data_away = df.rename(columns = {'Away':'Team', 'AwayScore':'GoalScore','HomeScore':'GoalCancel'})

        data_avg = pd.concat([data_home, data_away], ignore_index = True).groupby('Team').mean()

        data_avg['Attack'] = data_avg['GoalScore'].apply(lambda x: x / data_avg['GoalScore'].mean())
        data_avg['Defense'] = data_avg['GoalCancel'].apply(lambda x: x / data_avg['GoalCancel'].mean())

        if home_team not in data_avg.index:

            attack_home = 0
            defense_home = 0
            attack_away = data_avg.loc[away_team,'Attack']
            defense_away = data_avg.loc[away_team, 'Defense']

        if away_team not in data_avg.index:

            attack_home = data_avg.loc[home_team,'Attack']
            defense_home = data_avg.loc[home_team, 'Defense']
            attack_away = 0
            defense_away = 0
        else:
            attack_home = data_avg.loc[home_team,'Attack']
            defense_home = data_avg.loc[home_team, 'Defense']
            attack_away = data_avg.loc[away_team,'Attack']
            defense_away = data_avg.loc[away_team, 'Defense']

        return attack_home,defense_home, attack_away, defense_away

    def teamForm(self, df, home, away):
        #win sayılları toplamı
        df = df.assign(HomePoint = [3 if h>a else 0 if h<a else 1 for h,a in zip(df['HomeScore'], df['AwayScore'])])\
            .assign(AwayPoint = [3 if a>h else 0 if a<h else 1 for h,a in zip(df['HomeScore'], df['AwayScore'])])\
            .assign(HomeWin = [1 if h > a else 0 for h,a in zip(df['HomeScore'], df['AwayScore'])])\
            .assign(AwayWin = [1 if a > h else 0 for h,a in zip(df['HomeScore'], df['AwayScore'])])\
            .assign(Draw = [1 if a == h else 0 for h,a in zip(df['HomeScore'], df['AwayScore'])])
        
        data_home = df.rename(columns = {'Home':'Team','HomeScore':'GoalScore','AwayScore':'GoalCancel','HomeWin':'Win','HomePoint':'Point'})
        data_away = df.rename(columns = {'Away':'Team','AwayScore':'GoalScore','HomeScore':'GoalCancel','AwayWin':'Win','AwayPoint':'Point'})

        data_avg = pd.concat([data_home, data_away]).groupby('Team').agg({'GoalScore':'mean','GoalCancel':'mean','Point':'mean','Win':'sum'})\
                .loc[:,['Win','Point']]
        
        if home not in data_avg.index:
            h_w = 0
            a_w = data_avg.loc[away, 'Win']

        if away not in data_avg.index:
            h_w = data_avg.loc[home, 'Win']
            a_w = 0
            
        else:
            h_w = data_avg.loc[home, 'Win']
            a_w = data_avg.loc[away, 'Win']

        return h_w, a_w
    
    def ScoreDifference(self, df : pd.DataFrame):

        """
        Keyword arguments:
        df -- played_match of new season
        Return: pd.DataFrame
        """
        data_home = df[['Home','HomeScore', 'AwayScore']].rename(columns = {'Home':'Team','HomeScore':'Score', 'AwayScore':'ScoreCancel'})
        data_away = df[['Away','AwayScore', 'HomeScore']].rename(columns = {'Away':'Team','AwayScore':'Score', 'HomeScore':'ScoreCancel'})

        result = pd.concat([data_home, data_away], ignore_index=True).groupby('Team')[['Score','ScoreCancel']].sum()\
            .sort_values(by = 'Score', ascending = False)
        
        return result

    def goalDiff(self, df,home, away):

        result = self.ScoreDifference(df = df)
        
        if home not in result.index:
            
            home_goal = 0
            home_cancel = 0
            away_goal = result.loc[away, "Score"]
            away_cancel = result.loc[away, "ScoreCancel"]

        if away not in result.index:

            home_goal = result.loc[home, "Score"]
            home_cancel = result.loc[home, "ScoreCancel"]
            away_goal = 0
            away_cancel = 0
        else:
            home_goal = result.loc[home, "Score"]
            home_cancel = result.loc[home, "ScoreCancel"]
            away_goal = result.loc[away, "Score"]
            away_cancel = result.loc[away, "ScoreCancel"]

        return home_goal, home_cancel, away_goal, away_cancel

    def matchPoint(self, df, home, away):

        df = df.assign(HomePoint = [3 if h>a else 1 if h==a else 0 for h,a in zip(df['HomeScore'], df["AwayScore"])])\
        .assign(AwayPoint = [3 if a>h else 1 if h==a else 0 for h,a in zip(df['HomeScore'], df["AwayScore"])])

        data_home = df.rename(columns = {'Home':'Team','HomePoint':'Point'})
        data_away = df.rename(columns = {'Away':'Team','AwayPoint':'Point'})

        result = pd.concat([data_home, data_away], ignore_index=True).groupby("Team")["Point"].mean().to_frame("mbp")

        if home not in result.index:

            home_point = 0
            away_point = result.loc[away, "mbp"]

        if away not in result.index:

            home_point = result.loc[home, "mbp"]
            away_point = 0
        else:
            home_point = result.loc[home, "mbp"]
            away_point = result.loc[away, "mbp"]

        return home_point, away_point

    def importance_table(self, df,model):

        imp_table = pd.DataFrame()
        importance = model.feature_importances_
        names = df.columns
        name_list, imp_list = list(), list()

        for name,imp in zip(names,importance):

            name_list.append(name)
            imp_list.append(imp)
        
        imp_table['Columns'] = name_list
        imp_table['importance'] = imp_list
        imp_table.sort_values('importance', ascending = False, inplace = True)
        
        return imp_table.reset_index(drop = True)

    def getPlayedMatch(self, df):

        played_idx = []
        for idx, col in df.iterrows():
            if col["HomeScore"].isnumeric():
                played_idx.append(idx)

        play_df = self.new_data.loc[played_idx]

        play_df["Home"] = play_df["Home"].str.strip()
        play_df["Away"] = play_df["Away"].str.strip()

        play_df["HomeScore"] = play_df["HomeScore"].astype("int")
        play_df["AwayScore"] = play_df["AwayScore"].astype("int")

        return play_df

    def mbp(self, df):
        """
        - df : Played match data
        """
        mbp_data = df.assign(HomePoint = [3 if h>a else 1 if h==a else 0 for h,a in zip(df['HomeScore'], df["AwayScore"])])\
            .assign(AwayPoint = [3 if a>h else 1 if h==a else 0 for h,a in zip(df['HomeScore'], df["AwayScore"])])

        data_home = mbp_data.rename(columns = {'Home':'Team','HomePoint':'Point'})
        data_away = mbp_data.rename(columns = {'Away':'Team','AwayPoint':'Point'})

        result = pd.concat([data_home, data_away], ignore_index=True).groupby("Team")["Point"].mean().to_frame("mbp").apply(lambda x: round(x,2))

        return result
    
    def predResult(self, home, away, model,team_data, play_df):
        
        team = pd.DataFrame()
        #team_rank = {team : cnt +1 for cnt, (team, rank) in enumerate(soccer.uptadeEloRating_().loc[:,'EloRating'].items())} #elo rating değerlerine göre sıralama
        team_rank = {team : cnt +1 for cnt, (team, rank) in enumerate(team_data.loc[:,"EloRating"].sort_values(ascending=False).items())}

        h_w, a_w = self.teamForm(df = play_df, home=home, away=away)

        team['Elo_h_before'] = [team_data.loc[home,'EloRating']]
        team['Elo_a_before'] = [team_data.loc[away,'EloRating']]
        team['Elo_difference'] = team['Elo_h_before'] - team['Elo_a_before']

        team["HomeRank"] = team_rank[home]
        team["AwayRank"] = team_rank[away]
        team['HomeAttack'] = team_data.loc[home,'GoalScore']
        team['HomeDefense'] = team_data.loc[home,'GoalCancel']
        team['AwayAttack'] = team_data.loc[away,'GoalScore']
        team['AwayDefense'] = team_data.loc[away,'GoalCancel']
        team['HomeForm'] = h_w 
        team['AwayForm'] = a_w
        team['HomeMBP'] = self.mbp(df = play_df).loc[home].values[0]
        team["AwayMBP"] = self.mbp(df = play_df).loc[away].values[0]
        team["GoalScoreDifference"] = team_data.loc[home,"Score"] - team_data.loc[away,"Score"]
        team["GoalCancelDifference"] = team_data.loc[home,"ScoreCancel"] - team_data.loc[away,"ScoreCancel"]
        team["HomeAv"] = team_data.loc[home, "Av"]
        team['AwayAv'] = team_data.loc[away, "Av"]
        team["AvDifference"] = team["HomeAv"] - team["AwayAv"]
        
        team = team.reindex(['Elo_h_before','Elo_a_before','Elo_difference','HomeRank','AwayRank',
                            'HomeAttack','HomeDefense','AwayAttack','AwayDefense','HomeForm','AwayForm',"HomeMBP","AwayMBP","GoalScoreDifference","GoalCancelDifference",
                            "HomeAv","AwayAv", "AvDifference"], 
                            axis=1)
        
        prob_cache = {"Home Win": round(model.predict_proba(team)[0][1], 2), #tahmin probaların tutulduğu dictionary
                    "Draw" : round(model.predict_proba(team)[0][0], 2),
                    "Away" : round(model.predict_proba(team)[0][2], 2)
                    }

        return prob_cache['Home Win'],prob_cache['Draw'], prob_cache['Away']

    def probWeek(self, wk, team_data, play_df, model):

        new_data = pd.read_csv("2023_2024_sezonu.csv").drop("Unnamed: 0", axis=1) # 2023-2024 sezon maçlarının olduğu csv 

        result, home,away, h_p, d_p, a_p = pd.DataFrame(), [],[],[],[],[]

        for idx, col in new_data.loc[new_data['Hafta'].isin([wk])].iterrows():

            h, d, a = self.predResult(home = col['Home'], away = col['Away'], model = model, team_data=team_data, play_df=play_df)
            home.append(col['Home'])
            away.append(col['Away'])
            h_p.append(h)
            d_p.append(d)
            a_p.append(a)

        result['Home'] = home
        result['Home_Prob'] = h_p
        result['Draw'] = d_p
        result['Away_Prob'] = a_p
        result['Away'] = away

        return result

    def getTeamData(self):

        model = pickle.load(open("tff_model", "rb")) #load ai model
        play_df = gData.getNewData(played = True).drop(['Score','Day'], axis=1)

        team_data = soccer.teamStrength(df = play_df) #takımların güçlerini alırız. Attack, defense.
        team_data = soccer.attackRank(df = team_data) # takımların attack değerine göre rankını alırız.
        team_data = soccer.defenseRank(df = team_data) #takmların defense değerine göre rankını alırız.
        team_data = soccer.eloRank(df = team_data) #takımların elo rating değerlerini ekleriz.

        mbp_data = self.mbp(df = play_df)
        score_diff = self.ScoreDifference(df = play_df)

        team_data = pd.merge(team_data, mbp_data, left_index=True, right_index=True)
        team_data = pd.merge(team_data, score_diff, left_index=True, right_index=True)

        team_data = team_data.assign(Av = lambda x: x["Score"] - x["ScoreCancel"])

        return team_data, play_df, model

    def predictPipeline(self, wk : int, plotting = False):

        team_data, play_df, model = self.getTeamData() #tahmin için gerekli data ve model

        result = self.probWeek(wk = wk, team_data = team_data, play_df = play_df, model = model)

        result = result.assign(Home_Prob = round(result['Home_Prob'] * 100,2))\
                        .assign(Draw = round(result['Draw'] * 100, 2))\
                        .assign(Away_Prob = round(result['Away_Prob'] * 100,2))
        if plotting:
            result_df = plot.imgAdd(result_df = result)
            plot.weeklyProbPlot(df = result_df)
        return result
    
    def saveStats(self, wk):

        poisson = poissonmodel()
        user_cache = {'ai': self.predictPipeline,
                    'poisson' : poisson.poissonPredictPipeline,
                    'table' : self.main}
        
        for key,function in user_cache.items():
            #save fonksiyonun da path değişeceği için her seferinde dictionary içeerisindeki fonksiyonları çalıştıran scriptlerin olduğu pathe gittik
            os.chdir(r'C:\\Users\\koray\\OneDrive\\Masaüstü\\SuperLig\\süperligAI')

            if key  != 'table':
                df = function(wk = wk)
            else:
                df =  function(user = 'Stats')

            save(df = df, statsName = key)

    def main(self, user):

        if user == "Pred":
            predWeek = input("Predict For Week = ")
            return self.predictPipeline(wk = int(predWeek))

        elif user == 'Rating':
            return soccer.uptadeEloRating_().reset_index().set_axis(np.arange(1,21), axis=0)

        elif user == "Weekly":

            week = input("Week = ")
            new_data = pd.read_csv("2023_2024_sezonu.csv").drop("Unnamed: 0", axis=1)

            return new_data.loc[new_data["Hafta"].isin([int(week)])].set_index('Tarih')\
                        .drop(['HomeScore','AwayScore'], axis=1)
    
        elif user == 'Stats':
                return plot.getTablePlot().drop('Img', axis = 1)
        
        elif user == "Poisson":
            week = input("Week = ")
            return poisson.poissonPredictPipeline(wk = int(week))
        
        elif user == 'Save':
            week = input("Week = ")
            self.saveStats(wk = week)
        