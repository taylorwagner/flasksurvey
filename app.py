from flask import Flask, request, render_template, redirect, flash, session, make_response
from surveys import surveys
from flask_debugtoolbar import DebugToolbarExtension


app = Flask(__name__)
app.config['SECRET_KEY'] = "survey"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

debug = DebugToolbarExtension(app)

CURRENT_SURVEY_KEY = "curr_survey"
RES_KEY = "responses"


@app.route('/')
def survey_choice():
    """Selecting a survey"""

    return render_template("choice.html", surveys=surveys)


@app.route('/', methods=["POST"])
def chosen_survey():

    survey_id = request.form['survey_code']

    #cannot take survey again until cookies times out
    if request.cookies.get(f"completed_{survey_id}"):
        return render_template("already-done.html")

    survey = surveys[survey_id]
    session[CURRENT_SURVEY_KEY] = survey_id
    
    return render_template("index.html", survey=survey)


@app.route("/questions", methods=["POST"])
def start():
    """Clear the responses"""

    session[RES_KEY] = []

    return redirect("/questions/0")


@app.route("/answer", methods=["POST"])
def handle_q():
    """Save response and redirect to next question"""

    #get response choice
    choice = request.form['answer']
    text = request.form.get("text", "")

    #append responses to the list in the session
    res = session[RES_KEY]
    res.append({"choice": choice, "text": text})

    #append response to the session
    session[RES_KEY] = res
    survey_code = session[CURRENT_SURVEY_KEY]
    survey = surveys[survey_code]
    
    if(len(res) == len(survey.questions)):
        #finished survey, answered all the questions -- need to thank
        return redirect("/complete")

    else:
        return redirect(f"/questions/{len(res)}")


@app.route('/questions/<int:q>')
def questions_page(q):
    """Display the current question"""
    responses = session.get(RES_KEY)
    survey_code = session[CURRENT_SURVEY_KEY]
    survey = surveys[survey_code]

    if(responses is None):
        #accessing questions page before selecting survey
        return redirect("/")

    if(len(responses) == len(survey.questions)):
        #answered all of the questions -- need to thank
        return redirect("/complete")
    
    if(len(responses) != q):
        #answering questions out of order
        flash(f"Invalid question id: {q}!")
        return redirect(f"/questions/{len(responses)}")

    question = survey.questions[q]

    return render_template("questions.html", question_num=q, question=question)


@app.route("/complete")
def finished():
    """Finished survey. Show "thank you" message with a list of the responses from survey"""

    survey_id = session[CURRENT_SURVEY_KEY]
    survey = surveys[survey_id]
    res = session[RES_KEY]

    html = render_template("completion.html", survey=survey, res=res)

    #set the cookie so that survey is completed thus cannot be completed again

    res = make_response(html)
    res.set_cookie(f"completed_{survey_id}", "yes", max_age=60)
    return res