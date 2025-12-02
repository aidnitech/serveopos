#!/usr/bin/env python
"""
Tests for accounting and collections features
"""
from app import create_app
from extensions import db
from models import User
from werkzeug.security import generate_password_hash
import json

app = create_app()
app.config['WTF_CSRF_ENABLED'] = False
client = app.test_client()


def setup_test_data():
    with app.app_context():
        db.drop_all()
        db.create_all()
        admin = User(username='admin', password_hash=generate_password_hash('admin'), role='admin')
        manager = User(username='manager', password_hash=generate_password_hash('manager'), role='manager')
        db.session.add_all([admin, manager])
        db.session.commit()


def login(user, pw):
    return client.post('/auth/login', data={'username': user, 'password': pw})


def logout():
    return client.get('/auth/logout')


def test_transactions_and_summary():
    print('\n🔍 Testing transactions and accounting summary...')
    setup_test_data()
    login('admin', 'admin')

    # create income
    res = client.post('/admin/api/transactions', data=json.dumps({'transaction_type':'income','amount':100.0,'category':'sales','description':'test income'}), content_type='application/json')
    assert res.status_code == 201
    tid1 = res.get_json().get('id')

    # create expense
    res = client.post('/admin/api/transactions', data=json.dumps({'transaction_type':'expense','amount':40.0,'category':'supplies','description':'test expense'}), content_type='application/json')
    assert res.status_code == 201
    tid2 = res.get_json().get('id')

    # fetch transactions
    res = client.get('/admin/api/transactions')
    assert res.status_code == 200
    txns = res.get_json()
    assert any(t['id'] == tid1 for t in txns)
    assert any(t['id'] == tid2 for t in txns)

    # accounting summary
    res = client.get('/admin/api/accounting/summary')
    assert res.status_code == 200
    s = res.get_json()
    assert float(s.get('income',0)) >= 100.0
    assert float(s.get('expenses',0)) >= 40.0

    logout()


def test_collections_and_payments():
    print('\n🔍 Testing collections and payments...')
    setup_test_data()
    login('admin', 'admin')

    # create collection
    res = client.post('/admin/api/collections', data=json.dumps({'customer':'ACME Ltd','phone':'123','total':200.0}), content_type='application/json')
    assert res.status_code == 201
    col_id = res.get_json().get('id')

    # fetch collections
    res = client.get('/admin/api/collections')
    assert res.status_code == 200
    cols = res.get_json()
    assert any(c['id'] == col_id for c in cols)

    # add payment partial
    res = client.post(f'/admin/api/collections/{col_id}/payment', data=json.dumps({'amount':50.0,'method':'cash'}), content_type='application/json')
    assert res.status_code == 201

    # check collection updated
    res = client.get(f'/admin/api/collections/{col_id}')
    assert res.status_code == 200
    c = res.get_json()
    assert float(c.get('paid',0)) >= 50.0
    assert float(c.get('balance',0)) <= 150.0

    # add final payment
    res = client.post(f'/admin/api/collections/{col_id}/payment', data=json.dumps({'amount':150.0,'method':'card'}), content_type='application/json')
    assert res.status_code == 201

    res = client.get(f'/admin/api/collections/{col_id}')
    c = res.get_json()
    assert float(c.get('balance',0)) == 0.0
    assert c.get('status') in ['collected', 'paid'] or c.get('status') == 'collected'

    # collection summary
    res = client.get('/admin/api/collection/summary')
    assert res.status_code == 200
    summary = res.get_json()
    assert float(summary.get('collected',0)) >= 200.0

    logout()


def test_permissions_for_collections_and_accounting():
    print('\n🔍 Testing permission enforcement for accounting & collections...')
    setup_test_data()
    # create a waiter user
    client.post('/auth/login', data={'username':'admin','password':'admin'})
    # create waiter
    client.post('/admin/api/users', json={'username':'waiter','password':'waiter','role':'waiter'})
    client.get('/auth/logout')

    # login as waiter
    client.post('/auth/login', data={'username':'waiter','password':'waiter'})
    # waiter should NOT be able to create transaction
    res = client.post('/admin/api/transactions', data=json.dumps({'transaction_type':'income','amount':10}), content_type='application/json')
    assert res.status_code == 403
    # waiter should NOT be able to create collection
    res = client.post('/admin/api/collections', data=json.dumps({'customer':'X','total':10}), content_type='application/json')
    assert res.status_code == 403
    client.get('/auth/logout')
    print('  ✓ Permission enforcement for accounting & collections works (waiter denied)')


if __name__ == '__main__':
    ok = True
    try:
        test_transactions_and_summary()
        test_collections_and_payments()
        print('\n✅ Accounting & Collections tests passed')
    except AssertionError as e:
        print('\n❌ Test failed:', e)
        ok = False
    exit(0 if ok else 1)
