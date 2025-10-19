# 🚀 DineWise Quick Start Guide

Get DineWise running in **5 minutes**!

---

## ⚡ Fast Setup (Copy & Paste)

### 1️⃣ **Backend Setup** (Terminal 1)

```bash
# Navigate to backend
cd backend

# Activate virtual environment
# Windows PowerShell:
.\venv\Scripts\Activate.ps1
# Mac/Linux:
# source venv/bin/activate

# Start backend server
uvicorn app.main:app --reload
```

✅ Backend should be running at: **http://localhost:8000**

---

### 2️⃣ **Frontend Setup** (Terminal 2)

```bash
# Navigate to frontend
cd frontend

# Create environment file
copy .env.local.template .env.local
# Mac/Linux: cp .env.local.template .env.local

# Edit .env.local and add your Firebase credentials
# (See Firebase Setup below)

# Start frontend
npm run dev
```

✅ Frontend should be running at: **http://localhost:5173**

---

## 🔥 Firebase Setup (Required for Auth)

### Quick Firebase Setup:

1. **Go to**: https://console.firebase.google.com/
2. **Create a project** (or use existing)
3. **Enable Authentication**:
   - Click "Authentication" in left sidebar
   - Click "Get Started"
   - Enable "Email/Password" sign-in method
4. **Get your config**:
   - Click the gear icon → Project Settings
   - Scroll to "Your apps" → Web app
   - Copy the `firebaseConfig` values
5. **Paste into** `frontend/.env.local`:

```env
VITE_FIREBASE_API_KEY=your_api_key_here
VITE_FIREBASE_AUTH_DOMAIN=your-project.firebaseapp.com
VITE_FIREBASE_PROJECT_ID=your-project-id
VITE_FIREBASE_STORAGE_BUCKET=your-project.appspot.com
VITE_FIREBASE_MESSAGING_SENDER_ID=123456789
VITE_FIREBASE_APP_ID=1:123456789:web:abcdef
VITE_API_BASE_URL=http://localhost:8000
```

---

## 🎯 Testing the App

### 1. **Create an Account**
- Navigate to http://localhost:5173
- Click "Sign In" → "Sign up"
- Enter email, password, and name
- Submit!

### 2. **Search for Restaurants**
- Go to Home page
- Enter search query (e.g., "pizza")
- Enter location (e.g., "Manhattan")
- Click "Search Restaurants"

### 3. **View Restaurant Details**
- Click on any restaurant card
- View details, reviews, photos
- Add to wishlist ❤️
- Write a review ⭐

### 4. **Try the Map**
- Go to "Locator" page
- Allow location access
- See nearby restaurants on map
- Click markers for details

### 5. **Check Your Profile**
- Go to "My Profile"
- View your wishlist
- View your reviews
- Manage saved items

---

## 🔍 Quick Troubleshooting

### Backend won't start?
```bash
# Make sure you're in the backend directory
cd backend

# Check if database is running
# Check if .env file exists with DATABASE_URL
```

### Frontend won't start?
```bash
# Try reinstalling dependencies
npm install

# Check if .env.local exists
# Make sure port 5173 is not in use
```

### Can't sign in?
- Check Firebase credentials in `.env.local`
- Check browser console for errors
- Verify Email/Password is enabled in Firebase Console

### No search results?
- Verify backend is running
- Check YELP_API_KEY in backend `.env`
- Try different search terms

---

## 📱 App Features to Try

✅ **Authentication**
- Sign up with email/password
- Sign in
- Password reset (via email)
- Sign out

✅ **Search & Browse**
- Text search with filters
- Filter by price ($, $$, $$$, $$$$)
- Filter by rating (3.0+, 4.0+, 4.5+)
- Filter by cuisine type

✅ **Restaurant Details**
- View full info
- Read Yelp reviews
- Read community reviews
- Write your own review
- Add to wishlist
- Mark as visited
- Opt-in to promos

✅ **Map Features**
- Find nearby restaurants
- Interactive markers
- Distance calculation
- Click markers for info

✅ **Profile Management**
- View wishlist
- Manage saved restaurants
- View all your reviews
- Delete reviews
- User statistics

---

## 🎨 API Documentation

Once backend is running, visit:
- **Interactive API Docs**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc

---

## 📦 What's Included

### Backend API (20+ endpoints)
- `/restaurants/{id}` - Get restaurant details
- `/wishlist` - Wishlist CRUD
- `/reviews` - Reviews CRUD
- `/flags` - User preference flags
- `/search/query` - Search restaurants
- `/auth/register` - User registration

### Frontend Pages
- **Home** - Search and discover
- **Locator** - Map-based search
- **Restaurant Details** - Full information
- **Profile** - Wishlist & reviews
- **Login** - Authentication

---

## 🔐 Security Notes

- Firebase handles authentication securely
- JWT tokens auto-attached to API requests
- Protected routes redirect to login
- Users can only delete their own reviews
- Backend validates all inputs

---

## 💡 Pro Tips

1. **Search Tips**:
   - Use specific terms: "italian pasta", "sushi bar"
   - Include neighborhood: "pizza brooklyn"
   - Combine filters for better results

2. **Map Usage**:
   - Allow location for best experience
   - Zoom in/out to adjust search area
   - Click markers for quick info

3. **Review Tips**:
   - Be descriptive in reviews
   - Rate honestly (1-5 stars)
   - Help other diners decide!

---

## 🆘 Need Help?

Check these files for detailed info:
- `IMPLEMENTATION_COMPLETE.md` - Full technical details
- `README.md` - Project overview
- `docs/api_contract.md` - API documentation

---

**🎉 You're all set! Enjoy using DineWise!**

Start exploring restaurants in NYC and sharing your dining experiences! 🍽️


