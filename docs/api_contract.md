# DineWise API Contract

## Authentication

### Authorization Header
All protected endpoints require an `Authorization` header with a Firebase ID token:

```
Authorization: Bearer <firebase_id_token>
```

### Example
```bash
curl -X GET "http://localhost:8000/auth/me" \
  -H "Authorization: Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9..."
```

## Endpoints

### Authentication Endpoints

#### GET /auth/me
**Description:** Get current authenticated user information

**Headers:**
- `Authorization: Bearer <firebase_id_token>` (required)

**Response (200):**
```json
{
  "user_id": 1,
  "email": "user@example.com",
  "full_name": "John Doe",
  "firebase_uid": "abc123def456",
  "created_at": "2024-01-01T00:00:00"
}
```

**Response (401):**
```json
{
  "detail": "Invalid authentication token"
}
```

#### GET /auth/test
**Description:** Test authentication system status (public endpoint)

**Headers:** None required

**Response (200):**
```json
{
  "message": "Authentication system is running",
  "status": "ok",
  "endpoints": {
    "protected": "/auth/me (requires Authorization header)",
    "public": "/auth/test (no auth required)"
  }
}
```

### Health Endpoints

#### GET /health/
**Description:** Health check endpoint

**Response (200):**
```json
{
  "status": "ok"
}
```

### Root Endpoint

#### GET /
**Description:** API information and available endpoints

**Response (200):**
```json
{
  "message": "Welcome to DineWise API",
  "version": "1.0.0",
  "docs": "/docs",
  "health": "/health/",
  "auth": "/auth/"
}
```

## Error Responses

### 401 Unauthorized
```json
{
  "detail": "Not authenticated"
}
```

### 403 Forbidden
```json
{
  "detail": "Invalid authentication token"
}
```

### 422 Validation Error
```json
{
  "detail": [
    {
      "loc": ["body", "field_name"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

## Authentication Flow

1. **User logs in** with Firebase (frontend)
2. **Firebase returns** ID token
3. **Frontend sends** token in Authorization header
4. **Backend verifies** token with Firebase
5. **Backend creates/updates** user in database
6. **Backend returns** user information

## Token Format

Firebase ID tokens are JWT (JSON Web Token) format:
- **Header:** Contains algorithm and token type
- **Payload:** Contains user information and claims
- **Signature:** Verifies token authenticity

Example token structure:
```
eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJodHRwczovL3NlY3VyZXRva2VuLmdvb2dsZS5jb20vZGlud2lzZS1hcGkiLCJhdWQiOiJkaW53aXNlLWFwaSIsImF1dGhfdGltZSI6MTYzNDU2Nzg5MCwidXNlcl9pZCI6InRlc3QtdXNlci0xMjMiLCJzdWIiOiJ0ZXN0LXVzZXItMTIzIiwiaWF0IjoxNjM0NTY3ODkwLCJleHAiOjE2MzQ1NzE0OTAsImVtYWlsIjoidGVzdEBleGFtcGxlLmNvbSIsImVtYWlsX3ZlcmlmaWVkIjpmYWxzZSwiZmlyZWJhc2UiOnsiaWRlbnRpdGllcyI6eyJlbWFpbCI6WyJ0ZXN0QGV4YW1wbGUuY29tIl19LCJzaWduX2luX3Byb3ZpZGVyIjoicGFzc3dvcmQifX0.signature_here
```

## Development Notes

- **Base URL:** `http://localhost:8000`
- **API Documentation:** `http://localhost:8000/docs` (Swagger UI)
- **Firebase Project ID:** `serene-boulder-458623-n3`
- **CORS Origins:** `http://localhost:5173`, `http://localhost:3000`