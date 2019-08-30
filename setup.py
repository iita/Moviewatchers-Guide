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
userstatesF = pd.DataFrame(users_tbl[users_tbl.Gender=="F"].State.value_counts())
userstatesM = pd.DataFrame(users_tbl[users_tbl.Gender=="M"].State.value_counts())
states_bar = go.Figure([go.Bar(name="MaleUsers",x=userstatesM.index, y=userstatesM.State),
                        go.Bar(name="FemaleUsers",x=userstatesF.index, y=userstatesF.State)]) 
states_bar.update_layout(barmode='stack')
states_bar.write_html("userStates.html")
webbrowser.open('file://'+ os.path.realpath("userStates.html"))

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
medianrating = pd.DataFrame(ratings_tbl.groupby(by=["Date"]).Rating.median())
stdrating = pd.DataFrame(ratings_tbl.groupby(by=["Date"]).Rating.std())

#%%
trace0 = go.Figure(go.Scatter(name="Number of reviews",
    x=nreviews.index,
    y=nreviews.UserID)
)

trace0.add_trace(go.Scatter(name="Number of unique users"
    x=uniqueusers.index,
    y=uniqueusers.UserID)
)
trace0.add_trace(go.Scatter(name="Number of unique movies"
    x=uniquemovies.index,
    y=uniquemovies.MovieID)
)

trace0.write_html("basicCounts.html")
webbrowser.open('file://'+ os.path.realpath("basicCounts.html"))
#%%

trace1 = go.Figure(go.Scatter(name="Average rating",
    x=avgrating.index,
    y=avgrating.Rating)
)

trace1.add_trace(go.Scatter(name="Median rating",
    x=medianrating.index,
    y=medianrating.Rating))


trace1.add_trace(go.Scatter(name="Standard deviation of rating",
    x=stdrating.index,
    y=stdrating.Rating))
trace1.write_html("RatingOverTime.html")
webbrowser.open('file://'+ os.path.realpath("RatingOverTime.html"))
#%%
nratings = pd.DataFrame(ratings_tbl.groupby("UserID").MovieID.count())
avgRatingsByPerson = nratings.mean()
medianRatingsByPerson = nratings.median()

#%%
genres = ["Action","Adventure","Animation","Children's","Comedy","Crime","Documentary","Drama","Fantasy","Film-Noir","Horror","Musical","Mystery","Romance","Sci-Fi","Thriller","War","Western"]
genre_dict={}
for x in genres:
    genre_dict[x] = {"thisGenre": movies_tbl[movies_tbl.Genres.str.contains(x)].MovieID.count(), "multiGenre":  movies_tbl[movies_tbl.Genres.str.contains(x) & movies_tbl.Genres.str.contains("\|")].MovieID.count() }

#%%
movies_tbl[movies_tbl.Genres.str.contains(x)].MovieID.count()
movies_tbl[movies_tbl.Genres.str.contains("\|")].MovieID.count()

#%%
genres_tbl = pd.DataFrame.from_dict(data=genre_dict, orient="index")
#%%
genresplot = go.Figure(data=[
    go.Bar(name='thisGenre', x=genres_tbl.index, y=genres_tbl.thisGenre),
    go.Bar(name='multiGenre', x=genres_tbl.index, y=genres_tbl.multiGenre)
])

genresplot.update_layout(barmode='group')
genresplot.write_html("genresbars.html")
webbrowser.open('file://'+ os.path.realpath("genresbars.html"))
#%%
movies_ratings = {}
for m in movies_tbl.MovieID:
    if m not in movies_ratings:
        movies_ratings[m] = {"title": movies_tbl[movies_tbl.MovieID==m].Title,"nRated": ratings_tbl[(ratings_tbl.MovieID==m)].Rating.count(),"rate5": ratings_tbl[(ratings_tbl.MovieID==m) & (ratings_tbl.Rating==5)].Rating.count(), "rate1": ratings_tbl[(ratings_tbl.MovieID==m) & (ratings_tbl.Rating==1)].Rating.count(), "avgRating": ratings_tbl[ratings_tbl.MovieID==m].Rating.mean(), "medianRating": ratings_tbl[ratings_tbl.MovieID==m].Rating.median(), "stdRating": ratings_tbl[ratings_tbl.MovieID==m].Rating.std()}

#%%
movieratings_tbl = pd.DataFrame.from_dict(data=movies_ratings, orient="index")

#%%
sameyear = full_tbl[full_tbl.ReleaseYear==full_tbl.Year]
#%%

movieratings_tbl.sort_values(by=["stdRating"], ascending=False, na_position="last")


#%%
movieratings_tbl["percentage5"] = movieratings_tbl.rate5/movieratings_tbl.nRated
movieratings_tbl["percentage1"] = movieratings_tbl.rate1/movieratings_tbl.nRated

#%%
movieratings_tbl[movieratings_tbl.nRated>1000].sort_values(by=["stdRating"], ascending=False, na_position="last").head(10)


#%%
movieratings_tbl.sort_values(by="rate5", ascending=False, na_position="last").head(10)
#movieratings_tbl[movieratings_tbl.nRated>500].sort_values(by="percentage1", ascending=False, na_position="last").head(10)

#%%
new_movies_ratings = {}
for m in sameyear.MovieID:
    if m not in new_movies_ratings:
        new_movies_ratings[m] = {"title": movies_tbl[movies_tbl.MovieID==m].Title,"nRated": sameyear[(sameyear.MovieID==m)].Rating.count(),"rate5": sameyear[(sameyear.MovieID==m) & (sameyear.Rating==5)].Rating.count(), "rate1": sameyear[(sameyear.MovieID==m) & (sameyear.Rating==1)].Rating.count(), "avgRating": sameyear[sameyear.MovieID==m].Rating.mean(), "medianRating": sameyear[sameyear.MovieID==m].Rating.median(), "stdRating": sameyear[sameyear.MovieID==m].Rating.std()}


#%%
new_movieratings_tbl = pd.DataFrame.from_dict(data=new_movies_ratings, orient="index")


#%%
ratings_tbl[ratings_tbl.Rating==5].groupby("MovieID").Rating.count()

#%%
ratings_tbl[ratings_tbl.Rating==5].Rating.count()

#%%
movieratings_tbl.sort_values(by="rate5", ascending=False, na_position="last").head(50).rate5.sum()


#%%


#%%
