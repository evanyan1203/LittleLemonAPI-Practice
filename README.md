# 🍋 Little Lemon API

A RESTful API built with **Django REST Framework** for managing restaurant menus, orders, and user authentication.

This project was developed as part of the **Meta Back-End Developer Professional Certificate** to demonstrate key back-end skills such as API design, database modeling, authentication, and testing.

---

## 🚀 Features
- User authentication with JWT
- CRUD operations for menu items and orders
- Role-based access control (Manager, Delivery Crew, Customer)
- Database integration with SQLite/PostgreSQL
- Unit tests using Django’s test framework
- REST API built following best practices

---

## 🛠️ Tech Stack
- **Python** (3.10+)
- **Django** (4.x)
- **Django REST Framework**
- **SQLite / PostgreSQL**
- **Docker (optional)**

---

## 📦 Installation

```bash
# Clone the repository
git clone https://github.com/evanyan1203/LittleLemonAPI-Practice.git
cd LittleLemonAPI-Practice

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run migrations and start the server
python manage.py migrate
python manage.py runserver
