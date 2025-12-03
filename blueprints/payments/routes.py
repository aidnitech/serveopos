from flask import request, jsonify, current_app
from . import payments_bp
from decorators import permission_required, admin_required
from flask_login import login_required

# Payment endpoints are intentionally provider-agnostic. Concrete provider integrations
# should implement the PaymentProvider interface in services/payment_providers.py

@payments_bp.route('/create-intent', methods=['POST'])
@login_required
@permission_required('process_payments')
def create_payment_intent():
    data = request.get_json() or {}
    # Expected: {amount: float, currency: 'USD', payment_method: 'card', metadata: {...}}
    # For now, return a stubbed intent reference so provider implementations can wire this.
    amount = float(data.get('amount', 0))
    currency = data.get('currency', current_app.config.get('BASE_CURRENCY', 'USD'))
    intent = {
        'id': 'pi_stub_{}'.format(int(amount*100)),
        'amount': amount,
        'currency': currency,
        'status': 'requires_provider_action',
        'provider': None
    }
    return jsonify({'intent': intent}), 201


@payments_bp.route('/webhook', methods=['POST'])
def payment_webhook():
    # Generic webhook receiver. Concrete providers should handle verification and processing.
    payload = request.get_json() or {}
    # Log or process the payload as needed.
    return jsonify({'received': True}), 200
