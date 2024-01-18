
from getData import * 
import statsmodels.api as sm
import statsmodels.formula.api as smf
from scipy.stats import poisson,skellam
import seaborn as sns 
import matplotlib.pyplot as plt
from helper import *

gData = getData()
h = helper()

class poissonmodel():

    def __init__(self, home_team, away_team):

        self.home_team = home_team
        self.away_team = away_team
        self.max_goals = 7

    def poissonModel(self):

        data = gData.mergeData() #history data ile bu sezon oynanan maçlardaki dataları birleştirir

        goal_model_data = pd.concat([data[['Home','Away','HomeScore']].assign(home=1).rename(
                columns={'Home':'team', 'Away':'opponent','HomeScore':'goals'}),
            data[['Away','Home','AwayScore']].assign(home=0).rename(
                columns={'Away':'team', 'Home':'opponent','AwayScore':'goals'})])

        poisson_model = smf.glm(formula="goals ~ home + team + opponent", data=goal_model_data,
                                family=sm.families.Poisson()).fit()
        return poisson_model

    def simulateMatch(self):

        poisson_mdoel = self.poissonModel()
        home_goals_avg = poisson_mdoel.predict(pd.DataFrame(data={'team': self.home_team,
                                                            'opponent': self.away_team, 'home': 1},
                                                        index=[1])).values[0]
        
        away_goals_avg = poisson_mdoel.predict(pd.DataFrame(data={'team': self.away_team,
                                                            'opponent': self.home_team, 'home': 0},
                                                        index=[1])).values[0]
        
        team_pred = [[poisson.pmf(i, team_avg) for i in range(0, self.max_goals + 1)] for team_avg in
                    [home_goals_avg, away_goals_avg]]
        
        return pd.DataFrame((np.outer(np.array(team_pred[0]), np.array(team_pred[1]))))
    

    def poissonPredict(self):

        score_matrix = self.simulateMatch()

        #Home, draw, away probabilities
        homewin=np.sum(np.tril(score_matrix, -1))
        draw=np.sum(np.diag(score_matrix))
        awaywin=np.sum(np.triu(score_matrix, 1))

        return homewin, draw, awaywin

    def goalsProbPlot(self):
        
        score_df = self.simulateMatch()
        fig=plt.figure(figsize=(10,5))
        ax=fig.add_subplot(1,1,1)
        sns.heatmap(score_df, 
                    #annot=score_df.applymap(lambda x: round(x*100,2)), #plot üzerindeki proba textleri için
                    annot=score_df.applymap(lambda x: "<" if x < 0.04 else round(x,2)), 
                    fmt= "",
                    cmap = plt.cm.Reds,
                    cbar = False)
        ax.xaxis.tick_top()
        ax.set_xlabel('Goals scored by ' + self.away_team)
        ax.set_ylabel('Goals scored by ' + self.home_team)
        ax.xaxis.tick_top()
        ax.yaxis.get_inverted()
        plt.title(f"{self.home_team} - {self.away_team} Outcome Probability")
        return fig 

