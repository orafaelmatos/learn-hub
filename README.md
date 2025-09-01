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

### Autenticação
- `POST /api/v1/auth/register/` - Registro de usuário
- `POST /api/v1/auth/login/` - Login
- `POST /api/v1/auth/logout/` - Logout
- `POST /api/v1/auth/token/refresh/` - Renovar token
- `POST /api/v1/auth/change-password/` - Alterar senha

### Usuários
- `GET /api/v1/profile/` - Perfil do usuário
- `PUT /api/v1/profile/update/` - Atualizar perfil
- `GET /api/v1/teachers/` - Listar professores

### Cursos
- `GET /api/v1/courses/` - Listar cursos
- `POST /api/v1/courses/` - Criar curso (professor)
- `GET /api/v1/courses/{id}/` - Detalhes do curso
- `PUT /api/v1/courses/{id}/` - Atualizar curso (professor)
- `POST /api/v1/courses/{id}/enroll/` - Matricular em curso
- `POST /api/v1/courses/{id}/rate/` - Avaliar curso

### Materiais
- `GET /api/v1/materials/` - Listar materiais
- `POST /api/v1/materials/` - Upload de material (professor)
- `GET /api/v1/materials/{id}/download/` - Download de material
- `POST /api/v1/materials/{id}/view/` - Registrar visualização

### Aulas ao Vivo
- `GET /api/v1/live-classes/` - Listar aulas ao vivo
- `POST /api/v1/live-classes/` - Criar aula (professor)
- `POST /api/v1/live-classes/{id}/start/` - Iniciar aula (professor)
- `POST /api/v1/live-classes/{id}/join/` - Juntar-se à aula
- `GET /api/v1/live-classes/{id}/messages/` - Chat da aula

## 🔐 Autenticação

O projeto usa JWT (JSON Web Tokens) para autenticação:

```bash
# Login
curl -X POST http://localhost:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password"}'

# Usar token
curl -X GET http://localhost:8000/api/v1/profile/ \
  -H "Authorization: Bearer <your-access-token>"
```

## 📊 Modelos de Dados

### Usuários
- **User**: Usuário customizado com tipos (professor, aluno, admin)
- **Perfil**: Informações pessoais e preferências

### Cursos
- **Category**: Categorias de cursos
- **Course**: Informações do curso
- **CourseEnrollment**: Matrículas de alunos
- **CourseRating**: Avaliações e reviews

### Materiais
- **Material**: Arquivos de estudo
- **MaterialFolder**: Organização em pastas
- **MaterialAccess**: Controle de acesso e estatísticas

### Aulas ao Vivo
- **LiveClass**: Agendamento e configuração
- **LiveClassParticipant**: Participantes e presença
- **LiveClassMessage**: Chat durante a aula
- **LiveClassRecording**: Gravações das aulas

## 🧪 Testes

```bash
# Executar todos os testes
python manage.py test

# Executar testes de um app específico
python manage.py test users
python manage.py test courses
python manage.py test materials
python manage.py test live_classes
```

## 📝 Documentação da API

Acesse a documentação interativa da API:

- **Swagger UI**: http://localhost:8000/swagger/
- **ReDoc**: http://localhost:8000/redoc/

## 🚀 Deploy

### Produção

1. Configure as variáveis de ambiente para produção
2. Use um servidor WSGI como Gunicorn
3. Configure um proxy reverso (Nginx)
4. Use um banco PostgreSQL em produção
5. Configure Redis para cache e Celery

### Docker (opcional)

```bash
# Construir imagem
docker build -t education-platform .

# Executar container
docker run -p 8000:8000 education-platform
```

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## 📞 Suporte

Para suporte, envie um email para support@educationplatform.com ou abra uma issue no GitHub.

## 🔄 Changelog

### v1.0.0
- Implementação inicial do backend
- Sistema de autenticação JWT
- Gestão completa de cursos e materiais
- Sistema de aulas ao vivo
- API RESTful documentada
- Princípios SOLID aplicados 