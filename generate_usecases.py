import re
import matplotlib as plt
#
import tkinter as tk
from tkinter import *
from tkinter import ttk

import nltk
import pandas as pd
import networkx as nx
#
from nltk import pos_tag
from nltk import word_tokenize
from nltk.stem import WordNetLemmatizer

# Instantiate tk inter for GUI support
win = Tk()
# Random screen size,enough to show controls
win.geometry("335x300")
frm = ttk.Frame(win)
# Create a grid for easier display of the controls
frm.grid()
the_label = Label(frm, text="Potential Actors in your document for your Use Cases.\n"
                            "Vantage Point: Are these Entities/Concepts in your Domain?\n")
the_label.pack()
ctr = 1
listbox = Listbox(frm, width=50)


# This function outputs list of actors into a CSV file
def show_actors():
    win.title("Listing Actors, please wait...")
    # Using dataframes, open the actors.csv that contains list of well known actors
    df = pd.DataFrame(the_schema)
    df.to_csv("actors.csv", index=False)
    # Open the graph
    G = nx.Graph()
    # Add a root node called System from which the Actors emanate
    G.add_edge("[System]", "", )
    for an_actor in df["actor_token"]:
        G.add_edge("[System]", an_actor)

    # Setup formatting options, tune these to enhance diagram look and feel
    options = {
        "font_size": 6.5,
        "node_size": 700,
        "node_color": "white",
        "edgecolors": "red",
        "linewidths": 0.6,
        "width": 0.5,
    }
    # Draw the network
    nx.draw_networkx(G, **options)
    plt.show()
    #
    return


# This function renders the network of Use Cases
def show_usecase_net():
    win.title("Rendering the Use Case Model, please wait...")
    the_sym_net = nx.Graph()

    # Setup formatting options, tune these to enhance diagram look and feel
    options2 = {
        "font_size": 6.5,
        "node_size": 600,
        "node_color": "grey",
        "edgecolors": "blue",
        "linewidths": 0.6,
        "width": 0.5,
    }
    # Robust requirements are written using the "shall" clause
    for an_item in ret_val:
        # Actor
        the_actor, the_usecase = an_item.split(" shall ")[0], an_item.split(" shall ")[1]
        # Create network node
        the_sym_net.add_edge(the_actor, the_usecase)
    # Draw the use case diagram using networks
    nx.draw_networkx(the_sym_net, **options2)
    #
    return


# This function renders the network of the Actors
def show_actors_net():
    win.title("Rendering the Use Case Model, please wait...")
    the_sym_net2 = nx.Graph()
    for an_item in ret_val:
        # Actor
        the_actor, the_usecase = an_item.split(" shall ")[0], an_item.split(" shall ")[1]
        # Create network node
        the_sym_net2.add_edge(the_actor, the_usecase)
    # Draw the actor diagram using networks
    nx.draw_networkx(the_sym_net2)
    #
    return


# The function searches the candidates for the use cases
def search_using_RegEx(in_text: str, to_find: str):
    # \w+ shall \w+
    # use RegEx to search to find first instance of "commonly called" Actors
    # that are already part of a pre-defined vocabulary
    pattern = re.compile(to_find)
    matches = pattern.finditer(in_text)
    loc_list = []
    for the_found in matches:
        loc_list.append(the_found.group())
    #
    return loc_list


#
# Setup buttons for the tkinter window. Buttons will help show the network diagrams
actor_button = Button(frm, text="Show Actors", relief=tk.RAISED, command=show_actors, width=30)
usecase_button = Button(frm, text="Show Use Cases", relief=tk.RAISED, command=show_usecase_net, width=30)
# Pack the buttons so these are registered
actor_button.pack()
usecase_button.pack()

# open the source requirement specification or business requirement document
# or any other document you use to document the requirements in your organization
text_in_which_to_search = open("clientspecs.txt", "rt").read().lower()
ret_val = search_using_RegEx(text_in_which_to_search, "system shall [^.]*\.")
# system shall [^.]*\.
d = {"Col1": ret_val}
df = pd.DataFrame(d)
df.to_csv("usecases.csv", index=False)
# Clean the text. Ideally use a stopword approach for extensibility
# for now this will suffice to make the point
interim_text = text_in_which_to_search. \
    replace("\n", " ").replace("\xa0", " ").replace("\t", " ").replace(".", " ")
unique_interim_text = set(interim_text.split(" ")).__str__().replace("'", "").replace(",", ""). \
    replace(">", ""). \
    replace("<", "")

# We fill find Proper nouns,  Personal pronouns and Possessive pronouns
# Generate tokens that are potential candidate Actors
tagged_text = pos_tag(word_tokenize(unique_interim_text))

# Lemmatize to simplify the variations of words and reach the root form
the_lemmatizer = WordNetLemmatizer()
# open the actor file as dataframe
# this file contains the strings that are proven actors in the software world
# you can add more nouns to this file if you know the actors in your domain and want
# them found pre-emptively
df_actors = pd.read_csv("sb_actor_tags.csv")
actor_token = []
actor_true_false = []
# this dictionary will help generate dataframe quickly and easily
the_schema = {"actor_token": actor_token, "actor_yes_no": actor_true_false}

# iterate and search in the document
for the_key in df_actors["actor_tag"]:
    # use RegEx to search to find first instance of commonly "called" Actors
    # that are already part of a pre-defined vocabulary
    pattern = re.compile(the_key)
    matches = pattern.finditer(unique_interim_text)
    for found in matches:
        if len(the_key) > 2:
            actor_token.append(the_key.title())
            listbox.insert(ctr, "Known Actor: " + the_key.title())
            actor_true_false.append(True)
            # break right after instance of a potential actor is found
            # if you want to find all instances, remove break but that would duplicate
            break

# Look for all nouns and pronouns. These 'Things' tend to be Actors!
for t in tagged_text:
    # Use a loop though you can use smaller lambda functions
    if t[1] == "NN" or t[1] == "NNS" \
            or t[1] == "NNP" or t[1] == "NNPS" \
            or t[1] == "PRP" or t[1] == "PRP$":
        # Lemmatize to reduce variations and to go the root word
        potential_actor = the_lemmatizer.lemmatize(t[0])
        # ignore two character strings
        # you can use stopwords if you want to reduce invalid data
        if len(potential_actor) > 2:
            actor_token.append(potential_actor)
            actor_true_false.append(True)
            listbox.insert(ctr, "Additional Actor: " + potential_actor.title())
            #
            ctr += 1
listbox.configure(borderwidth=3)
listbox.pack()

# Statistically the Actors that appear the most are central to the system
# so pay special attention to these
# I use Frequency Distribution to sample the top 20, just random number
# you can choose to increase or decrease this number depending on this length of your document
fd = nltk.FreqDist(samples=actor_token)
top20 = fd.most_common(20)
for most_common in top20:
    ctr += 1
    listbox.insert(ctr, "Prominent Actor: " + str.title(most_common[0]))

# Start the tkinter message loop for event processing
win.mainloop()
