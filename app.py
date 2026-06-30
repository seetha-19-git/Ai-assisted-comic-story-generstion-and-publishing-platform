import os
import sqlite3
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.utils import secure_filename
import fitz
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
# In a real app, use a secure random key. For MVP, this is fine.
app.secret_key = 'super_secret_kids_comic_library_key'

UPLOAD_FOLDER = os.path.join('static', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

DATABASE = 'database.db'

# --- DATABASE SETUP ---
def get_db_connection():
    conn = sqlite3.connect(DATABASE, detect_types=sqlite3.PARSE_DECLTYPES)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    # Create users table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            role TEXT NOT NULL
        )
    ''')
    
    # Create stories table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS stories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            moral TEXT NOT NULL,
            theme TEXT NOT NULL,
            age INTEGER NOT NULL,
            character TEXT NOT NULL,
            content TEXT NOT NULL,
            status TEXT NOT NULL,
            file_path TEXT,
            is_upload INTEGER DEFAULT 0,
            extracted_text TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Insert default users if they don't exist
    admin_check = conn.execute('SELECT * FROM users WHERE username = ?', ('admin',)).fetchone()
    if not admin_check:
        conn.execute('INSERT INTO users (username, password, role) VALUES (?, ?, ?)', 
                     ('admin', 'admin123', 'admin'))
        
    parent_check = conn.execute('SELECT * FROM users WHERE username = ?', ('parent',)).fetchone()
    if not parent_check:
        conn.execute('INSERT INTO users (username, password, role) VALUES (?, ?, ?)', 
                     ('parent', 'parent123', 'parent'))
        
    conn.commit()
    conn.close()

# Initialize DB on startup
with app.app_context():
    init_db()

# --- AI INTEGRATION ---
def generate_story_with_ai(theme, moral, character, age):
    api_key = os.environ.get('GEMINI_API_KEY')
    if not api_key or api_key == 'your_actual_key_here':
        return "Error: Gemini API key not configured. Please add it to your .env file."
        
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        prompt = (
            f"Write a short children's comic story for a {age}-year-old. "
            f"The main character is a {character}. "
            f"The theme is {theme}. "
            f"The moral lesson is {moral}. "
            f"The story should be fun, simple, engaging, and end with a clear moral. "
            f"Format the story in short paragraphs. Each paragraph describes one comic panel. "
            f"Include what the illustration would show at the start of each panel description in brackets, e.g. [Illustration: ...]"
        )
        
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error generating story: {str(e)}"

# --- PUBLIC ROUTES ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

# --- PARENT ROUTES ---
@app.route('/parent/login', methods=['GET', 'POST'])
def parent_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ? AND password = ? AND role = ?', 
                            (username, password, 'parent')).fetchone()
        conn.close()
        
        if user:
            session['username'] = user['username']
            session['role'] = user['role']
            return redirect(url_for('parent_dashboard'))
        else:
            flash('Invalid username or password. Please try again.', 'danger')
            
    return render_template('parent_login.html')

@app.route('/parent/dashboard')
def parent_dashboard():
    if session.get('role') != 'parent':
        return redirect(url_for('parent_login'))
        
    moral_filter = request.args.get('moral', 'All')
    theme_filter = request.args.get('theme', 'All')
    age_filter = request.args.get('age', 'All')
    
    query = 'SELECT * FROM stories WHERE status = "published"'
    params = []
    
    if moral_filter != 'All':
        query += ' AND moral = ?'
        params.append(moral_filter)
    if theme_filter != 'All':
        query += ' AND theme = ?'
        params.append(theme_filter)
    if age_filter != 'All':
        query += ' AND age = ?'
        params.append(age_filter)
        
    query += ' ORDER BY created_at DESC'
    
    conn = get_db_connection()
    stories = conn.execute(query, params).fetchall()
    conn.close()
    
    return render_template('parent_dashboard.html', 
                           stories=stories,
                           current_moral=moral_filter,
                           current_theme=theme_filter,
                           current_age=age_filter)

@app.route('/parent/story/<int:story_id>')
def read_story(story_id):
    if session.get('role') != 'parent':
        return redirect(url_for('parent_login'))
        
    conn = get_db_connection()
    story = conn.execute('SELECT * FROM stories WHERE id = ? AND status = "published"', (story_id,)).fetchone()
    conn.close()
    
    if not story:
        flash('Story not found or not published.', 'danger')
        return redirect(url_for('parent_dashboard'))
        
    return render_template('read_story.html', story=story)

# --- ADMIN ROUTES ---
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ? AND password = ? AND role = ?', 
                            (username, password, 'admin')).fetchone()
        conn.close()
        
        if user:
            session['username'] = user['username']
            session['role'] = user['role']
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid username or password. Please try again.', 'danger')
            
    return render_template('admin_login.html')

@app.route('/admin/dashboard')
def admin_dashboard():
    if session.get('role') != 'admin':
        return redirect(url_for('admin_login'))
        
    conn = get_db_connection()
    drafts = conn.execute('SELECT * FROM stories WHERE status = "draft" ORDER BY created_at DESC').fetchall()
    published = conn.execute('SELECT * FROM stories WHERE status = "published" ORDER BY created_at DESC').fetchall()
    conn.close()
    
    return render_template('admin_dashboard.html', drafts=drafts, published=published)

@app.route('/admin/generate', methods=['GET', 'POST'])
def generate_story():
    if session.get('role') != 'admin':
        return redirect(url_for('admin_login'))
        
    generated_story = None
    form_data = {}
    
    if request.method == 'POST':
        theme = request.form['theme']
        moral = request.form['moral']
        character = request.form['character']
        age = request.form['age']
        title = request.form['title']
        
        form_data = {
            'theme': theme,
            'moral': moral,
            'character': character,
            'age': age,
            'title': title
        }
        
        generated_story = generate_story_with_ai(theme, moral, character, age)
        
    return render_template('generate_story.html', generated_story=generated_story, form_data=form_data)

@app.route('/admin/save', methods=['POST'])
def save_story():
    if session.get('role') != 'admin':
        return redirect(url_for('admin_login'))
        
    title = request.form['title']
    moral = request.form['moral']
    theme = request.form['theme']
    age = request.form['age']
    character = request.form['character']
    content = request.form['content']
    
    conn = get_db_connection()
    conn.execute('''
        INSERT INTO stories (title, moral, theme, age, character, content, status)
        VALUES (?, ?, ?, ?, ?, ?, 'draft')
    ''', (title, moral, theme, age, character, content))
    conn.commit()
    conn.close()
    
    flash('Story saved as draft!', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/publish/<int:story_id>', methods=['POST'])
def publish_story(story_id):
    if session.get('role') != 'admin':
        return redirect(url_for('admin_login'))
        
    conn = get_db_connection()
    conn.execute('UPDATE stories SET status = "published" WHERE id = ?', (story_id,))
    conn.commit()
    conn.close()
    
    flash('Story published successfully!', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/unpublish/<int:story_id>', methods=['POST'])
def unpublish_story(story_id):
    if session.get('role') != 'admin':
        return redirect(url_for('admin_login'))
        
    conn = get_db_connection()
    conn.execute('UPDATE stories SET status = "draft" WHERE id = ?', (story_id,))
    conn.commit()
    conn.close()
    
    flash('Story unpublished and moved to drafts.', 'warning')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/delete/<int:story_id>', methods=['POST'])
def delete_story(story_id):
    if session.get('role') != 'admin':
        return redirect(url_for('admin_login'))
        
    conn = get_db_connection()
    conn.execute('DELETE FROM stories WHERE id = ?', (story_id,))
    conn.commit()
    conn.close()
    
    flash('Story deleted permanently.', 'danger')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/preview/<int:story_id>')
def preview_story(story_id):
    if session.get('role') != 'admin':
        return redirect(url_for('admin_login'))
        
    conn = get_db_connection()
    story = conn.execute('SELECT * FROM stories WHERE id = ?', (story_id,)).fetchone()
    conn.close()
    
    if not story:
        flash('Story not found.', 'danger')
        return redirect(url_for('admin_dashboard'))
        
    return render_template('preview_story.html', story=story)

AI_OPERATIONS = {
    1: "Summarize the story in 3 sentences.",
    2: "Extract the main characters and their descriptions.",
    3: "Translate the story to Spanish.",
    4: "Translate the story to French.",
    5: "Simplify the language for a 3-year-old.",
    6: "Rewrite the story so that it rhymes.",
    7: "Suggest 3 alternative catchy titles.",
    8: "Write a short sequel idea based on this story.",
    9: "Change the tone to be very humorous and silly.",
    10: "Change the tone to be serious and dramatic.",
    11: "Expand the story by adding more descriptive details.",
    12: "Shorten the story to be a 1-minute read.",
    13: "Rewrite the story from the villain's or secondary character's perspective.",
    14: "Add a cliffhanger ending to the story.",
    15: "Generate 3 reading comprehension questions for children.",
    16: "Identify difficult vocabulary words and provide definitions.",
    17: "Convert the story into a script format with dialogue and stage directions.",
    18: "Analyze the core themes of the story.",
    19: "Generate 2 interactive prompts to ask the reader during the story.",
    20: "Suggest alternative moral lessons that could be drawn from this."
}

def process_ai_action(action_id, text):
    prompt_instruction = AI_OPERATIONS.get(action_id)
    if not prompt_instruction:
        return "Invalid action."
        
    api_key = os.environ.get('GEMINI_API_KEY')
    if not api_key or api_key == 'your_actual_key_here':
        return "Error: Gemini API key not configured. Please add it to your .env file."
        
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        prompt = f"{prompt_instruction}\n\nHere is the story text:\n{text}"
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error: {str(e)}"

@app.route('/admin/upload', methods=['GET', 'POST'])
def upload_story():
    if session.get('role') != 'admin':
        return redirect(url_for('admin_login'))
        
    if request.method == 'POST':
        title = request.form.get('title', 'Untitled')
        moral = request.form.get('moral', '')
        theme = request.form.get('theme', '')
        age = request.form.get('age', '0')
        character = request.form.get('character', '')
        status = request.form.get('status', 'draft')
        
        file = request.files.get('file')
        if not file or file.filename == '':
            flash('No file selected', 'danger')
            return redirect(request.url)
            
        if file:
            filename = secure_filename(file.filename)
            file_path_full = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path_full)
            
            extracted_text = ""
            if filename.lower().endswith('.pdf'):
                try:
                    doc = fitz.open(file_path_full)
                    for page in doc:
                        extracted_text += page.get_text() + "\n"
                except Exception as e:
                    extracted_text = f"Error extracting text: {e}"
            
            conn = get_db_connection()
            conn.execute('''
                INSERT INTO stories (title, moral, theme, age, character, content, status, file_path, is_upload, extracted_text)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (title, moral, theme, age, character, 'Uploaded file', status, f'uploads/{filename}', 1, extracted_text))
            conn.commit()
            conn.close()
            
            flash('Story uploaded successfully!', 'success')
            return redirect(url_for('admin_dashboard'))
            
    return render_template('upload_story.html')

@app.route('/admin/ai_editor/<int:story_id>')
def ai_editor(story_id):
    if session.get('role') != 'admin':
        return redirect(url_for('admin_login'))
        
    conn = get_db_connection()
    story = conn.execute('SELECT * FROM stories WHERE id = ?', (story_id,)).fetchone()
    conn.close()
    
    if not story:
        flash('Story not found.', 'danger')
        return redirect(url_for('admin_dashboard'))
        
    return render_template('ai_editor.html', story=story, operations=AI_OPERATIONS)

@app.route('/api/ai_action', methods=['POST'])
def api_ai_action():
    if session.get('role') != 'admin':
        return jsonify({"error": "Unauthorized"}), 403
        
    data = request.json
    story_id = data.get('story_id')
    action_id = int(data.get('action_id'))
    
    conn = get_db_connection()
    story = conn.execute('SELECT * FROM stories WHERE id = ?', (story_id,)).fetchone()
    conn.close()
    
    if not story:
        return jsonify({"error": "Story not found"}), 404
        
    text_to_process = story['extracted_text'] if story['is_upload'] else story['content']
    if not text_to_process:
        text_to_process = "No text content found for this story."
    
    result = process_ai_action(action_id, text_to_process)
    return jsonify({"result": result})



if __name__ == '__main__':
    app.run(debug=True, port=5000)
