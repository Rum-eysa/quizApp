from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os


app = Flask(__name__)
app.secret_key = os.urandom(24)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"]= False

db=SQLAlchemy(app)
migrate = Migrate(app, db)

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.Text, nullable=False) 
    option1 = db.Column(db.Text, nullable=False)
    option2 = db.Column(db.Text, nullable=False)
    option3 = db.Column(db.Text, nullable=False)
    option4 = db.Column(db.Text, nullable=False)  

    correct_option = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f"<Question {self.question}>"
    
    def get_correct_option(self):
       options = {
            1: self.option1,
            2: self.option2,
            3: self.option3,
            4: self.option4
        }
       return options.get(self.correct_option)
   
class Score(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    correct_count = db.Column(db.Integer, nullable=False)
    total_score = db.Column(db.Float, nullable=False)
       
    def __repr__(self):
        return f"<Score {self.total_score}>"


def add_questions():
        Question.query.delete()
        
        q1 = Question(
            question="Which algorithm type is used for detecting an object in an image?",
            option1="Text processing algorithms",
            option2="Object detection algorithms",
            option3="Speech recognition algorithms",
            option4="Graphic design algorithms",
            correct_option=2
        )
        q2 = Question(
            question="What is Convolutional Neural Networks (CNN) commonly used for in computer vision?",
            option1="Speech analysis",
            option2="Text prediction",
            option3="Image classification",
            option4="Data encryption",
            correct_option=3
        )
        q3 = Question(
            question="What is 'edge detection' used for in computer vision?",
            option1="Determining the shapes of objects",
            option2="Changing colors",
            option3="Speeding up videos",
            option4="Making text clearer",
            correct_option=1
        )
    
        q4 = Question(
            question="Which machine learning technique is used for classifying objects in an image?",
            option1="Decision trees",
            option2="Support vector machines",
            option3="Artificial neural networks",
            option4="Logistic regression",
            correct_option=3
        )
        q5 = Question(
            question="Which dataset is used for recognizing handwritten digits in computer vision?",
            option1="CIFAR-10",
            option2="ImageNet",
            option3="MNIST",
            option4="COCO",
            correct_option=3
        )

        db.session.add(q1)
        db.session.add(q2)
        db.session.add(q3)
        db.session.add(q4)
        db.session.add(q5)
        db.session.commit()
        
@app.route('/')
def quiz():
   
    questions_list = Question.query.all()
    highest_score = Score.query.order_by(Score.total_score.desc()).first()
    return render_template("quiz.html", questions_list = questions_list, highest_score=highest_score)

@app.route("/submitquiz", methods=['POST','GET'])
def submit():
    correct_count = 0
    
    questions_list = Question.query.all()
    total_questions = len(questions_list)
    
    for question in questions_list:
        question_id = str(question.id)  
        selected_option = request.form.get(question_id)  
        
        
        
        if selected_option is not None:  
                selected_option = int(selected_option)  
                correct_option = question.correct_option

        if selected_option == correct_option:
            correct_count += 1
        else:
           
            print(f"Question ID {question_id} not found in form data")
        
    score = (correct_count / total_questions) * 100
    
    highest_score = Score.query.order_by(Score.total_score.desc()).first()


    if highest_score and score > highest_score.total_score:
        highest_score.correct_count = correct_count
        highest_score.total_score = score
        db.session.commit()
    elif not highest_score:
        new_score = Score(correct_count=correct_count, total_score=score)
        db.session.add(new_score)
        db.session.commit()
    highest_score = Score.query.order_by(Score.total_score.desc()).first()

    result_message = f"Congrats! {correct_count} you answered the question correctly. Your score: {score:.2f}%"
    highest_score_message = f"Best score: {highest_score.total_score:.2f}% " if highest_score else "There is no score yet."

    
    return render_template("result.html", result_message=result_message ,highest_score_message=highest_score_message)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        add_questions()
    app.run(debug=True)

