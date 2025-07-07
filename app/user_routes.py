from flask import render_template, request, redirect, url_for, flash,Blueprint,current_app
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
import sqlite3
import re
user = Blueprint('user', __name__)

@user.route('/user/<email>')
def user_profile(email):
    print(current_user.email,email)
    if current_user.email != email:
        return redirect(url_for("main.home"))
    conn = sqlite3.connect(current_app.config['DATABASE'])
    c = conn.cursor()

    # Get user info
    c.execute("SELECT id, username FROM users WHERE email = ?", (email,))
    user_row = c.fetchone()
    if not user_row:
        conn.close()
        return "User not found", 404

    user_id = user_row[0]

    # Get comments
    c.execute('''
        SELECT news.title, comments.content, comments.created_at, comments.news_id
        FROM comments
        JOIN news ON comments.news_id = news.id
        WHERE comments.user_id = ?
        ORDER BY comments.created_at DESC
    ''', (user_id,))
    comments = c.fetchall()

    # Count total comments
    c.execute("SELECT COUNT(*) FROM comments WHERE user_id = ?", (user_id,))
    comment_count = c.fetchone()[0]

    # Get liked news
    c.execute('''
        SELECT news.id, news.title
        FROM likes
        JOIN news ON likes.news_id = news.id
        WHERE likes.user_id = ?
    ''', (user_id,))
    liked_news = c.fetchall()

    # Count total likes
    c.execute("SELECT COUNT(*) FROM likes WHERE user_id = ?", (user_id,))
    like_count = c.fetchone()[0]

    conn.close()
    return render_template("user_profile.html", user=user_row, comments=comments, liked_news=liked_news,
                           comment_count=comment_count, like_count=like_count)

@user.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    conn = sqlite3.connect(current_app.config['DATABASE'])
    c = conn.cursor()

    if request.method == 'POST':
        username = request.form['username'].strip()
        new_email = request.form['email'].strip()
        new_password = request.form['password'].strip()

        email_pattern = r'^[\w\.-]+@[\w\.-]+\.\w{2,}$'

        # Update username
        if username:
            c.execute("UPDATE users SET username = ? WHERE id = ?", (username, current_user.id))
            flash("Name updated successfully.")

        # Check for email conflict before updating
        if new_email:
            if not re.match(email_pattern,new_email):
                flash("Invalid email format")
            else:
                c.execute("SELECT id FROM users WHERE email = ? AND id != ?", (new_email, current_user.id))
                email_owner = c.fetchone()
                if email_owner:
                    flash("⚠️ This email is already in use by another account.")
                else:
                    c.execute("UPDATE users SET email = ? WHERE id = ?", (new_email, current_user.id))
                    flash("Email updated successfully.")

        # Update password if provided
        if new_password:
            hashed_pw = generate_password_hash(new_password)
            c.execute("UPDATE users SET password = ? WHERE id = ?", (hashed_pw, current_user.id))
            flash("Password updated successfully.")

        conn.commit()
        conn.close()
        return redirect(url_for('user.edit_profile'))

    # GET request: fetch current user info
    c.execute("SELECT username, email FROM users WHERE id = ?", (current_user.id,))
    user = c.fetchone()
    conn.close()

    return render_template('edit_profile.html', username=user[0], email=user[1])
