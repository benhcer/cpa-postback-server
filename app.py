from flask import Flask, request
import firebase_admin
from firebase_admin import credentials, db
import os

# Initialize Flask app
app = Flask(__name__)

# Initialize Firebase
cred = credentials.Certificate('firebase_config.json')
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://taskbot-824c1-default-rtdb.asia-southeast1.firebasedatabase.app/'
})

@app.route('/postback', methods=['GET'])
def postback():
    user_id = request.args.get('sub1')  # Telegram user ID
    payout = request.args.get('payout')  # Offer payout in dollars

    if not user_id or not payout:
        return 'Missing parameters', 400

    try:
        # Convert payout to coins
        coins = int(float(payout) * 35)

        # Reference to user
        user_ref = db.reference(f'users/{user_id}')
        user_data = user_ref.get()

        if user_data:
            current_coins = user_data.get('coins', 0)
            user_ref.update({'coins': current_coins + coins})
        else:
            # Create new user if not present
            user_ref.set({'coins': coins, 'referrer': None})

        # ✅ Handle referral bonus only on first task
        if user_data and user_data.get('referrer') and not user_data.get('first_task_done'):
            referrer_id = user_data['referrer']
            referrer_ref = db.reference(f'users/{referrer_id}')
            referrer_data = referrer_ref.get()

            if referrer_data:
                referrer_coins = referrer_data.get('coins', 0) + 35
                referrer_ref.update({'coins': referrer_coins})

            # Mark this user has completed their first task
            user_ref.update({'first_task_done': True})

        return 'Success', 200

    except Exception as e:
        return f'Error: {str(e)}', 500

# 🚀 Make compatible with Render.com deployment
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))  # use dynamic port on Render
    app.run(host='0.0.0.0', port=port)
