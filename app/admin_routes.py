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

    conn = sqlite3.connect(current_app.config['DATABASE'])
    c = conn.cursor()

    c.execute("SELECT id, name FROM categories")
    categories = c.fetchall()

    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        image = request.files.get('image')
        category_id = request.form['category']

        filename = None
        if image and allowed_file(image.filename):
            filename = secure_filename(image.filename)
            image.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))

        
        c.execute("INSERT INTO news (title, content, image, category_id, author_id) VALUES (?, ?, ?, ?, ?)",
                  (title, content, filename, category_id, current_user.id))
        conn.commit()
        conn.close()

        flash('News article added successfully.')
        return redirect(url_for('main.home'))

    return render_template('add_news.html',categories=categories)


# route for admin to edit article   
@admin.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_only
def edit_news(id):
    conn = sqlite3.connect(current_app.config['DATABASE'])
    c = conn.cursor()

    c.execute("SELECT id, name FROM categories")
    categories = c.fetchall()

    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        category_id = request.form['category']
        c.execute("UPDATE news SET title = ?, content = ?, category_id = ? WHERE id = ?",
          (title, content, category_id, id))
        conn.commit()
        conn.close()
        flash('News updated successfully.')
        return redirect(url_for('main.home'))

    c.execute("SELECT id, title, content FROM news WHERE id = ?", (id,))
    news = c.fetchone()
    conn.close()

    if not news:
        return "News not found", 404

    return render_template('edit_news.html', news=news,categories=categories)

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

@admin.route('/admin/dashboard')
@login_required
@admin_only
def dashboard():
    conn = sqlite3.connect(current_app.config['DATABASE'])
    c = conn.cursor()

    c.execute("SELECT COUNT(*) FROM news")
    total_news = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM users")
    total_users = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM comments")
    total_comments = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM likes")
    total_likes = c.fetchone()[0]

    c.execute("SELECT title, id FROM news ORDER BY id DESC LIMIT 5")
    latest_news = c.fetchall()

    conn.close()

    return render_template('admin/dashboard.html', 
        total_news=total_news, 
        total_users=total_users,
        total_comments=total_comments,
        total_likes=total_likes,
        latest_news=latest_news
    )

@admin.route('/admin/manage-users')
@login_required
@admin_only
def manage_users():
    # 🔢 Get page number from URL query (?page=2)
    page = int(request.args.get('page', 1))
    per_page = 10  # Users per page
    offset = (page - 1) * per_page

    conn = sqlite3.connect(current_app.config['DATABASE'])
    c = conn.cursor()

    # Get paginated users
    c.execute("SELECT id, username, email, role FROM users LIMIT ? OFFSET ?", (per_page, offset))
    users = c.fetchall()

    # Total user count (for calculating max pages)
    c.execute("SELECT COUNT(*) FROM users")
    total_users = c.fetchone()[0]
    conn.close()

    total_pages = (total_users + per_page - 1) // per_page

    return render_template(
        'admin/users.html',
        users=users,
        page=page,
        total_pages=total_pages
    )


@admin.route('/users/promote/<int:user_id>')
@login_required
@admin_only
def promote_user(user_id):
    conn = sqlite3.connect(current_app.config['DATABASE'])
    c = conn.cursor()
    c.execute("UPDATE users SET role = 'admin' WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()
    flash("User promoted to admin.")
    return redirect(url_for('admin.manage_users'))

@admin.route('/users/demote/<int:user_id>')
@login_required
@admin_only
def demote_user(user_id):
    conn = sqlite3.connect(current_app.config['DATABASE'])
    c = conn.cursor()
    c.execute("UPDATE users SET role = 'user' WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()
    flash("User demoted to regular user.")
    return redirect(url_for('admin.manage_users'))

@admin.route('/users/delete/<int:user_id>')
@login_required
@admin_only
def delete_user(user_id):
    conn = sqlite3.connect(current_app.config['DATABASE'])
    c = conn.cursor()
    c.execute("DELETE FROM users WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()
    flash("User deleted.")
    return redirect(url_for('admin.manage_users'))

@admin.route('/admin/manage-comments')
@login_required
@admin_only
def manage_comments():

    page = int(request.args.get('page', 1))
    per_page = 10
    offset = (page - 1) * per_page

    conn = sqlite3.connect(current_app.config['DATABASE'])
    c = conn.cursor()

    # Paginated comments
    c.execute("""
        SELECT comments.id, comments.content, comments.created_at, users.username, news.title
        FROM comments
        JOIN users ON comments.user_id = users.id
        JOIN news ON comments.news_id = news.id
        ORDER BY comments.created_at DESC
        LIMIT ? OFFSET ?
    """, (per_page, offset))
    comments = c.fetchall()

    # Total comment count
    c.execute("SELECT COUNT(*) FROM comments")
    total_comments = c.fetchone()[0]
    conn.close()

    total_pages = (total_comments + per_page - 1) // per_page

    return render_template(
        'admin/comments.html',
        comments=comments,
        page=page,
        total_pages=total_pages
    )

@admin.route('/comments/delete/<int:comment_id>', methods=['POST'])
@login_required
def delete_comment(comment_id):
    if current_user.role != 'admin':
        return "Unauthorized", 403

    conn = sqlite3.connect(current_app.config['DATABASE'])
    c = conn.cursor()
    c.execute("DELETE FROM comments WHERE id = ?", (comment_id,))
    conn.commit()
    conn.close()

    flash("Comment deleted.")
    return redirect(url_for('admin.manage_comments'))

# ****** These routes are for managing categories ******
@admin.route('/admin/categories')
@login_required
@admin_only
def manage_categories():
    conn = sqlite3.connect(current_app.config['DATABASE'])
    c = conn.cursor()
    c.execute("SELECT id, name FROM categories ORDER BY name")
    categories = c.fetchall()
    conn.close()

    return render_template('admin/categories.html', categories=categories)

@admin.route('/admin/categories/add', methods=['POST'])
@login_required
@admin_only
def add_category():
    name = request.form['name'].strip()
    if name:
        conn = sqlite3.connect(current_app.config['DATABASE'])
        c = conn.cursor()
        try:
            c.execute("INSERT INTO categories (name) VALUES (?)", (name,))
            conn.commit()
            flash("Category added.")
        except sqlite3.IntegrityError:
            flash("Category already exists.")
        finally:
            conn.close()

    return redirect(url_for('admin.manage_categories'))

@admin.route('/admin/categories/delete/<int:category_id>', methods=['POST'])
@login_required
@admin_only
def delete_category(category_id):
    conn = sqlite3.connect(current_app.config['DATABASE'])
    c = conn.cursor()
    c.execute("DELETE FROM categories WHERE id = ?", (category_id,))
    conn.commit()
    conn.close()

    flash("Category deleted.")
    return redirect(url_for('admin.manage_categories'))


@admin.route('/subscribers')
@login_required
@admin_only
def view_subscribers():
    conn = sqlite3.connect(current_app.config['DATABASE'])
    c = conn.cursor()
    c.execute("SELECT email, created_at FROM subscribers ORDER BY created_at DESC")
    subscribers = c.fetchall()
    conn.close()
    return render_template('admin/subscribers.html', subscribers=subscribers)


@admin.route('/subscribers/export')
@login_required
@admin_only
def export_subscribers():
    import csv
    from flask import Response
    conn = sqlite3.connect(current_app.config['DATABASE'])
    c = conn.cursor()
    c.execute("SELECT email, created_at FROM subscribers ORDER BY created_at DESC")
    rows = c.fetchall()
    conn.close()

    def generate():
        data = csv.writer(open('/tmp/subscribers.csv', 'w', newline=''))
        yield 'Email,Subscribed At\n'
        for row in rows:
            yield f"{row[0]},{row[1]}\n"

    return Response(
        generate(),
        mimetype='text/csv',
        headers={
            "Content-Disposition": "attachment; filename=subscribers.csv"
        }
    )