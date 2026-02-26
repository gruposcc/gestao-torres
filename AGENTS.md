# AGENTS.md

This file contains guidelines and commands for agentic coding agents working in this repository.

## Build/Test Commands

### Python Commands (using `uv`)
```bash
# Install Python dependencies
uv sync

# Run development server
uv run --env-file .env scripts/dev.py

# Create database migrations
alembic revision --autogenerate -m "message"
uv run --env-file .env alembic upgrade head

# Create admin user
uv run --env-file .env scripts/create_superuser.py

# Run specific Python file
uv run --env-file .env path/to/script.py
```

### JavaScript Commands (using `pnpm`)
```bash
# Install JavaScript dependencies
pnpm install

# Build CSS with TailwindCSS
pnpm run build.css

# Build JavaScript with Esbuild
pnpm run build.js

# Start development server (CSS + JS)
pnpm run dev

# Watch and rebuild JavaScript
pnpm run watch.js

# Watch and rebuild CSS
pnpm run watch.css
```

### Make Commands
```bash
# Run full stack development (frontend + backend)
make dev-full

# Run backend only
make dev

# Create admin user
make create_superuser

# Generate database migration
make migration

# Apply database migrations
make migrate

# Remove database volume
make prune_db

# Remove migration files
make prune_migrations
```

### Docker Commands
```bash
# Start PostgreSQL database
docker-compose up -d postgres
```

## Code Style Guidelines

### Python
- **Type hints**: Use Pydantic schemas for API models, SQLAlchemy models with type hints
- **Async/await**: All database operations must use async patterns
- **Import organization**: Standard library → third-party → local imports
- **Naming**: snake_case for variables/functions, PascalCase for classes
- **Error handling**: Use FastAPI HTTPException for API errors, structured logging

### JavaScript
- **ES modules**: Use import/export syntax throughout
- **Alpine.js**: Use x-data stores for state management, x-ref for DOM references
- **htmx.org**: Server-rendered HTML with minimal client-side JavaScript
- **Naming**: camelCase for variables/functions, kebab-case for HTML attributes
- **Error handling**: Use try/catch blocks, console.error for debugging

### CSS
- **TailwindCSS**: Utility-first approach, custom theme variables in app.css
- **DaisyUI**: Component library for consistent UI elements
- **Responsive design**: Mobile-first approach with Tailwind's responsive prefixes

## Project Structure

```
gestao-torres/
├── src/
│   ├── app.py                    # Main FastAPI application
│   ├── core/                     # Core utilities and configurations
│   ├── models/                   # SQLAlchemy models
│   ├── schemas/                  # Pydantic schemas
│   ├── services/                 # Business logic
│   ├── routes/                   # API routes (pages and htmx)
│   ├── templates/                # HTML templates
│   ├── static/                   # Static assets
│   └── alembic/                  # Database migrations
├── scripts/                      # Development scripts
├── dist/                         # Build output
├── uploads/                      # File uploads
└── .env.example                  # Environment variables template
```

## Database Patterns

- **UUID primary keys**: All models use UUID as primary key
- **StatusMixin**: Common status field for soft deletes
- **TimeStampMixin**: created_at and updated_at timestamps
- **Polymorphic models**: Client types (PF/PJ) using inheritance
- **Connection management**: Session manager with async context

## JavaScript Patterns

### Alpine.js Stores
```javascript
// Define store
Alpine.store('sidebar', {
  currentPath: window.location.pathname,
  // other state properties
});

// Use in component
x-data="sidebarStore"
```

### htmx Patterns
```html
<!-- Server-rendered form with HTMX -->
<form hx-post="/endpoint" hx-target="#content" hx-swap="innerHTML">
  <!-- form fields -->
</form>

<!-- Search with delay -->
<input 
  hx-post="/search" 
  hx-trigger="keyup changed delay:350ms" 
  hx-target="#results"
>
```

## Error Handling

### Python (FastAPI)
```python
from fastapi import HTTPException

async def get_item(item_id: str):
    item = await get_item_from_db(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item
```

### JavaScript (Alpine.js)
```javascript
const component = () => ({
  async doSomething() {
    try {
      const result = await someAsyncOperation();
      this.data = result;
    } catch (error) {
      console.error('Operation failed:', error);
      this.showError = true;
    }
  }
});
```

## Development Workflow

1. **Setup**: Copy `.env.example` to `.env` and configure database credentials
2. **Dependencies**: Run `uv sync` and `pnpm install`
3. **Database**: Start PostgreSQL with `docker-compose up -d postgres`
4. **Migrations**: Apply with `uv run --env-file .env alembic upgrade head`
5. **Development**: Use `make dev-full` for full stack or `make dev` for backend only
6. **Frontend**: Auto-build with `watch.js` and `watch.css` scripts

## Testing

- **Test framework**: Not currently configured - check with team for testing approach
- **Single test**: Use `uv run --env-file .env pytest path/to/test.py` if pytest is available
- **Test database**: Use separate test database configuration in `.env.test`

## Security Considerations

- **Environment variables**: Never commit `.env` files, use `.env.example`
- **Input validation**: Use Pydantic schemas for all API input
- **Authentication**: JWT with LDAP support for enterprise integration
- **CORS**: Configured for cross-origin requests

## Performance Patterns

- **Database**: Use async operations, connection pooling via asyncpg
- **Frontend**: Minimal JavaScript, server-rendered HTML with htmx
- **Caching**: No-cache middleware for API responses
- **Real-time**: SSE notifications for live updates