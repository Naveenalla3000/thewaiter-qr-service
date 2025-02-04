import os
from dotenv import load_dotenv
load_dotenv()
from flask import Flask, request, jsonify
import qrcode
import io
import uuid
import datetime
from PIL import Image, ImageDraw, ImageFont

app = Flask(__name__)

from .mongo import qr_collection
from .utils import upload_to_s3,store_qr_code
from .kafka import producer

PORT = os.getenv('PORT') or 5050
DOMAIN = os.getenv('DOMAIN') or f'http://localhost/{PORT}'
KAFKA_TOPIC = os.getenv('KAFKA_TOPIC')

@app.route('/generate-qr', methods=['GET'])
def generate_qr():
    restaurant_id = request.args.get('restaurantId')
    table_number = request.args.get('tableNumber')
    if not restaurant_id or not table_number:
        return {"error": "Missing parameters"}, 400
    
    qr_code = qr_collection.find_one({"restaurant_id": restaurant_id, "table_number": table_number})
    if qr_code:
        if qr_code['status'] == 'active':
            return jsonify({"message": "QR already generated", "qr_url": qr_code['qr_url']})
        elif qr_code['status'] == 'invalid':
            qr_collection.delete_one({"qr_token": qr_code['qr_token']})
    unique_token = store_qr_code(restaurant_id, table_number)
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    
    qr.add_data(f'{DOMAIN}/link/{unique_token}')
    qr.make(fit=True)
    buffer = io.BytesIO()
    qr.make_image().save(buffer, 'PNG')
    buffer.seek(0)
    file_name = f"qr_codes/{unique_token}.png"
    s3_url = upload_to_s3(buffer, file_name)
    qr_collection.update_one({"qr_token": unique_token}, {"$set": {"qr_url": s3_url}})
    return jsonify({"message": "QR generated", "qr_url": s3_url})

@app.route('/delete/<qr_token>', methods=['POST'])
def invalidate_qr(qr_token):
    qr_code = qr_collection.find_one({"qr_token": qr_token})

    if not qr_code:
        return {"error": "QR not found"}, 404

    qr_collection.update_one({"qr_token": qr_token}, {"$set": {"status": "invalid"}})

    return {"message": "QR Code has been invalidated."}


@app.route('/scan_qr')
def scan_qr():
    qr_token = request.args.get('qr_token')
    
    qr_code = qr_collection.find_one({"qr_token": qr_token})

    if not qr_code:
        return {"error": "Invalid QR. Contact queries@naveenalla.in."}, 400

    if qr_code["status"] == "invalid":
        return {"error": "QR expired. Contact queries@naveenalla.in."}, 400
    
    restaurant_id = qr_code["restaurant_id"]
    table_number = qr_code["table_number"]

    alert_message = {
        "restaurant_id": restaurant_id,
        "table_number": table_number,
        "timestamp": str(datetime.datetime.now()),
        "message": f"Customer arrived at Table {table_number}. Please take the order."
    }
    producer.send(KAFKA_TOPIC, alert_message)

    return {"message": "Waiter has been notified!"}


def generate_unique_token():
    return str(uuid.uuid4())
