from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import HttpResponse
from ..services.customer_service import CustomerService
import logging

class CustomerListView(APIView):
    def get(self, request):
        """Get all customers"""
        try:
            customer_service = CustomerService()
            customers = customer_service.get_all_customers()
            return Response(customers, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def post(self, request):
        """Create new customer"""
        try:
            customer_service = CustomerService()
            customer_data = request.data
            new_customer = customer_service.create_customer(customer_data)
            return Response(new_customer, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )

class CustomerDetailView(APIView):
    def get(self, request, customer_id):
        """Get customer by ID"""
        try:
            customer_service = CustomerService()
            customer = customer_service.get_customer_by_id(customer_id)
            if customer:
                return Response(customer, status=status.HTTP_200_OK)
            return Response(
                {"error": "Customer not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def put(self, request, customer_id):
        """Update customer"""
        try:
            customer_service = CustomerService()
            customer_data = request.data
            updated_customer = customer_service.update_customer(customer_id, customer_data)
            if updated_customer:
                return Response(updated_customer, status=status.HTTP_200_OK)
            return Response(
                {"error": "Customer not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def delete(self, request, customer_id):
        """Delete customer"""
        try:
            customer_service = CustomerService()
            deleted = customer_service.delete_customer(customer_id)
            if deleted:
                return Response(
                    {"message": "Customer deleted successfully"}, 
                    status=status.HTTP_200_OK
                )
            return Response(
                {"error": "Customer not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

# ================ Customer KPI Views ================
class ActiveCustomerKPIView(APIView):
    def get(self, request):
        try:
            customer_service = CustomerService()
            activeCount = customer_service.get_active_customers()
            return Response({"active_customers": activeCount}, status=status.HTTP_200_OK)
        except Exception as e:
            logging.error(f"Active CustomerKPI error: {str(e)}")
            print(f"Active CustomerKPI error: {str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class MonthlyCustomerKPIView(APIView):
    def get(self, request):
        try:
            customer_service = CustomerService()
            monthlyCount = customer_service.get_monthly_users()
            return Response({"monthly_customers": monthlyCount}, status=status.HTTP_200_OK)
        except Exception as e:
            logging.error(f"Monthly CustomerKPI error: {str(e)}")
            print(f"Monthly CustomerKPI error: {str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class DailyCustomerKPIView(APIView):
    def get(self, request):
        try:
            customer_service = CustomerService()
            dailyCount = customer_service.get_daily_logins()
            return Response({"daily_customers": dailyCount}, status=status.HTTP_200_OK)
        except Exception as e:
            logging.error(f"Daily CustomerKPI error: {str(e)}")
            print(f"Daily CustomerKPI error: {str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)