import matplotlib.pyplot as plt 
import matplotlib
import plotly
import plotly.express as px
import kaleido 
import os
from datetime import datetime
from modelHelper import * 

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

        if fileName in file:
            return True
        else: 
            return False

def save(df, statsName):

    statsCache = {"ai": "aiPredict.csv",
                  'poisson' : "poissonPredict.csv",
                  'table' : "tableStats.csv"
                  }
    os.chdir(path = pathOutput)
    df.to_csv(statsCache[statsName])

    print(f" '{statsCache[statsName]}' dosyası '{path}' pathına kaydedildi")

def saveStats(wk):

    modelFunc = modelHelper()
    user_cache = {'ai': modelFunc.predictPipeline,
                  'poisson' : poisson.poissonPredictPipeline,
                  'table' : modelFunc.main}
    
    for key,function in user_cache.items():
         #save fonksiyonun da path değişeceği için her seferinde dictionary içeerisindeki fonksiyonları çalıştıran scriptlerin olduğu pathe gittik
        os.chdir(r'C:\\Users\\koray\\OneDrive\\Masaüstü\\SuperLig\\süperligAI')

        if key  != 'table':
            df = function(wk = wk)
        else:
           df =  function(user = 'Stats')

        save(df = df, statsName = key)