# ✅ PDEffer User Authentication & Account System Roadmap

This roadmap outlines all tasks required to implement secure, email-verified user authentication in a FastAPI backend.

---

## 🔧 Setup

- [ ] Set up a PostgreSQL or SQLite database for development
- [ ] Install auth dependencies:
  - `fastapi`, `sqlalchemy`, `passlib[bcrypt]`, `python-jose`, `email-validator`

---

## 🧱 Database Models

- [ ] Create a `User` model with fields:
  - `id`, `email`, `hashed_password`, `is_active`, `verification_code`, `created_at`
- [ ] Optionally add a `Document` model to store uploaded files tied to `user_id`

---

## 🔐 Password Security

- [ ] Implement password hashing with `passlib`
  - `hash_password(password)`
  - `verify_password(password, hashed)`

---

## 📩 Email Verification

- [ ] Create a function to generate a random verification code
- [ ] Add a utility to send email (via `smtplib`, Mailtrap, or SendGrid)
- [ ] Create `/signup` endpoint:
  - Validate input
  - Check for duplicates
  - Hash password
  - Store verification code
  - Send verification code to email
- [ ] Create `/verify-email` endpoint:
  - Accept email + code
  - Set `is_active = True` if code matches

---

## 🔐 Login System

- [ ] Create `/login` endpoint:
  - Verify email and password
  - Check `is_active`
  - Return signed JWT token

---

## 🪪 Token Authentication

- [ ] Use `python-jose` to:
  - Sign JWT with a secret key
  - Store user ID and expiration in token
- [ ] Create utility to extract user from token
- [ ] Protect authenticated routes with `Depends(get_current_user)`

---

## 🛡 Secure API Routes

- [ ] Protect these endpoints:
  - `/upload-pdf`
  - `/my-documents`
- [ ] Return HTTP 401/403 for unauthenticated access

---

## 🧪 Testing & Debugging

- [ ] Add test user data to DB (manual or script)
- [ ] Test:
  - Signup with valid/invalid email
  - Email delivery
  - Verification flow
  - Login with correct/wrong credentials
  - Accessing secure endpoints
- [ ] Log user events to console for debugging

---

## 🗃 Optional Enhancements

- [ ] Add password reset flow via email
- [ ] Add refresh tokens
- [ ] Add "resend verification email" endpoint
- [ ] Add frontend integration (e.g., login form, email input)
- [ ] Log registration/IP metadata for abuse detection

---

## 📦 Deployment Prep

- [ ] Store sensitive secrets in environment variables (`.env`)
- [ ] Use HTTPS for all traffic in production
- [ ] Rate-limit auth endpoints to prevent brute force
- [ ] Switch to production email provider (e.g., SendGrid)

---

_This roadmap will guide implementation of a secure, email-verified user account system for PDEffer. You can check off steps as you complete them._

