#%%%
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
#%%
# Creating the necessary folders for this
BASEPATH = os.path.abspath('')
DATADIR = os.path.join(BASEPATH, '.data')

REPORTDIR = os.path.join(BASEPATH, 'reports')

# For extracting useful dates from epoch
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


def generate_report(filename: str='report.html', open_browser: bool=False):
    if not os.path.exists(DATADIR):
        os.makedirs(DATADIR)
    if not os.path.exists(REPORTDIR):
            os.makedirs(REPORTDIR)
	# Fetching the actual data as a .zip file
    blob = rq.get("http://files.grouplens.org/datasets/movielens/ml-1m.zip")
    zip_file = ZipFile(BytesIO(blob.content))
    zip_file.extractall(DATADIR)

	#%%
	# Reading in the three data tables
    os.path.join(DATADIR, 'ml-1m', 'users.dat')
    users_tbl = pd.read_table(os.path.join(DATADIR, 'ml-1m', 'users.dat'), sep="::", names=["UserID", "Gender","Age", "Occupation", "ZipCode"], engine="python")
    movies_tbl = pd.read_table(os.path.join(DATADIR, 'ml-1m', 'movies.dat'), sep="::", names=["MovieID", "Title","Genres"], engine="python")
    ratings_tbl = pd.read_table(os.path.join(DATADIR, 'ml-1m', 'ratings.dat'), sep="::", names=["UserID", "MovieID","Rating", "Timestamp"], engine="python")

	#%%

    ratings_tbl["Year"] = [getdatetype(row, "year") for row in ratings_tbl.Timestamp]
    ratings_tbl["Month"] = [getdatetype(row, "month") for row in ratings_tbl.Timestamp]
    ratings_tbl["Day"] = [getdatetype(row, "day") for row in ratings_tbl.Timestamp]
    ratings_tbl["Weekday"] = [getdatetype(row, "weekday") for row in ratings_tbl.Timestamp]
    ratings_tbl["Time"] = [getdatetype(row, "time") for row in ratings_tbl.Timestamp]
    ratings_tbl["Date"] = [getdatetype(row, "date") for row in ratings_tbl.Timestamp]
	# Noticed that "Title" also includes release year, that seems relevant
    movies_tbl["ReleaseYear"] = [int(row[-5:-1]) for row in movies_tbl.Title]

	#%%
	# Clarifying age ranges - "Age==1" was pretty worrisome for a bit
    users_tbl["AgeRange"] = users_tbl.Age
    users_tbl.loc[users_tbl['Age'] ==1, ["AgeRange"]] = "0to17"
    users_tbl.loc[users_tbl['Age'] ==18, ["AgeRange"]] = "18to24"
    users_tbl.loc[users_tbl['Age'] ==25, ["AgeRange"]] = "25to34"
    users_tbl.loc[users_tbl['Age'] ==35, ["AgeRange"]] = "35to44"
    users_tbl.loc[users_tbl['Age'] ==45, ["AgeRange"]] = "45to49"
    users_tbl.loc[users_tbl['Age'] ==50, ["AgeRange"]] = "50to55"
    users_tbl.loc[users_tbl['Age'] ==56, ["AgeRange"]] = "56+"
	#%%
	# No one reads a separate table for group name references so let's put them in the graph
    occupation_names={0:  "other or not specified",
    1:  "academic/educator",
    2:  "artist",
    3:  "clerical/admin",
    4:  "college/grad student",
    5:  "customer service",
    6:  "doctor/health care",
    7:  "executive/managerial",
    8:  "farmer",
    9:  "homemaker",
    10:  "K-12 student",
    11:  "lawyer",
    12:  "programmer",
    13:  "retired",
    14:  "sales/marketing",
    15:  "scientist",
    16:  "self-employed",
    17:  "technician/engineer",
    18:  "tradesman/craftsman",
    19:  "unemployed",
    20:  "writer",}
    users_tbl["OccupationName"] = [occupation_names.get(row) for row in users_tbl.Occupation]

	#%%
    nomi = pg.Nominatim("us")
	# I should fix this into one dict but no time right now, so since there's no use for state_name atm, let's just hide that
	#    zip_states = {}
	#    for z in users_tbl.ZipCode:
	#        if z not in zip_states:
	#            zip_states[z] = nomi.query_postal_code(z).state_name

    zip_statecodes = {}
    for z in users_tbl.ZipCode:
        if z not in zip_statecodes:
            zip_statecodes[z] = nomi.query_postal_code(z).state_code
	#%%
  #  users_tbl["State"] = [zip_states.get(str(row)) for row in users_tbl.ZipCode]
    users_tbl["StateCode"] = [zip_statecodes.get(str(row)) for row in users_tbl.ZipCode]
	#%%
	# Might re-include later but not necessary at the moment
    #   userstatesF = pd.DataFrame(users_tbl[users_tbl.Gender=="F"].State.value_counts())
    #   userstatesM = pd.DataFrame(users_tbl[users_tbl.Gender=="M"].State.value_counts())
    #   states_bar = go.Figure([go.Bar(name="MaleUsers",x=userstatesM.index, y=userstatesM.State),
    #                           go.Bar(name="FemaleUsers",x=userstatesF.index, y=userstatesF.State)]) 
    #   states_bar.update_layout(barmode='stack')
    #   states_bar.write_html("html_files/userStates.html")
    #   #webbrowser.open('file://'+ os.path.realpath("html_files/userStates.html"))

	#%%
	# In case you want to group by ALL THE THINGS
    full_tbl = pd.merge(pd.merge(movies_tbl[["MovieID", "Genres", "ReleaseYear"]], 
    ratings_tbl[["MovieID", "UserID", "Rating", "Year", "Month", "Day", "Weekday", "Time"]], "inner", on="MovieID"), 
    users_tbl[["UserID", "Age", "Gender", "Occupation", "StateCode"]], "inner", on="UserID") #let's not look at incomplete data since there's very little of it

	#%%
	# red for girls, blue for boys, because we all need our easy visual shorthand
    femaleusers = pd.DataFrame(users_tbl[users_tbl.Gender=="F"].AgeRange.value_counts()).sort_index()
    maleusers = pd.DataFrame(users_tbl[users_tbl.Gender=="M"].AgeRange.value_counts()).sort_index()
	#%%
    userages = go.Figure(data=[
        go.Bar(name='Men', x=maleusers.index, y=maleusers.AgeRange),
        go.Bar(name='Women', x=femaleusers.index, y=femaleusers.AgeRange)
    ])
    # Change the bar mode
    userages.update_layout(barmode='group')
    userages.write_html("html_files/userages.html")
    ages_url = 'file:///'+ os.path.realpath("html_files/userages.html")
	#%%
	# For graphing changes in basic values over time
    uniqueusers = pd.DataFrame(ratings_tbl.groupby(by=["Date"]).UserID.nunique())
    uniquemovies = pd.DataFrame(ratings_tbl.groupby(by=["Date"]).MovieID.nunique())
    nreviews = pd.DataFrame(ratings_tbl.groupby(by=["Date"]).UserID.count())
    avgrating = pd.DataFrame(ratings_tbl.groupby(by=["Date"]).Rating.mean())
    medianrating = pd.DataFrame(ratings_tbl.groupby(by=["Date"]).Rating.median())
    stdrating = pd.DataFrame(ratings_tbl.groupby(by=["Date"]).Rating.std())
	#%%
    n_users = users_tbl.UserID.count()
    n_movies = movies_tbl.MovieID.count()
    n_reviews = pd.merge(ratings_tbl, movies_tbl, "inner", on="MovieID").Rating.count()
 
	#%%
	# Plotting review count, user count, and movie count for trend graphing
    reviewsGraph = go.Figure(go.Scatter(name="Number of reviews",
        x=nreviews.index,
        y=nreviews.UserID)
    )

    reviewsGraph.add_trace(go.Scatter(name="Number of unique users",
        x=uniqueusers.index,
        y=uniqueusers.UserID)
    )
    reviewsGraph.add_trace(go.Scatter(name="Number of unique movies",
        x=uniquemovies.index,
        y=uniquemovies.MovieID)
    )

    reviewsGraph.write_html("html_files/reviewsGraph.html")
    #webbrowser.open('file://'+ os.path.realpath("html_files/basicCounts.html"))
    reviewsG_url = 'file:///'+ os.path.realpath("html_files/reviewsGraph.html")


	#%%
	# Should rename the traces but currently out of creativity
	# Plotting rating over time
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
    trace1.write_html("html_files/RatingOverTime.html")
    #webbrowser.open('file://'+ os.path.realpath("html_files/RatingOverTime.html"))
    ratingsG_url = 'file:///'+ os.path.realpath("html_files/RatingOverTime.html")
	#%%
	# Did not end up using this but I think it could be interesting
    #   nratings = pd.DataFrame(ratings_tbl.groupby("UserID").MovieID.count())
    #   avgRatingsByPerson = nratings.mean()
    #   medianRatingsByPerson = nratings.median()

	#%%
	# Eventually: onlyThisGenre
    genres = ["Action",
    "Adventure",
    "Animation",
    "Children's",
    "Comedy",
    "Crime",
    "Documentary",
    "Drama",
    "Fantasy",
    "Film-Noir",
    "Horror",
    "Musical",
    "Mystery",
    "Romance",
    "Sci-Fi",
    "Thriller",
    "War",
    "Western"]
    genre_dict={}
    for x in genres:
        genre_dict[x] = {"thisGenre": movies_tbl[movies_tbl.Genres.str.contains(x)].MovieID.count(),
         "multiGenre":  movies_tbl[movies_tbl.Genres.str.contains(x) & movies_tbl.Genres.str.contains("\|")].MovieID.count(),
         "nRatings": full_tbl[full_tbl.Genres.str.contains(x)].Rating.count(),
        "meanRatings": full_tbl[full_tbl.Genres.str.contains(x)].Rating.mean() }


	#%%
    genres_tbl = pd.DataFrame.from_dict(data=genre_dict, orient="index")
	#%%
	# Bar graphs for genre; number of movies per genre, having that genre at all, and having that genre + at least one more
    genresplot = go.Figure(data=[
        go.Bar(name='thisGenre', x=genres_tbl.index, y=genres_tbl.thisGenre/n_movies),
        go.Bar(name='multiGenre', x=genres_tbl.index, y=genres_tbl.multiGenre/n_movies)
    ])
	# Same for ratings
    genreratingsplot =  go.Figure(data=[
        go.Bar(name='percentage of all ratings', x=genres_tbl.index, y=genres_tbl.nRatings/n_reviews),
        go.Bar(name='median rating', x=genres_tbl.index, y=genres_tbl.meanRatings)
    ])

    genresplot.update_layout(barmode='group')
    genresplot.write_html("html_files/genresbars.html")
    genreratingsplot.write_html("html_files/genreratingsbars.html")
    #webbrowser.open('file://'+ os.path.realpath("html_files/genresbars.html"))
    genres_url = 'file:///'+ os.path.realpath("html_files/genresbars.html")
    genreratings_url = 'file:///'+ os.path.realpath("html_files/genreratingsbars.html")
	#%%
	# For creating a table with ratings-related values per movie
    movies_ratings = {}
    for m in movies_tbl.MovieID:
        if m not in movies_ratings:
            movies_ratings[m] = {"title": movies_tbl[movies_tbl.MovieID==m].Title,
            "nRated": ratings_tbl[(ratings_tbl.MovieID==m)].Rating.count(),
            "rate5": ratings_tbl[(ratings_tbl.MovieID==m) & (ratings_tbl.Rating==5)].Rating.count(),
             "rate1": ratings_tbl[(ratings_tbl.MovieID==m) & (ratings_tbl.Rating==1)].Rating.count(),
             "avgRating": ratings_tbl[ratings_tbl.MovieID==m].Rating.mean(),
              "medianRating": ratings_tbl[ratings_tbl.MovieID==m].Rating.median(),
               "stdRating": ratings_tbl[ratings_tbl.MovieID==m].Rating.std()}

	#%%
    movieratings_tbl = pd.DataFrame.from_dict(data=movies_ratings, orient="index")

	#%%
	# I assume BigCorporation cares about trendsetters and new movies
    sameyear = full_tbl[full_tbl.ReleaseYear==full_tbl.Year]

	#%%
	# Percentage of reviews being 5 (==best) and 1 (==worst)
    movieratings_tbl["percentage5"] = movieratings_tbl.rate5/movieratings_tbl.nRated
    movieratings_tbl["percentage1"] = movieratings_tbl.rate1/movieratings_tbl.nRated


	#%%
    new_movies_ratings = {}
    for m in sameyear.MovieID:
        if m not in new_movies_ratings:
            new_movies_ratings[m] = {"title": movies_tbl[movies_tbl.MovieID==m].Title,
            "nRated": sameyear[(sameyear.MovieID==m)].Rating.count(),
            "rate5": sameyear[(sameyear.MovieID==m) & (sameyear.Rating==5)].Rating.count(),
             "rate1": sameyear[(sameyear.MovieID==m) & (sameyear.Rating==1)].Rating.count(),
              "avgRating": sameyear[sameyear.MovieID==m].Rating.mean(),
              "medianRating": sameyear[sameyear.MovieID==m].Rating.median(),
              "stdRating": sameyear[sameyear.MovieID==m].Rating.std()}


	#%%
    new_movieratings_tbl = pd.DataFrame.from_dict(data=new_movies_ratings, orient="index")
	#%%
	# For plotting how many times a rating was given; not really surprising but kinda necessary
    rates = pd.DataFrame(ratings_tbl.Rating.value_counts())
	#%%
    newrates = pd.DataFrame(full_tbl[full_tbl.ReleaseYear==full_tbl.Year])
    nnewrates = newrates.Rating.count()


	#%%
    ratingsplot = go.Figure(data=[
        go.Bar(name="All movies",
        x=rates.index,
        y=rates.Rating/n_reviews),
        go.Bar(name="New movies",
        x=pd.DataFrame(newrates.Rating.value_counts()).index,
        y=pd.DataFrame(newrates.Rating.value_counts()).Rating/nnewrates)
    ])
	# Bar graph with number of ratings, as percentage of all ratings
    ratingsplot.update_layout(barmode='group')
    ratingsplot.write_html("html_files/ratingsplot.html")
    ratingsplot_url = 'file:///'+ os.path.realpath("html_files/ratingsplot.html")

	#%%
	# Using the occupation names!
    femaleoccupations = pd.DataFrame(users_tbl[users_tbl.Gender=="F"].OccupationName.value_counts()).sort_index()
    maleoccupations = pd.DataFrame(users_tbl[users_tbl.Gender=="M"].OccupationName.value_counts()).sort_index()
    useroccupations = go.Figure(data=[
        go.Bar(name='Men', x=maleoccupations.index, y=maleoccupations.OccupationName),
        go.Bar(name='Women', x=femaleoccupations.index, y=femaleoccupations.OccupationName)
    ])
    # Change the bar mode
    useroccupations.update_layout(barmode='group')
    useroccupations.write_html("html_files/useroccupations.html")
    #webbrowser.open('file://'+ os.path.realpath("html_files/useroccupations.html"))
    occupations_url = 'file:///'+ os.path.realpath("html_files/useroccupations.html")
	#%%
	# All relevant major corporations are American so let's give them a map of the states, corporations love maps
    statecounts = pd.DataFrame(users_tbl.StateCode.value_counts())
    statereviews = pd.merge(ratings_tbl[["Rating", "UserID", "Date"]], users_tbl[["UserID", "StateCode"]], on="UserID")

	#%%
    fig1 = go.Figure(data=go.Choropleth(
        locations=statecounts.index, # Spatial coordinates
        z = statecounts['StateCode'].astype(float), # Data to be color-coded
        locationmode = 'USA-states', # set of locations match entries in `locations`
        colorscale = 'Reds',
        colorbar_title = "Number of people",
    ))

    fig1.update_layout(
        title_text = 'Total unique users per state',
        geo_scope='usa', # limite map scope to USA
    )

    fig1.write_html("html_files/userschloropleth.html")
    #webbrowser.open('file://'+ os.path.realpath("userschloropleth.html"))
    usersmap_url = 'file:///'+ os.path.realpath("userschloropleth.html")
	#%%
	# Did not end up using any of this so commenting out for performance; might be interesting later
	#    reviewstd = pd.DataFrame(statereviews.groupby("StateCode").Rating.std())
	#
	##%%
	#    reviewcounts = pd.DataFrame(statereviews.groupby("StateCode").Rating.count())
	#
	##%%
	#
	#    fig2 = go.Figure(data=go.Choropleth(
	#        locations=reviewcounts.index, # Spatial coordinates
	#        z = reviewcounts['Rating'].astype(float)/1000, # Data to be color-coded
	#        locationmode = 'USA-states', # set of locations match entries in `locations`
	#        colorscale = 'Reds',
	#        colorbar_title = "Thousand reviews",
	#    ))
	#
	#    fig2.update_layout(
	#        title_text = 'Number of unique reviews per state',
	#        geo_scope='usa', # limite map scope to USA
	#    )
	#
	#    fig2.write_html("html_files/reviewschloropleth.html")
	#    #webbrowser.open('file://'+ os.path.realpath("html_files/reviewschloropleth.html"))
	#    reviews_url = 'file:///'+ os.path.realpath("reviewschloropleth.html")
	##%%
	#
	#    fig4 = go.Figure(data=go.Choropleth(
	#        locations=reviewstd.index, # Spatial coordinates
	#        z = reviewstd['Rating'].astype(float), # Data to be color-coded
	#        locationmode = 'USA-states', # set of locations match entries in `locations`
	#        colorscale = 'Reds',
	#        colorbar_title = "Standard deviation of reviews",
	#    ))
	#
	#    fig4.update_layout(
	#        title_text = 'Deviation in reviews per state',
	#        geo_scope='usa', # limite map scope to USA
	#    )
	#
	#    fig4.write_html("html_files/ratingsDchloropleth.html")
	#    #webbrowser.open('file://'+ os.path.realpath("html_files/ratingsDchloropleth.html"))
	#    ratingsDev_url = 'file:///'+ os.path.realpath("ratingsDchloropleth.html")
	#

	#%%
    reviewavg = pd.DataFrame(statereviews.groupby("StateCode").Rating.mean())
	#%%

    fig3 = go.Figure(data=go.Choropleth(
        locations=reviewavg.index, # Spatial coordinates
        z = reviewavg['Rating'].astype(float), # Data to be color-coded
        locationmode = 'USA-states', # set of locations match entries in `locations`
        colorscale = 'Greens',
        colorbar_title = "Average rating of reviews",
    ))

    fig3.update_layout(
        title_text = 'Average reviews per state',
        geo_scope='usa', # limite map scope to USA
    )

    fig3.write_html("html_files/ratingschloropleth.html")
    #webbrowser.open('file://'+ os.path.realpath("html_files/ratingschloropleth.html"))
    ratingsAvg_url = 'file:///'+ os.path.realpath("html_files/ratingschloropleth.html")
	#%%
    toprate = pd.DataFrame(movieratings_tbl.sort_values(by="rate5", ascending=False, na_position="last").head(10))
    bottomrate = pd.DataFrame(movieratings_tbl.sort_values(by="rate1", ascending=False, na_position="last").head(10))
	#%%
	# Tables look professional so let's add some, though I did name the columns pretty badly
    summary_table_1 = toprate
    summary_table_1 = summary_table_1\
        .to_html()\
        .replace('<table border="1" class="dataframe">','<table class="table table-striped">')
    #%%
    summary_table_2 = bottomrate
    summary_table_2 = summary_table_2\
        .to_html()\
        .replace('<table border="1" class="dataframe">','<table class="table table-striped">')
	#%%
    summary_table_3 = new_movieratings_tbl.sort_values("nRated", ascending=False, na_position="last").head(10)
    summary_table_3 = summary_table_3\
        .to_html()\
        .replace('<table border="1" class="dataframe">','<table class="table table-striped">')
	#%%
    summary_table_4 = new_movieratings_tbl.sort_values("rate5", ascending=False, na_position="last").head(10)
    summary_table_4 = summary_table_4\
        .to_html()\
        .replace('<table border="1" class="dataframe">','<table class="table table-striped">')
	#%%
    summary_table_5 = new_movieratings_tbl.sort_values("rate1", ascending=False, na_position="last").head(10)
    summary_table_5 = summary_table_5\
        .to_html()\
        .replace('<table border="1" class="dataframe">','<table class="table table-striped">')
	#%%
	#%%
    #I swear I looked into it and iframe is really the recommended option, outside of Dash.
    html_string = '''
    <html>
        <head>
            <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.1/css/bootstrap.min.css">
            <style>body{{ margin:0 100; background:whitesmoke; }}</style>
        </head>
        <body>
            <h1>BigCorporation review of historical movie ratings</h1>

            <!-- *** Section 1 *** --->
            <h2>Section 1: The Data</h2>
            <h3>Section 1.1: Basics</h3>
            <ul>
                <li>Total number of reviews {nreviews}</li>
                <li>Total number of users {nusers}</li>
                <li>Total number of movies {nmovies}</li>
            </ul>
            <h3>Section 1.2: Users</h3>
            <iframe width="1000" height="550" frameborder="0" seamless="seamless" scrolling="no" \
    src="{usersmap}"></iframe>
            <p>Unsurprisingly, many of the users are from the most populous states.</p>
            <p>The top 5 most populous states in the US:</p>
            <ol>
                <li>California</li>
                <li>Texas</li>
                <li>Florida</li>
                <li>New York</li>
                <li>Pennsylvania</li>
            </ol>
            <h4>Number of unique active users per day</h4>
            <iframe width="1000" height="550" frameborder="0" seamless="seamless" scrolling="no" \
    src="{reviewsG}"></iframe>
            <p>Since most users were active in early 2000, it is important to note that the data may be biased.</p>
            <h4>User base by age and gender</h4>
            <iframe width="1000" height="550" frameborder="0" seamless="seamless" scrolling="no" \
    src="{ages}"></iframe>
            <h4>User base by occupation and gender</h4>
            <iframe width="1000" height="550" frameborder="0" seamless="seamless" scrolling="no" \
            src="{occupations}"></iframe>
            <h3>Section 1.3: Movies</h3>
            <h4>Movies by genre</h4>
            <iframe width="1000" height="550" frameborder="0" seamless="seamless" scrolling="no" \
            src="{genres}"></iframe>
            <h3>Section 1.4: Ratings</h3>
            <h4>Distribution of ratings</h4>
            <iframe width="1000" height="550" frameborder="0" seamless="seamless" scrolling="no" \
            src="{ratingsplot}"></iframe>
            <h4>Ratings over time</h4>
            <iframe width="1000" height="550" frameborder="0" seamless="seamless" scrolling="no" \
            src="{ratingG}"></iframe>
            <h4>Ratings based on state</h4>
            <iframe width="1000" height="550" frameborder="0" seamless="seamless" scrolling="no" \
            src="{ratingsAvg}"></iframe>
            <h4>Ratings based on genre; distribution across genres and average rating per genre</h4>
            <iframe width="1000" height="550" frameborder="0" seamless="seamless" scrolling="no" \
            src="{genreratings}"></iframe>
            <!-- *** Section 2 *** --->
            <h2>Section 2: Top movies per category</h2>
            <h3>Section 2.1: All time</h3>
            <h4>Top 10 most rated at 5</h4>
            {summary1}
            <h4>Top 10 most rated at 1</h4>
            {summary2}
            <h3>Section 2.2: New movies</h3>
            <h4>Top 10 most rated new movies</h4>
            {summary3}
            <h4>Top 10 most liked new movies</h4>
            {summary4}
            <h4>Top 10 most disliked new movies</h4>
            {summary5}


        </body>
    </html>'''.format(nreviews=str(n_reviews), 
    nusers=str(n_users), 
    nmovies=str(n_movies), 
    usersmap=usersmap_url, 
    reviewsG=reviewsG_url, 
    ages=ages_url,
    occupations=occupations_url, 
    genres=genres_url, 
    genreratings=genreratings_url,
    ratingsplot=ratingsplot_url,
    ratingG=ratingsG_url, 
    ratingsAvg=ratingsAvg_url, 
    summary1=summary_table_1, 
    summary2=summary_table_2, 
    summary3=summary_table_3, 
    summary4=summary_table_4, 
    summary5= summary_table_5)

	#%%
    f = open(filename,'w')
    f.write(html_string)
    f.close()

	#%%
    if open_browser:
        webbrowser.open('file://'+ os.path.realpath(filename))

	#%%
if __name__ == '__main__':
    generate_report('report.html', open_browser=True)