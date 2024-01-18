
from getData import * 
import statsmodels.api as sm
import statsmodels.formula.api as smf
from scipy.stats import poisson,skellam

gData = getData()

class poissonmodel():

    def poissonModel(self):

        data = gData.mergeData() #history data ile bu sezon oynanan maçlardaki dataları birleştirir

        goal_model_data = pd.concat([data[['Home','Away','HomeScore']].assign(home=1).rename(
                columns={'Home':'team', 'Away':'opponent','HomeScore':'goals'}),
            data[['Away','Home','AwayScore']].assign(home=0).rename(
                columns={'Away':'team', 'Home':'opponent','AwayScore':'goals'})])

        poisson_model = smf.glm(formula="goals ~ home + team + opponent", data=goal_model_data,
                                family=sm.families.Poisson()).fit()
        return poisson_model

    def simulate_match(poisson_mdoel, homeTeam, awayTeam, max_goals=10):
        
        home_goals_avg = poisson_mdoel.predict(pd.DataFrame(data={'team': homeTeam,
                                                            'opponent': awayTeam, 'home': 1},
                                                        index=[1])).values[0]
        away_goals_avg = poisson_mdoel.predict(pd.DataFrame(data={'team': awayTeam,
                                                            'opponent': homeTeam, 'home': 0},
                                                        index=[1])).values[0]
        team_pred = [[poisson.pmf(i, team_avg) for i in range(0, max_goals + 1)] for team_avg in
                    [home_goals_avg, away_goals_avg]]
        return (np.outer(np.array(team_pred[0]), np.array(team_pred[1])))

