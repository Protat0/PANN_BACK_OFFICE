<template>
    <div class="LogsContainer">
        <!-- Header Controls -->
        <div class="header-controls">
            <div class="Categories">
                <select class="form-select" aria-label="Filter logs" style="width:200px;">
                    <option selected>All Categories</option>
                    <option value="login">Login</option>
                    <option value="logout">Logout</option>
                    <option value="session">Session</option>
                </select>
            </div>
            
            <!-- Records per page selector -->
            <div class="records-per-page">
                <label for="pageSize" class="form-label">Show:</label>
                <select 
                    id="pageSize" 
                    class="form-select form-select-sm" 
                    v-model="pageSize" 
                    @change="changePageSize"
                    style="width: 80px;">
                    <option value="10">10</option>
                    <option value="50">50</option>
                    <option value="100">100</option>
                </select>
                <span class="records-info">records per page</span>
            </div>
        </div>
        
        <!-- Loading state -->
        <div v-if="loading" class="loading-container">
            <div class="spinner-border text-primary"></div>
            <p>Loading session logs...</p>
        </div>
        
        <!-- Error state -->
        <div v-else-if="error" class="error-container">
            <div class="alert alert-danger">
                <p>Error loading logs: {{ error }}</p>
                <button @click="loadLogs" class="btn btn-primary">Retry</button>
            </div>
        </div>
        
        <!-- Data Table -->
        <div v-else class="Data-Table">
            <!-- Table Info -->
            <div class="table-info">
                <span>
                    Showing {{ startRecord }} to {{ endRecord }} of {{ totalRecords }} entries
                </span>
            </div>
            
            <table class="table table-striped">
                <thead>
                    <tr>
                        <th scope="col">Log ID</th>
                        <th scope="col">User ID</th>
                        <th scope="col">Ref. Id</th>
                        <th scope="col">Event Type</th>
                        <th scope="col">Amount/Qty.</th>
                        <th scope="col">Status</th>
                        <th scope="col">Timestamp</th>
                        <th scope="col">Remarks</th>
                    </tr>
                </thead>
                <tbody class="table-group-divider">
                    <tr v-for="(sessionLog, index) in paginatedLogs" :key="sessionLog.log_id || sessionLog._id || index">
                        <td>{{ sessionLog.log_id }}</td>
                        <td>{{ sessionLog.user_id }}</td>
                        <td>{{ sessionLog.ref_id }}</td>
                        <td>{{ sessionLog.event_type }}</td>
                        <td>{{ getAmountQty(sessionLog) }}</td>
                        <td>
                            <span :class="getStatusClass(sessionLog.status)">
                                {{ sessionLog.status }}
                            </span>
                        </td>
                        <td>{{ sessionLog.timestamp }}</td>
                        <td>{{ sessionLog.remarks }}</td>
                    </tr>
                </tbody>
            </table>
            
            <!-- Empty state -->
            <div v-if="session_logs.length === 0" class="empty-state">
                <i class="bi bi-file-text" style="font-size: 3rem; color: #6b7280;"></i>
                <p>No session logs found</p>
                <button @click="loadLogs" class="btn btn-primary">Refresh</button>
            </div>
            
            <!-- Pagination Controls -->
            <div v-if="session_logs.length > 0" class="pagination-container">
                <nav aria-label="Logs pagination">
                    <ul class="pagination pagination-sm justify-content-center">
                        <!-- Previous button -->
                        <li class="page-item" :class="{ disabled: currentPage === 1 }">
                            <button 
                                class="page-link" 
                                @click="goToPage(currentPage - 1)"
                                :disabled="currentPage === 1">
                                <i class="bi bi-chevron-left"></i> Previous
                            </button>
                        </li>
                        
                        <!-- Page numbers -->
                        <li 
                            v-for="(page, index) in visiblePages" 
                            :key="index"
                            class="page-item" 
                            :class="{ 
                                active: page === currentPage,
                                disabled: page === '...'
                            }">
                            <button 
                                v-if="page !== '...'"
                                class="page-link" 
                                @click="goToPage(page)">
                                {{ page }}
                            </button>
                            <span v-else class="page-link">{{ page }}</span>
                        </li>
                        
                        <!-- Next button -->
                        <li class="page-item" :class="{ disabled: currentPage === totalPages }">
                            <button 
                                class="page-link" 
                                @click="goToPage(currentPage + 1)"
                                :disabled="currentPage === totalPages">
                                Next <i class="bi bi-chevron-right"></i>
                            </button>
                        </li>
                    </ul>
                </nav>
                
                <!-- Pagination info -->
                <div class="pagination-info">
                    <small class="text-muted">
                        Page {{ currentPage }} of {{ totalPages }} 
                        ({{ totalRecords }} total records)
                    </small>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import APILogs from '@/services/apiLogs'

export default {
    name: 'SystemLogs',
    data() {
        return {
            session_logs: [],
            loading: false,
            error: null,
            
            // Pagination data
            currentPage: 1,
            pageSize: 10,
            totalRecords: 0
        };
    },
    
    computed: {
        // Calculate total pages
        totalPages() {
            return Math.ceil(this.session_logs.length / this.pageSize);
        },
        
        // Get logs for current page
        paginatedLogs() {
            const start = (this.currentPage - 1) * this.pageSize;
            const end = start + this.pageSize;
            return this.session_logs.slice(start, end);
        },
        
        // Calculate record numbers for display
        startRecord() {
            return this.session_logs.length === 0 ? 0 : (this.currentPage - 1) * this.pageSize + 1;
        },
        
        endRecord() {
            const end = this.currentPage * this.pageSize;
            return end > this.session_logs.length ? this.session_logs.length : end;
        },
        
        // Visible page numbers for pagination
        visiblePages() {
            const pages = [];
            const delta = 2; // Show 2 pages on each side of current page
            
            // For small number of total pages, show all
            if (this.totalPages <= 7) {
                for (let i = 1; i <= this.totalPages; i++) {
                    pages.push(i);
                }
                return pages;
            }
            
            // Always include first page
            pages.push(1);
            
            // Calculate start and end of middle range
            const start = Math.max(2, this.currentPage - delta);
            const end = Math.min(this.totalPages - 1, this.currentPage + delta);
            
            // Add gap if needed between 1 and start
            if (start > 2) {
                pages.push('...');
            }
            
            // Add middle range (excluding first and last page)
            for (let i = start; i <= end; i++) {
                if (i !== 1 && i !== this.totalPages) {
                    pages.push(i);
                }
            }
            
            // Add gap if needed between end and last page
            if (end < this.totalPages - 1) {
                pages.push('...');
            }
            
            // Always include last page (if not page 1)
            if (this.totalPages > 1) {
                pages.push(this.totalPages);
            }
            
            return pages;
        }
    },
    
    // Load data when component mounts
    async mounted() {
        await this.loadLogs();
    },
    
    methods: {
        async loadLogs() {
            this.loading = true;
            this.error = null;
            
            try {
                console.log("Loading session logs...");
                
                const response = await APILogs.DisplayLogs();
                console.log("API Response:", response);
                
                // Handle different response formats
                if (response && response.success && response.data) {
                    this.session_logs = response.data;
                } else if (Array.isArray(response)) {
                    this.session_logs = response;
                } else if (response && response.data) {
                    this.session_logs = response.data;
                } else {
                    this.session_logs = [];
                }
                
                this.totalRecords = this.session_logs.length;
                
                // Reset to first page when data loads
                this.currentPage = 1;
                
                console.log(`Loaded ${this.totalRecords} session logs`);
                
            } catch (error) {
                console.error("Error loading session logs:", error);
                this.error = error.message || 'Failed to load session logs';
                this.session_logs = [];
                this.totalRecords = 0;
            } finally {
                this.loading = false;
            }
        },
        
        // Navigate to specific page
        goToPage(page) {
            if (page >= 1 && page <= this.totalPages) {
                this.currentPage = page;
            }
        },
        
        // Change page size
        changePageSize() {
            this.currentPage = 1; // Reset to first page
            console.log(`Page size changed to: ${this.pageSize}`);
        },
        
        // Get amount/qty based on event type
        getAmountQty(sessionLog) {
            const eventType = (sessionLog.event_type || '').toLowerCase();
            
            // If event is "session", return "None"
            if (eventType === 'session' || eventType === 'session complete') {
                return 'None';
            }
            
            // For other events, return the amount_qty or default
            return sessionLog.amount_qty || '-';
        },
        
        // Get status badge class
        getStatusClass(status) {
            const statusLower = (status || '').toLowerCase();
            switch (statusLower) {
                case 'completed':
                case 'success':
                    return 'badge bg-success';
                case 'active':
                    return 'badge bg-primary';
                case 'failed':
                case 'error':
                    return 'badge bg-danger';
                default:
                    return 'badge bg-secondary';
            }
        }
    },
    
    // Watch for page size changes
    watch: {
        pageSize() {
            this.currentPage = 1;
        }
    }
}
</script>

<style>
@import url('https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css');
@import url('https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.0/font/bootstrap-icons.css');

.LogsContainer {
    width: 100%;
    min-height: 100vh;
    padding: 20px;
    background-color: #f8f9fa;
}

.header-controls {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
    padding: 15px;
    background: white;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.records-per-page {
    display: flex;
    align-items: center;
    gap: 8px;
}

.records-per-page .form-label {
    margin: 0;
    font-size: 14px;
    color: #6c757d;
}

.records-info {
    font-size: 14px;
    color: #6c757d;
}

.Data-Table {
    background: white;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    overflow: hidden;
}

.table-info {
    padding: 15px;
    background-color: #f8f9fa;
    border-bottom: 1px solid #dee2e6;
    font-size: 14px;
    color: #6c757d;
}

.table {
    margin: 0;
}

.table thead th {
    background-color: #6f42c1;
    color: white;
    border: none;
    padding: 12px;
    font-weight: 500;
    font-size: 13px;
}

.table tbody td {
    padding: 10px 12px;
    vertical-align: middle;
    font-size: 13px;
}

.table tbody tr:hover {
    background-color: #f8f9fa;
}

.badge {
    font-size: 11px;
    padding: 4px 8px;
}

.loading-container, 
.error-container, 
.empty-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 60px 20px;
    text-align: center;
}

.error-container {
    color: #dc3545;
}

.pagination-container {
    padding: 20px;
    border-top: 1px solid #dee2e6;
    background-color: #f8f9fa;
}

.pagination {
    margin-bottom: 10px;
}

.pagination-info {
    text-align: center;
}

.page-link {
    border: 1px solid #dee2e6;
    color: #6f42c1;
    padding: 6px 12px;
}

.page-link:hover {
    background-color: #e9ecef;
    border-color: #6f42c1;
}

.page-item.active .page-link {
    background-color: #6f42c1;
    border-color: #6f42c1;
}

.page-item.disabled .page-link {
    color: #6c757d;
    background-color: #fff;
    border-color: #dee2e6;
}

/* Responsive design */
@media (max-width: 768px) {
    .header-controls {
        flex-direction: column;
        gap: 15px;
        align-items: stretch;
    }
    
    .records-per-page {
        justify-content: center;
    }
    
    .table-responsive {
        overflow-x: auto;
    }
    
    .pagination {
        flex-wrap: wrap;
        justify-content: center;
    }
}
</style>