from datetime import datetime, timedelta
from ..database import db_manager


class OnlineTransactionService:
    """Minimal online transaction service for creating customer web orders.

    This mirrors the essential behavior from PANN_POS_SYSTEM to support
    Ramyeonsite checkout. It focuses on order creation and totals computation.
    """

    def __init__(self):
        self.db = db_manager.get_database()
        self.customers = self.db.customers
        self.online_transactions = self.db.online_transactions

    # ------------------------- Helpers -------------------------
    def _generate_order_id(self) -> str:
        count = self.online_transactions.count_documents({}) + 1
        return f"ONLINE-{count:06d}"

    def _compute_items(self, items):
        computed = []
        subtotal = 0.0
        for item in items or []:
            price = float(item.get('price', 0))
            qty = int(item.get('quantity', 1))
            line_subtotal = round(price * qty, 2)
            computed.append({
                'product_id': item.get('product_id') or item.get('id') or item.get('productId'),
                'product_name': item.get('name') or item.get('product_name'),
                'quantity': qty,
                'price': price,
                'subtotal': line_subtotal,
            })
            subtotal += line_subtotal
        return computed, round(subtotal, 2)

    def _compute_fees(self, delivery_type: str):
        delivery_fee = 50.0 if (delivery_type or '').lower() == 'delivery' else 0.0
        service_fee = 15.0
        return round(delivery_fee, 2), round(service_fee, 2)

    def _compute_points_discount(self, points_to_redeem: int, subtotal: float):
        try:
            pts = int(points_to_redeem or 0)
        except Exception:
            pts = 0
        discount = round(pts / 4.0, 2)  # 4 points = ₱1
        return float(min(discount, subtotal)), pts

    def _compute_points_earned(self, subtotal_after_discount: float) -> int:
        # Earn rate: 20% of order value (matches existing UI assumptions)
        return int(round(subtotal_after_discount * 0.20))

    # ------------------------- Public API -------------------------
    def create_online_order(self, order_data: dict, customer_id: str):
        if not customer_id:
            raise ValueError("customer_id is required")

        items_in = order_data.get('items', [])
        delivery_address = order_data.get('delivery_address', {})
        payment_method = order_data.get('payment_method', 'cod')
        delivery_type = order_data.get('delivery_type', 'delivery')
        points_to_redeem = int(order_data.get('points_to_redeem', 0) or 0)
        notes = order_data.get('notes') or order_data.get('special_instructions') or ''

        # Lookup customer (allow guest orders if no matching customer)
        customer = None
        if customer_id:
            try:
                customer = self.customers.find_one({'_id': customer_id})
            except Exception:
                customer = None

        # Build items and totals
        items, subtotal = self._compute_items(items_in)
        points_discount, pts_used = self._compute_points_discount(points_to_redeem, subtotal)
        subtotal_after_discount = round(subtotal - points_discount, 2)
        delivery_fee, service_fee = self._compute_fees(delivery_type)
        total_amount = round(subtotal_after_discount + delivery_fee + service_fee, 2)

        # Generate order id
        order_id = self._generate_order_id()

        # Prepare order record
        # Timestamps: store naive UTC datetimes (pymongo requirement) and local (Asia/Manila, +08:00)
        now_utc = datetime.utcnow()  # naive UTC
        now_local = now_utc + timedelta(hours=8)  # Asia/Manila approximation
        order_record = {
            '_id': order_id,
            'customer_id': customer_id or 'GUEST',
            'customer_name': (customer.get('full_name') if customer else 'Guest') or (customer.get('username') if customer else 'Guest') or (customer.get('email') if customer else 'guest'),
            'customer_email': customer.get('email') if customer else None,
            'customer_phone': customer.get('phone') if customer else None,
            'transaction_date': now_utc,
            'transaction_date_local': now_local,
            'timezone': 'Asia/Manila',
            'utc_offset_minutes': 480,
            'delivery_address': delivery_address,
            'delivery_type': delivery_type,
            'items': items,
            'subtotal': subtotal,
            'points_redeemed': pts_used,
            'points_discount': points_discount,
            'subtotal_after_discount': subtotal_after_discount,
            'delivery_fee': delivery_fee,
            'service_fee': service_fee,
            'service_fee_breakdown': {'platform': service_fee},
            'total_amount': total_amount,
            'payment_method': payment_method,
            'payment_status': 'pending',
            'payment_reference': None,
            'order_status': 'pending',
            'status': 'pending',
            'notes': notes,
            'status_history': [
                {'status': 'pending', 'timestamp': now_utc}
            ],
            'loyalty_points_earned': self._compute_points_earned(subtotal_after_discount),
            'created_at': now_utc,
            'updated_at': now_utc,
        }

        self.online_transactions.insert_one(order_record)
        doc = order_record
        if customer:
            earned_points = order_record.get('loyalty_points_earned', 0)
            redeemed_points = order_record.get('points_redeemed', 0)

            # Current points (default 0)
            current_points = int(customer.get('loyalty_points', 0))

            # Compute new total
            new_total = current_points - redeemed_points + earned_points
            new_total = max(new_total, 0)  # prevent negative

            # Update customer record
            self.customers.update_one(
                {'_id': customer_id},
                {'$set': {'loyalty_points': new_total}}
            )

            # Reflect in response
            order_record['updated_loyalty_points'] = new_total

        return {
            'success': True,
            'data': {
                'order_id': order_id,
                'order': order_record,
            }
        }


