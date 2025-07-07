from flask import Blueprint, render_template, request, redirect, url_for, session, flash, current_app, jsonify
from flask_login import login_user, login_required, logout_user, current_user
import os
import sqlite3
from app.models import create_user, validate_user, User
main = Blueprint('main', __name__)


# Main route news in pagination 
@main.route('/')
def home():
    page = request.args.get('page', 1, type=int)
    per_page = 6
    offset = (page - 1) * per_page

    conn = sqlite3.connect(current_app.config['DATABASE'])
    c = conn.cursor()
    # Get total number of articles
    c.execute("SELECT COUNT(*) FROM news")
    total = c.fetchone()[0]


    c.execute('''
        SELECT news.id, news.title, news.content, news.image, users.username,news.category
        FROM news
        JOIN users ON news.author_id = users.id
        ORDER BY news.id DESC 
        LIMIT ? OFFSET ?
    ''',(per_page, offset))
    articles = c.fetchall()
    conn.close()
    total_pages = (total + per_page - 1) // per_page  # ceil
    return render_template('home.html', articles=articles,page=page, total_pages=total_pages)

# fetch single news for reading 
# also add comments here 
@main.route('/news/<int:id>', methods=['GET', 'POST'])
def view_news(id):
    conn = sqlite3.connect(current_app.config['DATABASE'])
    c = conn.cursor()

    c.execute("UPDATE news SET views = views + 1 WHERE id = ?", (id,))

    if request.method == 'POST' and current_user.is_authenticated:
        content = request.form['comment'].strip()
        if content:
            c.execute("INSERT INTO comments (user_id, news_id, content, created_at) VALUES (?, ?, ?, datetime('now'))",
                  (current_user.id, id, content))
            conn.commit()
            flash("Comment posted!")
            return redirect(url_for('main.view_news', id=id))

    conn.commit()
    # Get article + like count
    c.execute('''
        SELECT news.id, news.title, news.content, news.image, users.username, news.category, news.views,
               (SELECT COUNT(*) FROM likes WHERE news_id = news.id) as like_count
        FROM news
        JOIN users ON news.author_id = users.id
        WHERE news.id = ?
    ''', (id,))
    article = c.fetchone()

    if not article:
        conn.close()
        return "News not found", 404

    # Get comments
    c.execute('''
        SELECT comments.content, comments.created_at, users.username
        FROM comments
        JOIN users ON comments.user_id = users.id
        WHERE comments.news_id = ?
        ORDER BY comments.created_at DESC
    ''', (id,))
    comments = c.fetchall()


    # 👇 Check if the current user already liked the post
    user_liked = False
    if current_user.is_authenticated:
        c.execute("SELECT 1 FROM likes WHERE user_id = ? AND news_id = ?", (current_user.id, id))
        if c.fetchone():
            user_liked = True


    conn.close()
    return render_template("view_news.html", article=article, comments=comments, user_liked=user_liked)



# route for register
@main.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))

    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        success = create_user(username,email, password)
        if success:
            flash('Registration successful. Please log in.')
            return redirect(url_for('main.login'))
        else:
            flash('Username already exists.')
    return render_template('register.html')

# route for login
@main.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:

        return redirect(url_for('main.home'))
    
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = validate_user(email, password)
        if user:
            login_user(user)
            return redirect(url_for('main.home'))
        else:
            flash('Invalid username or password.')
    return render_template('login.html')

# route for logout
@main.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('main.home'))

# search route
@main.route('/search')
def search():
    query = request.args.get('q', '').strip()

    if not query:
        flash("Please enter a search term.")
        return redirect(url_for('main.home'))

    conn = sqlite3.connect(current_app.config['DATABASE'])
    c = conn.cursor()
    c.execute('''
        SELECT news.id, news.title, news.content, news.image, users.username
        FROM news
        JOIN users ON news.author_id = users.id
        WHERE news.title LIKE ? OR news.content LIKE ?
        ORDER BY news.id DESC
    ''', (f'%{query}%', f'%{query}%'))
    articles = c.fetchall()
    conn.close()

    return render_template('search_results.html', articles=articles, query=query)

# route for filtering by category
@main.route('/category/<name>')
def filter_by_category(name):
    page = request.args.get('page', 1, type=int)
    per_page = 6
    offset = (page - 1) * per_page

    conn = sqlite3.connect(current_app.config['DATABASE'])
    c = conn.cursor()

    c.execute("SELECT COUNT(*) FROM news WHERE category = ?", (name,))
    total = c.fetchone()[0]

    c.execute('''
        SELECT news.id, news.title, news.content, news.image, users.username, news.category
        FROM news
        JOIN users ON news.author_id = users.id
        WHERE news.category = ?
        ORDER BY news.id DESC
        LIMIT ? OFFSET ?
    ''', (name, per_page, offset))

    articles = c.fetchall()
    conn.close()
    total_pages = (total + per_page - 1) // per_page  # ceil
    return render_template(
        'category.html',
        articles=articles,
        category=name,
        page=page,
        total_pages=total_pages
    )

# route for liking/unliking news
@main.route('/like/<int:news_id>', methods=['POST'])
@login_required
def toggle_like(news_id):
    conn = sqlite3.connect(current_app.config['DATABASE'])
    c = conn.cursor()

    # Check if already liked
    c.execute('SELECT id FROM likes WHERE user_id = ? AND news_id = ?', (current_user.id, news_id))
    like = c.fetchone()

    if like:
        # Unlike
        c.execute('DELETE FROM likes WHERE id = ?', (like[0],))
        conn.commit()
        liked = False
    else:
        # Like
        c.execute('INSERT INTO likes (user_id, news_id) VALUES (?, ?)', (current_user.id, news_id))
        conn.commit()
        liked = True

    c.execute("SELECT COUNT(*) FROM likes WHERE news_id = ?", (news_id,))
    like_count = c.fetchone()[0]
    conn.close()
    return jsonify({'liked': liked, 'like_count': like_count})

    
