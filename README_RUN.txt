Install dependencies:
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt

Run the API:
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

Environment:
Copy .env.example to .env and set values for MongoDB and Hugging Face.
