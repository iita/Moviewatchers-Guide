#%%%
from jupyterthemes import jtplot
from datetime import datetime
from zipfile import ZipFile
from io import BytesIO
import requests as rq
import pandas as pd
import pgeocode as pg 
import plotly.graph_objs as go
import webbrowser
import os 

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
    elif datetype=="date":
        return datetime.fromtimestamp(x).strftime("%Y-%m-%d")
    

ratings_tbl["Year"] = [getdatetype(row, "year") for row in ratings_tbl.Timestamp]
ratings_tbl["Month"] = [getdatetype(row, "month") for row in ratings_tbl.Timestamp]
ratings_tbl["Day"] = [getdatetype(row, "day") for row in ratings_tbl.Timestamp]
ratings_tbl["Weekday"] = [getdatetype(row, "weekday") for row in ratings_tbl.Timestamp]
ratings_tbl["Time"] = [getdatetype(row, "time") for row in ratings_tbl.Timestamp]
ratings_tbl["Date"] = [getdatetype(row, "date") for row in ratings_tbl.Timestamp]
movies_tbl["ReleaseYear"] = [int(row[-5:-1]) for row in movies_tbl.Title]
users_tbl["isFemale"] = [1 if row=="F" else 0 for row in users_tbl.Gender]

#%%
users_tbl["AgeRange"] = users_tbl.Age
users_tbl.loc[users_tbl['Age'] ==1, ["AgeRange"]] = "0to17"
users_tbl.loc[users_tbl['Age'] ==18, ["AgeRange"]] = "18to24"
users_tbl.loc[users_tbl['Age'] ==25, ["AgeRange"]] = "25to34"
users_tbl.loc[users_tbl['Age'] ==35, ["AgeRange"]] = "35to44"
users_tbl.loc[users_tbl['Age'] ==45, ["AgeRange"]] = "45to49"
users_tbl.loc[users_tbl['Age'] ==50, ["AgeRange"]] = "50to55"
users_tbl.loc[users_tbl['Age'] ==56, ["AgeRange"]] = "56+"


#%%
nomi = pg.Nominatim("us")

zip_states = {}
for z in users_tbl.ZipCode:
    if z not in zip_states:
        zip_states[z] = nomi.query_postal_code(z).state_name
#%%
users_tbl["State"] = [zip_states.get(str(row)) for row in users_tbl.ZipCode]

#%%
full_tbl = pd.merge(pd.merge(movies_tbl[["MovieID", "Genres", "ReleaseYear"]], ratings_tbl[["MovieID", "UserID", "Rating", "Year", "Month", "Day", "Weekday", "Time"]], "inner", on="MovieID"), users_tbl[["UserID", "Age", "isFemale", "Occupation", "State"]], "inner", on="UserID") #let's not look at incomplete data since there's very little of it

#%%
cframe = full_tbl.corr()
fig = go.Figure(data=go.Heatmap(
                   z=cframe.values,
                   x=cframe.columns.values,
                   y=cframe.index.values))
fig.show()
fig.write_html("helloworld.html")
#%%

#%%
webbrowser.open('file://'+ os.path.realpath("helloworld.html"))

#%%
femaleusers = pd.DataFrame(users_tbl[users_tbl.Gender=="F"].AgeRange.value_counts()).sort_index()
maleusers = pd.DataFrame(users_tbl[users_tbl.Gender=="M"].AgeRange.value_counts()).sort_index()
#%%
userages = go.Figure(data=[
    go.Bar(name='Men', x=maleusers.index, y=maleusers.AgeRange),
    go.Bar(name='Women', x=femaleusers.index, y=femaleusers.AgeRange)
])
# Change the bar mode
userages.update_layout(barmode='group')
userages.write_html("userages.html")

#%%
uniqueusers = pd.DataFrame(ratings_tbl.groupby(by=["Date"]).UserID.nunique())
uniquemovies = pd.DataFrame(ratings_tbl.groupby(by=["Date"]).MovieID.nunique())
nreviews = pd.DataFrame(ratings_tbl.groupby(by=["Date"]).UserID.count())
avgrating = pd.DataFrame(ratings_tbl.groupby(by=["Date"]).Rating.mean())

#%%
trace0 = go.Figure(go.Scatter(
    x=nreviews.index,
    y=nreviews.UserID)
)

trace0.add_trace(go.Scatter(
    x=uniqueusers.index,
    y=uniqueusers.UserID)
)
trace0.add_trace(go.Scatter(
    x=uniquemovies.index,
    y=uniquemovies.MovieID)
)

trace0.write_html("basicCounts.html")
webbrowser.open('file://'+ os.path.realpath("basicCounts.html"))
#%%

trace1 = go.Figure(go.Scatter(
    x=avgrating.index,
    y=avgrating.Rating)
)
trace1.write_html("avgRatingOverTime.html")
webbrowser.open('file://'+ os.path.realpath("avgRatingOverTime.html"))
#%%
nratings = pd.DataFrame(ratings_tbl.groupby("UserID").MovieID.count())
avgRatingsByPerson = nratings.mean()
medianRatingsByPerson = nratings.median()

#%%
genres = ["Action","Adventure","Animation","Children's","Comedy","Crime","Documentary","Drama","Fantasy","Film-Noir","Horror","Musical","Mystery","Romance","Sci-Fi","Thriller","War","Western"]
genre_count={}
for x in genres:
    genre_count[x] = movies_tbl[movies_tbl.Genres.str.contains(x)].MovieID.count()

#%%
movies_tbl[movies_tbl.Genres.str.contains(x)].MovieID.count()
movies_tbl[movies_tbl.Genres.str.contains("\|")].MovieID.count()
#%%
multigenre_count={}
for x in genres:
    multigenre_count[x] = movies_tbl[movies_tbl.Genres.str.contains(x) & movies_tbl.Genres.str.contains("\|")].MovieID.count()

#%%
genres_tbl1 = pd.DataFrame.from_dict(data=genre_count, orient="index")
genres_tbl2 = pd.DataFrame.from_dict(data=multigenre_count, orient="index")
#%%
genres_tbl1["Genre"] = genres_tbl1.index
genres_tbl2["Genre"] = genres_tbl2.index
genres_tbl = pd.merge(genres_tbl1, genres_tbl2, on="Genre")
#%%
genres_tbl.columns = ["includesGenre", "Genre", "multiGenre"]
#%%
genresplot = go.Figure(data=[
    go.Bar(name='thisGenre', x=genres_tbl.Genre, y=genres_tbl.includesGenre),
    go.Bar(name='multiGenre', x=genres_tbl.Genre, y=genres_tbl.multiGenre)
])

genresplot.update_layout(barmode='group')
genresplot.write_html("genresbars.html")
webbrowser.open('file://'+ os.path.realpath("genresbars.html"))
#%%
