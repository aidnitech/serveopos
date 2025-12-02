from flask import render_template, request, jsonify, send_file
from flask_login import login_required, current_user
from . import admin_bp
from decorators import admin_required, permission_required
from extensions import db
from models import MenuItem, InventoryItem, PriceHistory, AuditLog, RolePermission
import csv, io
from datetime import datetime
from models import User
from werkzeug.security import generate_password_hash


@admin_bp.route("/")
@login_required
@admin_required
def dashboard():
    return render_template("admin_dashboard.html")


### Menu management API
@admin_bp.route("/api/menu", methods=["GET"])
@login_required
@permission_required('manage_menu')
def api_get_menu():
    try:
        items = MenuItem.query.order_by(MenuItem.id.desc()).all()
        return jsonify([{
            "id": i.id,
            "name": i.name,
            "description": i.description,
            "price": i.price,
            "available": i.available
        } for i in items])
    except Exception as e:
        return jsonify({"error": str(e)}), 500


### User management
@admin_bp.route('/api/users', methods=['GET'])
@login_required
@permission_required('manage_users')
def api_get_users():
    try:
        users = User.query.order_by(User.id.desc()).all()
        return jsonify([{"id": u.id, "username": u.username, "role": u.role} for u in users])
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@admin_bp.route('/api/users', methods=['POST'])
@login_required
@permission_required('manage_users')
def api_create_user():
    data = request.get_json() or {}
    try:
        username = data.get('username')
        password = data.get('password')
        role = data.get('role') or 'waiter'
        if not username or not password:
            return jsonify({'error':'username and password required'}), 400
        if User.query.filter_by(username=username).first():
            return jsonify({'error':'username exists'}), 400
        u = User(username=username, password_hash=generate_password_hash(password), role=role)
        db.session.add(u)
        db.session.commit()
        log = AuditLog(user_id=getattr(current_user,'id',None), username=getattr(current_user,'username',None), action='create', object_type='user', object_id=u.id, details=f'created user {username} role={role}')
        db.session.add(log)
        db.session.commit()
        return jsonify({'id': u.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/api/users/<int:user_id>', methods=['PUT'])
@login_required
@permission_required('manage_users')
def api_update_user(user_id):
    data = request.get_json() or {}
    try:
        u = User.query.get_or_404(user_id)
        changed = []
        if 'username' in data and data.get('username') != u.username:
            changed.append(f'username: {u.username} -> {data.get("username")}')
            u.username = data.get('username')
        if 'role' in data and data.get('role') != u.role:
            changed.append(f'role: {u.role} -> {data.get("role")}')
            u.role = data.get('role')
        db.session.commit()
        if changed:
            log = AuditLog(user_id=getattr(current_user,'id',None), username=getattr(current_user,'username',None), action='update', object_type='user', object_id=u.id, details='; '.join(changed))
            db.session.add(log)
            db.session.commit()
        return jsonify({'status':'ok'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/api/users/<int:user_id>/password', methods=['PUT'])
@login_required
@permission_required('manage_users')
def api_reset_password(user_id):
    data = request.get_json() or {}
    try:
        newpw = data.get('password')
        if not newpw:
            return jsonify({'error':'password required'}), 400
        u = User.query.get_or_404(user_id)
        u.password_hash = generate_password_hash(newpw)
        db.session.commit()
        log = AuditLog(user_id=getattr(current_user,'id',None), username=getattr(current_user,'username',None), action='reset_password', object_type='user', object_id=u.id, details='password reset')
        db.session.add(log)
        db.session.commit()
        return jsonify({'status':'ok'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/api/users/<int:user_id>', methods=['DELETE'])
@login_required
@permission_required('manage_users')
def api_delete_user(user_id):
    try:
        u = User.query.get_or_404(user_id)
        username = u.username
        db.session.delete(u)
        db.session.commit()
        log = AuditLog(user_id=getattr(current_user,'id',None), username=getattr(current_user,'username',None), action='delete', object_type='user', object_id=user_id, details=f'deleted {username}')
        db.session.add(log)
        db.session.commit()
        return jsonify({'status':'deleted'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/api/menu/<int:item_id>', methods=['GET'])
@login_required
@permission_required('manage_menu')
def api_get_menu_item(item_id):
    try:
        i = MenuItem.query.get_or_404(item_id)
        return jsonify({
            'id': i.id,
            'name': i.name,
            'description': i.description,
            'price': i.price,
            'available': i.available
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_bp.route("/api/menu", methods=["POST"])
@login_required
@permission_required('manage_menu')
def api_create_menu():
    data = request.get_json() or {}
    try:
        name = data.get("name")
        price = float(data.get("price", 0))
        description = data.get("description")
        available = bool(data.get("available", True))
        if not name:
            return jsonify({"error": "name is required"}), 400
        item = MenuItem(name=name, description=description, price=price, available=available)
        db.session.add(item)
        db.session.commit()
        # audit
        log = AuditLog(user_id=getattr(current_user, 'id', None), username=getattr(current_user, 'username', None), action='create', object_type='menu_item', object_id=item.id, details=f'created {item.name}')
        db.session.add(log)
        db.session.commit()
        return jsonify({"id": item.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@admin_bp.route("/api/menu/<int:item_id>", methods=["PUT"])
@login_required
@permission_required('manage_menu')
def api_update_menu(item_id):
    data = request.get_json() or {}
    try:
        item = MenuItem.query.get_or_404(item_id)
        changed = []
        if "name" in data and data.get("name")!=item.name:
            changed.append(f'name: {item.name} -> {data.get("name")}')
            item.name = data.get("name")
        if "description" in data and data.get("description")!=item.description:
            changed.append('description updated')
            item.description = data.get("description")
        if "price" in data:
            new_price = float(data.get("price"))
            if new_price != item.price:
                # record price history
                ph = PriceHistory(menu_item_id=item.id, old_price=item.price, new_price=new_price, changed_by=getattr(current_user,'username',None))
                db.session.add(ph)
                changed.append(f'price: {item.price} -> {new_price}')
                item.price = new_price
        if "available" in data and bool(data.get("available")) != item.available:
            changed.append(f'available: {item.available} -> {data.get("available")}')
            item.available = bool(data.get("available"))
        db.session.commit()
        # audit
        if changed:
            log = AuditLog(user_id=getattr(current_user,'id',None), username=getattr(current_user,'username',None), action='update', object_type='menu_item', object_id=item.id, details='; '.join(changed))
            db.session.add(log)
            db.session.commit()
        return jsonify({"status": "ok"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@admin_bp.route("/api/menu/<int:item_id>", methods=["DELETE"])
@login_required
@permission_required('manage_menu')
def api_delete_menu(item_id):
    try:
        item = MenuItem.query.get_or_404(item_id)
        name = item.name
        db.session.delete(item)
        db.session.commit()
        log = AuditLog(user_id=getattr(current_user,'id',None), username=getattr(current_user,'username',None), action='delete', object_type='menu_item', object_id=item_id, details=f'deleted {name}')
        db.session.add(log)
        db.session.commit()
        return jsonify({"status": "deleted"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@admin_bp.route('/api/menu/<int:item_id>/history', methods=['GET'])
@login_required
@permission_required('manage_menu')
def api_menu_history(item_id):
    try:
        rows = PriceHistory.query.filter_by(menu_item_id=item_id).order_by(PriceHistory.changed_at.desc()).limit(50).all()
        return jsonify([{"old_price": r.old_price, "new_price": r.new_price, "changed_by": r.changed_by, "changed_at": r.changed_at.isoformat()} for r in rows])
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@admin_bp.route('/api/inventory/<int:item_id>', methods=['GET'])
@login_required
@permission_required('manage_inventory')
def api_get_inventory_item(item_id):
    try:
        i = InventoryItem.query.get_or_404(item_id)
        return jsonify({
            'id': i.id,
            'name': i.name,
            'quantity': i.quantity,
            'unit': i.unit,
            'updated_at': i.updated_at.isoformat() if i.updated_at else None
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/api/menu/import', methods=['POST'])
@login_required
@permission_required('manage_menu')
def api_menu_import():
    try:
        f = request.files.get('file')
        if not f:
            return jsonify({'error':'file required'}), 400
        stream = io.StringIO(f.stream.read().decode('utf-8'))
        reader = csv.DictReader(stream)
        created = []
        results = []
        row_no = 0
        for row in reader:
            row_no += 1
            name = row.get('name') or row.get('Name')
            if not name:
                results.append({'row': row_no, 'status': 'skipped', 'reason': 'missing name'})
                continue
            try:
                price = float(row.get('price') or row.get('Price') or 0)
            except Exception:
                results.append({'row': row_no, 'status': 'error', 'reason': 'invalid price'})
                continue
            description = row.get('description') or row.get('Description')
            available = True
            try:
                item = MenuItem(name=name, price=price, description=description, available=available)
                db.session.add(item)
                db.session.flush()
                created.append(item.id)
                results.append({'row': row_no, 'status': 'created', 'id': item.id})
            except Exception as e:
                db.session.rollback()
                results.append({'row': row_no, 'status': 'error', 'reason': str(e)})
        db.session.commit()
        # audit
        log = AuditLog(user_id=getattr(current_user,'id',None), username=getattr(current_user,'username',None), action='import', object_type='menu_item', object_id=None, details=f'imported {len(created)} items')
        db.session.add(log)
        db.session.commit()
        return jsonify({'created': created, 'results': results}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/api/menu/export', methods=['GET'])
@login_required
@permission_required('manage_menu')
def api_menu_export():
    try:
        items = MenuItem.query.all()
        si = io.StringIO()
        writer = csv.writer(si)
        writer.writerow(['id','name','description','price','available'])
        for i in items:
            writer.writerow([i.id,i.name,i.description or '',i.price,i.available])
        si.seek(0)
        return send_file(io.BytesIO(si.getvalue().encode('utf-8')), mimetype='text/csv', as_attachment=True, download_name='menu_export.csv')
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/api/menu/template', methods=['GET'])
@login_required
@permission_required('manage_menu')
def api_menu_template():
    try:
        si = io.StringIO()
        writer = csv.writer(si)
        writer.writerow(['name','price','description'])
        si.seek(0)
        return send_file(io.BytesIO(si.getvalue().encode('utf-8')), mimetype='text/csv', as_attachment=True, download_name='menu_template.csv')
    except Exception as e:
        return jsonify({'error': str(e)}), 500


### Inventory management API
@admin_bp.route("/api/inventory", methods=["GET"])
@login_required
@permission_required('manage_inventory')
def api_get_inventory():
    try:
        items = InventoryItem.query.order_by(InventoryItem.id.desc()).all()
        return jsonify([{
            "id": i.id,
            "name": i.name,
            "quantity": i.quantity,
            "unit": i.unit,
            "updated_at": i.updated_at.isoformat() if i.updated_at else None
        } for i in items])
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@admin_bp.route("/api/inventory", methods=["POST"])
@login_required
@permission_required('manage_inventory')
def api_create_inventory():
    data = request.get_json() or {}
    try:
        name = data.get("name")
        quantity = int(data.get("quantity", 0))
        unit = data.get("unit", "unit")
        if not name:
            return jsonify({"error": "name is required"}), 400
        item = InventoryItem(name=name, quantity=quantity, unit=unit)
        db.session.add(item)
        db.session.commit()
        log = AuditLog(user_id=getattr(current_user,'id',None), username=getattr(current_user,'username',None), action='create', object_type='inventory_item', object_id=item.id, details=f'created {item.name}')
        db.session.add(log)
        db.session.commit()
        return jsonify({"id": item.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@admin_bp.route("/api/inventory/<int:item_id>", methods=["PUT"])
@login_required
@permission_required('manage_inventory')
def api_update_inventory(item_id):
    data = request.get_json() or {}
    try:
        item = InventoryItem.query.get_or_404(item_id)
        changes = []
        if "name" in data and data.get("name")!=item.name:
            changes.append(f'name: {item.name} -> {data.get("name")}')
            item.name = data.get("name")
        if "quantity" in data and int(data.get("quantity"))!=item.quantity:
            changes.append(f'quantity: {item.quantity} -> {data.get("quantity")}')
            item.quantity = int(data.get("quantity"))
        if "unit" in data and data.get("unit")!=item.unit:
            changes.append(f'unit: {item.unit} -> {data.get("unit")}')
            item.unit = data.get("unit")
        db.session.commit()
        if changes:
            log = AuditLog(user_id=getattr(current_user,'id',None), username=getattr(current_user,'username',None), action='update', object_type='inventory_item', object_id=item.id, details='; '.join(changes))
            db.session.add(log)
            db.session.commit()
        return jsonify({"status": "ok"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@admin_bp.route("/api/inventory/<int:item_id>", methods=["DELETE"])
@login_required
@permission_required('manage_inventory')
def api_delete_inventory(item_id):
    try:
        item = InventoryItem.query.get_or_404(item_id)
        name = item.name
        db.session.delete(item)
        db.session.commit()
        log = AuditLog(user_id=getattr(current_user,'id',None), username=getattr(current_user,'username',None), action='delete', object_type='inventory_item', object_id=item_id, details=f'deleted {name}')
        db.session.add(log)
        db.session.commit()
        return jsonify({"status": "deleted"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@admin_bp.route('/api/inventory/import', methods=['POST'])
@login_required
@permission_required('manage_inventory')
def api_inventory_import():
    try:
        f = request.files.get('file')
        if not f:
            return jsonify({'error':'file required'}), 400
        stream = io.StringIO(f.stream.read().decode('utf-8'))
        reader = csv.DictReader(stream)
        created = []
        results = []
        row_no = 0
        for row in reader:
            row_no += 1
            name = row.get('name') or row.get('Name')
            if not name:
                results.append({'row': row_no, 'status': 'skipped', 'reason': 'missing name'})
                continue
            try:
                quantity = int(float(row.get('quantity') or row.get('Quantity') or 0))
            except Exception:
                results.append({'row': row_no, 'status': 'error', 'reason': 'invalid quantity'})
                continue
            unit = row.get('unit') or row.get('Unit') or 'unit'
            try:
                item = InventoryItem(name=name, quantity=quantity, unit=unit)
                db.session.add(item)
                db.session.flush()
                created.append(item.id)
                results.append({'row': row_no, 'status': 'created', 'id': item.id})
            except Exception as e:
                db.session.rollback()
                results.append({'row': row_no, 'status': 'error', 'reason': str(e)})
        db.session.commit()
        log = AuditLog(user_id=getattr(current_user,'id',None), username=getattr(current_user,'username',None), action='import', object_type='inventory_item', object_id=None, details=f'imported {len(created)} items')
        db.session.add(log)
        db.session.commit()
        return jsonify({'created': created, 'results': results}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/api/inventory/export', methods=['GET'])
@login_required
@permission_required('manage_inventory')
def api_inventory_export():
    try:
        items = InventoryItem.query.all()
        si = io.StringIO()
        writer = csv.writer(si)
        writer.writerow(['id','name','quantity','unit','updated_at'])
        for i in items:
            writer.writerow([i.id,i.name,i.quantity,i.unit,i.updated_at.isoformat() if i.updated_at else ''])
        si.seek(0)
        return send_file(io.BytesIO(si.getvalue().encode('utf-8')), mimetype='text/csv', as_attachment=True, download_name='inventory_export.csv')
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/api/inventory/template', methods=['GET'])
@login_required
@permission_required('manage_inventory')
def api_inventory_template():
    try:
        si = io.StringIO()
        writer = csv.writer(si)
        writer.writerow(['name','quantity','unit'])
        si.seek(0)
        return send_file(io.BytesIO(si.getvalue().encode('utf-8')), mimetype='text/csv', as_attachment=True, download_name='inventory_template.csv')
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/api/logs', methods=['GET'])
@login_required
@admin_required
def api_get_logs():
    try:
        # allow optional filtering: user, action, object_type
        q = AuditLog.query
        user = request.args.get('user')
        action = request.args.get('action')
        object_type = request.args.get('object_type')
        if user:
            q = q.filter(AuditLog.username == user)
        if action:
            q = q.filter(AuditLog.action == action)
        if object_type:
            q = q.filter(AuditLog.object_type == object_type)
        rows = q.order_by(AuditLog.created_at.desc()).limit(200).all()
        return jsonify([{"id": r.id, "user_id": r.user_id, "username": r.username, "action": r.action, "object_type": r.object_type, "object_id": r.object_id, "details": r.details, "created_at": r.created_at.isoformat()} for r in rows])
    except Exception as e:
        return jsonify({"error": str(e)}), 500


### Role permissions
@admin_bp.route('/api/roles', methods=['GET'])
@login_required
@admin_required
def api_get_roles():
    try:
        # define canonical roles and permissions
        roles = ['admin', 'manager', 'waiter', 'kitchen']
        permissions = ['manage_menu', 'manage_inventory', 'manage_users', 'view_logs', 'manage_orders', 'view_analytics']
        # defaults when creating missing rows
        defaults = {
            'admin': {p: True for p in permissions},
            'manager': { 'manage_menu': True, 'manage_inventory': True, 'manage_users': False, 'view_logs': True, 'manage_orders': True, 'view_analytics': True },
            'waiter': { 'manage_menu': False, 'manage_inventory': False, 'manage_users': False, 'view_logs': False, 'manage_orders': True, 'view_analytics': False },
            'kitchen': { 'manage_menu': False, 'manage_inventory': False, 'manage_users': False, 'view_logs': False, 'manage_orders': True, 'view_analytics': False }
        }

        out = {}
        for role in roles:
            out[role] = {}
            for perm in permissions:
                rp = RolePermission.query.filter_by(role=role, permission=perm).first()
                if not rp:
                    # create default if missing
                    allowed = defaults.get(role, {}).get(perm, False)
                    rp = RolePermission(role=role, permission=perm, allowed=allowed)
                    db.session.add(rp)
                    db.session.flush()
                out[role][perm] = bool(rp.allowed)
        db.session.commit()
        return jsonify({'roles': out, 'permissions': permissions})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/api/roles', methods=['PUT'])
@login_required
@admin_required
def api_update_role():
    data = request.get_json() or {}
    try:
        role = data.get('role')
        perms = data.get('permissions') or {}
        if not role:
            return jsonify({'error':'role required'}), 400
        changed = []
        for perm, allowed in perms.items():
            rp = RolePermission.query.filter_by(role=role, permission=perm).first()
            if not rp:
                rp = RolePermission(role=role, permission=perm, allowed=bool(allowed))
                db.session.add(rp)
                changed.append(f'created {perm}={allowed}')
            else:
                if bool(rp.allowed) != bool(allowed):
                    changed.append(f'{perm}: {rp.allowed} -> {allowed}')
                    rp.allowed = bool(allowed)
        db.session.commit()
        if changed:
            log = AuditLog(user_id=getattr(current_user,'id',None), username=getattr(current_user,'username',None), action='update', object_type='role_permissions', object_id=None, details=f'{role}: ' + '; '.join(changed))
            db.session.add(log)
            db.session.commit()
        return jsonify({'status':'ok'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
