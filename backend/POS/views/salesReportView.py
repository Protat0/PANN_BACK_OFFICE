from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import HttpResponse
from services.salesReport import SalesReport
import logging

def get_authenticated_user_from_jwt(request):
    """Helper function to get authenticated user with proper username from JWT token"""
    try:
        authorization = request.headers.get("Authorization")
        if not authorization or not authorization.startswith("Bearer "):
            return None
        
        token = authorization.split(" ")[1]
        
        from ...app.services.auth_services import AuthService
        from bson import ObjectId
        
        auth_service = AuthService()
        user_data = auth_service.get_current_user(token)
        
        if not user_data:
            return None
        
        user_id = user_data.get('user_id')
        user_doc = auth_service.user_collection.find_one({"_id": ObjectId(user_id)})
        
        if not user_doc:
            return None
        
        actual_username = user_doc.get('username')
        if actual_username and actual_username.strip():
            display_username = actual_username
        else:
            display_username = user_doc.get('email', 'unknown')
        
        return {
            "user_id": user_id,
            "username": display_username,
            "email": user_doc.get('email'),
            "branch_id": 1,
            "role": user_doc.get('role', 'employee'),
            "ip_address": request.META.get('REMOTE_ADDR'),
            "user_agent": request.META.get('HTTP_USER_AGENT')
        }
        
    except Exception as e:
        print(f"JWT Auth helper error: {e}")
        return None

# ================================================================
# FIXED SALES REPORT VIEWS
# ================================================================

class DailyReports(APIView):
    """Get daily sales report"""
    def get(self, request):
        try:
            current_user = get_authenticated_user_from_jwt(request)
            
            if not current_user:
                return Response(
                    {"error": "Authentication required"}, 
                    status=status.HTTP_401_UNAUTHORIZED
                )

            sales_report = SalesReport()
            result = sales_report.get_todays_sales()
             
            # ✅ FIXED: Use 200 OK for GET requests, not 201 CREATED
            return Response(result, status=status.HTTP_200_OK)
           
        except Exception as e:
            logging.error(f"Error getting daily sales report: {str(e)}")
            return Response(
                {"error": f"Error getting daily sales report: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class WeeklyReports(APIView):
    """Get weekly sales report"""
    def get(self, request):
        try:
            current_user = get_authenticated_user_from_jwt(request)
            
            if not current_user:
                return Response(
                    {"error": "Authentication required"}, 
                    status=status.HTTP_401_UNAUTHORIZED
                )

            sales_report = SalesReport()
            result = sales_report.get_weekly_sales()
             
            return Response(result, status=status.HTTP_200_OK)
           
        except Exception as e:
            logging.error(f"Error getting weekly sales report: {str(e)}")
            return Response(
                {"error": f"Error getting weekly sales report: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            ) 

class MonthlyReports(APIView):
    """Get monthly sales report"""
    def get(self, request):
        try:
            current_user = get_authenticated_user_from_jwt(request)
            
            if not current_user:
                return Response(
                    {"error": "Authentication required"}, 
                    status=status.HTTP_401_UNAUTHORIZED
                )

            sales_report = SalesReport()
            result = sales_report.get_monthly_sales()
             
            return Response(result, status=status.HTTP_200_OK)
           
        except Exception as e:
            logging.error(f"Error getting monthly sales report: {str(e)}")
            return Response(
                {"error": f"Error getting monthly sales report: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            ) 

class YearlyReports(APIView):
    """Get yearly sales report"""
    def get(self, request):
        try:
            current_user = get_authenticated_user_from_jwt(request)
            
            if not current_user:
                return Response(
                    {"error": "Authentication required"}, 
                    status=status.HTTP_401_UNAUTHORIZED
                )

            sales_report = SalesReport()
            result = sales_report.get_yearly_sales()
             
            return Response(result, status=status.HTTP_200_OK)
           
        except Exception as e:
            logging.error(f"Error getting yearly sales report: {str(e)}")
            return Response(
                {"error": f"Error getting yearly sales report: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            ) 

class LastSevenDaysReports(APIView):
    """Get last 7 days sales report"""
    def get(self, request):
        try:
            current_user = get_authenticated_user_from_jwt(request)
            
            if not current_user:
                return Response(
                    {"error": "Authentication required"}, 
                    status=status.HTTP_401_UNAUTHORIZED
                )

            sales_report = SalesReport()
            result = sales_report.get_last_seven_days()
             
            return Response(result, status=status.HTTP_200_OK)
           
        except Exception as e:
            logging.error(f"Error getting last seven days sales report: {str(e)}")
            return Response(
                {"error": f"Error getting last seven days sales report: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            ) 
        
class LastWeekReports(APIView):
    """Get previous week sales report"""
    def get(self, request):
        try:
            current_user = get_authenticated_user_from_jwt(request)
            
            if not current_user:
                return Response(
                    {"error": "Authentication required"}, 
                    status=status.HTTP_401_UNAUTHORIZED
                )

            sales_report = SalesReport()
            result = sales_report.get_previous_week_sales()
             
            return Response(result, status=status.HTTP_200_OK)
           
        except Exception as e:
            logging.error(f"Error getting last week sales report: {str(e)}")
            return Response(
                {"error": f"Error getting last week sales report: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            ) 
        
class SalesComparisonView(APIView):
    """Get sales comparison between periods"""
    def get(self, request):
        try:
            current_user = get_authenticated_user_from_jwt(request)
                
            if not current_user:
                return Response(
                    {"error": "Authentication required"}, 
                    status=status.HTTP_401_UNAUTHORIZED
                )

            # ✅ FIXED: Get period from query params, not request.period
            period = request.GET.get('period', 'week')
            
            if period not in ['week', 'month']:
                return Response(
                    {"error": "Period must be 'week' or 'month'"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

            sales_report = SalesReport()
            result = sales_report.get_sales_comparison(period)
                
            return Response(result, status=status.HTTP_200_OK)
            
        except Exception as e:
            logging.error(f"Error getting comparison report: {str(e)}")
            return Response(
                {"error": f"Error getting comparison report: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )    

# ✅ FIXED: Removed duplicate DashboardSummaryView classes
class DashboardSummaryView(APIView):
    """Get comprehensive dashboard data"""
    def get(self, request):
        try:
            current_user = get_authenticated_user_from_jwt(request)
                
            if not current_user:
                return Response(
                    {"error": "Authentication required"}, 
                    status=status.HTTP_401_UNAUTHORIZED
                )

            sales_report = SalesReport()
            result = sales_report.get_dashboard_summary()
                
            return Response(result, status=status.HTTP_200_OK)
            
        except Exception as e:
            logging.error(f"Error getting dashboard summary: {str(e)}")
            return Response(
                {"error": f"Error getting dashboard summary: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )