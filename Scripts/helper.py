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

        if isinstance(figure, plotly.graph_objs._figure.Figure):

            figure.write_image(fr"{self.path}\{folderName}\{folderName}_{figDate}.png")

        else:
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




