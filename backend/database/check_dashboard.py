from sqlalchemy import text

from backend.app.database import engine


with engine.connect() as connection:
    result = connection.execute(
        text("SELECT to_regclass('public.dashboard_charts')")
    )

    print(result.scalar())