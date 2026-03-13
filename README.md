# Instagram CMS

A simple content management system for Instagram posts, built with Flask and SQLite.

## Tech Stack

- **Backend**: Flask (Python)
- **Database**: SQLite
- **Frontend**: Bootstrap 5, jQuery
- **Deployment**: Heroku (gunicorn)

## Features

- Schedule and manage Instagram posts with caption, image URL, status and hashtags
- Filter posts by status (draft / scheduled / published) and search by caption
- View post details with hashtag badges, comments and DMs
- Submit comments or DMs on any post
- Delete posts (removes linked hashtags and comments too)
- Analytics tracker — log follower snapshots and view history
- Top 5 most-used hashtags on the analytics page
- Dashboard with live stats: total posts, scheduled, published, drafts, latest followers

## Folder Structure

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

## How to Run

1. Clone the repo: `git clone <repo-url>`
2. Create a virtual environment: `python -m venv venv`
3. Activate it: `venv\Scripts\activate` (Windows) or `source venv/bin/activate` (Mac/Linux)
4. Install dependencies: `pip install -r requirements.txt`
5. Run the app: `python app.py`
6. Open browser at `http://localhost:5000`

## Notes

- Database is auto-created on first run
- Image upload is not supported — paste an image URL instead
- No login/auth required — this is a personal CMS tool
