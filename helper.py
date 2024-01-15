from soccerMetric import * 
from getPlot import *
import plotly.express as px
import kaleido 
import os
from datetime import datetime
plot = getPlot()

class helper(soccerMetric):

    @staticmethod
    def getCurrentDate():

        date = datetime.now()
        return "-".join(str(dt) for dt in [date.day,date.month,date.year])
    
    def _getInfo(self, fileName):

        return f"WeeklyChange görseli weeklyChange klasörü içerisinde wkChange{fileName} adı ile kaydedildi."
    
    def _saveFig(self, figure,figName):

        figure.write_image(fr"C:\Users\UserName\Masaüstü\SuperLeague\Output\weeklyChange\wkChange{figName}.png")
        
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
        
        #fig.write_image(fr"C:\Users\koray\OneDrive\Masaüstü\SuperLig\Output\weeklyChange\wkChange{current_date}.png")
        #print(f"WeeklyChange görseli weeklyChange klasörü içerisinde wkChange{current_date} adı ile kaydedildi.")

    
    def mainRatingImg(self):

        data = self.mergeData() #history data ile bu sezon oynanan maçlardaki dataları birleştirir
        team_data = self.teamStrength(df = data) #takımların güçlerini alırız. Attack, defense.
        team_data = self.attackRank(df = team_data) # takımların attack değerine göre rankını alırız.
        team_data = self.defenseRank(df = team_data) #takmların defense değerine göre rankını alırız.
        team_data = self.eloRank(df = team_data) #takımların elo rating değerlerini ekleriz
        team_rating = self.uptadeRating_(df = data) #takımların spi rating, attack ve defense değerlerinin bize verir.
        team_rating = plot.teamRatingImg(df = team_rating)
        img = plot.plotTeamsRating(df = team_rating)

        #img.savefig(f"{imgName}.png")
        #info = f"{imgName}.png, dosyası {os.getcwd()} klasörüne kaydedildi"
        #print(info)

