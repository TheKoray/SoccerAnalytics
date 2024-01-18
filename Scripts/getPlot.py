import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from plottable import ColumnDefinition, Table
from plottable.plots import circled_image # image
from matplotlib.colors import LinearSegmentedColormap
from plottable.cmap import normed_cmap
import plotly.express as px
from plottable.formatters import decimal_to_percent
from plottable.plots import circled_image # image
import matplotlib
import matplotlib.patches as patches

class getPlot:

    def imgAdd(self,result_df):
        """
        Haftalık sonuçların bulunduğu dataya takımların logolarını ekler.
        - Home ve Away kolonunda ki takımların isimlerinin takımların logoları ile değişir.
        """
        team_img = pd.read_csv("tff_team_img.csv")
        
        for idx, col in result_df.iterrows():
            for i,j in team_img.iterrows():
                if col['Home'] == j['Home']:
                    result_df.loc[idx,'HomeImg'] = j['Img']
                if col['Away'] == j['Away']:
                    result_df.loc[idx,'AwayImg'] = j['Img']
        return result_df.reindex(['HomeImg','Home','Home_Prob','Draw','Away_Prob','Away','AwayImg'],
                                 axis=1)
    
    def teamRatingImg(self,df):
        
        """
        Takmıların attack , defense ve spi ratinglerin bulunduğu datadaki indexde bulunan takım isimlerini tkaımların logoları ile değiştiri.
        """
        df_img = pd.read_csv("tff_team_img.csv")
        df_img.drop('Unnamed: 0', axis=1, inplace = True)

        for i in df.index:
            for k,v in df_img.iterrows():
                if i == v['Home']:
                    df.loc[i,'Img'] = v['Img']

        #return df.reset_index().set_index('Img')
        return df
    
    def weeklyProbPlot(self,df):

        fig, ax = plt.subplots(figsize=(20, 10))
        col_defs = (
            [   ColumnDefinition(
                    name="HomeImg",
                    title="",
                    textprops={"ha": "center"},
                    width=0.5,
                    plot_fn=circled_image
                ),
                ColumnDefinition(
                    name="AwayImg",
                    title="",
                    textprops={"ha": "center"},
                    width=0.5,
                    plot_fn=circled_image
                ),
                ColumnDefinition(
                    name="Home",
                    title="",
                    textprops={"ha": "center",'weight':'bold'},
                    width=0.7 #yazıların (takım isimleri) boyutunu ayarlar.
                ),
                ColumnDefinition(
                    name="Away",
                    title="",
                    textprops={"ha": "center","weight":"bold"},
                    width=0.7
                ),
                ColumnDefinition(
                    name="Home_Prob",
                    textprops={"ha": "center", 'weight':'bold'},
                    width=1.5,
                    cmap=normed_cmap(df['Home_Prob'], cmap=matplotlib.cm.PiYG, num_stds=3)
                ),
                ColumnDefinition(
                    name="Draw",
                    textprops={"ha": "center", "weight": "bold"},
                    width=1.5,
                    cmap=normed_cmap(df['Draw'], cmap=matplotlib.cm.PiYG, num_stds=3)
                ),
                ColumnDefinition(
                    name="Away_Prob",
                    textprops={"ha": "center", "weight":"bold"},
                    width=1.5,
                    cmap=normed_cmap(df['Away_Prob'], cmap=matplotlib.cm.PiYG, num_stds=3)
                ),
                    ColumnDefinition(
                    name="index",
                    title = "",
                    textprops = ""
                    )]
        )
        tab = Table(df,row_dividers= True ,
                    column_definitions = col_defs,
                    row_divider_kw={"linewidth": 1, "linestyle": (0, (1, 5))})

        plt.show()

    def plotTeamsRating(self,df):
        
        df = df.reindex(['Img','Rating','Attack','Defense'], axis=1)
        fig, ax = plt.subplots(figsize=(9, 16))
        col_defs = ([
                    ColumnDefinition(
                        name="Img",
                        title="",
                        textprops={"ha": "center"},
                        width=0.5,
                        plot_fn=circled_image
                    ),
                    ColumnDefinition(
                        name="Team",
                        title="",
                        textprops={"ha": "center",'weight':'bold'},
                        width=0.5
                    ),
                    ColumnDefinition(
                        name = 'Rating',
                        textprops = {'weight':'bold',
                        "bbox": {"boxstyle": "circle", "pad": 0.35}},
                        cmap=normed_cmap(df['Rating'], cmap=matplotlib.cm.PiYG, num_stds=2.5)),
                    ColumnDefinition(
                        name = 'Attack',
                        width = 0.75,
                        textprops = {'weight':'bold',
                        "bbox": {"boxstyle": "circle", "pad": 0.35}},
                        cmap=normed_cmap(df['Attack'], cmap=matplotlib.cm.PiYG, num_stds=2.5)),
                    ColumnDefinition(
                        name = 'Defense',
                        width = 0.75,
                        textprops = {'weight':'bold',
                        "bbox": {"boxstyle": "circle", "pad": 0.35}},
                        cmap=normed_cmap(df['Defense'], cmap=matplotlib.cm.PiYG_r, num_stds=2.5)),
                    ColumnDefinition(
                        name = 'Team',
                        textprops = {'weight':'bold'}
                    )
        ])
        tab = Table(df, column_definitions = col_defs).autoset_fontcolors(colnames = ['Rating'])
        plt.show()
        return fig

    def getTablePlot(self,df):
        
        df = df.reindex(['Img','OM','W','D','L','AG','YG','AV','Point','MBP',
                         'WeeklyChange','Change','Form'], axis=1)
        
        fig, ax = plt.subplots(figsize=(21, 18))

        row_colors = {
            "top2": "#82b7f5",
            "top4": "#fadba2",
            "playoffs": "#8d9386",
            "relegation": "#fa7769",
            "even": "#627979",
            "odd": "#68817e",
        }

        form_text = {"W":"#43e815", "D":"#e3d14b", "L":"#f54633"}

        bg_color = row_colors["odd"]
        text_color = "#111212"
        plt.rcParams["text.color"] = text_color
        #plt.rcParams["font.family"] = "Roboto"
        fig.set_facecolor(bg_color)
        #ax.set_facecolor(bg_color)
        col_defs = ([
                    ColumnDefinition(
                        name="Img",
                        title="",
                        textprops={"ha": "center"},
                        width=0.65,
                        plot_fn=circled_image
                    ),
                    ColumnDefinition(
                        name="Team",
                        title="",
                        textprops={"fontsize":12,"ha": "center",'weight':'bold'},
                        width=0.65
                    ),
                    ColumnDefinition(
                        name="OM",
                        textprops={"ha": "right",'weight':'bold'},
                        width=0.5
                    ),
                    ColumnDefinition(
                        name="W",
                        textprops={"ha": "right",'weight':'bold',
                                   "bbox": {"boxstyle": "circle", "pad": 0.8}},
                        width=0.5,
                        cmap=normed_cmap(df['W'], cmap=matplotlib.cm.PiYG, num_stds=3)
                    ),
                    ColumnDefinition(
                        name="D",
                        textprops={"ha": "right",'weight':'bold',
                                    "bbox": {"boxstyle": "circle", "pad": 0.8}},
                        width=0.5,
                        cmap=normed_cmap(df['D'], cmap=matplotlib.cm.PiYG_r, num_stds=3)
                    ),
                    ColumnDefinition(
                        name="L",
                        textprops={"ha": "right",'weight':'bold',
                                    "bbox": {"boxstyle": "circle", "pad": 0.8}},
                        width=0.5,
                        cmap=normed_cmap(df['L'], cmap=matplotlib.cm.PiYG_r, num_stds=3)
                    ),
                    ColumnDefinition(
                        name="MBP",
                        textprops={"ha": "right",'weight':'bold',
                                    "bbox": {"boxstyle": "circle", "pad": 0.8}},
                        width=0.5,
                        cmap=normed_cmap(df['MBP'], cmap=matplotlib.cm.PiYG, num_stds=3)
                    ),
                    ColumnDefinition(
                        name = 'AG',
                        width = 0.75,
                        textprops = {'weight':'bold',
                        "bbox": {"boxstyle": "circle", "pad": 0.8}},
                        cmap=normed_cmap(df['AG'], cmap=matplotlib.cm.PiYG, num_stds=3)),
                        ColumnDefinition(
                        name="Form",
                        textprops={"fontsize":12,"ha": "center",'weight':'bold'},
                        width=0.5
                    ),
                    ColumnDefinition(
                        name = 'YG',
                        width = 0.75,
                        textprops = {'weight':'bold',
                        "bbox": {"boxstyle": "circle", "pad": 0.8}},
                        cmap=normed_cmap(df['YG'], cmap=matplotlib.cm.PiYG_r, num_stds=3)),
                    ColumnDefinition(
                        name = 'AV',
                        width = 0.75,
                        textprops = {'weight':'bold',
                        "bbox": {"boxstyle": "circle", "pad": 0.8}},
                        cmap=normed_cmap(df['AV'], cmap=matplotlib.cm.PiYG, num_stds=3)),
                    ColumnDefinition(
                        name = 'Point',
                        width = 0.75,
                        textprops = {'weight':'bold',
                        "bbox": {"boxstyle": "circle", "pad": 0.8}},
                        cmap = normed_cmap(df['Point'], cmap = matplotlib.cm.Greens, num_stds=2.5)),
                    ColumnDefinition(
                        name = 'WeeklyChange',
                        textprops = {'weight':'bold',
                        "bbox": {"boxstyle": "circle", "pad": 0.35}},
                        cmap = normed_cmap(df['WeeklyChange'], cmap = matplotlib.cm.PiYG, num_stds=2.5)),
                    ColumnDefinition(
                        name = 'Change',
                        textprops = {'weight':'bold',
                        "bbox": {"boxstyle": "circle", "pad": 0.35}},
                        cmap = normed_cmap(df['Change'], cmap = matplotlib.cm.PiYG, num_stds=2.5)),
                    ])
        table = Table(df, 
                    column_definitions = col_defs,
                    row_dividers = True,
                    footer_divider = True,
                    textprops={"ha": "center","weight":"bold"},
                    row_divider_kw={"linewidth": 1, "linestyle": (0, (1, 5))},
                    ax = ax).autoset_fontcolors(colnames=["AG","YG","AV","Point"])

        for idx in [0, 1]:
            table.rows[idx].set_facecolor(row_colors["top2"]) #ilk 2 satır boyadık
            
        for idx in [2,3]:
            table.rows[idx].set_facecolor(row_colors["top4"]) #3. ve 4. satır boyadık
            
        for idx in [17,18,19]:
            table.rows[idx].set_facecolor(row_colors["relegation"]) # son 3 satır boyadık

        plt.show()
        fig.savefig("puan_tablosu")
        return fig 
    
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
    
    def TeamRating(self):

        data = self.mergeData() #history data ile bu sezon oynanan maçlardaki dataları birleştirir
        team_data = self.teamStrength(df = data) #takımların güçlerini alırız. Attack, defense.
        team_data = self.attackRank(df = team_data) # takımların attack değerine göre rankını alırız.
        team_data = self.defenseRank(df = team_data) #takmların defense değerine göre rankını alırız.
        team_data = self.eloRank(df = team_data) #takımların elo rating değerlerini ekleriz
        team_rating = self.uptadeRating_(df = data) #takımların spi rating, attack ve defense değerlerinin bize verir.
        team_rating = self.teamRatingImg(df = team_rating)
        img = self.plotTeamsRating(df = team_rating)
        
        self._saveFig(figure = img, figName = "TeamRating")
        self._getInfo(figName = "TeamRating")