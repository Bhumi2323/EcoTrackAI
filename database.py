import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")

DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"

engine = create_engine(DATABASE_URL)


# =========================
# SMART BIN FUNCTIONS
# =========================

def get_bins():

    with engine.connect() as connection:

        result = connection.execute(
            text("SELECT * FROM bins")
        )

        return [
            dict(row._mapping)
            for row in result
        ]


def update_bin(bin_id, fill_level):

    if fill_level < 70:
        status = "NORMAL"

    elif fill_level < 85:
        status = "ALMOST FULL"

    else:
        status = "COLLECTION REQUIRED"

    query = text("""
        UPDATE bins
        SET fill_level = :fill_level,
            status = :status,
            last_updated = CURRENT_TIMESTAMP
        WHERE bin_id = :bin_id
    """)

    with engine.begin() as connection:

        connection.execute(
            query,
            {
                "bin_id": bin_id,
                "fill_level": fill_level,
                "status": status
            }
        )

    return status


def get_alert_bins():

    with engine.connect() as connection:

        result = connection.execute(
            text("""
                SELECT *
                FROM bins
                WHERE fill_level >= 85
                ORDER BY fill_level DESC
            """)
        )

        return [
            dict(row._mapping)
            for row in result
        ]


# =========================
# E-WASTE FUNCTIONS
# =========================

def get_ewaste_assets():

    with engine.connect() as connection:

        result = connection.execute(
            text("""
                SELECT *
                FROM e_waste_assets
                ORDER BY id DESC
            """)
        )

        return [
            dict(row._mapping)
            for row in result
        ]


def get_ewaste_asset(asset_code):

    with engine.connect() as connection:

        result = connection.execute(
            text("""
                SELECT *
                FROM e_waste_assets
                WHERE asset_code = :asset_code
            """),
            {
                "asset_code": asset_code
            }
        )

        row = result.fetchone()

        if row:
            return dict(row._mapping)

        return None


def update_ewaste_status(
    asset_code,
    status,
    recycler_name=None
):

    with engine.begin() as connection:

        connection.execute(
            text("""
                UPDATE e_waste_assets
                SET lifecycle_status = :status,
                    recycler_name = :recycler_name
                WHERE asset_code = :asset_code
            """),
            {
                "asset_code": asset_code,
                "status": status,
                "recycler_name": recycler_name
            }
        )

    return status

    # =========================
# GREEN CREDITS
# =========================

def add_green_credits(user_name, action, points):

    with engine.begin() as connection:

        connection.execute(
            text("""
                INSERT INTO green_credits
                (user_name, action, points)
                VALUES
                (:user_name, :action, :points)
            """),
            {
                "user_name": user_name,
                "action": action,
                "points": points
            }
        )


def get_green_credits(user_name):

    with engine.connect() as connection:

        result = connection.execute(
            text("""
                SELECT
                    COALESCE(SUM(points), 0) AS total_points
                FROM green_credits
                WHERE user_name = :user_name
            """),
            {
                "user_name": user_name
            }
        )

        row = result.fetchone()

        return row._mapping["total_points"]