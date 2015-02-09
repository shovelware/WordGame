from flask import Flask, render_template, url_for, request, redirect, session
from threading import Thread
import wordgamemain as game

app = Flask(__name__)

###Pages###
"""Home page, displays rules and play button"""
@app.route("/")
def display_pregame():
    return render_template("wgpregame.html",
                            playgame_url = url_for("display_playgame"),
                            score_url = url_for("display_scores"),
			    )

"""Gameplay page, shows source and takes guesses"""
@app.route("/play")
def display_playgame():
	#get a source word
	session["source_word"] = game.get_source()
	#take a game start timestamp
	session["time_started"] = game.get_timestamp()
	return render_template("wgplaygame.html",
                            source_word = session.get("source_word", "errored"),
				            submit_url = url_for("submit_guesses"),
                            )

"""Postgame page, displays errors and score, takes name"""
@app.route('/post')
def display_postgame():
        #process words
	session["words_scored"] = game.calc_score(session.get("guesses"), session.get("error_dict"), session.get("source_word"), session.get("total_time"))
	session["total_score"] = game.total_score(session.get("words_scored"))
	return render_template("wgpostgame.html",
				pregame_url = url_for("display_pregame"),
				total_time = round(session.get("total_time"), 2),
				submit_url = url_for("submit_name"),
				words_scored = game.dict_to_string(session.get("words_scored")),
				total_score = session.get("total_score"),
				)

"""Hiscore page, displays scores"""
@app.route('/scores')
def display_scores():
    return render_template("wgscores.html",
                           pregame_url = url_for("display_pregame"),
                           score_text = game.get_top_ten(),
                           )

"""Error page, for when the user really messes up"""
@app.route("/error")
def display_error():
    return render_template("wgerror.html",
                            pregame_url = url_for("display_pregame"),
                            error_text = game.dict_to_string(session.get("error_dict")),
                            )

###Form stuff###
"""Runs when guesses are submitted, redirects to postgame"""
@app.route('/submitguesses', methods=["POST"])
def submit_guesses():
        #take in words as string and process them
        session["guesses"] = game.string_to_list(request.form["guesses"])

        #check against source, store errors
        session["error_dict"] = game.test_guesses(session.get("source_word"), session.get("guesses"))

        #if we have no errors, finish the game
        if session.get("error_dict") == {}: #paul not sure if this test for equality works
            #get a game finish timestamp
            session["time_finished"] = game.get_timestamp()
            #calculate the time taken from timestamps
            session["total_time"] = game.calc_timetaken(session.get("time_started"), session.get("time_finished"))
            #add a var to ensure you can't double score
            session["game_complete"] = True
            return redirect(url_for("display_postgame"))

        #but if we do, chuck us out
        else:
            return redirect(url_for("display_error"))

"""Runs when name is submitted, redirects to scores"""
@app.route('/submitname', methods=["POST"])
def submit_name():
    #disable double scoring
    if session.get("game_complete") == True:
        session["name"] = request.form["name"]
        #Make sure there's a name, any name
        if session.get("name") == "":
            session["name"] = "anon"

        t = Thread(target = save_score, args = (session.get("name"), session.get("total_score")))
        t.start()

    session["game_complete"] = False

    return redirect(url_for("display_scores"))

def save_score(name, score):
    game.save_score(name, score)

app.config["SECRET_KEY"] = "Whocares"
app.run(debug = True)
