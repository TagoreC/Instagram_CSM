# Instagram CMS

A minimalist, functional content management system for Instagram posts, built with Flask and SQLite. It provides role-based user management, post scheduling, media uploads, and analytics tracking.

## Tech Stack

- **Backend**: Flask (Python)
- **Database**: SQLite
- **Frontend**: HTML/CSS (Minimalist Design), JavaScript
- **Deployment Ready**: Includes `Procfile` and `runtime.txt` for Heroku/Gunicorn deployment.

## Key Features

- **User Authentication**: Secure login and registration flows.
- **Role-Based Access Control**: `admin` and `user` roles. Admins have an exclusive dashboard to add, view, and delete users.
- **Profile Management**: Customize your username, bio, and upload a profile photo. Track follower and following counts.
- **Post Management**: 
  - Create posts with captions, statuses (draft/scheduled/published), and scheduled times.
  - Support for local media file uploads (images & videos: png, jpg, mp4, etc.) or external image URLs.
  - Hashtag tracking.
- **User Interactions**: Submit comments on individual posts. 
- **Analytics Tracking**: Log snapshots of followers, reach, and total posts over time. View trends and top 5 most-used hashtags on the analytics page.
- **Dashboard**: Live stats overview including total posts, breakdown by status, and latest follower count.

## Folder Structure

```
instagram-cms/
├── static/
│   ├── css/
│   │   └── style.css
│   ├── js/
│   │   └── main.js
│   ├── images/
│   └── uploads/       # Created automatically for uploaded media
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── login.html
│   ├── profile.html
│   ├── admin_users.html
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

## How to Run Locally

1. **Clone the repository**: `git clone <repo-url>`
2. **Setup Virtual Environment**:
   - `python -m venv venv`
   - Activate on Windows: `venv\Scripts\activate`
   - Activate on Mac/Linux: `source venv/bin/activate`
3. **Install Dependencies**: `pip install -r requirements.txt`
4. **Run the Application**: `python app.py`
5. **Access the Application**: Open your web browser and navigate to `http://localhost:5000`

## Initial Setup & Notes

- **Database**: The SQLite database (`instagram_cms.db`) is auto-created and seeded on the first run.
- **Admin Account**: If no users exist in the database upon startup, a default admin account is automatically created:
  - **Username**: 
  - **Password**: 
  - **Role**: `admin`
- **Uploads**: Media uploads are saved locally in the `static/uploads/` directory, supporting a maximum size limit of 64MB.
##Deployment Link
https://instagram-csm.onrender.com
