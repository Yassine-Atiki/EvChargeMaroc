# EV Charge Maroc 🚗⚡

A Django-based web application for managing electric vehicle charging stations in Morocco. This platform connects EV owners with charging station providers, making it easier to find, book, and pay for charging services.

## Table of Contents 📑
- [Features](#features-)
- [Advanced Features](#advanced-features-)
- [Tech Stack](#tech-stack-)
- [Installation](#installation-)
- [Environment Variables](#environment-variables-)
- [Project Structure](#project-structure-)
- [API Integrations](#api-integrations-)
- [Contributing](#contributing-)
- [License](#license-)
- [Screenshots](#screenshots-)
- [Contact](#contact-)

## Features 🌟

- **User Authentication System**
  - Registration for both EV owners and station providers
  - Secure login and password reset functionality
  - Profile management

- **Station Management**
  - View available charging stations
  - Detailed station information (location, power, connectors)
  - Real-time availability status
  - Station ratings and reviews

- **Booking System**
  - Real-time slot booking
  - QR code generation for station access
  - Booking history

- **Payment Integration**
  - Secure payment processing with Stripe
  - Transaction history
  - Automated billing

- **Interactive Map**
  - Visual representation of charging stations
  - Station filtering and search
  - Distance calculation

## Advanced Features 🔥

- **Smart Booking System**
  - Dynamic time slot management
  - Automatic conflict detection
  - Real-time availability updates
  - Power consumption optimization
  - Intelligent pricing based on demand and time of day

- **Advanced Analytics**
  - Usage patterns and trends
  - Peak hours identification
  - Station performance metrics
  - User behavior analysis
  - Revenue and utilization reports

- **Intelligent Notifications**
  - Automated email reminders
  - Booking confirmation with QR codes
  - Low battery alerts for nearby stations
  - Maintenance schedules and alerts
  - Real-time status updates

- **Enhanced Security**
  - Multi-factor authentication
  - Session management
  - Secure payment processing
  - Data encryption
  - CSRF protection

- **Performance Optimization**
  - Caching system for faster loading
  - Optimized database queries
  - Lazy loading of images
  - Minified static files
  - Efficient API calls

## Tech Stack 💻

- **Backend**: Django 5.2
- **Database**: MySQL
- **Frontend**: HTML, CSS, JavaScript
- **Payment Processing**: Stripe
- **Maps Integration**: OpenChargeMap API
- **Email Service**: Gmail SMTP

## Installation 🚀

1. Clone the repository:
   ```bash
   git clone https://github.com/Yassine-Atiki/EvChargeMaroc.git
   cd EV_Charge_Maroc
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv env
   source env/bin/activate  # On Windows: env\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   - Copy `.env.example` to `.env`
   - Fill in your configuration values

5. Set up the database:
   ```bash
   python manage.py migrate
   ```

6. Create a superuser:
   ```bash
   python manage.py createsuperuser
   ```

7. Run the development server:
   ```bash
   python manage.py runserver
   ```

## Environment Variables ⚙️

Copy `.env.example` to `.env` and configure the following variables:

- Django Settings (SECRET_KEY, DEBUG, etc.)
- Database credentials
- Email configuration
- Stripe API keys
- OpenChargeMap API key

## Project Structure 📁

```
EV_Charge_Maroc/
├── Home/               # Home page and general views
├── users/             # User authentication and profiles
├── stations/          # Station management
├── payments/          # Payment processing
├── map/              # Map integration
├── help/             # Help and documentation
├── static/           # Static files (CSS, JS, images)
├── media/            # User-uploaded files
└── templates/        # HTML templates
```

## API Integrations 🔌

- **Stripe**: Payment processing
- **OpenChargeMap**: Station data and mapping
- **Gmail SMTP**: Email notifications

## Contributing 🤝

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License 📄

This project is licensed under the MIT License - see the LICENSE file for details.

## Screenshots 📸

[Screenshots will be added here]

## Contact 📧

**YASSINE ATIKI**
- Email: yassineatiki28@gmail.com
- LinkedIn: [@yassine-atiki](https://www.linkedin.com/in/yassine-atiki-b8a815332/)


Feel free to reach out for any questions or collaboration opportunities!