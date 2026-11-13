# YSR Shine Solutions

[![Copyright 2025](https://img.shields.io/badge/License-BUSL--1.1-orange.svg)](./LISENCE.md)

_If you like this project, please leave a star; it helps a lot!_

---

## Overview

[YSR Shine Solutions](https://ysrshinesolutions.com/) is a product catalog and contact platform for a cleaning solutions business.  
It combines a secure admin dashboard with an SEO-friendly customer experience, including infinite-scrolling product discovery and responsive layouts.

Built with **Flask**, **PostgreSQL**, **SQLite**, **Google Cloud Storage**, and **Google Cloud Run**, the project balances security, scalability, and usability in a production environment. It uses Google Cloud Run instances for deployment, custom SQLite-based security tokens and OTPs, and PostgreSQL for primary database management.

_Note: Page load speed may be impacted by current low-tier hosting configurations._

---

## Features

- **Product Catalog**
  - Products grouped by categories (tags).
  - Infinite scroll loads new categories without reloading the page.
  - SEO-friendly: initial categories are rendered server-side for indexing.

- **Admin Dashboard**
  - Secure login and role-based access (admin-only).
  - Add, edit, and delete products with names, descriptions, tags, and images.
  - Images uploaded to Google Cloud Storage using `secure_filename`.
  - Product–tag many-to-many relationship for flexible categorization.

- **Performance & UX**
  - Category-level pagination for efficient database queries.
  - Infinite scroll implemented with a custom JavaScript client.
  - Lazy product rendering to reduce initial load times.
  - Contact form with validation and CSRF protection.

- **Security**
  - CSRF protection across all forms and APIs.
  - Session-based tokens for publishing products.
  - Role-based admin access control.
  - Safe file handling with Werkzeug `secure_filename`.

---

## Tech Stack

- **Backend**: Flask, SQLAlchemy, Flask-Login, Flask-WTF  
- **Database**: PostgreSQL, SQLite
- **Frontend**: Jinja2, Vanilla JS (API calls, dynamic infinite scroll, animations), HTML5, CSS3  
- **Storage**: Google Cloud Storage (for product images)
- **Security**: CSRF protection, role-based access, secure file uploads
- **Hosting**: Google Cloud Run / Google Cloud VMs

---

## Screenshots

### Homepage – Hero & Contact
<img width="1905" height="992" alt="image" src="https://github.com/user-attachments/assets/700bcb06-a552-4d03-9ab1-10ec1a77e511" />
<img width="1897" height="990" alt="image" src="https://github.com/user-attachments/assets/c9d78805-ee53-44bc-861e-20906f609fd8" />

### Product Catalog with Infinite Scroll
<img width="1920" height="1080" alt="Screenshot 2026-01-13 170228" src="https://github.com/user-attachments/assets/1c26719f-da74-49a5-9085-2a96d7d9f84e" />
<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/4db235c8-da74-4d22-b81d-3d2ca1c2a259" />

### Admin Dashboard – Add Product
<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/6945d0d4-8fce-445c-b76d-67df681ccf32" />
<img width="1904" height="990" alt="image" src="https://github.com/user-attachments/assets/b3f31e16-7696-4118-a746-7051b8d01687" />

### Catalog Layout
<img width="1919" height="1079" alt="Screenshot 2026-01-13 170258" src="https://github.com/user-attachments/assets/86ed3a0b-35ab-489d-8bde-bcbe99bc93b2" />
<img width="1907" height="1079" alt="Screenshot 2026-01-13 170311" src="https://github.com/user-attachments/assets/566e7a4c-c193-46b1-b5fa-a94a6e15051f" />

### Responsive Design
<img width="410" height="897" alt="Screenshot 2026-01-13 170445" src="https://github.com/user-attachments/assets/a145dabd-cc81-4093-a062-133fbe3dbfd8" />
<img width="1620" height="840" alt="Screenshot 2026-01-13 170354" src="https://github.com/user-attachments/assets/a763c76c-f9fa-466e-9c02-43df13fd4d01" />
<img width="136" height="895" alt="Screenshot 2026-01-13 170543" src="https://github.com/user-attachments/assets/0f0148d5-788f-4b27-9cb1-6dde6d2ac944" />
<img width="417" height="899" alt="image" src="https://github.com/user-attachments/assets/85ec7fd2-c520-4520-bf9d-a8ac46fb2be2" />

---

## Important Disclaimer
**You are not permitted to clone this repository or use the code from it to deploy any commercial web applications or other software.**
For more information, see [The License](https://github.com/Charcoal4768/YSR/blob/main/LISENCE.md).
