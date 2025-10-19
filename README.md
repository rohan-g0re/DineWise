# DineWise 🍽️

> **A comprehensive restaurant discovery and review platform that helps users find, compare, and review local restaurants using Yelp API data.**

DineWise is a full-stack web application that combines the power of Yelp's restaurant data with a personalized user experience. Users can search for restaurants, save favorites to their wishlist, write reviews, and discover new places through an interactive map interface.

## 🚀 Features

### Core Functionality
- **🔍 Advanced Restaurant Search**: Search by location, cuisine, price range, and ratings
- **📍 Interactive Map Locator**: Discover nearby restaurants with geolocation
- **❤️ Personal Wishlist**: Save favorite restaurants for later
- **⭐ Community Reviews**: Write and read user-generated reviews
- **👤 User Profiles**: Manage personal reviews and wishlist
- **🏙️ NYC Borough Support**: Optimized search for Manhattan, Brooklyn, Queens, Bronx, and Staten Island

### Technical Features
- **🔐 Firebase Authentication**: Secure user registration and login
- **📱 Responsive Design**: Mobile-first interface with Tailwind CSS
- **⚡ Real-time Data**: Live Yelp API integration with intelligent caching
- **🗺️ Interactive Maps**: Leaflet-powered restaurant discovery
- **🎯 Smart Caching**: Reduced API calls with PostgreSQL caching

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React Frontend │    │  FastAPI Backend │    │ Supabase Postgres│
│                 │    │                 │    │                 │
│ • TypeScript    │◄──►│ • Python 3.13   │◄──►│ • PostgreSQL    │
│ • Tailwind CSS  │    │ • SQLModel      │    │ • Alembic       │
│ • React Query   │    │ • Firebase Auth │    │ • Caching       │
│ • Leaflet Maps  │    │ • Yelp API      │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │
         │                       │
         ▼                       ▼
┌─────────────────┐    ┌─────────────────┐
│  Firebase Auth  │    │   Yelp Fusion   │
│                 │    │      API        │
│ • Email/Password│    │ • Business Data │
│ • JWT Tokens    │    │ • Reviews       │
│ • User Mgmt     │    │ • Photos        │
└─────────────────┘    └─────────────────┘
```

## 🛠️ Tech Stack

### Frontend
- **React 19** with TypeScript
- **Vite** for fast development and building
- **Tailwind CSS** for styling
- **React Router** for navigation
- **React Query** for data fetching
- **Leaflet** for interactive maps
- **Firebase SDK** for authentication

### Backend
- **FastAPI** with Python 3.13
- **SQLModel** for database ORM
- **PostgreSQL** (Supabase) for data storage
- **Alembic** for database migrations
- **Firebase Admin SDK** for authentication
- **Yelp Fusion API** for restaurant data
- **Pydantic** for data validation

### Infrastructure
- **Supabase** for PostgreSQL hosting
- **Firebase** for authentication
- **Yelp Fusion API** for restaurant data

## 📋 Prerequisites

- **Node.js** 18+ and npm
- **Python** 3.13+
- **PostgreSQL** database (or Supabase account)
- **Firebase** project
- **Yelp Fusion API** key

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/dinewise-mvp.git
cd dinewise-mvp
```

### 2. Backend Setup
```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp env.template .env
# Edit .env with your database URL, Yelp API key, and Firebase config

# Run database migrations
alembic upgrade head

# Start the development server
uvicorn app.main:app --reload
```

### 3. Frontend Setup
```bash
cd frontend

# Install dependencies
npm install

# Set up environment variables
cp env.template .env.local
# Edit .env.local with your Firebase config and API URLs

# Start the development server
npm run dev
```

### 4. Access the Application
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## 🔧 Configuration

### Environment Variables

#### Backend (.env)
```env
# Database
DATABASE_URL=postgresql://user:password@host:port/database

# API Keys
YELP_API_KEY=your_yelp_api_key_here

# Firebase (for server-side verification)
FIREBASE_PROJECT_ID=your_firebase_project_id
FIREBASE_PRIVATE_KEY=your_firebase_private_key
FIREBASE_CLIENT_EMAIL=your_firebase_client_email

# Server Configuration
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
FRONTEND_URL=http://localhost:5173

# CORS Origins
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

#### Frontend (.env.local)
```env
# Firebase Configuration
VITE_FIREBASE_API_KEY=your_firebase_api_key
VITE_FIREBASE_AUTH_DOMAIN=your_project.firebaseapp.com
VITE_FIREBASE_PROJECT_ID=your_firebase_project_id
VITE_FIREBASE_STORAGE_BUCKET=your_project.appspot.com
VITE_FIREBASE_MESSAGING_SENDER_ID=your_sender_id
VITE_FIREBASE_APP_ID=your_app_id

# API Configuration
VITE_API_BASE_URL=http://localhost:8000
```

## 📊 Database Schema

The application uses 5 main tables:

1. **Users**: User authentication and profile data
2. **Restaurant Cache**: Cached restaurant data from Yelp
3. **Wishlist**: User's saved restaurants
4. **Reviews**: Community reviews for restaurants
5. **User Restaurant Flags**: User preferences (visited, promo opt-in)

See [docs/data_model.md](docs/data_model.md) for detailed schema information.

## 🔌 API Documentation

The API provides comprehensive endpoints for:

- **Authentication**: User login and profile management
- **Search**: Restaurant search with advanced filtering
- **Restaurants**: Detailed restaurant information
- **Wishlist**: Personal restaurant collections
- **Reviews**: Community review system
- **Flags**: User preferences and settings

See [docs/api_contract.md](docs/api_contract.md) for complete API documentation.

## 🗺️ NYC Borough Support

DineWise is optimized for New York City with cached data for all 5 boroughs:

- **MAN**: Manhattan
- **BK**: Brooklyn  
- **QN**: Queens
- **BX**: Bronx
- **SI**: Staten Island

Searching within these boroughs uses cached data for faster results, while custom locations use live Yelp API calls.

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest
```

### Frontend Tests
```bash
cd frontend
npm test
```

## 📦 Deployment

### Backend Deployment
1. Set up PostgreSQL database (Supabase recommended)
2. Configure environment variables
3. Run database migrations
4. Deploy to your preferred platform (Railway, Heroku, etc.)

### Frontend Deployment
1. Build the application: `npm run build`
2. Deploy to Vercel, Netlify, or your preferred platform
3. Configure environment variables

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'Add amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Yelp Fusion API** for comprehensive restaurant data
- **Firebase** for authentication services
- **Supabase** for PostgreSQL hosting
- **React** and **FastAPI** communities for excellent documentation

## 📞 Support

If you have any questions or need help, please:

1. Check the [documentation](docs/)
2. Search existing [issues](https://github.com/your-username/dinewise-mvp/issues)
3. Create a new issue if needed

---

**Built with ❤️ for food lovers everywhere** 🍕🍜🍔
