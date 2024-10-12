import os
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

from flask import Flask, redirect, url_for, render_template, request, session, abort, jsonify
from flask_dance.contrib.github import make_github_blueprint, github
from datetime import datetime, timedelta
import math
import json
import re
import markdown

from py_tools import *

app = Flask(__name__)
app.secret_key = env_to_var("FLASK_SECRET_KEY")
github_blueprint = make_github_blueprint(client_id=env_to_var("GITHUB_CLIENT_ID"),
                                         client_secret=env_to_var("GITHUB_CLIENT_SECRET"))

app.register_blueprint(github_blueprint, url_prefix="/login")

ALLOWED_EXTENSIONS = {'pdf'}

@app.route("/")
def index():
    if not github.authorized:
        return render_template("index.html")
    
    resp = github.get("/user")
    assert resp.ok, resp.text
    
    UPLOAD_FOLDER = f'static/PDFS/{resp.json()["login"]}'
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    
    return render_template("calender.html")

@app.route("/login")
def login():
    if not github.authorized:
        return redirect(url_for("github.login"))

    return redirect(url_for("index"))

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return render_template("error.html", message='No file part')
    
    file = request.files['file']
    date_difference = request.form.get('date_difference')
    
    if file.filename == '':
        return render_template("error.html", message='No selected file')
    
    if file and allowed_file(file.filename):
        filename = file.filename
        try:
            striped_filename = filename.replace('.pdf', '')
            striped_filename += f'.{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}'
            
            path = os.path.join(app.config['UPLOAD_FOLDER'], striped_filename, filename)

            os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], striped_filename), exist_ok=True)
            file.save(path)
            
        except:
             return redirect(url_for("index"))
        
        # make parts dir in PDF/parts and save all parts there
        os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], striped_filename, "parts"), exist_ok=True)
        split_pdf(path, os.path.join(app.config['UPLOAD_FOLDER'], striped_filename, "parts", filename), int(date_difference))
        
        cur_date = datetime.now()
        rounded_time = cur_date.replace(hour=0, minute=0, second=0, microsecond=0)
        rounded_time = rounded_time.isoformat()

        dates = []
        for i in range(int(date_difference)):
            dates.append((cur_date.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=i)).isoformat())

        path = os.path.join(app.config['UPLOAD_FOLDER'], striped_filename, "parts")

        files = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
        files = sorted(files, key=lambda f: os.path.getctime(os.path.join(path, f)))
        
        cprint(f"Dates: {len(dates)}", 'grey', attrs=['bold'])
        cprint(f"Files: {len(files)}", 'grey', attrs=['bold'])
        
        dict_dates = {}
        
        for idx, i in enumerate(dates):
            dict_dates[i] = files[idx]
            
        path = os.path.join(app.config['UPLOAD_FOLDER'], striped_filename, "data.json")
        with open(path, 'w') as json_file:
            json.dump(dict_dates, json_file, indent=4)

        
        return redirect(url_for("dashboard"))
    
    return render_template("error.html", message='Invalid file type')

@app.route('/dashboard')
def dashboard():
    try:
        app.config['UPLOAD_FOLDER']
    except:
        return redirect(url_for("index"))
    
    big_data = {}
        
    for file in os.listdir(app.config['UPLOAD_FOLDER']):
        if os.path.isdir(os.path.join(app.config['UPLOAD_FOLDER'], file)):
            with open(os.path.join(app.config['UPLOAD_FOLDER'], file, "data.json"), 'r') as json_file:
                data = json.load(json_file)
                big_data[file] = data
    
    
    cur_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    cur_date = cur_date.isoformat() 
    
    files = []
    cprint(f"Current date: {cur_date}", "green", attrs=['bold'])
    for key, geometry_data in big_data.items():
        for date, filename in geometry_data.items():
            cprint(f"Date: {date}, File: {filename}, key: {key}", "green", attrs=['bold'])
            if cur_date == date:
                files.append((filename, os.path.join(app.config['UPLOAD_FOLDER'], key, "parts", filename).replace("\\", "/"), date))
                cprint(f"Date: {date}, File: {filename}, key: {key}", "green", attrs=['bold'])

    cprint(f"Files: {files}", "green", attrs=['bold'])
    
    # return jsonify(big_data)
    return render_template("dashboard.html", files=files, datetime=datetime)

@app.route('/add_date', methods=['POST'])
def add_date():
    date = request.form.get('date')
    cprint(f'Received date: {date}', 'grey', attrs=['bold'])

    return jsonify({'date': date})



@app.route('/show_data')
def show_data():
    date_str = request.args.get('date')
    date = datetime.strptime(date_str, "%Y-%m-%d")
    
    cur_date = datetime.now()

    date_difference = date - cur_date + timedelta(days=1)
    
    #round down
    date_difference = math.floor(date_difference.total_seconds() / (24 * 3600))
    
    cprint(f"Date difference: {date_difference}", 'grey', attrs=['bold'])

    return render_template("upload.html", date_difference=date_difference)

@app.route('/ai-chat/', methods=['GET', 'POST'])
def ai_chat():
    if request.method == 'POST':
        message = request.form.get('user-input')

        full_path = request.form.get('full-path')
        pdf_text = pdf_read.extract_text_from_pdf(full_path)
        
        prompt = f"The following is an excerpt from a pdf. The user is asking the following question {message}. If the message is asking to generate questions, be sure to include the answer too. But also don't include A), B), C), D), etc. Instead, write question 1,2,3,4, etc and make those bold and a new line. Make the answers formatted like: QUESTION NUMBER - ANSWER: and that should be bolded, but the body shouldn't be bolded and a new line too. Answer this question using the PDF: {pdf_text}"
        
        ai = groq()
        ai_msg = ai.send_message(prompt)
        
        html_text = markdown.markdown(ai_msg)
        
        return render_template("ai_chat.html", path=request.form.get('path'), full_path=full_path, ai_msg=html_text)
    
    path = request.args.get('path')
    full_path = request.args.get('full-path')
    full_path = full_path.replace("static/", "")
    cprint(f"Path: {path}, Full path: {full_path}", 'grey', attrs=['bold'])    
    return render_template("ai_chat.html", path=path, full_path=full_path, ai_msg="")   
    
@app.route('/logout')
def logout():
    session.clear()
    
    return redirect(url_for("index"))

@app.context_processor
def inject_user():
    return dict(is_authenticated=github.authorized)

if __name__ == "__main__":
    app.run(debug=True)