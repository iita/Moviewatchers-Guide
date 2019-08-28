from zipfile import ZipFile
from io import BytesIO
import requests as rq
import pandas as pd
import plotly as py
import plotly.graph_objs as go
import chart_studio.plotly as csp

d= rq.get("http://files.grouplens.org/datasets/movielens/ml-1m.zip")
dd = ZipFile(BytesIO(d.content))
dd.extractall("Documents\\MovieLens1M")

users_tbl = pd.read_table("Documents\\MovieLens1M\\ml-1m\\users.dat", sep="::", names=["UserID", "Gender","Age", "Occupation", "ZipCode"], engine="python")
movies_tbl = pd.read_table("Documents\\MovieLens1M\\ml-1m\\movies.dat", sep="::", names=["MovieID", "Title","Genres"], engine="python")
ratings_tbl = pd.read_table("Documents\\MovieLens1M\\ml-1m\\ratings.dat", sep="::", names=["UserID", "MovieID","Rating", "Timestamp"], engine="python")

users_tbl.describe()
movies_tbl.describe()
ratings_tbl.head()

full_tbl = pd.merge(pd.merge(movies_tbl, ratings_tbl, "outer", on="MovieID"), users_tbl, "outer", on="UserID")
