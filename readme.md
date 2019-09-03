# Moviewatchers Guide for BigCorporation

## Introduction
This project exists to showcase generating an interactive report with Python and Plotly.py; the data used is the MovieLens 1M dataset, 
and the resulting report should not look too out of place in a corporate setting.

## Motivation
Obviously I am trying to get a job, but this was actually a lot of fun and I hope to continue improving on this in the weeks to come; 
I would especially like to work on visualisation clarity and coherence in presentation.

## Technologies
Main relevant tools are
- Python 3.7
- Plotly.py 4.1
- Pandas 0.25.1
the rest can be found in requirements.txt

## Data choices
Since it is not clear what BigCorporation's main industry or field is, and since the task as presented only states that the board has decided that movie reviews are important,
it seems like the first task should be to have a good overview of the basic shape of the data, to know what further insights could be gleaned from it.
The graphs are meant to be very self explanatory; to drive further research questions or to give an indication where to dwelve deeper.
Since corporations are most likely interested in consumers, a lot of space is devoted to describing the user base, and their preferences;
less on the movies themselves.

After the basic dataset description, the report includes five reference tables for the top ten most liked/disliked movies - because everyone loves a crowd pleaser.
This is also a fruitful start for further analysis, because one could see whose reviews are pushing the top movies to the top (for example - the majority of reviewers are male,
so one of the top ten being there mostly through ratings from women would be a great insight, especially if BigCorporation is looking to increase its female consumer base). 

Unfortunately, the time allotted for this project, and the time I could spend on it this week, do not support very in depth analysis.

## Generating the report
Requires python 3.x and libraries specified in `requirements.txt`, which can be installed with:
```pip install -r requirements.txt```

Report is created by executing:
```python main.py```
