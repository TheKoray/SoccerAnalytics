from soccerMetric import * 
from getPlot import *
import plotly
import plotly.express as px
import kaleido 
import os
from datetime import datetime
plot = getPlot()

TODO = "according to plotting type update savefig function"

class helper(soccerMetric):

    path = r"C:\Users\koray\OneDrive\Masaüstü\SuperLig\Output"

    @staticmethod
    def getCurrentDate():

        date = datetime.now()
        return "-".join(str(dt) for dt in [date.day,date.month,date.year])

    def _getPlotInfo(self, figName): #grafiğe göre klasör ismi döndürür.

        folderCache = {'WeeklyChange' : 'weeklyChange',
                        'TeamRating': 'TeamRating',
                        'pred' : 'Pred'
                        }
        folderName = "".join([v for k,v in folderCache.items() if figName == k]) #path'deki ilgili figure göre klasör ismini aldık.

        return folderName

    def _saveFig(self, figName, figure): # plotu kaydeder
        
        folderName = self._getPlotInfo(figName=figName)
        figDate = self.getCurrentDate()

        assert isinstance(figure,(plotly.graph_objs._figure.Figure, matplotlib.figure.Figure)), "figure parameter not figure type"

        if figName == 'WeeklyChange':

            figure.write_image(fr"{self.path}\{folderName}\{folderName}_{figDate}.png")

        elif figName == "TeamRating":

            os.chdir(fr"{self.path}\{folderName}")
            figure.savefig(f"{folderName}_{figDate}")
    
    def _getInfo(self,figName):

        figDate = self.getCurrentDate()
        folderName = self._getPlotInfo(figName=figName)

        print(f"{self.path}\{folderName} klasörüne {folderName}_{figDate} adında kaydedildi")
        
    def getTable(self):

        play_df = self.getNewData(played = True) #bu sezon sadece oynanan maçları alıyoruz.
        elo_df = self.updateElo(df = play_df) 
        data_avg = self.teamTable(df = elo_df)
        elo_change_df = plot.teamRatingImg(df = data_avg)

        return elo_change_df.drop('Img', axis=1)
    
    def WeeklyChange(self):

        play_df = self.getNewData(played = True) #bu sezon sadece oynanan maçları alıyoruz.
        elo_df = self.updateElo(df = play_df) 
        data_avg = self.teamTable(df = elo_df)

        fig = px.bar(data_avg, y = 'WeeklyChange', x = data_avg.index, 
             color = "WeeklyChange",
             color_continuous_scale = "Reds_r", #cmap parametresi. weeklyChange değişkeninde ki değerleri eksiden artıya cmap ayarladık.
             text= [str(data_avg["WeeklyChange"]) for i in data_avg['WeeklyChange']], #bar üzerinde ki değerleri yazdık
             labels = {"color" : "Change >0 or <0"})

        fig.update_layout(
            title_text="Weekly Change of Performance Rating For Teams",
            title_x=0.5, #title position
            height=400,
            width=1000,
            xaxis={'categoryorder': 'total descending'},
            template="plotly_dark"
        )

        fig.update_layout(
            font_family="Courier New",
            font_color= "white", #grafikte yazıların rengi
            title_font_family="Times New Roman",
            title_font_color= "white", #title rengi
            legend_title_font_color="white" #label rengi (blue, red üzerinde ki color'ın rengi)
        )

        self._saveFig(figure = fig, figName = "WeeklyChange") #figure save
        self._getInfo(figName = "WeeklyChange") #path ve figure bilgisi
    
    def TeamRating(self):

        data = self.mergeData() #history data ile bu sezon oynanan maçlardaki dataları birleştirir
        team_data = self.teamStrength(df = data) #takımların güçlerini alırız. Attack, defense.
        team_data = self.attackRank(df = team_data) # takımların attack değerine göre rankını alırız.
        team_data = self.defenseRank(df = team_data) #takmların defense değerine göre rankını alırız.
        team_data = self.eloRank(df = team_data) #takımların elo rating değerlerini ekleriz
        team_rating = self.uptadeRating_(df = data) #takımların spi rating, attack ve defense değerlerinin bize verir.
        team_rating = plot.teamRatingImg(df = team_rating)
        img = plot.plotTeamsRating(df = team_rating)
        
        self._saveFig(figure = img, figName = "TeamRating")
        self._getInfo(figName = "TeamRating")


