from flask import Flask, request, render_template, redirect, flash, session
from surveys import satisfaction_survey as survey
from flask_debugtoolbar import DebugToolbarExtension


app = Flask(__name__)
app.config['SECRET_KEY'] = "survey"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

debug = DebugToolbarExtension(app)


RES_KEY = "responses"


@app.route('/')
def index():
    """Selecting a survey"""

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

    #include response to session
    res = session[RES_KEY]
    res.append(choice)
    session[RES_KEY] = res
    
    if(len(res) == len(survey.questions)):
        #finished survey, answered all the questions -- need to thank
        return redirect("/complete")

    else:
        return redirect(f"/questions/{len(res)}")


@app.route('/questions/<int:q>')
def questions_page(q):
    """Display the current question"""
    responses = session.get(RES_KEY)

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
    """Finished survey. Show "thank you" message"""

    return render_template("completion.html")