# YSR Shine Solutions
[![License: BUSL-1.1](https://img.shields.io/badge/License-BUSL--1.1-orange.svg)](./LICENSE)
**Full-stack Flask platform for managing and showcasing cleaning products.**

⭐ _If you like this project, please leave a star; it helps a lot!_

---

## 🚀 Overview

[YSR Shine Solutions](https://ysrshinesolutions.com/) appears as the frist search result in google for "ysr shine" and "ysr shine solutions" with 0$ of advertisement budget.

YSR Shine Solutions is a product catalog and contact platform for a cleaning solutions business.  
It combines a secure admin dashboard with a smooth, SEO-friendly customer experience, including infinite scrolling product discovery. Responsive down to 50px viewport widths and has perfect core web vitals.

Built with **Flask**, **PostgreSQL**, and **Google Cloud Storage**, **Google Cloud VMs**, **PostgreSQL**, **SQLite** the project demonstrates how to balance security, scalability, and UX in a real-world business setting.
Uses Google Cloud VM instances with Gunicorn workers for production deplyoment.
Custom SQLite based security tokens and OTPs, PostgreSQL based database management

---

## ✨ Features

- **Product Catalog**
  - Products grouped by categories (tags).
  - Infinite scroll loads new categories seamlessly without reloading the page.
  - SEO-friendly: first categories rendered server-side for indexing.

- **Admin Dashboard**
  - Secure login and role-based access (admin-only).
  - Add/edit/delete products with name, description, tags, and images.
  - Images uploaded securely to Google Cloud Storage with `secure_filename`.
  - Product–tag many-to-many relationship for flexible categorization.

- **Performance & UX**
  - Category-level pagination for efficient database queries.
  - Infinite scroll implemented with a custom JavaScript client.
  - Lazy product rendering to minimize load times.
  - Contact form with validation and CSRF protection.

- **Security**
  - CSRF protection across all forms and APIs.
  - Session-based tokens for publishing products.
  - Role-based admin access control.
  - Safe file handling with Werkzeug `secure_filename`.

---

## 🛠️ Tech Stack

- **Backend**: Flask, SQLAlchemy, Flask-Login, Flask-WTF  
- **Database**: PostgreSQL, SQLite
- **Frontend**: Jinja2, Vanilla JS (api calls, dynamic infinite scroll, smooth animations, etc), HTML5, CSS3  
- **Storage**: Google Cloud Storage (for product images)
- **Security**: CSRF protection, role-based access, secure file uploads
- **Hosting**: Google Cloud VMs

---

## 📸 Screenshots

### Homepage – Hero & Contact
<img width="1905" height="992" alt="image" src="https://github.com/user-attachments/assets/700bcb06-a552-4d03-9ab1-10ec1a77e511" />
<img width="1897" height="990" alt="image" src="https://github.com/user-attachments/assets/c9d78805-ee53-44bc-861e-20906f609fd8" />


### Product Catalog with Infinite Scroll
<img width="1901" height="995" alt="image" src="https://github.com/user-attachments/assets/c78fa8a1-7fb6-4196-b1e7-53cc4220889f" />
<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/218a67c9-46eb-4081-acfa-2f96dd74d675" />


### Admin Dashboard – Add Product
<img width="1905" height="995" alt="image" src="https://github.com/user-attachments/assets/599cd642-7f7f-4fb3-b5ca-46dc7f103f2c" />
<img width="1904" height="990" alt="image" src="https://github.com/user-attachments/assets/b3f31e16-7696-4118-a746-7051b8d01687" />


---

## IMPORTANT DISCLAIMER
**YOU ARE NOT PERMITTED TO CLONE THIS REPO OR USE THE CODE FROM IT TO DEPLOY ANY COMMERCIAL WEB APPLICATIONS OR OTHER SOFTWARE.**
For more information, see: [The License](https://github.com/Charcoal4768/YSR/blob/main/LISENCE.md)
