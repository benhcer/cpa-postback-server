from flask import Flask, request
import firebase_admin
from firebase_admin import credentials, db

app = Flask(__name__)

# Initialize Firebase Admin SDK
cred = credentials.Certificate('firebase_config.json')
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://taskbot-824c1-default-rtdb.asia-southeast1.firebasedatabase.app/'
})

@app.route('/postback', methods=['GET'])
def postback():
    user_id = request.args.get('sub1')
    payout = request.args.get('payout')

    if not user_id or not payout:
        return 'Missing parameters', 400

    try:
        coins = int(float(payout) * 35)  # Convert payout to coins
        user_ref = db.reference(f'users/{user_id}')
        user_data = user_ref.get()

        if user_data:
            current_coins = user_data.get('coins', 0)
            user_ref.update({'coins': current_coins + coins})
        else:
            user_ref.set({'coins': coins, 'referrer': None})

        return 'Success', 200
    except Exception as e:
        return f'Error: {str(e)}', 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)

import os

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)


