# Small Table – Backend API

A backend system for managing catering and event food orders, built with Django and Django REST Framework.  
The system includes modules for users, roles, vendors, products, packages, addons, orders, and reviews.

## Technologies

- Python 3.12
- Django 5.x
- Django REST Framework
- JWT Authentication (SimpleJWT)
- django-filters
- PostgreSQL / SQLite
- Docker (optional)

## Project Structure
```
small-table-backend/
├── users/
├── roles/
├── user_roles/
├── vendors/
├── products/
├── packages/
├── addons/
├── orders/
├── reviews/
└── small_table_config/
```


## Main API Endpoints

### Users
GET /api/users/  
POST /api/users/  
GET /api/users/<id>/  
PUT /api/users/<id>/  
DELETE /api/users/<id>/  

### Vendors
GET /api/vendors/  
POST /api/vendors/  

### Products
GET /api/products/  
POST /api/products/  

### Packages
GET /api/packages/  
GET /api/package-categories/  

### Orders
GET /api/orders/  
POST /api/orders/  

## Setup & Installation

### Create Environment
```
git clone <repo-url>
cd small-table-backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### Run Server
```
python manage.py migrate
python manage.py runserver
```

### Create Admin User
```
python manage.py createsuperuser
```

## Testing Tools

- Postman
- Thunder Client
- Django REST Framework Browsable API

## Key Features

- User and role management
- JWT authentication
- Filtering with django-filters
- Product and package management
- Image upload support
- Modular REST API design
- Order price calculations

## Developed by
Rivka Asher  & Ayala Yeary

Full-Stack Developer (Django + React)
