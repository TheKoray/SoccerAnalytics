import matplotlib.pyplot as plt 
import matplotlib
import plotly
import plotly.express as px
import kaleido 
import os
from datetime import datetime

path = r"C:\Users\koray\OneDrive\Masaüstü\SuperLig\Output"
pathOutput = r'C:\\Users\\koray\\OneDrive\\Masaüstü\\SuperLig\\süperligAI\TableStatsData'

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
                    'pred' : 'Pred',
                    'GoalsProba' : 'GoalsProba'
                    }
    folderName = "".join([v for k,v in folderCache.items() if figName == k]) #path'deki ilgili figure göre klasör ismini aldık.

    return folderName

def saveFig(figName, figure): #save figure 
    
    folderName = getPlotInfo(figName=figName)
    figDate = getCurrentDate()

    assert isinstance(figure,(plotly.graph_objs._figure.Figure, matplotlib.figure.Figure)), "figure parameter not figure type"

    if isinstance(figure, plotly.graph_objs._figure.Figure):

        figure.write_image(fr"{path}\{folderName}\{folderName}_{figDate}.png")

    else:
        os.chdir(fr"{path}\{folderName}")
        figure.savefig(f"{folderName}_{figDate}")

def getInfo(figName): #give me figure info for folder and path 

    figDate = getCurrentDate()
    folderName = getPlotInfo(figName=figName)

    print(f"{path}\{folderName} klasörüne {folderName}_{figDate} adında kaydedildi")

def isFile(fileName):

    for _,_,file in os.walk(pathOutput):

        if fileName in file:return True
        else: return False