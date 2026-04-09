# 🚀 Kalpathon Hackathon  

## 📌 Submission  

# UVTech_VarunGaur  

---

## 👥 Team Name  
**UVTech**

---

## 💡 Project Name  
# FixBuddy 🔧  

---

## 🧭 Selected Track  
**Web Development**

---

## 📄 Selected Problem Statement (PS)  
**1. Neighbourhood Service Marketplace**

---

## 👑 Team Leader  
- **Name:** VARUN GAUR  
- **Phone:** 9569970915  

---

## 👨‍💻 Team Members & Roles  

| Name            | Role                              |
|-----------------|-----------------------------------|
| VARUN GAUR      | TEAM LEADER & FULL STACK          |
| UMA JAISHWAL    | AI EXPERT & FRONT-END DEVELOPER   |

---

## 📖 Project Description  

### 🏘️ Neighbourhood Service Marketplace  

Build a full-stack web startup platform connecting local service providers (plumbers, tutors, electricians, delivery agents) with customers.

---

## ❗ Problem  

In everyday life, people often find it difficult to get trusted local service providers like plumbers, electricians, tutors, or delivery helpers. Most of the time, they depend on word of mouth or random contacts, which is not always reliable or convenient.  

At the same time, many skilled workers don’t have a proper platform to showcase their services and reach more customers.

---

## 💡 Solution  

To solve this problem, we built a **Neighbourhood Service Marketplace**, a web platform that connects customers with nearby service providers.  

Users can easily search for services, view details, and book professionals based on their needs.  

Service providers can register on the platform, list their services, and manage bookings in one place.  

This makes the whole process **simpler, faster, and more organized** for both sides.

---

## ⭐ Key Features  

- Easy service booking system for users  
- Dedicated dashboard for service providers  
- Rating and review system to maintain trust and quality  

---

## 🛠️ Tech Stack  

- **Frontend:** HTML, CSS, Bootstrap  
- **Backend:** Django (Python)  
- **Database:** SQLite / MySQL  
- **Authentication:** Django built-in system  

---

## 🌍 Impact  

This project makes it easier for people to find reliable services in their local area without wasting time.  

It also helps small service providers grow their work by giving them an online presence.  

Overall, it creates a more **connected and efficient local service system**.

---

## 🚀 Deployment Guide

### Local Development Setup

#### Prerequisites
- Python 3.12+
- Git

#### Installation Steps

1. **Clone the repository:**
   ```bash
   git clone https://github.com/UVTech_VarunGaur/UVTech_VarunGaur.git
   cd UVTech_VarunGaur
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Run migrations:**
   ```bash
   python manage.py migrate
   ```

6. **Collect static files:**
   ```bash
   python manage.py collectstatic
   ```

7. **Run development server:**
   ```bash
   python manage.py runserver
   ```

### Production Deployment

#### Environment Variables Required

Create a `.env` file with the following variables:

```env
# Django Configuration
DJANGO_SECRET_KEY=your-50-character-secret-key
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Database Configuration (PostgreSQL recommended for production)
DB_NAME=uvtech_db
DB_USER=uvtech_user
DB_PASSWORD=your-db-password
DB_HOST=localhost
DB_PORT=5432

# Razorpay Payment Gateway
RAZORPAY_KEY_ID=rzp_live_your_key_id
RAZORPAY_KEY_SECRET=your_secret_key

# Email Configuration
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=noreply@yourdomain.com
```

#### Heroku Deployment

1. **Install Heroku CLI and login:**
   ```bash
   heroku login
   ```

2. **Create Heroku app:**
   ```bash
   heroku create your-app-name
   ```

3. **Set environment variables:**
   ```bash
   heroku config:set DJANGO_SECRET_KEY=your-secret-key
   heroku config:set DJANGO_DEBUG=False
   heroku config:set DJANGO_ALLOWED_HOSTS=your-app-name.herokuapp.com
   heroku config:set RAZORPAY_KEY_ID=your-razorpay-key
   heroku config:set RAZORPAY_KEY_SECRET=your-razorpay-secret
   ```

4. **Deploy:**
   ```bash
   git push heroku main
   ```

5. **Run migrations on Heroku:**
   ```bash
   heroku run python manage.py migrate
   heroku run python manage.py collectstatic --noinput
   ```

#### Other Deployment Options

**DigitalOcean App Platform:**
- Connect your GitHub repository
- Set environment variables in the dashboard
- Use the provided `Procfile` and `runtime.txt`

**AWS/DigitalOcean Droplet:**
- Install Python 3.12, PostgreSQL, Nginx
- Configure Gunicorn and Nginx
- Set up SSL certificates

### Security Features

- Environment-based configuration
- HTTPS enforcement in production
- Secure cookie settings
- CSRF protection
- XSS protection
- Content Security Policy ready

### Payment System

- **Razorpay Integration**: Complete payment gateway
- **Commission System**: 20% platform fee
- **QR Code Generation**: For payment verification
- **Provider Balance Tracking**: Earnings dashboard

---

## 🎥 Presentation

🔗 **Link:** [Add your presentation link here]

---
