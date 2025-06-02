POS System
A modern Point of Sale system built with Vue.js frontend and Django backend, using MongoDB for data storage.
Tech Stack

Frontend: Vue.js with Vite
Backend: Django REST Framework
Database: MongoDB (local development) / MongoDB Atlas (production)
Deployment: Netlify (frontend) + Render (backend)

Project Structure
PANN_POS/
├── frontend/              # Vue.js application
│   ├── src/
│   ├── public/
│   ├── package.json
│   └── vite.config.js
├── backend/               # Django application
│   ├── posbackend/        # Django project
│   ├── settings/          # Organized settings
│   │   ├── base.py        # Common settings
│   │   ├── local.py       # Development settings
│   │   └── production.py  # Production settings
│   ├── api/               # API endpoints
│   ├── venv/              # Virtual environment
│   └── manage.py
├── .gitignore
└── README.md
Prerequisites
Before setting up the project, ensure you have:

Node.js (v16 or higher) - Download here
Python (v3.9 or higher) - Download here
Git - Download here
MongoDB Community Edition - Download here

Installation & Setup
1. Clone the Repository
bashgit clone https://github.com/yourusername/PANN_POS.git
cd PANN_POS
2. Backend Setup (Django)
bash# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# For Windows Command Prompt:
venv\Scripts\activate
# For Git Bash/Mac/Linux:
source venv/Scripts/activate

# Install Python dependencies
pip install django djangorestframework django-cors-headers pymongo djongo python-decouple pytz dnspython

# Run migrations (creates initial database tables)
python manage.py migrate

# Create a superuser (optional, for admin access)
python manage.py createsuperuser

# Start the development server
python manage.py runserver
The Django backend will be running at http://localhost:8000
3. Frontend Setup (Vue.js)
bash# Open a new terminal and navigate to frontend directory
cd frontend

# Install Node.js dependencies
npm install

# Install additional packages (if not already included)
npm install axios

# Start the development server
npm run dev
The Vue frontend will be running at http://localhost:5173
4. Database Setup
Option A: Local MongoDB

MongoDB should automatically start as a Windows service after installation
The app will connect to mongodb://localhost:27017 by default

Option B: MongoDB Atlas (Cloud)

Create account at MongoDB Atlas
Create a new cluster
Get your connection string
Update settings/local.py with your Atlas connection string

Environment Configuration
Backend Environment Variables
Create a .env file in the backend/ directory:
envDEBUG=True
SECRET_KEY=your-secret-key-here
DATABASE_URL=mongodb://localhost:27017/pos_system_dev
Frontend Environment Variables
Create a .env file in the frontend/ directory:
envVITE_API_URL=http://localhost:8000/api
Testing the Connection

Make sure both servers are running:

Backend: http://localhost:8000
Frontend: http://localhost:5173


Test the API endpoint directly:

Visit: http://localhost:8000/api/status/
You should see: {"message": "POS System API is running!", "status": "active", "version": "1.0.0"}


Test frontend-backend connection:

Go to the Vue app at http://localhost:5173
Click the "Test Backend Connection" button
You should see the API response displayed



Development Workflow
Daily Development Setup
bash# Terminal 1: Backend
cd backend
source venv/Scripts/activate  # or venv\Scripts\activate on Windows
python manage.py runserver

# Terminal 2: Frontend  
cd frontend
npm run dev
Common Commands
Backend Commands
bash# Create new Django app
python manage.py startapp app_name

# Make migrations after model changes
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Collect static files (for production)
python manage.py collectstatic
Frontend Commands
bash# Install new package
npm install package-name

# Build for production
npm run build

# Run linting
npm run lint

# Run tests
npm run test
API Endpoints

GET /api/status/ - Check API status
GET /admin/ - Django admin interface

Troubleshooting
Common Issues
1. Module not found errors:

Make sure virtual environment is activated: source venv/Scripts/activate
Reinstall dependencies: pip install -r requirements.txt

2. CORS errors:

Check that corsheaders is installed and configured in settings
Verify frontend URL is in CORS_ALLOWED_ORIGINS

3. Database connection errors:

Ensure MongoDB is running: Check Windows Services for MongoDB
Verify connection string in settings

4. Port already in use:

Change port: python manage.py runserver 8001
Or kill existing process

5. Node modules issues:

Delete node_modules and run npm install again
Clear npm cache: npm cache clean --force