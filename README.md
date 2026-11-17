How to Run on local:

install deps
uv sync

Run the app:
uvicorn main:app --reload  



Endpoint to Hit windows shell:
curl.exe --location --request POST "http://127.0.0.1:8000/chat" --header "Content-Type: application/json" --data-raw "{\"session_id\":\"abc\",\"customer_email\":\"cgmailcom\",\"message\":\"How are you doing?\"}"