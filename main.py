from fastapi import FastAPI, Form
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from database import init_db, get_db_connection
import os

app = FastAPI()

# Note: The startup_event block was removed from here to prevent the cloud crash

# Mount the static directory for your CSS styles
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=FileResponse)
async def home():
    # FileResponse safely skips Jinja2 entirely to prevent the dictionary crash
    return FileResponse(os.path.join("templates", "index.html"))

@app.post("/book", response_class=HTMLResponse)
async def handle_booking(
    full_name: str = Form(...),
    email: str = Form(...),
    phone: str = Form(...),
    check_in: str = Form(...),
    check_out: str = Form(...),
    room_type: str = Form(...),
    guests: int = Form(...),
    special_requests: str = Form(None)
):
    conn = get_db_connection()
    query = """
        INSERT INTO bookings (full_name, email, phone, check_in, check_out, room_type, guests, special_requests)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
    """
    with conn.cursor() as cur:
        cur.execute(query, (full_name, email, phone, check_in, check_out, room_type, guests, special_requests))
        conn.commit()
    conn.close()

    # Clean custom response window when someone successfully books
    success_html = f"""
    <html>
        <head>
            <title>Booking Success</title>
            <link rel="stylesheet" href="/static/style.css">
        </head>
        <body style="font-family: Arial, sans-serif; text-align: center; padding: 50px; background-color: #f4f7f6;">
            <div style="background: white; padding: 40px; border-radius: 8px; display: inline-block; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                <h1 style="color: #2ecc71;">🎉 Booking Confirmed!</h1>
                <p>Thank you <strong>{full_name}</strong>. Your reservation has been safely recorded.</p>
                <br>
                <a href="/" style="background: #3498db; color: white; padding: 10px 20px; text-decoration: none; border-radius: 4px;">Back to Portal</a>
            </div>
        </body>
    </html>
    """
    return HTMLResponse(content=success_html)
