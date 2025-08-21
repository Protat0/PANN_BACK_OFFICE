import { api } from './api.js';

class DashboardAPIService{

    async getTotalOrders() {
        try {
            const response = await api.get('/invoices/stats/'); 
            const countRespo = response.data.total_transactions; 
            return countRespo;
        } catch (error) {
            console.error('Error fetching total products:', error);
            return 0; 
        }
    }

    async getMonthlyProfit() {
        try {
            const now = new Date();
            const startOfMonth = new Date(now.getFullYear(), now.getMonth(), 1);
            const endOfMonth = new Date(now.getFullYear(), now.getMonth() + 1, 0);
            
            const startDate = startOfMonth.toISOString().split('T')[0];
            const endDate = endOfMonth.toISOString().split('T')[0];
            
            console.log('Monthly Profit Debug:');
            console.log('Start Date:', startDate);
            console.log('End Date:', endDate);
            console.log('Current Date:', now.toISOString().split('T')[0]);
            
            const response = await api.get('sales-report/by-period/', {
                params: {
                    start_date: startDate,
                    end_date: endDate,
                    period: 'monthly'
                }
            });
            
            console.log('Monthly Profit Response:', response.data);
            
            // Check if you want total_transactions or total_sales
            if (response.data.total_sales !== undefined) {
                console.log('Using total_sales:', response.data.total_sales);
                return response.data.total_sales; // Maybe you want sales, not transaction count?
            }
            
            console.log('Using total_transactions:', response.data.total_sales);
            return response.data.total_transactions;
            
        } catch (error) {
            console.error('Error fetching current monthly profit:', error);
            return 0;
        }
    }

    async getTotalProfits() {
        try {
            const response = await api.get('/invoices/stats/'); 
            const countRespo = response.data.total_sales; 
            return countRespo;
        } catch (error) {
            console.error('Error fetching total products:', error);
            return 0; 
        }
    }

    async getTotalProducts() {
        try {
            const response = await api.get('/products/'); 
            const countRespo = response.data.length; 
            return countRespo;
        } catch (error) {
            console.error('Error fetching total orders:', error);
            return 0; 
        }
    }

    async getTotalSold() {
        try {
            const response = await api.get('/invoices/'); 
            
            let totalQuantity = 0;
            
            // Loop through all invoices
            response.data.invoices.forEach(invoice => {
                // Check if invoice has item_list
                if (invoice.item_list && Array.isArray(invoice.item_list)) {
                    // Loop through each item in the invoice
                    invoice.item_list.forEach(item => {
                        totalQuantity += item.quantity || 0;
                    });
                }
            });
            
            return totalQuantity;
        } catch (error) {
            console.error('Error fetching total products sold:', error);
            return 0; 
        }
    }

    async chartData(){
         try {
            const response = await api.get('/category/display'); 
            
             return response.data
        } catch (error) {
            console.error('Error fetching category data:', error)
            throw error
        }
    }
}

const dashboardApiService = new DashboardAPIService();
export default dashboardApiService;