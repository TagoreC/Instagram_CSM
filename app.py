from flask import Flask, render_template, request, redirect, url_for, g, flash
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'instagram_cms_secret_2024'

DATABASE = 'instagram_cms.db'

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
        db.close()  # close connection

def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

# init db on startup
with app.app_context():
    if not os.path.exists(DATABASE):
        init_db()


# --- dashboard route ---
@app.route('/')
def index():
    db = get_db()

    # get post counts
    result = db.execute("SELECT COUNT(*) as total FROM posts").fetchone()
    total = result['total']

    scheduled = db.execute("SELECT COUNT(*) as cnt FROM posts WHERE status='scheduled'").fetchone()['cnt']
    published = db.execute("SELECT COUNT(*) as cnt FROM posts WHERE status='published'").fetchone()['cnt']
    drafts = db.execute("SELECT COUNT(*) as cnt FROM posts WHERE status='draft'").fetchone()['cnt']

    # get latest analytics snapshot
    latest = db.execute("SELECT * FROM analytics ORDER BY recorded_at DESC LIMIT 1").fetchone()

    followers = latest['followers'] if latest else 0

    return render_template('index.html',
        total=total,
        scheduled=scheduled,
        published=published,
        drafts=drafts,
        followers=followers
    )


# --- add post ---
@app.route('/add-post', methods=['GET', 'POST'])
def add_post():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        caption = request.form.get('caption', '').strip()
        image_url = request.form.get('image_url', '').strip()
        status = request.form.get('status', 'draft')
        scheduled_at = request.form.get('scheduled_at', '')
        likes = request.form.get('likes', 0)
        hashtags_raw = request.form.get('hashtags', '')

        # basic validation
        if not username or not caption or not image_url:
            flash('Please fill in all required fields.', 'danger')
            return redirect(url_for('add_post'))

        if not likes:
            likes = 0

        db = get_db()

        # insert post into db
        db.execute(
            "INSERT INTO posts (username, caption, image_url, status, scheduled_at, likes) VALUES (?, ?, ?, ?, ?, ?)",
            (username, caption, image_url, status, scheduled_at if scheduled_at else None, likes)
        )
        db.commit()

        # get the new post id
        row = db.execute("SELECT last_insert_rowid() as id").fetchone()
        post_id = row['id']
        # print(post_id)

        # split hashtags by comma and insert each one
        if hashtags_raw:
            tags = [t.strip() for t in hashtags_raw.split(',') if t.strip()]
            for tag in tags:
                db.execute("INSERT INTO hashtags (post_id, tag) VALUES (?, ?)", (post_id, tag))
            db.commit()

        flash('Post saved successfully!', 'success')
        return redirect(url_for('success'))

    return render_template('add_post.html')


# --- list all posts ---
@app.route('/posts')
def list_posts():
    db = get_db()

    status_filter = request.args.get('status', '')
    search_query = request.args.get('q', '').strip()

    # TODO: add pagination later
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
        # get all posts
        posts = db.execute("SELECT * FROM posts ORDER BY created_at DESC").fetchall()

    return render_template('list_posts.html', posts=posts, status_filter=status_filter, search_query=search_query)


# --- single post detail ---
@app.route('/post/<int:id>')
def detail_post(id):
    db = get_db()

    post = db.execute("SELECT * FROM posts WHERE id=?", (id,)).fetchone()
    if not post:
        flash('Post not found.', 'danger')
        return redirect(url_for('list_posts'))

    # get hashtags for this post
    hashtags = db.execute("SELECT tag FROM hashtags WHERE post_id=?", (id,)).fetchall()

    # get all comments and dms
    comments = db.execute("SELECT * FROM comments WHERE post_id=? ORDER BY created_at DESC", (id,)).fetchall()

    return render_template('detail_post.html', post=post, hashtags=hashtags, comments=comments)


# --- submit comment or dm ---
@app.route('/submit-comment/<int:id>', methods=['POST'])
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


# --- delete a post ---
@app.route('/delete-post/<int:id>', methods=['POST'])
def delete_post(id):
    db = get_db()

    # delete hashtags and comments first
    db.execute("DELETE FROM hashtags WHERE post_id=?", (id,))
    db.execute("DELETE FROM comments WHERE post_id=?", (id,))
    db.execute("DELETE FROM posts WHERE id=?", (id,))
    db.commit()

    flash('Post deleted.', 'success')
    return redirect(url_for('list_posts'))


# --- analytics page ---
@app.route('/analytics')
def analytics():
    db = get_db()

    # get all analytics rows newest first
    data = db.execute("SELECT * FROM analytics ORDER BY recorded_at DESC").fetchall()

    latest = data[0] if data else None

    # top 5 hashtags by usage count
    top_tags = db.execute(
        "SELECT tag, COUNT(*) as cnt FROM hashtags GROUP BY tag ORDER BY COUNT(*) DESC LIMIT 5"
    ).fetchall()

    return render_template('analytics.html', data=data, latest=latest, top_tags=top_tags)


# --- add analytics snapshot ---
@app.route('/add-analytics', methods=['GET', 'POST'])
def add_analytics():
    if request.method == 'POST':
        followers = request.form.get('followers', 0)
        following = request.form.get('following', 0)
        total_posts = request.form.get('total_posts', 0)
        avg_likes = request.form.get('avg_likes', 0.0)
        avg_reach = request.form.get('avg_reach', 0.0)

        # basic check
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


# --- success page ---
@app.route('/success')
def success():
    return render_template('success.html')


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
