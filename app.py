from fastapi import FastAPI, UploadFile, File
from fastapi.responses import HTMLResponse, FileResponse

from database import (
    get_bins,
    update_bin,
    get_alert_bins,
    get_ewaste_assets,
    get_ewaste_asset,
    update_ewaste_status,
    add_green_credits,
    get_green_credits
)

from ai_model.ai_classifier import classify_waste


app = FastAPI(title="EcoTrackAI")


# =========================
# HOME
# =========================

@app.get("/", response_class=HTMLResponse)
def home():

    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>EcoTrackAI</title>

        <style>
            body {
                font-family: Arial;
                margin: 0;
                background: #f1f8f4;
                text-align: center;
            }

            header {
                background: #168a45;
                color: white;
                padding: 25px;
            }

            .container {
                padding: 40px;
            }

            .card {
                display: inline-block;
                width: 220px;
                margin: 15px;
                padding: 25px;
                background: white;
                border-radius: 15px;
                box-shadow: 0 3px 10px #ccc;
            }

            a {
                display: inline-block;
                padding: 12px 20px;
                background: #168a45;
                color: white;
                text-decoration: none;
                border-radius: 8px;
            }

            a:hover {
                background: #0f6e37;
            }
        </style>
    </head>

    <body>

        <header>
            <h1>🌱 EcoTrackAI</h1>
            <p>AI-Powered Smart Waste Management System</p>
        </header>

        <div class="container">

            <div class="card">
                <h2>🗑️ Smart Bins</h2>
                <p>Monitor bin levels and collection alerts.</p>
                <a href="/dashboard">Open Dashboard</a>
            </div>

            <div class="card">
                <h2>🤖 AI Classification</h2>
                <p>Classify waste using AI.</p>
                <a href="/waste">Classify Waste</a>
            </div>

            <div class="card">
                <h2>♻️ E-Waste</h2>
                <p>Track electronic waste lifecycle.</p>
                <a href="/ewaste">Open Auditor</a>
            </div>

        </div>

    </body>
    </html>
    """


# =========================
# PAGES
# =========================

@app.get("/dashboard", response_class=HTMLResponse)
def dashboard():

    with open("templates/dashboard.html", "r", encoding="utf-8") as file:
        return file.read()


@app.get("/waste", response_class=HTMLResponse)
def waste():

    with open("templates/waste.html", "r", encoding="utf-8") as file:
        return file.read()


@app.get("/ewaste")
def ewaste_page():

    return FileResponse("templates/ewaste.html")


# =========================
# SMART BINS
# =========================

@app.get("/bins")
def show_bins():

    return get_bins()


@app.post("/bins/update")
def change_bin(bin_id: int, fill_level: int):

    status = update_bin(
        bin_id,
        fill_level
    )

    return {
        "bin_id": bin_id,
        "fill_level": fill_level,
        "status": status
    }


@app.get("/bins/alerts")
def bin_alerts():

    alerts = get_alert_bins()

    return {
        "alert_count": len(alerts),
        "alerts": alerts
    }


# =========================
# AI WASTE CLASSIFICATION
# =========================

@app.post("/classify")
async def classify(image: UploadFile = File(...)):

    result = classify_waste(image.file)

    return result


# =========================
# E-WASTE
# =========================

@app.get("/api/ewaste")
def ewaste_assets():

    return get_ewaste_assets()


@app.get("/api/ewaste/{asset_code}")
def ewaste_asset(asset_code):

    asset = get_ewaste_asset(asset_code)

    if asset is None:

        return {
            "error": "Asset not found"
        }

    return asset


@app.put("/api/ewaste/{asset_code}")
def change_ewaste_status(
    asset_code: str,
    status: str,
    recycler_name: str = None
):

    update_ewaste_status(
        asset_code,
        status,
        recycler_name
    )

    return {
        "message": "E-Waste status updated successfully"
    }


# =========================
# QR ASSET PAGE
# =========================

@app.get("/ewaste/{asset_code}")
def ewaste_asset_page(asset_code: str):

    asset = get_ewaste_asset(asset_code)

    if asset is None:

        return HTMLResponse(
            "<h1>Asset not found</h1>"
        )

    return HTMLResponse(f"""
        <!DOCTYPE html>
        <html>

        <head>
            <title>EcoTrackAI - {asset["asset_code"]}</title>

            <style>
                body {{
                    font-family: Arial;
                    background: #f1f8f4;
                    padding: 30px;
                }}

                .box {{
                    max-width: 600px;
                    margin: auto;
                    background: white;
                    padding: 30px;
                    border-radius: 15px;
                    box-shadow: 0 3px 10px #ccc;
                }}

                a {{
                    display: inline-block;
                    margin-top: 20px;
                    padding: 10px 20px;
                    background: #168a45;
                    color: white;
                    text-decoration: none;
                    border-radius: 8px;
                }}
            </style>
        </head>

        <body>

            <div class="box">

                <h1>🌱 EcoTrackAI</h1>

                <h2>♻️ E-Waste Asset</h2>

                <p>
                    <b>Asset ID:</b>
                    {asset["asset_code"]}
                </p>

                <p>
                    <b>Device:</b>
                    {asset["device_name"]}
                </p>

                <p>
                    <b>Category:</b>
                    {asset["category"]}
                </p>

                <p>
                    <b>Location:</b>
                    {asset["location"]}
                </p>

                <p>
                    <b>Condition:</b>
                    {asset["condition_status"]}
                </p>

                <p>
                    <b>Lifecycle Status:</b>
                    {asset["lifecycle_status"]}
                </p>

                <p>
                    <b>Recycler:</b>
                    {asset["recycler_name"] or "Not assigned"}
                </p>

                <a href="/ewaste">
                    Back to E-Waste Auditor
                </a>

                <a href="/dashboard">
                    Dashboard
                </a>

            </div>

        </body>

        </html>
    """)


# =========================
# GREEN CREDITS
# =========================

@app.post("/credits/add")
def add_credits(
    user_name: str,
    action: str,
    points: int
):

    add_green_credits(
        user_name,
        action,
        points
    )

    return {
        "message": "Green credits added",
        "user_name": user_name,
        "points": points
    }


@app.get("/credits/{user_name}")
def credits(user_name: str):

    total = get_green_credits(user_name)

    return {
        "user_name": user_name,
        "total_points": total
    }

@app.get("/scanner")
def scanner_page():

    return FileResponse("templates/scanner.html")    

@app.post("/bins/arduino")
def arduino_bin_update(
    bin_id: int,
    fill_level: int
):
    status = update_bin(bin_id, fill_level)

    return {
        "bin_id": bin_id,
        "fill_level": fill_level,
        "status": status
    }    