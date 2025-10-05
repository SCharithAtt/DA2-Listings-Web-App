# DA2 Listings Web App - Frontend

A modern, feature-rich listings application built with React, TypeScript, and Vite.

## Features

### Authentication
- ✅ User registration and login
- ✅ JWT-based authentication
- ✅ Role-based access control (user/admin)
- ✅ Protected routes

### Listings Management
- ✅ View latest listings on homepage
- ✅ Browse by category
- ✅ Create new listings (authenticated users only)
- ✅ Upload images (required for listings)
- ✅ Edit and delete own listings
- ✅ Set expiry time (7/14/30/90 days)
- ✅ Add tags for better searchability

### Search
- ✅ Smart semantic search (handles typos)
- ✅ Fallback to keyword search
- ✅ Filter by category, city, tags
- ✅ Relevance scoring

### Analytics (Admin Only)
- ✅ Top cities
- ✅ Top categories
- ✅ Popular tags
- ✅ Daily new listings

## Pages

### Public Pages
- **Home** (`/`) - Browse latest listings, filter by category
- **Login** (`/login`) - User login
- **Register** (`/register`) - New user registration
- **Listing Detail** (`/listing/:id`) - View full listing details with image gallery
- **Search Results** (`/search`) - Smart search results

### Protected Pages (Login Required)
- **Create Listing** (`/create`) - Create new listing with image upload
- **My Listings** (`/my-listings`) - Manage your active listings

### Admin Pages
- **Analytics** (`/analytics`) - View aggregated statistics (admin only)

## Running the App

### Prerequisites
- Node.js 16+
- Backend API running on http://localhost:8000

### Setup
```bash
cd frontend
npm install
npm run dev
```

The app will be available at http://localhost:5173

### Environment Variables
Create a `.env` file in the frontend directory:
```
VITE_API_URL=http://localhost:8000
```

## Technology Stack
- **React 18** - UI library
- **TypeScript** - Type safety
- **Vite** - Build tool and dev server
- **React Router v6** - Client-side routing
- **Context API** - State management for auth

## User Flows

### Guest User
1. View homepage with latest listings
2. Browse by category
3. Search for listings
4. View listing details
5. Login or register to create listings

### Authenticated User
1. All guest abilities, plus:
2. Create new listings (title, description, image, expiry required)
3. View "My Listings"
4. Upload additional images to own listings
5. Delete own listings

### Admin User
1. All user abilities, plus:
2. Access analytics dashboard
3. View aggregated statistics

## Features Implemented

### ✅ Proper Routing
- Multiple pages with React Router
- Protected routes for authenticated users
- Admin-only routes

### ✅ Clean UI/UX
- Responsive design
- Modern card-based layout
- Sticky header with navigation
- Image galleries
- Category filtering
- Loading and error states

### ✅ Smart Search
- Semantic search by default (handles typos)
- Automatic fallback to keyword search
- Relevance scoring displayed

### ✅ Listing Requirements
- Title, description, image, expiry are mandatory
- Tags are optional
- Image preview before upload
- Multiple images supported

### ✅ User Management
- Persistent login (localStorage)
- JWT token management
- Role-based UI (show/hide based on permissions)

## API Integration

All API calls are made to the backend at `VITE_API_URL`:

- `POST /auth/register` - User registration
- `POST /auth/login` - User login
- `GET /listings` - List all listings
- `GET /listings/latest` - Latest listings
- `GET /listings/categories` - Available categories
- `GET /listings/:id` - Get listing details
- `POST /listings` - Create listing (auth required)
- `DELETE /listings/:id` - Delete listing (owner only)
- `POST /listings/:id/images` - Upload image (owner only)
- `GET /listings/me` - User's listings (auth required)
- `GET /listings/search/semantic` - Smart search
- `GET /listings/search/advanced` - Keyword search
- `GET /analytics/summary` - Analytics (admin only)

## Styling

Custom CSS with modern design system:
- CSS variables for theming
- Responsive grid layouts
- Smooth transitions and hover effects
- Mobile-first responsive design
- Gradient hero section
- Card-based layouts

## Notes

- Images are mandatory when creating listings (enforced in frontend)
- Semantic search requires backend `ENABLE_SEMANTIC_SEARCH=true`
- If semantic search fails, automatically falls back to keyword search
- Listings auto-expire based on selected expiry days
- Only active (non-expired) listings shown by default
