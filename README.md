# Education Platform Backend

A complete Django backend for an educational platform that allows teachers to manage courses, materials, and live classes. The project follows SOLID principles and modern development best practices.

This version is fully Docker-ready, allowing you to run the project with minimal setup.
## 🚀 Features

### 👨‍🏫 For Teachers
- Course management (create, edit, manage)
- Upload documents, videos, and presentations
- Schedule and host live classes with integrated chat
- Manage student permissions
- Track engagement and statistics

### 👨‍🎓 For Students
- Enroll in courses
- Access and download study materials
- Join live classes
- Rate courses and teachers


## 🏗️ Architecture & Principles

The backend is built using Django REST Framework and follows SOLID principles:

- **S** - Single Responsibility Principle  
- **O** - Open/Closed Principle  
- **L** - Liskov Substitution Principle  
- **I** - Interface Segregation Principle  
- **D** - Dependency Inversion Principle  


## 🛠️ Technologies

- Django 4.2
- Django REST Framework
- PostgreSQL
- JWT authentication
- Redis (optional, caching)
- Docker & Docker Compose
- Swagger/OpenAPI


## 📁 Project Structure

```
backend/
├── core/ # Main settings and configuration
├── users/ # User app (models, serializers, views)
├── courses/ # Courses app
├── materials/ # Materials app
├── live_classes/ # Live classes app
├── manage.py # Django management script
├── requirements.txt # Python dependencies
├── Dockerfile # Docker image definition
├── docker-compose.yml # Docker services
└── README.md
```

## 📦 Docker Setup

### 1️⃣ Environment Variables

Create a `.env` file at the project root:

```env
  # Django
  DJANGO_SECRET_KEY=your-secret-key
  DJANGO_DEBUG=True
  DJANGO_ALLOWED_HOSTS=localhost 127.0.0.1 [::1]

  # Database
  DB_NAME=mydb
  DB_USER=myuser
  DB_PASSWORD=mypassword
  DB_HOST=postgres
  DB_PORT=5432
```

### 2️⃣ Build & Run

```bash
docker-compose up --build
```
- Django backend: http://localhost:8000
- PostgreSQL runs internally (postgres:5432)
- Redis runs internally (redis:6379)

### 3️⃣ Run Migrations & Create Superuser

```bash
# Apply migrations
docker-compose exec web python manage.py migrate

# Create admin user
docker-compose exec web python manage.py createsuperuser
```

## 📚 API Endpoints

### Authentication
  - `POST /api/v1/auth/register/` – Register user
  - `POST /api/v1/auth/login/` – Login
  - `POST /api/v1/auth/logout/` – Logout
  - `POST /api/v1/auth/token/refresh/` – Refresh token
  - `POST /api/v1/auth/change-password/` – Change password

### Users
- `GET /api/v1/profile/` - User profile
- `PUT /api/v1/profile/update/` - Atualizar perfil
- `GET /api/v1/teachers/` - Listar professores

### Courses
- `GET /api/v1/courses/` - List courses
- `POST /api/v1/courses/` - Create course (teacher)
- `GET /api/v1/courses/{id}/` - Course details
- `PUT /api/v1/courses/{id}/` - Update course (teacher)
- `POST /api/v1/courses/{id}/enroll/` - Enroll in course
- `POST /api/v1/courses/{id}/rate/` - Rate course

### Materials
- `GET /api/v1/materials/` - List materials
- `POST /api/v1/materials/` - Upload material (teacher)
- `GET /api/v1/materials/{id}/download/` - Download material
- `POST /api/v1/materials/{id}/view/` - Register view

### Live Classes
- `GET /api/v1/live-classes/` - List live classes
- `POST /api/v1/live-classes/` - Create live class (teacher)
- `POST /api/v1/live-classes/{id}/start/` - Start class (teacher)
- `POST /api/v1/live-classes/{id}/join/` - Join class
- `GET /api/v1/live-classes/{id}/messages/` - Class chat

### API Documentation
When running in Docker, access the docs at:
  - Swagger UI: http://localhost:8000/swagger/
  - ReDoc: http://localhost:8000/redoc/


## 📊 Data Models

### Users
- **User**: Custom user with types (teacher, student, admin)
- **Profile**: Personal information and preferences

### Courses
- **Category**: Course categories
- **Course**: Course information
- **CourseEnrollment**: Student enrollments
- **CourseRating**: Ratings and reviews

### Materials
- **Material**: Study files
- **MaterialFolder**: Folder organization
- **MaterialAccess**: Access control and statistics

### Live Classes
- **LiveClass**: Scheduling and configuration
- **LiveClassParticipant**: Participants and attendance
- **LiveClassMessage**: Live class chat
- **LiveClassRecording**: Class recordings


## 📝 API documentation

Access the interactive API documentation:

- **Swagger UI**: http://localhost:8000/swagger/
- **ReDoc**: http://localhost:8000/redoc/

``