# The starting point: a minimal Linux with Python 3.12 already on it.
# "slim" = no compilers, docs, or extras you don't need. Smaller box, less to attack.
FROM python:3.12-slim

# Bring uv in from its own official image — pinned to 0.7.20, the SAME version
# you run locally. Not :latest. Unpinned things drift, and drift lies.
COPY --from=ghcr.io/astral-sh/uv:0.7.20 /uv /uvx /bin/

# Everything after this happens inside /app in the box.
WORKDIR /app

# PYTHONDONTWRITEBYTECODE: don't litter .pyc files — the box is disposable.
# PYTHONUNBUFFERED: print logs immediately instead of holding them in a buffer.
#   Without this, container logs arrive late or vanish on crash. Always set it.
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# ─── Dependencies FIRST, code SECOND. The order is deliberate. ───
# Docker caches each step. Deps change rarely, code changes constantly.
# Copying deps alone means editing views.py does NOT re-download 37 packages.
COPY pyproject.toml uv.lock ./
RUN uv sync --locked --no-dev

# ─── Now the code. This is the layer that actually changes day to day. ───
COPY . .

# Put the venv's binaries on PATH so `gunicorn` is callable by name.
ENV PATH="/app/.venv/bin:$PATH"

# ─── Gather static files into the image so whitenoise can serve them. ───
# collectstatic runs settings.py, which now DEMANDS a SECRET_KEY (fail-loud) —
# but there is no .env during a build. So we hand it THROWAWAY values, alive
# only for this one command (same idea as CI's fake secret). collectstatic
# never touches the database, so fake DB creds are fine — they only let
# settings.py finish loading.
RUN SECRET_KEY=build-only-not-used \
    POSTGRES_DB=x POSTGRES_USER=x POSTGRES_PASSWORD=x \
    python manage.py collectstatic --noinput

# Documentation only — says "this box speaks on 8000". Doesn't open anything.
EXPOSE 8000

# What runs when the box starts.
# NOT runserver — Django's own docs say never use it in production.
# 0.0.0.0 (not 127.0.0.1) so the port is reachable from OUTSIDE the box.
# 127.0.0.1 here would mean "only I can talk to me" and nothing could connect.
CMD ["gunicorn", "dashboard.wsgi:application", "--bind", "0.0.0.0:8000"]
