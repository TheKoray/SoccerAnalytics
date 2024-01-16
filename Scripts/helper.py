from soccerMetric import * 
from getPlot import *
import plotly.express as px
import kaleido 
import os
from datetime import datetime
plot = getPlot()

TODO = '_getInfo path update, _saveFig function update for savefig function'

class helper(soccerMetric):

    @staticmethod
    def getCurrentDate():

        date = datetime.now()
        return "-".join(str(dt) for dt in [date.day,date.month,date.year])
    
    def _getInfo(self, fileName):

        print(f"{fileName} görseli weeklyChange klasörü içerisinde wkChange{fileName} adı ile kaydedildi.")

    def _getPlotInfo(self, figName):


        
        folderCache = {'wk' : 'wkChange',
                       'rating': 'TeamRating',
                       'pred' : 'Pred'
                       }
        folderName = "".join([v for k,v in folderCache.items() if figName == k]) #path'deki ilgili figure göre klasör ismini aldık.
    
    def _saveFig(self, figure,figName):

        folderCache = {'wk' : 'wkChange',
                       'rating': 'TeamRating',
                       'pred' : 'Pred'
                       }
        folderName = "".join([v for k,v in folderCache.items() if figName == k]) #path'deki ilgili figure göre klasör ismini aldık.

        if figName == 'wk':
            figure.write_image(fr"C:\Users\koray\OneDrive\Masaüstü\SuperLig\Output\{folderName}\wkChange{figName}.png")
        else:
            os.chdir(fr"C:\Users\koray\OneDrive\Masaüstü\SuperLig\Output\{folderName}")
            figure.savefig(f"{figName}")
        
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
        current_date = self.getCurrentDate() #current date al
        self._saveFig(figure = fig, figName = current_date) #figure save
        self._getInfo(fileName = current_date) #path ve figure bilgisi
    
    def TeamRating(self):

        data = self.mergeData() #history data ile bu sezon oynanan maçlardaki dataları birleştirir
        team_data = self.teamStrength(df = data) #takımların güçlerini alırız. Attack, defense.
        team_data = self.attackRank(df = team_data) # takımların attack değerine göre rankını alırız.
        team_data = self.defenseRank(df = team_data) #takmların defense değerine göre rankını alırız.
        team_data = self.eloRank(df = team_data) #takımların elo rating değerlerini ekleriz
        team_rating = self.uptadeRating_(df = data) #takımların spi rating, attack ve defense değerlerinin bize verir.
        team_rating = plot.teamRatingImg(df = team_rating)
        img = plot.plotTeamsRating(df = team_rating)
        
        current_date = self.getCurrentDate()
        self._saveFig(figure = img, figName = current_date)
        self._getInfo(fileName = current_date)


