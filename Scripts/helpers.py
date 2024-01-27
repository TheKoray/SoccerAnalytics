import matplotlib.pyplot as plt 
import matplotlib
import plotly
import plotly.express as px
import kaleido 
import os
from datetime import datetime

<<<<<<< HEAD
TODO = "get table fonksiyonunda teamRatingImg fonksiyonu hata veriyor. getPlot classına ait fonskiyon olduğu için selfde hata veriyor."

path = r"C:\Users\koray\OneDrive\Masaüstü\SuperLig\Output"
=======
path = r"--yourPath--"
>>>>>>> ee92c72f7f06829f52cab3597d473d0d44333161

def getCurrentDate():

    """
    get current date
    Return: string current date
    """
    date = datetime.now()
    return "-".join(str(dt) for dt in [date.day,date.month,date.year])

def getPlotInfo(figName): #grafiğe göre klasör ismi döndürür.

    folderCache = {'WeeklyChange' : 'weeklyChange',
                    'TeamRating': 'TeamRating',
                    'pred' : 'Pred'
                    }
    folderName = "".join([v for k,v in folderCache.items() if figName == k]) #path'deki ilgili figure göre klasör ismini aldık.

    return folderName

def saveFig(figName, figure): #plotu kaydeder
    
    folderName = getPlotInfo(figName=figName)
    figDate = getCurrentDate()

    assert isinstance(figure,(plotly.graph_objs._figure.Figure, matplotlib.figure.Figure)), "figure parameter not figure type"

    if isinstance(figure, plotly.graph_objs._figure.Figure):

        figure.write_image(fr"{path}\{folderName}\{folderName}_{figDate}.png")

    else:
        os.chdir(fr"{path}\{folderName}")
        figure.savefig(f"{folderName}_{figDate}")

def getInfo(figName):

    figDate = getCurrentDate()
    folderName = getPlotInfo(figName=figName)

    print(f"{path}\{folderName} klasörüne {folderName}_{figDate} adında kaydedildi")
<<<<<<< HEAD
=======

"""
def getTable(self):

    play_df = self.getNewData(played = True) #bu sezon sadece oynanan maçları alıyoruz.
    elo_df = self.updateElo(df = play_df) 
    data_avg = self.teamTable(df = elo_df)
    elo_change_df = self.teamRatingImg(df = data_avg)

    return elo_change_df.drop('Img', axis=1)"""
>>>>>>> ee92c72f7f06829f52cab3597d473d0d44333161
