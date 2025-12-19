from flask import Flask, render_template, request, redirect, url_for, flash
import json
import os
from datetime import date

app = Flask(__name__)
app.secret_key = 'super_secret_key'

DATA_FILE = os.path.join('data', 'habits.json')

def load_data():
    if not os.path.exists(DATA_FILE):
        return {"habits": []}
    with open(DATA_FILE, 'r') as f:
        return json.load(f)

def save_data(data):
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=4)

@app.route('/')
def index():
    data = load_data()
    today = date.today().isoformat()
    save_data(data)  # Ensures file/folder exists on first visit
    return render_template('index.html', habits=data['habits'], today=today)

@app.route('/add', methods=['GET', 'POST'])
def add_habit():
    data = load_data()
    if request.method == 'POST':
        name = request.form['name'].strip()
        if name and not any(h['name'].lower() == name.lower() for h in data['habits']):
            data['habits'].append({
                "name": name,
                "completed_dates": []
            })
            save_data(data)
            flash('Habit added successfully!', 'success')
            return redirect(url_for('add_habit'))
        else:
            flash('Habit name empty or already exists.', 'danger')
    return render_template('add_habit.html', habits=data['habits'])

@app.route('/progress')
def progress():
    data = load_data()
    today = date.today().isoformat()
    return render_template('progress.html', habits=data['habits'], today=today)

@app.route('/toggle/<int:habit_idx>', methods=['POST'])
def toggle_habit(habit_idx):
    data = load_data()
    today = date.today().isoformat()
    if 0 <= habit_idx < len(data['habits']):
        habit = data['habits'][habit_idx]
        if today in habit['completed_dates']:
            habit['completed_dates'].remove(today)
            flash(f"'{habit['name']}' unmarked for today.", 'info')
        else:
            habit['completed_dates'].append(today)
            flash(f"'{habit['name']}' marked complete for today!", 'success')
        save_data(data)
    return redirect(url_for('progress'))

@app.route('/delete/<int:habit_idx>', methods=['POST'])
def delete_habit(habit_idx):
    data = load_data()
    if 0 <= habit_idx < len(data['habits']):
        removed = data['habits'].pop(habit_idx)
        save_data(data)
        flash(f"Habit '{removed['name']}' deleted.", 'info')
    return redirect(url_for('add_habit'))

if __name__ == '__main__':
    app.run(debug=True)
