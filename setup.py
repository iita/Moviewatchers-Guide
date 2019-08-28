#%%%
from jupyterthemes import jtplot
from datetime import datetime
from zipfile import ZipFile
from io import BytesIO
import requests as rq
import pandas as pd
import pgeocode as pg 

#%%
jtplot.style("monokai")
#%%

d= rq.get("http://files.grouplens.org/datasets/movielens/ml-1m.zip")
dd = ZipFile(BytesIO(d.content))
dd.extractall("Documents\\MovieLens1M")

users_tbl = pd.read_table("Documents\\MovieLens1M\\ml-1m\\users.dat", sep="::", names=["UserID", "Gender","Age", "Occupation", "ZipCode"], engine="python")
movies_tbl = pd.read_table("Documents\\MovieLens1M\\ml-1m\\movies.dat", sep="::", names=["MovieID", "Title","Genres"], engine="python")
ratings_tbl = pd.read_table("Documents\\MovieLens1M\\ml-1m\\ratings.dat", sep="::", names=["UserID", "MovieID","Rating", "Timestamp"], engine="python")

#%%

def getdatetype(x, datetype):
    if datetype=="year":
        return datetime.fromtimestamp(x).year 
    elif datetype=="month":
        return datetime.fromtimestamp(x).month
    elif datetype=="day":
        return int(datetime.fromtimestamp(x).strftime("%d"))
    elif datetype=="weekday":
        return int(datetime.fromtimestamp(x).strftime("%w"))
    elif datetype=="time":
        return int(datetime.fromtimestamp(x).strftime("%H"))
    

ratings_tbl["Year"] = [getdatetype(row, "year") for row in ratings_tbl.Timestamp]
ratings_tbl["Month"] = [getdatetype(row, "month") for row in ratings_tbl.Timestamp]
ratings_tbl["Day"] = [getdatetype(row, "day") for row in ratings_tbl.Timestamp]
ratings_tbl["Weekday"] = [getdatetype(row, "weekday") for row in ratings_tbl.Timestamp]
ratings_tbl["Time"] = [getdatetype(row, "time") for row in ratings_tbl.Timestamp]
movies_tbl["ReleaseYear"] = [int(row[-5:-1]) for row in movies_tbl.Title]
users_tbl["isFemale"] = [1 if row=="F" else 0 for row in users_tbl.Gender]


#%%
nomi = pg.Nominatim("us")
nomi.query_postal_code(94110).state_name

zip_states = {}
for z in users_tbl.ZipCode:
    if z not in zip_states:
        zip_states[z] = nomi.query_postal_code(z).state_name
#%%
users_tbl["State"] = [zip_states.get(str(row)) for row in users_tbl.ZipCode]

#%%
full_tbl = pd.merge(pd.merge(movies_tbl[["MovieID", "Genres", "ReleaseYear"]], ratings_tbl[["MovieID", "UserID", "Rating", "Year", "Month", "Day", "Weekday", "Time"]], "inner", on="MovieID"), users_tbl[["UserID", "Age", "isFemale", "Occupation", "State"]], "inner", on="UserID") #let's not look at incomplete data since there's very little of it

#%%
cframe = df.corr()
fig = go.Figure(data=go.Heatmap(
                   z=cframe.values,
                   x=cframe.columns.values,
                   y=cframe.index.values))
fig.show()
#%%
