# sellix-ecommerce
# A project for Database-431

# Sellix Ecommerce Platform

A comprehensive multi-vendor ecommerce platform built with Flask, featuring seller shops, product management, order processing, and custom page creation.

## 🚀 Features

### **Core Functionality**
- **Multi-vendor marketplace** with individual seller shops
- **Product catalog** with categories, images, and inventory management
- **Shopping cart** and checkout system
- **Order management** for both customers and sellers
- **User authentication** with email verification
- **Admin dashboard** for platform management

### **Seller Features**
- **Seller registration** and shop setup
- **Product management** (add, edit, delete products)
- **Order tracking** and status updates
- **Custom shop pages** with slug-based URLs
- **Shop customization** (logo, banner, theme colors)
- **Inventory management** with stock tracking

### **Customer Features**
- **Product browsing** with search and filtering
- **Shopping cart** functionality
- **Order placement** and tracking
- **Product reviews** and ratings
- **User profile** management

### **Admin Features**
- **User management** (view, edit, toggle admin status)
- **Seller verification** and management
- **Category management** (hierarchical categories)
- **Product oversight** and moderation
- **Order monitoring** and status updates
- **Platform analytics** and statistics

## 🛠️ Technology Stack

- **Backend**: Flask (Python)
- **Database**: MySQL with PyMySQL
- **Authentication**: Flask sessions with password hashing
- **Email**: Flask-Mail for verification emails
- **File Uploads**: Werkzeug for secure file handling
- **Frontend**: HTML templates with Bootstrap (assumed)

## 📋 Prerequisites

- Python 3.7+
- MySQL Server
- SMTP server for email verification (Gmail recommended)

## ⚙️ Installation

### 1. Clone the Repository
```bash
git clone <repository-url>
cd sellix-ecommerce
```

### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Database Setup
```bash
# Create MySQL database
mysql -u root -p
CREATE DATABASE ecommerce;
exit
```

### 5. Environment Configuration
Create a `.env` file in the project root:
```env
SECRET_KEY=your-secret-key-here
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your-mysql-password
DB_NAME=ecommerce

# Email Configuration
MAIL_USERNAME=your-gmail@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_DEFAULT_SENDER=your-gmail@gmail.com
SECURITY_PASSWORD_SALT=your-salt-here
```

### 6. Initialize Database
The application will automatically create tables on first run using the `db.sql` schema.

### 7. Run the Application
```bash
python app.py
```

The application will be available at `http://localhost:5000`

## 📁 Project Structure

```
sellix-ecommerce/
├── app.py                 # Main application file
├── config.py              # Configuration settings
├── models.py              # Database models
├── db.sql                 # Database schema
├── requirements.txt       # Python dependencies
├── routes/
│   ├── auth.py           # Authentication routes
│   ├── market.py         # Marketplace routes
│   ├── seller.py         # Seller dashboard routes
│   ├── admin.py          # Admin panel routes
│   └── pages_route.py    # Custom page routes
├── static/
│   └── uploads/          # File upload directory
└── templates/            
```

## 🗄️ Database Schema

### Core Tables
- **users**: User accounts and authentication
- **sellers**: Seller profiles and shop information
- **products**: Product catalog with pricing and inventory
- **categories**: Hierarchical product categories
- **orders**: Customer orders and order tracking
- **cart**: Shopping cart items
- **pages**: Custom seller pages
- **reviews**: Product reviews and ratings

### Key Features
- **Foreign key relationships** for data integrity
- **Indexing** for optimized search performance
- **Stored procedures** for complex queries
- **Database views** for simplified data access

## 🔐 Authentication & Security

### User Authentication
- **Registration** with email verification
- **OTP-based email verification** (6-digit codes)
- **Password hashing** using Werkzeug
- **Session management** with Flask sessions
- **Role-based access control** (Customer, Seller, Admin)

### Security Features
- **Input validation** and sanitization
- **Secure file uploads** with type restrictions
- **CSRF protection** through form tokens
- **SQL injection prevention** with parameterized queries

## 🛍️ Marketplace Features

### Product Management
- **Multi-image support** with primary image selection
- **Category assignment** with hierarchical structure
- **Inventory tracking** with stock quantities
- **Pricing options** including discount pricing
- **Product activation/deactivation**

### Order Processing
- **Cart management** with real-time updates
- **Checkout process** with shipping information
- **Order status tracking** (pending, processing, shipped, delivered)
- **Payment status** (pending, paid, failed, refunded)
- **Multi-seller order support**

### Search & Discovery
- **Product search** by name and description
- **Category filtering**
- **Pagination** for large product catalogs
- **Related products** suggestions

## 👥 User Roles & Permissions

### **Customer**
- Browse products and categories
- Add items to cart and place orders
- Leave product reviews
- Manage profile information

### **Seller**
- Create and manage product listings
- Process and fulfill orders
- Create custom shop pages
- Customize shop appearance
- View sales analytics

### **Admin**
- Manage all users and sellers
- Moderate products and reviews
- Manage categories
- Access platform analytics
- System configuration

## 🎨 Custom Shop Pages

Sellers can create custom pages for their shops:
- **Slug-based URLs** for SEO-friendly links
- **Rich content** support
- **Publish/unpublish** functionality
- **Shop navigation** integration

## 📧 Email System

### Verification Emails
- **Registration confirmation** with OTP
- **Email change verification**
- **Password reset** (if implemented)

### Configuration
Supports Gmail SMTP with app passwords for secure email delivery.

## 🔧 Configuration Options

### Upload Settings
- **File types**: PNG, JPG, JPEG, GIF
- **Max file size**: 16MB
- **Upload directory**: `static/uploads/`

### Pagination
- **Items per page**: 12 (configurable)

### Session Management
- **Session lifetime**: 7 days
- **Secure session handling**

## 🚀 Deployment

### Production Considerations
1. **Environment Variables**: Use production-grade secret keys
2. **Database**: Configure MySQL for production use
3. **File Storage**: Consider cloud storage for uploads
4. **Email Service**: Use reliable SMTP service
5. **SSL/HTTPS**: Enable secure connections
6. **Load Balancing**: For high-traffic scenarios

### Docker Deployment (Optional)
Create a `Dockerfile` and `docker-compose.yml` for containerized deployment.

## 🐛 Troubleshooting

### Common Issues
1. **Database Connection**: Verify MySQL credentials and server status
2. **Email Delivery**: Check SMTP settings and app passwords
3. **File Uploads**: Ensure upload directory permissions
4. **Session Issues**: Verify secret key configuration




