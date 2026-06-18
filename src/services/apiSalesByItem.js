// src/services/apiSalesByItem.js
// Sales-by-item report service — backed by /api/v1/admin/reports/ (v5 DynamoDB)
import { api } from './api';

class SalesDisplayService {
  /**
   * Per-product sales totals (table, chart, top items).
   * Returns an array of rows: { product_id, product_name, category_name,
   * sku, unit, selling_price, stock, is_taxable, items_sold, total_sales }
   * sorted by total_sales descending.
   *
   * @param {string} startDate - YYYY-MM-DD
   * @param {string} endDate - YYYY-MM-DD
   * @param {boolean} includeVoided - include voided transactions (optional)
   */
  async getSalesByItem(startDate, endDate, includeVoided = false) {
    const params = {};
    if (startDate) params.start_date = startDate;
    if (endDate) params.end_date = endDate;
    if (includeVoided) params.include_voided = includeVoided;

    const response = await api.get('reports/sales-by-item/', { params });
    return response.data;
  }

  /**
   * Aggregate totals: revenue, transactions, discounts, by payment method.
   *
   * @param {string} startDate - YYYY-MM-DD
   * @param {string} endDate - YYYY-MM-DD
   */
  async getSalesSummary(startDate, endDate) {
    const params = {};
    if (startDate) params.start_date = startDate;
    if (endDate) params.end_date = endDate;

    const response = await api.get('reports/sales-summary/', { params });
    return response.data;
  }
}

// Export a singleton instance and the class
const salesDisplayService = new SalesDisplayService();
export default salesDisplayService;
export { SalesDisplayService };
