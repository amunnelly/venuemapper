import pandas as pd
import folium
from folium.plugins import MarkerCluster
import numpy as np

class VenueMaker(object):

    def __init__(self, fixtures):
        self.df = pd.read_csv('data/fixtures.csv')
        self.fix_dates()
        self.match_locations()
        self.create_map()


    def fix_dates(self):
        gamedate = []
        for a, b in self.df.iterrows():
            gamedate.append(" ".join([b['date'], b['time']]))
        self.df['gamedate'] = gamedate
        self.df['gamedate'] = pd.to_datetime(self.df['gamedate'])
        self.df.drop(['date', 'time'], axis=1, inplace=True)


    def match_locations(self):
        grounds = pd.read_csv('data/mayo_gaa_grounds.csv')
        grounds = grounds.to_dict('records')
        lat, long = [], []
        for a, b in self.df.iterrows():
            checker = True
            for g in grounds:
                if b['venue'] in (g['venue'], g['ground'], g['club']):
                    lat.append(g['lat'])
                    long.append(g['long'])
                    checker = False
                    break
            if checker:
                lat.append(None)
                long.append(None)
                print(b['venue'])
        self.df['lat'] = lat
        self.df['long'] = long


    def tooltip_creator(self, d):
        venue = "".join(["<b>", d['venue'], "</b>"])
        match = "".join([d['teamA'], " v ", d['teamB']])
        time = d['gamedate'].strftime('%a') + " " + d['gamedate'].strftime("%H:%M")
        details = "".join([d['level'], " ", str(d['stage'])])
        return "<br>".join([venue, match, time, details])


    def create_table(self):
        gamedates = self.df.gamedate.value_counts()
        gamedates = pd.DataFrame(gamedates)
        gamedates.reset_index(inplace=True)
        gamedates.sort_values('index', inplace=True)
        # gamedates
        df3 = pd.pivot_table(self.df, index='gamedate', columns='category', values='stage', aggfunc=lambda x: len(x))
        df3.fillna(0, inplace=True)
        df3 = df3.astype(int)
        df3.reset_index(inplace=True)
        # df3
        df3['gamedate'] = df3.gamedate.apply(lambda x: x.strftime('%a, %H:%M'))
        # df3


    def create_map(self):
        colors = {"Senior": "darkred",
                    "Intermediate": "red",
                    "Junior": "lightred",
                    "Junior B": "lightred"}

        self.m = folium.Map(location=[self.df.lat.mean(), self.df.long.mean()],
                zoom_start=9,
                control_scale=True)

        senior_group = folium.FeatureGroup(name='senior')
        intermediate_group = folium.FeatureGroup(name='intermediate')
        junior_group = folium.FeatureGroup(name='junior')

        senior_cluster = MarkerCluster()
        intermediate_cluster = MarkerCluster()
        junior_cluster = MarkerCluster()

        for a, b in self.df.iterrows():
            marker = folium.Marker([b['lat'], b['long']],
                                tooltip = self.tooltip_creator(b),
                                icon=folium.Icon(color=colors[b['level']]))
            if b['level'] == 'Senior':
                senior_cluster.add_child(marker)
            elif b['level'] == 'Intermediate':
                intermediate_cluster.add_child(marker)
            else:
                junior_cluster.add_child(marker)

        senior_group.add_child(senior_cluster)
        intermediate_group.add_child(intermediate_cluster)
        junior_group.add_child(junior_cluster)

        self.m.add_child(senior_group)
        self.m.add_child(intermediate_group)
        self.m.add_child(junior_group)

        self.m.add_child(folium.LayerControl())

        self.m.save('maps/fixtures.html')
        
        


if __name__ == "__main__":
    x = VenueMaker('data/fixtures.csv')