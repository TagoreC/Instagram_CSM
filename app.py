from flask import Flask, render_template, request, redirect, url_for, g, flash, session
from functools import wraps
import sqlite3
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'instagram_cms_secret_2024'

DATABASE = 'instagram_cms.db'
UPLOAD_FOLDER = os.path.join('static', 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'mp4', 'mov', 'webm'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 64 * 1024 * 1024  # 64 MB max upload

# make sure uploads folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_media_type(filename):
    ext = filename.rsplit('.', 1)[1].lower()
    if ext in {'mp4', 'mov', 'webm'}:
        return 'video'
    return 'image'


# ─── Auth decorators ──────────────────────────────────────────────────────────

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to continue.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to continue.', 'warning')
            return redirect(url_for('login'))
        if session.get('role') != 'admin':
            flash('Access denied. Admins only.', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated


# ─── Startup: migrate & seed ─────────────────────────────────────────────────

with app.app_context():
    if not os.path.exists(DATABASE):
        init_db()
    else:
        db = get_db()
        # add new columns if they don't exist
        try:
            db.execute("ALTER TABLE posts ADD COLUMN media_file TEXT DEFAULT ''")
            db.commit()
        except Exception:
            pass
        try:
            db.execute("ALTER TABLE posts ADD COLUMN media_type TEXT DEFAULT 'image'")
            db.commit()
        except Exception:
            pass
        # create profiles table
        db.execute("""
            CREATE TABLE IF NOT EXISTS profiles (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                username      TEXT NOT NULL DEFAULT 'my_account',
                bio           TEXT DEFAULT '',
                profile_photo TEXT DEFAULT '',
                followers     INTEGER DEFAULT 0,
                following     INTEGER DEFAULT 0,
                is_followed   INTEGER DEFAULT 0
            )
        """)
        db.commit()
        # default profile row
        row = db.execute("SELECT COUNT(*) as cnt FROM profiles").fetchone()
        if row['cnt'] == 0:
            db.execute("INSERT INTO profiles (username, bio) VALUES ('my_account', 'Welcome to my Instagram CMS!')")
            db.commit()

        # create users table
        db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                username   TEXT NOT NULL UNIQUE,
                password   TEXT NOT NULL,
                role       TEXT NOT NULL DEFAULT 'user',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        db.commit()

        # seed admin account if no users exist
        user_count = db.execute("SELECT COUNT(*) as cnt FROM users").fetchone()['cnt']
        if user_count == 0:
            db.execute(
                "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                ('vensunreddy', 'admin123', 'admin')
            )
            db.commit()


# ─── Auth routes ─────────────────────────────────────────────────────────────

@app.route('/login', methods=['GET', 'POST'])
def login():
    # already logged in → go home
    if 'user_id' in session:
        return redirect(url_for('index'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()

        if not username or not password:
            flash('Username and password are required.', 'danger')
            return render_template('login.html', active_tab='signin')

        db = get_db()
        user = db.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (username, password)
        ).fetchone()

        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['role'] = user['role']
            flash(f"Welcome back, {user['username']}!", 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password.', 'danger')
            return render_template('login.html', active_tab='signin')

    return render_template('login.html', active_tab='signin')


@app.route('/register', methods=['POST'])
def register():
    # already logged in → go home
    if 'user_id' in session:
        return redirect(url_for('index'))

    username = request.form.get('username', '').strip()
    password = request.form.get('password', '').strip()
    confirm  = request.form.get('confirm', '').strip()

    if not username or not password:
        flash('Username and password are required.', 'danger')
        return render_template('login.html', active_tab='register')

    if password != confirm:
        flash('Passwords do not match. Please try again.', 'danger')
        return render_template('login.html', active_tab='register')

    db = get_db()
    existing = db.execute("SELECT id FROM users WHERE username=?", (username,)).fetchone()
    if existing:
        flash(f'Username "{username}" is already taken. Please choose a different one.', 'danger')
        return render_template('login.html', active_tab='register')

    db.execute(
        "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
        (username, password, 'user')
    )
    db.commit()

    # auto login after registration
    new_user = db.execute("SELECT * FROM users WHERE username=?", (username,)).fetchone()
    session['user_id'] = new_user['id']
    session['username'] = new_user['username']
    session['role']     = new_user['role']

    flash(f'Account created! Welcome, {username}!', 'success')
    return redirect(url_for('index'))


@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))


# ─── Admin: user management ──────────────────────────────────────────────────

@app.route('/admin/users')
@admin_required
def admin_users():
    db = get_db()
    users = db.execute("SELECT * FROM users ORDER BY created_at DESC").fetchall()
    return render_template('admin_users.html', users=users)


@app.route('/admin/users/add', methods=['POST'])
@admin_required
def admin_add_user():
    username = request.form.get('username', '').strip()
    password = request.form.get('password', '').strip()
    role = request.form.get('role', 'user').strip()

    if not username or not password:
        flash('Username and password are required.', 'danger')
        return redirect(url_for('admin_users'))

    db = get_db()
    existing = db.execute("SELECT id FROM users WHERE username=?", (username,)).fetchone()
    if existing:
        flash(f'Username "{username}" already exists.', 'danger')
        return redirect(url_for('admin_users'))

    db.execute(
        "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
        (username, password, role)
    )
    db.commit()
    flash(f'User "{username}" added successfully!', 'success')
    return redirect(url_for('admin_users'))


@app.route('/admin/users/delete/<int:uid>', methods=['POST'])
@admin_required
def admin_delete_user(uid):
    if uid == session.get('user_id'):
        flash('You cannot delete your own account.', 'danger')
        return redirect(url_for('admin_users'))
    db = get_db()
    db.execute("DELETE FROM users WHERE id=?", (uid,))
    db.commit()
    flash('User deleted.', 'success')
    return redirect(url_for('admin_users'))


# ─── Dashboard ───────────────────────────────────────────────────────────────

@app.route('/')
@login_required
def index():
    db = get_db()
    result = db.execute("SELECT COUNT(*) as total FROM posts").fetchone()
    total = result['total']
    scheduled = db.execute("SELECT COUNT(*) as cnt FROM posts WHERE status='scheduled'").fetchone()['cnt']
    published = db.execute("SELECT COUNT(*) as cnt FROM posts WHERE status='published'").fetchone()['cnt']
    drafts = db.execute("SELECT COUNT(*) as cnt FROM posts WHERE status='draft'").fetchone()['cnt']
    latest = db.execute("SELECT * FROM analytics ORDER BY recorded_at DESC LIMIT 1").fetchone()
    followers = latest['followers'] if latest else 0
    return render_template('index.html',
        total=total,
        scheduled=scheduled,
        published=published,
        drafts=drafts,
        followers=followers
    )


# ─── Profile ─────────────────────────────────────────────────────────────────

@app.route('/profile')
@login_required
def profile():
    db = get_db()
    prof = db.execute("SELECT * FROM profiles LIMIT 1").fetchone()
    posts = db.execute("SELECT * FROM posts ORDER BY created_at DESC").fetchall()
    latest = db.execute("SELECT * FROM analytics ORDER BY recorded_at DESC LIMIT 1").fetchone()
    if latest:
        follower_count = latest['followers']
        following_count = latest['following']
    else:
        follower_count = prof['followers'] if prof else 0
        following_count = prof['following'] if prof else 0
    total_posts = db.execute("SELECT COUNT(*) as cnt FROM posts").fetchone()['cnt']
    return render_template('profile.html',
        prof=prof,
        posts=posts,
        follower_count=follower_count,
        following_count=following_count,
        total_posts=total_posts
    )


@app.route('/profile/follow', methods=['POST'])
@login_required
def toggle_follow():
    db = get_db()
    prof = db.execute("SELECT * FROM profiles LIMIT 1").fetchone()
    if prof:
        new_val = 0 if prof['is_followed'] else 1
        db.execute("UPDATE profiles SET is_followed=? WHERE id=?", (new_val, prof['id']))
        db.commit()
    return redirect(url_for('profile'))


@app.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    db = get_db()
    prof = db.execute("SELECT * FROM profiles LIMIT 1").fetchone()

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        bio = request.form.get('bio', '').strip()
        if not username:
            flash('Username is required.', 'danger')
            return redirect(url_for('edit_profile'))

        photo_filename = prof['profile_photo'] if prof else ''
        file = request.files.get('profile_photo')
        if file and file.filename != '' and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filename = 'profile_' + filename
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            photo_filename = filename

        if prof:
            db.execute(
                "UPDATE profiles SET username=?, bio=?, profile_photo=? WHERE id=?",
                (username, bio, photo_filename, prof['id'])
            )
        else:
            db.execute(
                "INSERT INTO profiles (username, bio, profile_photo) VALUES (?, ?, ?)",
                (username, bio, photo_filename)
            )
        db.commit()
        flash('Profile updated!', 'success')
        return redirect(url_for('profile'))

    return render_template('edit_profile.html', prof=prof)


# ─── Posts ───────────────────────────────────────────────────────────────────

@app.route('/add-post', methods=['GET', 'POST'])
@login_required
def add_post():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        caption = request.form.get('caption', '').strip()
        image_url = request.form.get('image_url', '').strip()
        status = request.form.get('status', 'draft')
        scheduled_at = request.form.get('scheduled_at', '')
        likes = request.form.get('likes', 0)
        hashtags_raw = request.form.get('hashtags', '')

        media_filename = ''
        media_type = 'image'
        file = request.files.get('media_file')
        if file and file.filename != '' and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            media_filename = filename
            media_type = get_media_type(filename)

        if not username or not caption:
            flash('Username and caption are required.', 'danger')
            return redirect(url_for('add_post'))

        if not media_filename and not image_url:
            flash('Please upload a file or provide an image URL.', 'danger')
            return redirect(url_for('add_post'))

        if not likes:
            likes = 0

        db = get_db()
        db.execute(
            "INSERT INTO posts (username, caption, image_url, status, scheduled_at, likes, media_file, media_type) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (username, caption, image_url, status, scheduled_at if scheduled_at else None, likes, media_filename, media_type)
        )
        db.commit()
        row = db.execute("SELECT last_insert_rowid() as id").fetchone()
        post_id = row['id']
        if hashtags_raw:
            tags = [t.strip() for t in hashtags_raw.split(',') if t.strip()]
            for tag in tags:
                db.execute("INSERT INTO hashtags (post_id, tag) VALUES (?, ?)", (post_id, tag))
            db.commit()

        flash('Post saved successfully!', 'success')
        return redirect(url_for('success'))

    return render_template('add_post.html')


@app.route('/posts')
@login_required
def list_posts():
    db = get_db()
    status_filter = request.args.get('status', '')
    search_query = request.args.get('q', '').strip()

    if status_filter and search_query:
        posts = db.execute(
            "SELECT * FROM posts WHERE status=? AND caption LIKE ? ORDER BY created_at DESC",
            (status_filter, '%' + search_query + '%')
        ).fetchall()
    elif status_filter:
        posts = db.execute(
            "SELECT * FROM posts WHERE status=? ORDER BY created_at DESC",
            (status_filter,)
        ).fetchall()
    elif search_query:
        posts = db.execute(
            "SELECT * FROM posts WHERE caption LIKE ? ORDER BY created_at DESC",
            ('%' + search_query + '%',)
        ).fetchall()
    else:
        posts = db.execute("SELECT * FROM posts ORDER BY created_at DESC").fetchall()

    return render_template('list_posts.html', posts=posts, status_filter=status_filter, search_query=search_query)


@app.route('/post/<int:id>')
@login_required
def detail_post(id):
    db = get_db()
    post = db.execute("SELECT * FROM posts WHERE id=?", (id,)).fetchone()
    if not post:
        flash('Post not found.', 'danger')
        return redirect(url_for('list_posts'))
    hashtags = db.execute("SELECT tag FROM hashtags WHERE post_id=?", (id,)).fetchall()
    comments = db.execute("SELECT * FROM comments WHERE post_id=? ORDER BY created_at DESC", (id,)).fetchall()
    return render_template('detail_post.html', post=post, hashtags=hashtags, comments=comments)


@app.route('/submit-comment/<int:id>', methods=['POST'])
@login_required
def submit_comment(id):
    commenter = request.form.get('commenter', '').strip()
    body = request.form.get('body', '').strip()
    type_ = request.form.get('type', 'comment')
    if not commenter or not body:
        flash('Name and comment are required.', 'danger')
        return redirect(url_for('detail_post', id=id))
    db = get_db()
    db.execute(
        "INSERT INTO comments (post_id, commenter, body, type) VALUES (?, ?, ?, ?)",
        (id, commenter, body, type_)
    )
    db.commit()
    flash('Comment posted!', 'success')
    return redirect(url_for('detail_post', id=id))


@app.route('/delete-post/<int:id>', methods=['POST'])
@login_required
def delete_post(id):
    db = get_db()
    db.execute("DELETE FROM hashtags WHERE post_id=?", (id,))
    db.execute("DELETE FROM comments WHERE post_id=?", (id,))
    db.execute("DELETE FROM posts WHERE id=?", (id,))
    db.commit()
    flash('Post deleted.', 'success')
    return redirect(url_for('list_posts'))


# ─── Analytics ───────────────────────────────────────────────────────────────

@app.route('/analytics')
@login_required
def analytics():
    db = get_db()
    data = db.execute("SELECT * FROM analytics ORDER BY recorded_at DESC").fetchall()
    latest = data[0] if data else None
    top_tags = db.execute(
        "SELECT tag, COUNT(*) as cnt FROM hashtags GROUP BY tag ORDER BY COUNT(*) DESC LIMIT 5"
    ).fetchall()
    return render_template('analytics.html', data=data, latest=latest, top_tags=top_tags)


@app.route('/add-analytics', methods=['GET', 'POST'])
@login_required
def add_analytics():
    if request.method == 'POST':
        followers = request.form.get('followers', 0)
        following = request.form.get('following', 0)
        total_posts = request.form.get('total_posts', 0)
        avg_likes = request.form.get('avg_likes', 0.0)
        avg_reach = request.form.get('avg_reach', 0.0)
        if not followers or not following or not total_posts:
            flash('All fields are required.', 'danger')
            return redirect(url_for('add_analytics'))
        db = get_db()
        db.execute(
            "INSERT INTO analytics (followers, following, total_posts, avg_likes, avg_reach) VALUES (?, ?, ?, ?, ?)",
            (followers, following, total_posts, avg_likes, avg_reach)
        )
        db.commit()
        flash('Snapshot logged!', 'success')
        return redirect(url_for('analytics'))
    return render_template('add_analytics.html')


# ─── Success ─────────────────────────────────────────────────────────────────

@app.route('/success')
@login_required
def success():
    return render_template('success.html')


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
