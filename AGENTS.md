# AGENTS.md

Guidelines and commands for agentic coding agents working in this repository.

## Build/Test Commands

### Python (using `uv`)
```bash
uv sync                              # Install dependencies
uv run --env-file .env scripts/dev.py  # Run dev server
uv run --env-file .env alembic upgrade head  # Apply migrations
uv run --env-file .env alembic revision --autogenerate -m "message"  # Create migration
uv run --env-file .env scripts/create_superuser.py  # Create admin user
```

### JavaScript (using `pnpm`)
```bash
pnpm install           # Install dependencies
pnpm run build.css    # Build TailwindCSS
pnpm run build.js     # Build with Esbuild
pnpm run dev          # Watch mode (CSS + JS)
```

### Make Commands
```bash
make dev-full         # Full stack dev (frontend + backend)
make dev              # Backend only
make migration        # Generate migration
make migrate          # Apply migrations
make create_superuser # Create admin user
```

### Docker
```bash
docker-compose up -d postgres  # Start PostgreSQL
```

## Code Style

### Python
- **Type hints**: Required for all functions. Use Pydantic for API input/output.
- **Async**: All database operations use `async`/`await`.
- **Imports**: Standard lib → third-party → local (`from uuid import UUID` → `from fastapi import HTTPException` → `from models import User`)
- **Naming**: `snake_case` for functions/variables, `PascalCase` for classes.
- **Pydantic**: Use `Field()` for validation, `field_validator` for custom validation.
- **SQLAlchemy**: Use `model_dump(exclude={...})` to convert to dict.

### JavaScript
- **Modules**: ES modules with `import`/`export`.
- **Alpine.js**: Use `x-data` for component state, `Alpine.store()` for global state.
- **htmx**: Server-rendered HTML with `hx-post`, `hx-get`, `hx-target`.
- **Naming**: `camelCase` for JS, `kebab-case` for HTML attributes.

### CSS
- **TailwindCSS**: Utility-first with `@apply` for reusable styles.
- **DaisyUI**: Use component classes for consistency.
- **Mobile-first**: Use Tailwind's `md:`, `lg:` prefixes.

## Project Structure
```
src/
├── app.py              # FastAPI entry point
├── core/               # Config, DB, security, utils
├── models/             # SQLAlchemy models
├── schemas/            # Pydantic schemas
├── services/           # Business logic
├── routes/             # API routes (pages/, htmx/, api/)
├── templates/          # Jinja2 HTML templates
├── static/             # CSS, JS assets
└── alembic/            # Migrations
```

## Database Patterns
- **UUID primary keys** for all models
- **StatusMixin**: `status` field for soft deletes
- **TimeStampMixin**: `created_at`, `updated_at`
- **Async session**: Use `async with get_db_session() as session:`

## Pydantic Patterns
```python
from pydantic import BaseModel, Field, field_validator

class ItemIn(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    value: Decimal = Field(..., gt=0)
    optional_field: Optional[str] = None

    @field_validator("field", mode="before")
    @classmethod
    def transform(cls, v):
        if v == "":  # Convert empty string to None
            return None
        return v
```

## Service Layer Pattern
```python
from core.service import AbstractModelService

class MyService(AbstractModelService[MyModel]):
    model = MyModel

    async def create(self, data: MySchemaIn, user_id: UUID) -> MyModel:
        obj = self.model(**data.model_dump())
        self.dbSession.add(obj)
        await self.dbSession.flush()
        await self.dbSession.commit()
        await self.dbSession.refresh(obj)
        return obj
```

## HTMX Patterns
```html
<form hx-post="/endpoint" hx-target="#result" hx-swap="innerHTML">
  <input hx-post="/search" hx-trigger="keyup changed delay:300ms" hx-target="#results">
</form>
```

## Error Handling
```python
from fastapi import HTTPException

async def get_item(item_id: UUID):
    item = await get_db(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Not found")
    return item
```

## Development Workflow
1. Copy `.env.example` to `.env` and configure
2. Run `uv sync` and `pnpm install`
3. Start DB: `docker-compose up -d postgres`
4. Apply migrations: `make migrate`
5. Run dev: `make dev-full`

## Testing
- No test framework configured yet
- For manual testing, use the dev server and browser

## Security
- Never commit `.env` files
- Use Pydantic schemas for all input validation
- JWT + LDAP authentication configured
