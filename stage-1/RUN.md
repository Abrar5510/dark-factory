# Building and Running Pocketful Stage 1

## Prerequisites
- Docker
- Or Node.js 20+ and npm

## Using Docker (Recommended)

### Build the image
```bash
docker build -t pocketful-stage1 .
```

### Run the container
```bash
docker run -p 8080:8080 -e PORT=8080 pocketful-stage1
```

### With custom port
```bash
docker run -p 3000:3000 -e PORT=3000 pocketful-stage1
```

## Without Docker

### Install dependencies
```bash
npm ci
```

### Build TypeScript
```bash
npm run build
```

### Start the service
```bash
PORT=8080 npm start
```

## Health Check
Once running, the service will be available at:
```
GET http://localhost:8080/health
```

Response: `{"status": "ok"}`

## Test Reset Endpoint
```bash
POST http://localhost:8080/_test/reset
Content-Type: application/json

{
  "currency": "EUR",
  "minor_units": 2,
  "users": [
    {
      "id": "u_ada",
      "email": "ada@example.com",
      "password": "correct horse",
      "display_name": "Ada",
      "handle": "ada",
      "balance": 10000
    }
  ],
  "payments": [],
  "requests": []
}
```

## Notes
- The service uses SQLite in-memory database by default
- No persistent storage between restarts
- All data is lost when the container stops
- Use `/test/reset` to seed initial data