from datetime import date, time, timedelta, datetime
from bson import ObjectId
from ..database import db_manager
from .promotionCon import PromoConnection  

class SalesReport:
    """
    Unified service that combines POS transactions and sales logging
    Works with both PromoConnection and SalesLogService
    """
    def __init__(self):
        self.db = db_manager.get_database()
        self.sales_collection = self.db.sales 
        self.sales_log_collection = self.db.sales_log  
        self.products_collection = self.db.products
        self.promotions_collection = self.db.promotions
        self.promo_connection = PromoConnection()

    def convert_object_id(self, document):
        """Convert ObjectId to string for JSON serialization"""
        if document and '_id' in document:
            document['_id'] = str(document['_id'])
        return document
    
    def process_pos_transaction(self, checkout_data, promotion_name=None, cashier_id=None):
        """
        Process POS transaction using existing PromoConnection logic
        This is just a wrapper for now - no changes to existing flow
        """
        try:
            # Use existing PromoConnection method
            result = self.promo_connection.pos_transaction(
                checkout_data=checkout_data,
                promotion_name=promotion_name,
                cashier_id=cashier_id
            )
            
            # Add source tracking to the response
            if result.get('success') and result.get('sales_record'):
                # Update the sales record to include source
                sales_id = result['sales_record']['_id']
                self.sales_collection.update_one(
                    {'_id': ObjectId(sales_id)},
                    {'$set': {'source': 'pos'}}
                )
                result['sales_record']['source'] = 'pos'
            
            return result
            
        except Exception as e:
            raise Exception(f"Error processing POS transaction: {str(e)}")

    # ================================================================
    # UNIFIED SALES SUMMARY (BOTH COLLECTIONS)
    # ================================================================
    
    def get_unified_sales_summary(self, date_range=None, include_source=None):
        """
        Get sales summary from BOTH sales and sales_log collections
        
        Args:
            date_range: {'start': datetime, 'end': datetime}
            include_source: ['pos', 'manual', 'csv'] or None for all
        """
        try:
            # Build date filter
            date_filter = {}
            if date_range:
                date_filter = {
                    'transaction_date': {
                        '$gte': date_range['start'],
                        '$lte': date_range['end']
                    }
                }
            
            # Build source filter
            source_filter = {}
            if include_source:
                source_filter = {'source': {'$in': include_source}}
            
            # Combine filters
            query = {}
            if date_filter and source_filter:
                query = {'$and': [date_filter, source_filter]}
            elif date_filter:
                query = date_filter
            elif source_filter:
                query = source_filter

            # Get POS sales (from sales collection)
            pos_sales = list(self.sales_collection.find(query))
            
            # Get manual/CSV sales (from sales_log collection)
            log_sales = list(self.sales_log_collection.find(query))
            
            # Process POS sales
            pos_totals = self._calculate_pos_totals(pos_sales)
            
            # Process sales_log sales
            log_totals = self._calculate_log_totals(log_sales)
            
            # Combine totals
            combined_totals = {
                'total_transactions': pos_totals['count'] + log_totals['count'],
                'total_revenue': round(pos_totals['revenue'] + log_totals['revenue'], 2),
                'gross_revenue': round(pos_totals['gross'] + log_totals['gross'], 2),
                'total_discounts': round(pos_totals['discounts'], 2),  # Only POS has discounts
                'average_transaction': 0
            }
            
            # Calculate average
            if combined_totals['total_transactions'] > 0:
                combined_totals['average_transaction'] = round(
                    combined_totals['total_revenue'] / combined_totals['total_transactions'], 2
                )
            
            # Source breakdown
            source_breakdown = {
                'pos': {
                    'count': pos_totals['count'],
                    'revenue': round(pos_totals['revenue'], 2),
                    'percentage': 0
                },
                'manual_csv': {
                    'count': log_totals['count'],
                    'revenue': round(log_totals['revenue'], 2),
                    'percentage': 0
                }
            }
            
            # Calculate percentages
            if combined_totals['total_revenue'] > 0:
                source_breakdown['pos']['percentage'] = round(
                    (pos_totals['revenue'] / combined_totals['total_revenue']) * 100, 1
                )
                source_breakdown['manual_csv']['percentage'] = round(
                    (log_totals['revenue'] / combined_totals['total_revenue']) * 100, 1
                )
            
            # Combine recent transactions (normalized format)
            recent_transactions = []
            
            # Add POS transactions
            for sale in pos_sales[-10:]:  # Last 10
                recent_transactions.append(self._normalize_pos_transaction(sale))
            
            # Add sales_log transactions
            for sale in log_sales[-10:]:  # Last 10
                recent_transactions.append(self._normalize_log_transaction(sale))
            
            # Sort by transaction date (most recent first)
            recent_transactions.sort(key=lambda x: x['transaction_date'], reverse=True)
            
            return {
                'summary': combined_totals,
                'source_breakdown': source_breakdown,
                'transactions': recent_transactions[:20]  # Show top 20
            }
            
        except Exception as e:
            raise Exception(f"Error getting unified sales summary: {str(e)}")
        
    def get_pos_sales_summary(self, date_range=None):
        """
        Get basic summary of POS sales only (for backward compatibility)
        """
        return self.get_unified_sales_summary(date_range, include_source=['pos'])

    # ================================================================
    # UPDATED REPORT METHODS (NOW USING UNIFIED DATA)
    # ================================================================

    def get_todays_sales(self):
        """Get today's sales from BOTH collections"""
        try:
            today = date.today()
            start_of_day = datetime.combine(today, time.min)
            end_of_day = datetime.combine(today, time.max)
            
            date_range = {'start': start_of_day, 'end': end_of_day}
            
            return self.get_unified_sales_summary(date_range)
            
        except Exception as e:
            raise Exception(f"Error getting today's sales: {str(e)}") 
        
    def get_weekly_sales(self):
        """Get this week's sales from BOTH collections"""
        try:
            today = date.today()
            days_since_monday = today.weekday()  # Monday = 0
            start_of_week = today - timedelta(days=days_since_monday)
            end_of_week = start_of_week + timedelta(days=6)
            
            # Convert to datetime objects
            start_of_week_dt = datetime.combine(start_of_week, time.min)
            end_of_week_dt = datetime.combine(end_of_week, time.max)
            
            date_range = {'start': start_of_week_dt, 'end': end_of_week_dt}
            
            result = self.get_unified_sales_summary(date_range)
            
            # Add week info
            result['week_info'] = {
                'start_date': start_of_week.isoformat(),
                'end_date': end_of_week.isoformat(),
                'week_number': start_of_week.isocalendar()[1]
            }
            
            return result
            
        except Exception as e:
            raise Exception(f"Error getting weekly sales: {str(e)}")
        
    def get_monthly_sales(self):
        """Get current month's sales from BOTH collections"""
        try:
            today = date.today()
            
            # First day of current month
            start_of_month = date(today.year, today.month, 1)
            
            # Last day of current month
            if today.month == 12:
                end_of_month = date(today.year + 1, 1, 1) - timedelta(days=1)
            else:
                end_of_month = date(today.year, today.month + 1, 1) - timedelta(days=1)
            
            # Convert to datetime
            start_of_month_dt = datetime.combine(start_of_month, time.min)
            end_of_month_dt = datetime.combine(end_of_month, time.max)
            
            date_range = {'start': start_of_month_dt, 'end': end_of_month_dt}
            
            result = self.get_unified_sales_summary(date_range)
            
            # Add month info
            result['month_info'] = {
                'year': today.year,
                'month': today.month,
                'month_name': today.strftime('%B'),
                'start_date': start_of_month.isoformat(),
                'end_date': end_of_month.isoformat()
            }
            
            return result
            
        except Exception as e:
            raise Exception(f"Error getting monthly sales: {str(e)}")
        
    def get_yearly_sales(self):
        """Get current year's sales from BOTH collections"""
        try:
            today = date.today()
            
            # First day of year
            start_of_year = date(today.year, 1, 1)
            # Last day of year
            end_of_year = date(today.year, 12, 31)
            
            # Convert to datetime
            start_of_year_dt = datetime.combine(start_of_year, time.min)
            end_of_year_dt = datetime.combine(end_of_year, time.max)
            
            date_range = {'start': start_of_year_dt, 'end': end_of_year_dt}
            
            result = self.get_unified_sales_summary(date_range)
            
            # Add year info
            result['year_info'] = {
                'year': today.year,
                'start_date': start_of_year.isoformat(),
                'end_date': end_of_year.isoformat()
            }
            
            return result
            
        except Exception as e:
            raise Exception(f"Error getting yearly sales: {str(e)}")
        
    def get_last_seven_days(self):
        """Get last 7 days sales from BOTH collections"""
        try:
            today = date.today()
            seven_days_ago = today - timedelta(days=7)
            
            start_dt = datetime.combine(seven_days_ago, time.min)
            end_dt = datetime.combine(today, time.max)
            
            date_range = {'start': start_dt, 'end': end_dt}
            
            result = self.get_unified_sales_summary(date_range)
            
            # Add period info
            result['period_info'] = {
                'start_date': seven_days_ago.isoformat(),
                'end_date': today.isoformat(),
                'period_type': 'last_7_days',
                'total_days': 7
            }
            
            return result
            
        except Exception as e:
            raise Exception(f"Error getting last 7 days sales: {str(e)}")
        
    def get_previous_week_sales(self):
        """Get last week's sales from BOTH collections"""
        try:
            today = date.today()
            
            # Calculate start of current week (Monday)
            days_since_monday = today.weekday()
            start_of_current_week = today - timedelta(days=days_since_monday)
            
            # Calculate previous week
            start_of_previous_week = start_of_current_week - timedelta(days=7)
            end_of_previous_week = start_of_previous_week + timedelta(days=6)
            
            # Convert to datetime
            start_dt = datetime.combine(start_of_previous_week, time.min)
            end_dt = datetime.combine(end_of_previous_week, time.max)
            
            date_range = {'start': start_dt, 'end': end_dt}
            
            result = self.get_unified_sales_summary(date_range)
            
            # Add week info
            result['week_info'] = {
                'start_date': start_of_previous_week.isoformat(),
                'end_date': end_of_previous_week.isoformat(),
                'week_number': start_of_previous_week.isocalendar()[1],
                'week_type': 'previous_week'
            }
            
            return result
            
        except Exception as e:
            raise Exception(f"Error getting previous week's sales: {str(e)}")

    def get_sales_comparison(self, period='week'):
        """Compare current vs previous period using unified data"""
        try:
            if period == 'week':
                current = self.get_weekly_sales()
                previous = self.get_previous_week_sales()
            elif period == 'month':
                current = self.get_monthly_sales()
                previous = self.get_previous_month_sales()
            else:
                raise ValueError("Period must be 'week' or 'month'")
            
            current_revenue = current['summary']['total_revenue']
            previous_revenue = previous['summary']['total_revenue']
            
            change = current_revenue - previous_revenue
            change_percent = 0
            if previous_revenue > 0:
                change_percent = (change / previous_revenue) * 100
            
            return {
                'current_period': current,
                'previous_period': previous,
                'comparison': {
                    'revenue_change': round(change, 2),
                    'revenue_change_percent': round(change_percent, 2),
                    'performance': 'improved' if change > 0 else 'declined' if change < 0 else 'same'
                }
            }
            
        except Exception as e:
            raise Exception(f"Error getting sales comparison: {str(e)}")
    
    def get_previous_month_sales(self):
        """Get previous month's sales from BOTH collections"""
        try:
            today = date.today()
            
            # Calculate previous month
            if today.month == 1:
                prev_year = today.year - 1
                prev_month = 12
            else:
                prev_year = today.year
                prev_month = today.month - 1
            
            # First day of previous month
            start_of_prev_month = date(prev_year, prev_month, 1)
            
            # Last day of previous month
            if prev_month == 12:
                end_of_prev_month = date(prev_year + 1, 1, 1) - timedelta(days=1)
            else:
                end_of_prev_month = date(prev_year, prev_month + 1, 1) - timedelta(days=1)
            
            # Convert to datetime
            start_dt = datetime.combine(start_of_prev_month, time.min)
            end_dt = datetime.combine(end_of_prev_month, time.max)
            
            date_range = {'start': start_dt, 'end': end_dt}
            
            result = self.get_unified_sales_summary(date_range)
            
            # Add month info
            result['month_info'] = {
                'year': prev_year,
                'month': prev_month,
                'month_name': start_of_prev_month.strftime('%B'),
                'start_date': start_of_prev_month.isoformat(),
                'end_date': end_of_prev_month.isoformat(),
                'month_type': 'previous_month'
            }
            
            return result
            
        except Exception as e:
            raise Exception(f"Error getting previous month sales: {str(e)}")

    def get_dashboard_summary(self):
        """Get comprehensive dashboard data from BOTH collections"""
        try:
            today_sales = self.get_todays_sales()
            week_sales = self.get_weekly_sales()
            month_sales = self.get_monthly_sales()
            week_comparison = self.get_sales_comparison('week')
            
            # Add breakdown info
            pos_today = self.get_unified_sales_summary({
                'start': datetime.combine(date.today(), time.min),
                'end': datetime.combine(date.today(), time.max)
            }, include_source=['pos'])
            
            return {
                'today': {
                    'total': today_sales['summary'],
                    'pos_only': pos_today['summary'],
                    'source_breakdown': today_sales['source_breakdown']
                },
                'this_week': week_sales['summary'],
                'this_month': month_sales['summary'],
                'week_vs_last_week': week_comparison['comparison'],
                'generated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            raise Exception(f"Error getting dashboard summary: {str(e)}")

    # ================================================================
    # HELPER METHODS FOR UNIFIED DATA
    # ================================================================
        
    def get_all_sales_unified(self, date_range=None, include_source=None):
        """
        Get sales from both collections for unified reporting
        
        Args:
            date_range: {'start': datetime, 'end': datetime}
            include_source: List of sources to include ['pos', 'csv', 'manual'] or None for all
        """
        try:
            match_conditions = []
            
            # Date range filter
            if date_range:
                date_filter = {
                    "transaction_date": {
                        "$gte": date_range['start'],
                        "$lte": date_range['end']
                    }
                }
                match_conditions.append(date_filter)

            # Source filter
            if include_source:
                source_filter = {"source": {"$in": include_source}}
                match_conditions.append(source_filter)

            # Build match stage
            match_stage = {"$and": match_conditions} if match_conditions else {}

            # Get POS sales
            pos_sales = list(self.sales_collection.find(match_stage))
            
            # Get sales log entries
            sales_log_entries = list(self.sales_log_collection.find(match_stage))

            # Normalize both formats
            unified_sales = []
            
            # Process POS sales
            for sale in pos_sales:
                unified_sale = self._normalize_pos_sale(sale)
                unified_sales.append(unified_sale)

            # Process sales log entries
            for sale in sales_log_entries:
                unified_sale = self._normalize_sales_log(sale)
                unified_sales.append(unified_sale)

            # Sort by transaction date
            unified_sales.sort(key=lambda x: x['transaction_date'], reverse=True)

            return unified_sales

        except Exception as e:
            raise Exception(f"Error getting unified sales: {str(e)}")
        
    def _calculate_pos_totals(self, pos_sales):
        """Calculate totals from POS sales"""
        count = len(pos_sales)
        revenue = sum(sale.get('final_amount', 0) for sale in pos_sales)
        gross = sum(sale.get('total_amount', 0) for sale in pos_sales)
        discounts = sum(sale.get('total_discount', 0) for sale in pos_sales)
        
        return {
            'count': count,
            'revenue': revenue,
            'gross': gross,
            'discounts': discounts
        }
    
    def _calculate_log_totals(self, log_sales):
        """Calculate totals from sales_log"""
        count = len(log_sales)
        revenue = sum(sale.get('total_amount', 0) for sale in log_sales)
        gross = revenue  # sales_log doesn't have separate gross/final amounts
        
        return {
            'count': count,
            'revenue': revenue,
            'gross': gross
        }
    
    def _normalize_pos_transaction(self, sale):
        """Convert POS transaction to standard format"""
        return {
            '_id': str(sale['_id']),
            'transaction_date': sale['transaction_date'],
            'total_amount': sale.get('final_amount', 0),
            'source': 'pos',
            'payment_method': sale.get('payment_method', 'cash'),
            'items_count': len(sale.get('items', [])),
            'cashier_id': sale.get('cashier_id'),
            'promotion_applied': sale.get('promotion_applied')
        }
    
    def _normalize_log_transaction(self, sale):
        """Convert sales_log transaction to standard format"""
        return {
            '_id': str(sale['_id']),
            'transaction_date': sale['transaction_date'],
            'total_amount': sale.get('total_amount', 0),
            'source': sale.get('source', 'manual'),
            'payment_method': sale.get('payment_method', 'cash'),
            'items_count': len(sale.get('item_list', [])),
            'user_id': str(sale['user_id']) if sale.get('user_id') else None,
            'sales_type': sale.get('sales_type', 'retail')
        }

    def _normalize_pos_sale(self, pos_sale):
        """Convert POS sale to unified format"""
        return {
            '_id': str(pos_sale['_id']),
            'transaction_date': pos_sale['transaction_date'],
            'total_amount': pos_sale.get('final_amount', pos_sale.get('total_amount', 0)),
            'gross_amount': pos_sale.get('total_amount', pos_sale.get('final_amount', 0)),
            'discount_amount': pos_sale.get('total_discount', 0),
            'payment_method': pos_sale.get('payment_method', 'cash'),
            'customer_id': pos_sale.get('customer_id'),
            'cashier_id': pos_sale.get('cashier_id'),
            'user_id': pos_sale.get('cashier_id'),  # Map cashier_id to user_id for consistency
            'promotion_applied': pos_sale.get('promotion_applied'),
            'items': pos_sale.get('items', []),
            'source': 'pos',
            'status': pos_sale.get('status', 'completed'),
            'collection': 'sales',
            'sales_type': 'retail',  # Default for POS
            'tax_amount': 0,  # POS sales don't typically track tax separately
            'notes': ''
        }

    def _normalize_sales_log(self, sales_log):
        """Convert sales log to unified format"""
        return {
            '_id': str(sales_log['_id']),
            'transaction_date': sales_log['transaction_date'],
            'total_amount': sales_log['total_amount'],
            'gross_amount': sales_log['total_amount'],
            'discount_amount': 0,  # Sales logs don't typically have discounts
            'payment_method': sales_log.get('payment_method', 'cash'),
            'customer_id': str(sales_log['customer_id']) if sales_log.get('customer_id') else None,
            'cashier_id': str(sales_log['user_id']) if sales_log.get('user_id') else None,
            'user_id': str(sales_log['user_id']) if sales_log.get('user_id') else None,
            'promotion_applied': None,
            'items': self._convert_item_list_to_items(sales_log.get('item_list', [])),
            'source': sales_log.get('source', 'manual'),
            'status': sales_log.get('status', 'completed'),
            'collection': 'sales_log',
            'sales_type': sales_log.get('sales_type', 'retail'),
            'tax_amount': sales_log.get('tax_amount', 0),
            'notes': sales_log.get('notes', '')
        }

    def _convert_item_list_to_items(self, item_list):
        """Convert sales log item_list to POS items format"""
        items = []
        for item in item_list:
            items.append({
                'product_id': item.get('item_code', ''),
                'product_name': item.get('item_name', ''),
                'quantity': item.get('quantity', 0),
                'price': item.get('unit_price', 0),
                'total': item.get('total_price', 0),
                'unit': item.get('unit_of_measure', 'pc')
            })
        return items

    # ================================================================
    # ADDITIONAL UTILITY METHODS
    # ================================================================
    
    def get_pos_only_summary(self, date_range=None):
        """Get POS-only sales (for comparison)"""
        return self.get_unified_sales_summary(date_range, include_source=['pos'])
    
    def get_manual_only_summary(self, date_range=None):
        """Get manual/CSV sales only"""
        return self.get_unified_sales_summary(date_range, include_source=['manual', 'csv'])