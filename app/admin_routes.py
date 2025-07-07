from flask import Blueprint,request,render_template,flash,redirect,url_for,current_app
from flask_login import login_required, current_user
from app.utils import admin_only
from werkzeug.utils import secure_filename
import sqlite3
import os

admin = Blueprint('admin', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
# 🔒 Helper to check file extension
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# route for admin to add article
@admin.route('/add', methods=['GET', 'POST'])
@login_required
@admin_only
def add_news():

    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        image = request.files.get('image')
        category = request.form.get('category')

        filename = None
        if image and allowed_file(image.filename):
            filename = secure_filename(image.filename)
            image.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))

        conn = sqlite3.connect(current_app.config['DATABASE'])
        c = conn.cursor()
        c.execute("INSERT INTO news (title, content, image, category, author_id) VALUES (?, ?, ?, ?, ?)",
                  (title, content, filename, category, current_user.id))
        conn.commit()
        conn.close()

        flash('News article added successfully.')
        return redirect(url_for('main.home'))

    return render_template('add_news.html')


# route for admin to edit article   
@admin.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_only
def edit_news(id):
    conn = sqlite3.connect(current_app.config['DATABASE'])
    c = conn.cursor()

    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        category = request.form.get('category')
        c.execute("UPDATE news SET title = ?, content = ?, category = ? WHERE id = ?",
          (title, content, category, id))
        conn.commit()
        conn.close()
        flash('News updated successfully.')
        return redirect(url_for('main.home'))

    c.execute("SELECT id, title, content FROM news WHERE id = ?", (id,))
    news = c.fetchone()
    conn.close()

    if not news:
        return "News not found", 404

    return render_template('edit_news.html', news=news)

# route for admin to delete article
@admin.route('/delete/<int:id>', methods=['POST'])
@login_required
@admin_only
def delete_news(id):

    conn = sqlite3.connect(current_app.config['DATABASE'])
    c = conn.cursor()
    c.execute("DELETE FROM news WHERE id = ?", (id,))
    conn.commit()
    conn.close()

    flash('News deleted successfully.')
    return redirect(url_for('main.home'))