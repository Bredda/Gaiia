api:
    cd apps/api && uv run uvicorn main:app --reload

web:
    cd apps/web && pnpm dev