#! /usr/bin/env bash
python -m alembic upgrade head
python -m uvicorn main:app --host 0.0.0.0 --port 8000