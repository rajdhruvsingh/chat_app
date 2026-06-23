# Chat App API

A team collaboration REST API built with Django and Django REST Framework — similar to a lightweight Slack/Discord backend.

**Live API:** https://chat-app-d3do.onrender.com/api/docs/

---

## Features

- **JWT Authentication** — register, login, token refresh
- **Workspaces** — create workspaces, invite/remove members with role-based access control
- **Role-Based Permissions** — Owner, Admin, and Member roles with different access levels
- **Channels** — create and manage channels within workspaces
- **Messages** — send and retrieve messages within channels
- **Reactions** — add/remove emoji reactions on messages (toggle behavior)
- **File Uploads** — attach files to messages
- **Notifications** — in-app notification system
- **Activity Logs** — track user actions across workspaces
- **Search** — search users by username or email
- **Filtering & Pagination** — filter messages by sender, search by content, paginated responses
- **Swagger Docs** — fully documented API with Swagger UI

---

## Tech Stack

- **Backend:** Python, Django, Django REST Framework
- **Database:** PostgreSQL
- **Authentication:** JWT (djangorestframework-simplejwt)
- **API Docs:** drf-spectacular (Swagger UI)
- **Testing:** pytest-django
- **Deployment:** Render

---

## API Endpoints

### Auth
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register/` | Register a new user |
| POST | `/api/auth/login/` | Login and receive JWT tokens |
| POST | `/api/auth/token/refresh/` | Refresh access token |

### Workspaces
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/workspaces/` | List user's workspaces |
| POST | `/api/workspaces/` | Create a workspace |
| GET | `/api/workspaces/<id>/` | Get workspace details |
| PUT | `/api/workspaces/<id>/` | Update workspace |
| DELETE | `/api/workspaces/<id>/` | Delete workspace |
| POST | `/api/workspaces/<id>/invite/` | Invite a member |
| DELETE | `/api/workspaces/<id>/members/<id>/remove/` | Remove a member |

### Channels
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/workspaces/<id>/channels/` | List channels |
| POST | `/api/workspaces/<id>/channels/` | Create a channel |
| GET | `/api/workspaces/<id>/channels/<id>/` | Get channel details |
| DELETE | `/api/workspaces/<id>/channels/<id>/` | Delete channel |

### Messages
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/workspaces/<id>/channels/<id>/messages/` | List messages |
| POST | `/api/workspaces/<id>/channels/<id>/messages/` | Send a message |
| PUT | `/api/workspaces/<id>/channels/<id>/messages/<id>/` | Edit message |
| DELETE | `/api/workspaces/<id>/channels/<id>/messages/<id>/` | Delete message |

### Other
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/messages/<id>/reactions/` | Add/remove reaction |
| POST | `/api/attachments/upload/` | Upload file attachment |
| GET | `/api/notifications/` | List notifications |
| GET | `/api/activities/` | List activity logs |
| GET | `/api/search/?query=` | Search users |

---

## Local Setup

**Prerequisites:** Python 3.10+, PostgreSQL

**1. Clone the repository:**
```bash
git clone https://github.com/yourusername/chat_app.git
cd chat_app
```

**2. Create virtual environment:**
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
```

**3. Install dependencies:**
```bash
pip install -r requirements.txt
```

**4. Create `.env` file:**
```
SECRET_KEY=your-secret-key-here
DEBUG=True
DATABASE_URL=your-postgresql-url-here
```

**5. Run migrations:**
```bash
python manage.py migrate
```

**6. Start server:**
```bash
python manage.py runserver
```

API will be available at `http://127.0.0.1:8000/api/`
Swagger docs at `http://127.0.0.1:8000/api/docs/`

---

## Running Tests

```bash
pytest chat/tests.py -v
```

8 tests covering authentication and role-based permissions.

---

## Design Decisions

**Custom User Model** — extended Django's `AbstractUser` to add avatar and verification fields while keeping all built-in auth functionality.

**Role-Based Access Control** — three roles (Owner, Admin, Member) with different permissions. Only owners and admins can invite/remove members and create/delete channels.

**JWT Authentication** — stateless token-based auth using `djangorestframework-simplejwt`. Access tokens are short-lived; refresh tokens allow seamless re-authentication.

**Nested URL Structure** — channels live under workspaces, messages live under channels. This enforces the data hierarchy at the URL level and makes permissions easier to reason about.

**Reaction Toggle** — using `get_or_create` to handle reactions means a single endpoint both adds and removes reactions, keeping the API clean.

---

## Project Structure

```
chat_app/
├── chat/
│   ├── models.py        # User, Workspace, Channel, Message, etc.
│   ├── serializers.py   # DRF serializers for all models
│   ├── views.py         # API views and viewsets
│   ├── urls.py          # App-level URL routing
│   └── tests.py         # pytest test suite
├── chat_app/
│   ├── settings.py      # Django settings
│   └── urls.py          # Project-level URL routing
├── requirements.txt
├── Procfile
└── README.md
```

---

## Author

Built by DHRUV RAJ SINGH — https://www.linkedin.com/in/dhruv-raj-singh-4b4575284/ | https://github.com/rajdhruvsingh