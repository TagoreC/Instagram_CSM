# Instagram CMS — Agent Task File
> Full-stack Flask project | HTML + Bootstrap + CSS + JS + jQuery + SQLite
> IMPORTANT: Write code like a college student — not like a senior engineer. See style rules below.

---

## ⚡ AUTONOMOUS EXECUTION — READ THIS FIRST

**Do NOT ask for permission at any step. Do NOT ask clarifying questions. Do NOT pause and wait for confirmation.**

- Just build everything end to end without stopping
- If you face a small ambiguity, make a reasonable decision and move on
- Do not say "Should I proceed?" or "Do you want me to..." — just do it
- Create every file, write every line, run every git command in sequence
- Only stop if there is a hard error you genuinely cannot resolve alone

---

## 🧠 CRITICAL — CODE STYLE RULES (READ FIRST)

This project must look like it was built by a **second/third year CSE student** over a few days. Follow these rules strictly:

### Python (app.py)
- Use simple variable names: `conn`, `db`, `row`, `data`, `result`
- Write short inline comments like `# get all posts`, `# insert into db`, `# close connection`
- Don't use type hints anywhere
- Write a `print()` debug statement in one place — commented out: `# print(post_id)`
- Don't be overly DRY — okay to repeat a couple of lines instead of abstracting
- Use `fetchall()` and `fetchone()` directly, no ORM
- Add a comment like `# TODO: add pagination later` somewhere

### HTML/Jinja2
- Use Bootstrap classes but not perfectly — occasionally inconsistent spacing utilities
- Write a few HTML comments like `<!-- main form -->`, `<!-- post cards -->`, `<!-- footer -->`
- Not every div gets a comment — just a few scattered ones

### CSS
- A commented-out debug line: `/* border: 1px solid red; */`
- Variable names like `--main-color`, `--dark-bg` — not over-engineered
- One or two `!important` flags

### JavaScript/jQuery
- Comments like `// validate before submit`, `// check if caption is empty`, `// clear errors first`
- Use `var` for at least 2-3 variables (mix of `var` and `let/const`)
- One `console.log()` commented out: `// console.log(isValid)`
- Validation logic is slightly verbose — not perfectly abstracted

---

## 📋 PROJECT DETAILS

```
Project Title  : Instagram CMS
Purpose        : A content management system to schedule Instagram posts,
                 manage hashtags, track follower analytics, and handle comments/DMs.
Main Entities  : posts, hashtags, comments, analytics
Core Features  :
  1. Schedule & manage posts (caption, image URL, scheduled date, status)
  2. Track followers/analytics (follower count, likes, reach — stored per entry)
  3. Manage comments/DMs (submit, view, delete comments on each post)
  4. Hashtag manager (add comma-separated hashtags per post, view top used tags)
  5. Filter/search all posts by status (draft / scheduled / published)
  6. Dashboard with stats: total posts, scheduled, published, drafts, avg likes
```

---

## 📁 FOLDER STRUCTURE

```
instagram-cms/
├── static/
│   ├── css/
│   │   └── style.css
│   ├── js/
│   │   └── main.js
│   └── images/
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── add_post.html
│   ├── list_posts.html
│   ├── detail_post.html
│   ├── analytics.html
│   └── success.html
├── app.py
├── schema.sql
├── requirements.txt
├── Procfile
├── runtime.txt
└── README.md
```

---

## 🗃️ DATABASE SCHEMA (`schema.sql`)

```sql
CREATE TABLE IF NOT EXISTS posts (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    username     TEXT NOT NULL,
    caption      TEXT NOT NULL,
    image_url    TEXT NOT NULL,
    status       TEXT NOT NULL DEFAULT 'draft',   -- draft / scheduled / published
    likes        INTEGER DEFAULT 0,
    reach        INTEGER DEFAULT 0,
    scheduled_at TEXT,
    created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS hashtags (
    id       INTEGER PRIMARY KEY AUTOINCREMENT,
    post_id  INTEGER NOT NULL,
    tag      TEXT NOT NULL,
    FOREIGN KEY (post_id) REFERENCES posts(id)
);

CREATE TABLE IF NOT EXISTS comments (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    post_id    INTEGER NOT NULL,
    commenter  TEXT NOT NULL,
    body       TEXT NOT NULL,
    type       TEXT NOT NULL DEFAULT 'comment',   -- comment / dm
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (post_id) REFERENCES posts(id)
);

CREATE TABLE IF NOT EXISTS analytics (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    followers     INTEGER NOT NULL,
    following     INTEGER NOT NULL,
    total_posts   INTEGER NOT NULL,
    avg_likes     REAL DEFAULT 0,
    avg_reach     REAL DEFAULT 0,
    recorded_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## ⚙️ BACKEND — `app.py`

Use this exact Flask boilerplate structure:

```python
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
        db.close()

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

# [ADD ALL ROUTES HERE]

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
```

Create routes for:
- `/` → Dashboard (post count stats + latest analytics snapshot)
- `/add-post` GET + POST → Form to add a new post (with hashtags as comma-separated input)
- `/posts` GET → List/search all posts, filter by status dropdown
- `/post/<int:id>` GET → Single post detail (full info + hashtags + comments/DMs)
- `/submit-comment/<int:id>` POST → Submit a comment or DM on a post (type field: comment/dm)
- `/delete-post/<int:id>` POST → Delete a post and its hashtags/comments
- `/analytics` GET → Analytics page (all recorded snapshots, latest follower stats)
- `/add-analytics` GET + POST → Form to log a new analytics snapshot
- `/success` GET → Confirmation page

**Route notes:**
- On `/add-post` POST: split hashtag input by comma, strip spaces, insert each into `hashtags` table linked to new `post_id`
- On `/posts` GET: support `?status=draft|scheduled|published` and `?q=` for caption search
- On `/` dashboard: show 5 stat cards (total posts, scheduled, published, drafts, latest follower count)
- On `/analytics` GET: fetch all rows from `analytics` table ordered by `recorded_at DESC`; also compute most-used hashtags with `GROUP BY tag ORDER BY COUNT(*) DESC LIMIT 5`

---

## 🌐 FRONTEND TEMPLATES

### `base.html`
- Bootstrap 5 CDN + jQuery 3.7 CDN
- Link `style.css` and `main.js`
- Navbar: brand "📸 InstaCMS", nav links: Home, Posts, Add Post, Analytics
- Navbar bg: dark (`bg-dark navbar-dark`)
- Collapsible hamburger on mobile
- Flash messages — `get_flashed_messages(with_categories=true)` → Bootstrap `.alert` with dismiss
- HTML comments: `<!-- navbar -->`, `<!-- flash messages -->`, `<!-- footer -->`
- Footer: "© 2024 Instagram CMS"

### `index.html` (Dashboard)
- Hero section with Instagram-style gradient background (purple → pink → orange)
- Heading "Instagram CMS", subtitle "Manage your posts, hashtags, analytics & comments in one place"
- 5 stat cards in a row: Total Posts / Scheduled / Published / Drafts / Latest Followers
- A "Create New Post" CTA button and "Browse Posts" button
- 4 feature highlight cards: Schedule Posts, Track Analytics, Hashtag Manager, Manage Comments & DMs

### `add_post.html`
- Form with `id="addForm"` POST to `/add-post`
- Fields:
  - Instagram Username (text, required)
  - Caption (textarea, required, max 2200 chars)
  - Image URL (text, required — just a URL input, no file upload)
  - Status (select: draft / scheduled / published)
  - Scheduled Date (date input, required only if status = scheduled)
  - Estimated Likes (number, optional)
  - Hashtags (text input, comma-separated e.g. `#travel, #photography`)
- Each field in `div.mb-3` with label + input + `<span class="error-msg"></span>`
- jQuery validates this form
- Submit button: "Save Post"

### `list_posts.html`
- Filter bar at top: status dropdown + caption search input + Submit button
- Bootstrap card grid `row-cols-1 row-cols-md-2 row-cols-lg-3 g-4` with Jinja2 loop
- Each post card shows:
  - Image (using `<img>` tag with the image_url, fallback placeholder if empty)
  - Username with 📸 icon
  - Caption (truncated to ~80 chars)
  - Status badge (color-coded: warning=draft, primary=scheduled, success=published)
  - Scheduled date if set
  - Likes count
  - "View Details" button
- Empty state `.alert.alert-info` if no posts

### `detail_post.html`
- Back button → `/posts`
- Left column (col-md-7): full post details card
  - Full image
  - Username, full caption
  - Status badge
  - Scheduled date, likes, created_at
  - Hashtags as Bootstrap badges (`#tag`)
  - List of all comments below
- Right column (col-md-5):
  - "Add a Comment / DM" form (`id="actionForm"` POST to `/submit-comment/<id>`)
  - Fields: Commenter Name (text), Type (select: comment / dm), Comment (textarea)
  - Submit button with spinner on click
  - Delete Post form (separate small form, POST to `/delete-post/<id>`, red button)

### `analytics.html`
- Page title "📊 Analytics"
- "Log New Snapshot" button → `/add-analytics`
- Latest snapshot card at top: Followers, Following, Total Posts, Avg Likes, Avg Reach
- Table of all past snapshots (recorded_at, followers, following, avg_likes, avg_reach)
- Top 5 hashtags section: list tags with their usage count as Bootstrap badges
- Empty state `.alert.alert-info` if no analytics recorded yet

### `add_analytics.html`
- Form with `id="addForm"` POST to `/add-analytics`
- Fields: Followers (number), Following (number), Total Posts (number), Avg Likes (number, decimal), Avg Reach (number, decimal)
- jQuery validates all fields are filled and numeric
- Submit button: "Log Snapshot"

### `success.html`
- Centered card, ✅ emoji, "Post Saved!" heading
- Subtext: "Your post has been added to the CMS. You can view it in the posts list."
- Two buttons: "Add Another Post" → `/add-post`, "View All Posts" → `/posts`
- Bootstrap Toast `id="successToast"` bottom-right, auto-show on load with message "Post added successfully!"

---

## 🎨 `static/css/style.css`

```css
/* instagram_cms - custom styles */
/* kept minimal, bootstrap handles most of it */

:root {
    --main-color: #833ab4;
    --accent-color: #fd1d1d;
    --dark-bg: #1a1a2e;
    --ig-gradient: linear-gradient(45deg, #f09433, #e6683c, #dc2743, #cc2366, #bc1888);
}

.hero-section {
    background: linear-gradient(135deg, #833ab4 0%, #fd1d1d 50%, #fcb045 100%);
    min-height: 420px;
    padding: 60px 0;
    color: white;
    display: flex;
    align-items: center;
}

.hero-section h1 {
    font-size: 2.5rem;
    font-weight: 700;
}

.item-card {
    transition: transform 0.2s, box-shadow 0.2s;
}

.item-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 8px 20px rgba(0,0,0,0.15) !important;
}

.accent-badge {
    background: var(--ig-gradient);
    color: white !important;
    padding: 4px 12px;
    border-radius: 20px;
    font-weight: 600;
    font-size: 0.9rem;
}

.hashtag-badge {
    background-color: #e8f4fd;
    color: #0d6efd;
    border-radius: 12px;
    padding: 3px 10px;
    font-size: 0.82rem;
    margin: 2px;
    display: inline-block;
}

.post-image {
    width: 100%;
    height: 200px;
    object-fit: cover;
    border-radius: 8px 8px 0 0;
}

.detail-image {
    width: 100%;
    max-height: 400px;
    object-fit: cover;
    border-radius: 8px;
    margin-bottom: 15px;
}

.stat-card {
    border-left: 4px solid var(--main-color);
    border-radius: 8px;
}

.field-error {
    border-color: #dc3545 !important;
}

.error-msg {
    color: #dc3545;
    font-size: 0.82rem;
    margin-top: 3px;
    display: block;
}

footer {
    background-color: #1a1a2e;
    color: #adb5bd;
    text-align: center;
    padding: 20px 0;
    margin-top: 50px;
}

.navbar-brand {
    font-weight: 700;
    font-size: 1.3rem;
}

/* tried this for debugging
border: 1px solid red; */
```

---

## ⚡ `static/js/main.js`

```javascript
// instagram_cms - main js
// form validation and small ui interactions

$(document).ready(function () {

    // highlight active nav link
    var currentPath = window.location.pathname;
    $('.navbar-nav .nav-link').each(function () {
        if ($(this).attr('href') === currentPath) {
            $(this).addClass('active');
        }
    });

    // set min date on scheduled date input to today
    var today = new Date().toISOString().split('T')[0];
    $('input[type="date"]').attr('min', today);

    // show/hide scheduled date field based on status dropdown
    var statusVal = $('#status').val();
    if (statusVal !== 'scheduled') {
        $('#scheduledDateGroup').hide();
    }
    $('#status').on('change', function () {
        if ($(this).val() === 'scheduled') {
            $('#scheduledDateGroup').show();
        } else {
            $('#scheduledDateGroup').hide();
            $('#scheduled_at').val('');
        }
    });

    // ---- add post form validation ----
    $('#addForm').on('submit', function (e) {
        e.preventDefault();
        var isValid = true;

        // clear old errors first
        $('.field-error').removeClass('field-error');
        $('.error-msg').text('');

        // validate username
        var username = $('#username').val().trim();
        if (username === '') {
            $('#username').addClass('field-error');
            $('#username').next('.error-msg').text('Username is required');
            isValid = false;
        }

        // validate caption
        var caption = $('#caption').val().trim();
        if (caption === '') {
            $('#caption').addClass('field-error');
            $('#caption').next('.error-msg').text('Caption cannot be empty');
            isValid = false;
        }

        // validate image url
        var imgUrl = $('#image_url').val().trim();
        if (imgUrl === '') {
            $('#image_url').addClass('field-error');
            $('#image_url').next('.error-msg').text('Image URL is required');
            isValid = false;
        }

        // if scheduled, check date is filled
        var status = $('#status').val();
        if (status === 'scheduled') {
            var schedDate = $('#scheduled_at').val();
            if (schedDate === '') {
                $('#scheduled_at').addClass('field-error');
                $('#scheduled_at').next('.error-msg').text('Please pick a scheduled date');
                isValid = false;
            }
        }

        // console.log(isValid);
        if (isValid) {
            this.submit();
        }
    });

    // ---- comment form validation ----
    $('#actionForm').on('submit', function (e) {
        e.preventDefault();
        let valid = true;

        $('.field-error').removeClass('field-error');
        $('.error-msg').text('');

        // check commenter name
        let commenter = $('#commenter').val().trim();
        if (commenter === '') {
            $('#commenter').addClass('field-error');
            $('#commenter').next('.error-msg').text('Name is required');
            valid = false;
        }

        // check comment body
        let body = $('#body').val().trim();
        if (body === '') {
            $('#body').addClass('field-error');
            $('#body').next('.error-msg').text('Comment cannot be empty');
            valid = false;
        }

        if (valid) {
            $('#submitBtn').html('<span class="spinner-border spinner-border-sm me-1"></span> Posting...');
            $('#submitBtn').prop('disabled', true);
            this.submit();
        }
    });

    // auto submit filter form on status change
    $('#statusFilter').on('change', function () {
        $(this).closest('form').submit();
    });

    // show toast on success page
    if ($('#successToast').length) {
        var toastEl = document.getElementById('successToast');
        var toast = new bootstrap.Toast(toastEl, { delay: 4000 });
        toast.show();
    }

});
```

---

## 📦 `requirements.txt`

```
Flask==3.0.3
gunicorn==21.2.0
```

---

## 🚀 HEROKU DEPLOYMENT FILES

### `Procfile` (no file extension, save exactly as `Procfile`)
```
web: gunicorn app:app
```

### `runtime.txt`
```
python-3.11.6
```

---

## 🗂️ GIT COMMIT SEQUENCE

**CRITICAL — USE FAKE DATES ON EVERY COMMIT.**

Every commit must use `GIT_AUTHOR_DATE` and `GIT_COMMITTER_DATE` to set a backdated timestamp. This makes GitHub show commits spread across 3 days. Vary the times slightly within each day (20–40 mins apart).

Use this exact pattern for every single commit — no exceptions:

```
GIT_AUTHOR_DATE="YYYY-MM-DDTHH:MM:00" GIT_COMMITTER_DATE="YYYY-MM-DDTHH:MM:00" git commit -m "message"
```

```bash
git init
git remote add origin https://github.com/YOUR_USERNAME/instagram-cms.git

# Day 1 - project setup (March 13)
git add README.md
GIT_AUTHOR_DATE="2025-03-13T09:45:00" GIT_COMMITTER_DATE="2025-03-13T09:45:00" git commit -m "initial commit"

git add requirements.txt schema.sql Procfile runtime.txt
GIT_AUTHOR_DATE="2025-03-13T10:20:00" GIT_COMMITTER_DATE="2025-03-13T10:20:00" git commit -m "added requirements, db schema and heroku config"

git add app.py
GIT_AUTHOR_DATE="2025-03-13T11:05:00" GIT_COMMITTER_DATE="2025-03-13T11:05:00" git commit -m "created flask app with routes for posts, comments and analytics"

git add templates/base.html
GIT_AUTHOR_DATE="2025-03-13T11:40:00" GIT_COMMITTER_DATE="2025-03-13T11:40:00" git commit -m "added base template with navbar and flash messages"

git add templates/index.html
GIT_AUTHOR_DATE="2025-03-13T14:15:00" GIT_COMMITTER_DATE="2025-03-13T14:15:00" git commit -m "added dashboard home page with stats cards"

# Day 2 - building pages (March 14)
git add templates/add_post.html
GIT_AUTHOR_DATE="2025-03-14T10:30:00" GIT_COMMITTER_DATE="2025-03-14T10:30:00" git commit -m "added add post form with hashtag input"

git add templates/list_posts.html
GIT_AUTHOR_DATE="2025-03-14T11:50:00" GIT_COMMITTER_DATE="2025-03-14T11:50:00" git commit -m "added posts list page with status filter and search"

git add templates/detail_post.html
GIT_AUTHOR_DATE="2025-03-14T13:10:00" GIT_COMMITTER_DATE="2025-03-14T13:10:00" git commit -m "added post detail page with comments and dm section"

git add templates/analytics.html templates/add_analytics.html
GIT_AUTHOR_DATE="2025-03-14T14:00:00" GIT_COMMITTER_DATE="2025-03-14T14:00:00" git commit -m "added analytics page and log snapshot form"

git add templates/success.html
GIT_AUTHOR_DATE="2025-03-14T15:10:00" GIT_COMMITTER_DATE="2025-03-14T15:10:00" git commit -m "added success page with toast notification"

git add static/css/style.css
GIT_AUTHOR_DATE="2025-03-14T16:25:00" GIT_COMMITTER_DATE="2025-03-14T16:25:00" git commit -m "added custom css with instagram gradient theme"

# Day 3 - js, bug fixes, cleanup (March 15)
git add static/js/main.js
GIT_AUTHOR_DATE="2025-03-15T09:55:00" GIT_COMMITTER_DATE="2025-03-15T09:55:00" git commit -m "added jquery validation for post, comment and analytics forms"

git add app.py
GIT_AUTHOR_DATE="2025-03-15T11:10:00" GIT_COMMITTER_DATE="2025-03-15T11:10:00" git commit -m "fixed bug in hashtag insert and analytics query"

git add templates/detail_post.html
GIT_AUTHOR_DATE="2025-03-15T12:30:00" GIT_COMMITTER_DATE="2025-03-15T12:30:00" git commit -m "fixed edge case when post has no hashtags or comments"

git add static/css/style.css templates/base.html
GIT_AUTHOR_DATE="2025-03-15T14:45:00" GIT_COMMITTER_DATE="2025-03-15T14:45:00" git commit -m "small ui fixes and mobile responsiveness tweaks"

git add README.md
GIT_AUTHOR_DATE="2025-03-15T15:20:00" GIT_COMMITTER_DATE="2025-03-15T15:20:00" git commit -m "updated readme with setup instructions"

git add .
GIT_AUTHOR_DATE="2025-03-15T16:00:00" GIT_COMMITTER_DATE="2025-03-15T16:00:00" git commit -m "final cleanup before submission"

git push -u origin main
```

---

## ☁️ HEROKU DEPLOY (via MCP)

After pushing to GitHub, use the Heroku MCP to:
1. Create a new Heroku app named `instagram-cms-app`
2. Set buildpack to Python
3. Connect the GitHub repo
4. Deploy the `main` branch
5. Open and verify the live URL

Do all steps via MCP tools. Do not stop to ask for confirmation.

---

## 📝 `README.md`

Write in a genuine student voice. Include:
- Project title: "Instagram CMS" and 1-line description
- Tech stack: Flask, SQLite, Bootstrap 5, jQuery
- Features list:
  - Schedule and manage Instagram posts with caption, image URL, status and hashtags
  - Filter posts by status (draft / scheduled / published) and search by caption
  - View post details with hashtag badges, comments and DMs
  - Submit comments or DMs on any post
  - Delete posts (removes linked hashtags and comments too)
  - Analytics tracker — log follower snapshots and view history
  - Top 5 most-used hashtags on the analytics page
  - Dashboard with live stats: total posts, scheduled, published, drafts, latest followers
- Folder structure (code block)
- How to Run (numbered steps: clone, venv, pip install, python app.py, open browser)
- Short notes at bottom

---

## ✅ ACCEPTANCE CRITERIA

- [ ] `python app.py` runs without errors, DB auto-created
- [ ] Add Post form works end to end (post + hashtags saved correctly)
- [ ] Posts list page filters by status and searches by caption
- [ ] Post detail shows image, hashtags as badges, and all comments/DMs
- [ ] Comment/DM type dropdown saved correctly in `comments` table
- [ ] Delete post removes post + its hashtags + comments
- [ ] Analytics page shows all snapshots + top 5 hashtags
- [ ] Log Snapshot form saves to `analytics` table
- [ ] Dashboard shows correct counts for total/scheduled/published/draft posts + latest followers
- [ ] jQuery validation blocks empty/invalid fields on all forms
- [ ] Scheduled date field shows/hides based on status dropdown selection
- [ ] Flash messages show on success and error
- [ ] Navbar highlights active page (Home, Posts, Add Post, Analytics)
- [ ] Mobile responsive
- [ ] 17 commits in order with correct fake dates pushed to `main`
- [ ] GitHub commit history shows 3 different days (March 13, 14, 15)
- [ ] `Procfile` and `runtime.txt` present for Heroku
- [ ] Code has student-style comments, mixed `var`/`let`, commented debug lines
- [ ] README is complete

---

## 🚫 DO NOT

- Do NOT use React, Vue, or any JS framework
- Do NOT add login/auth
- Do NOT write production-grade perfect code — keep it student-realistic
- Do NOT add docstrings or Python type hints
- Do NOT remove commented-out `print()` and `console.log()`
- Do NOT use more than ~70 lines of custom CSS
- Do NOT ask permission before any step — just build it
- Do NOT use today's real date on commits — always use the fake backdated timestamps
- Do NOT add file upload for images — just use a URL text input
