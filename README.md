# UAPConnect

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Django](https://img.shields.io/badge/Django-5.1.4-green.svg)](https://www.djangoproject.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A recruitment platform for UAP CSE students to connect with job opportunities.

## Features
- User authentication (register, login, password reset)
- Job postings management
- Application tracking system
- Recruiter dashboard
- Email notifications

# Features

- **User Authentication**
  - Login/Logout
  - Register with email verification
  - Password reset functionality
  
- **Job Management**
  - Create/Update/Delete/List Job Adverts
  - Browse available jobs
  - Track your posted jobs
  
- **Application Tracking**
  - Apply to jobs
  - Track your applications
  - View application status
  
- **Recruiter Features**
  - Review applications
  - Reject or interview candidates
  - Manage job postings

- **Email Notifications**
  - Console-based email backend (verification codes shown in terminal)
  - Account verification via email code
  - Password reset links

## Quick Start

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/UAPConnect.git
   cd UAPConnect
   ```

2. Set up environment:
   ```bash
   python -m venv venv
   .\venv\Scripts\activate  # Windows
   # source venv/bin/activate  # Linux/Mac
   pip install -r requirements.txt
   ```

3. Configure `.env` file:
   ```
   SECRET_KEY=your-secret-key-here
   DEBUG=True
   ```

4. Run migrations and start server:
   ```bash
   python manage.py migrate
   python manage.py runserver
   ```

5. Access the site at `http://127.0.0.1:8000/`

## Screenshots





