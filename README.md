# 📰 Flask News Portal

A fully featured **Flask-based News Publishing Platform** where admins can create, manage, and moderate content, while users can interact via likes and comments. Built with SQLite, Flask, and TailwindCSS.

### 👤 User Functionality

- Register & login securely (Flask-Login)
- Comment on news articles
- Like/unlike articles (with real-time update)
- View single news page with view counter
- View articles by category
- Edit personal profile (name, email, password)
- User profile page showing:
  - Total likes given
  - Comments made
  - Liked articles list

### 🛠️ Admin Panel

- Create/edit/delete news
- Manage users with pagination
- Manage comments (moderate/delete)
- Manage categories (add/edit/delete)
- View list of newsletter subscribers
- Export subscribers to CSV
- Admin-only routes protected via decorators

### 📬 Newsletter System

- Public users can sign up for the newsletter
- Admin can export subscriber emails to CSV

## 🗂️ Tech Stack

| Layer    | Tech                 |
| -------- | -------------------- |
| Backend  | Python, Flask        |
| Frontend | Jinja2, Tailwind CSS |
| Database | SQLite               |
| Auth     | Flask-Login          |
| Styling  | TailwindCDN          |

---

## 📦 Installation

### 🐍 Create a virtual environment (recommended)

```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows
```

```bash
uv pip install
uv pip install -r pyproject.toml
```

to run application

```bash
uv run run.py
```

that's it

### 📈 Future Improvements

- Analytics Dashboard (views, likes per article)
- Email sending to subscribers
- Tag support in addition to categories
- Dockerize for easy deployment
- PostgreSQL support for production

### Author

Amir Mansoor
