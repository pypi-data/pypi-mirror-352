// Dashboard data and chart initialization
document.addEventListener('DOMContentLoaded', function() {
    // Load and parse the dashboard data
    fetch('dashboard_data.json')
        .then(response => response.json())
        .then(data => {
            initializeDashboard(data);
        })
        .catch(error => {
            console.error('Error loading dashboard data:', error);
            // Use fallback data if JSON loading fails
            initializeDashboard(getFallbackData());
        });
});

function initializeDashboard(data) {
    // Update KPI values
    updateKPIs(data.kpis);
    
    // Initialize all charts
    createBranchChart(data.branch_data);
    createProductChart(data.product_data);
    createCustomerChart(data.customer_type_data);
    createPaymentChart(data.payment_data);
    createMonthlyChart(data.monthly_data);
    createGenderChart(data.gender_data);
}

function updateKPIs(kpis) {
    document.getElementById('total-revenue').textContent = `$${kpis.total_revenue.toLocaleString('en-US', {minimumFractionDigits: 2})}`;
    document.getElementById('total-transactions').textContent = kpis.total_transactions.toLocaleString();
    document.getElementById('avg-transaction').textContent = `$${kpis.avg_transaction_value.toFixed(2)}`;
    document.getElementById('total-items').textContent = kpis.total_quantity_sold.toLocaleString();
    document.getElementById('avg-rating').textContent = `${kpis.avg_rating.toFixed(1)}/10`;
}

function createBranchChart(branchData) {
    const ctx = document.getElementById('branchChart').getContext('2d');
    
    const labels = branchData.map(item => `Branch ${item.Branch} (${item.City})`);
    const revenues = branchData.map(item => item.Total);
    const quantities = branchData.map(item => item.Quantity);
    
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Revenue ($)',
                data: revenues,
                backgroundColor: ['#FF6384', '#36A2EB', '#FFCE56'],
                borderColor: ['#FF6384', '#36A2EB', '#FFCE56'],
                borderWidth: 2,
                yAxisID: 'y'
            }, {
                label: 'Quantity Sold',
                data: quantities,
                type: 'line',
                borderColor: '#4BC0C0',
                backgroundColor: 'rgba(75, 192, 192, 0.2)',
                borderWidth: 3,
                fill: false,
                yAxisID: 'y1'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'top',
                },
                tooltip: {
                    mode: 'index',
                    intersect: false,
                    callbacks: {
                        label: function(context) {
                            if (context.datasetIndex === 0) {
                                return `Revenue: $${context.parsed.y.toLocaleString()}`;
                            } else {
                                return `Quantity: ${context.parsed.y.toLocaleString()} items`;
                            }
                        }
                    }
                }
            },
            scales: {
                y: {
                    type: 'linear',
                    display: true,
                    position: 'left',
                    title: {
                        display: true,
                        text: 'Revenue ($)'
                    }
                },
                y1: {
                    type: 'linear',
                    display: true,
                    position: 'right',
                    title: {
                        display: true,
                        text: 'Quantity Sold'
                    },
                    grid: {
                        drawOnChartArea: false,
                    },
                }
            }
        }
    });
}

function createProductChart(productData) {
    const ctx = document.getElementById('productChart').getContext('2d');
    
    const labels = productData.map(item => item['Product line']);
    const revenues = productData.map(item => item.Total);
    
    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: revenues,
                backgroundColor: [
                    '#FF6384',
                    '#36A2EB',
                    '#FFCE56',
                    '#4BC0C0',
                    '#9966FF',
                    '#FF9F40'
                ],
                borderWidth: 2,
                borderColor: '#fff'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        padding: 20,
                        usePointStyle: true
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = ((context.parsed / total) * 100).toFixed(1);
                            return `${context.label}: $${context.parsed.toLocaleString()} (${percentage}%)`;
                        }
                    }
                }
            }
        }
    });
}

function createCustomerChart(customerData) {
    const ctx = document.getElementById('customerChart').getContext('2d');
    
    const labels = customerData.map(item => item['Customer type']);
    const revenues = customerData.map(item => item.Total);
    
    new Chart(ctx, {
        type: 'pie',
        data: {
            labels: labels,
            datasets: [{
                data: revenues,
                backgroundColor: ['#36A2EB', '#FF6384'],
                borderWidth: 2,
                borderColor: '#fff'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        padding: 20,
                        usePointStyle: true
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = ((context.parsed / total) * 100).toFixed(1);
                            return `${context.label}: $${context.parsed.toLocaleString()} (${percentage}%)`;
                        }
                    }
                }
            }
        }
    });
}

function createPaymentChart(paymentData) {
    const ctx = document.getElementById('paymentChart').getContext('2d');
    
    const labels = paymentData.map(item => item.Payment);
    const revenues = paymentData.map(item => item.Total);
    
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Revenue by Payment Method',
                data: revenues,
                backgroundColor: ['#FFCE56', '#4BC0C0', '#FF9F40'],
                borderColor: ['#FFCE56', '#4BC0C0', '#FF9F40'],
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `Revenue: $${context.parsed.y.toLocaleString()}`;
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Revenue ($)'
                    }
                }
            }
        }
    });
}

function createMonthlyChart(monthlyData) {
    const ctx = document.getElementById('monthlyChart').getContext('2d');
    
    const labels = monthlyData.map(item => {
        const [year, month] = item.Month.split('-');
        const monthNames = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
        return `${monthNames[parseInt(month) - 1]} ${year}`;
    });
    const revenues = monthlyData.map(item => item.Total);
    const quantities = monthlyData.map(item => item.Quantity);
    
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Monthly Revenue ($)',
                data: revenues,
                borderColor: '#36A2EB',
                backgroundColor: 'rgba(54, 162, 235, 0.1)',
                borderWidth: 3,
                fill: true,
                tension: 0.4,
                yAxisID: 'y'
            }, {
                label: 'Monthly Quantity',
                data: quantities,
                borderColor: '#FF6384',
                backgroundColor: 'rgba(255, 99, 132, 0.1)',
                borderWidth: 3,
                fill: true,
                tension: 0.4,
                yAxisID: 'y1'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'top',
                },
                tooltip: {
                    mode: 'index',
                    intersect: false,
                    callbacks: {
                        label: function(context) {
                            if (context.datasetIndex === 0) {
                                return `Revenue: $${context.parsed.y.toLocaleString()}`;
                            } else {
                                return `Quantity: ${context.parsed.y.toLocaleString()} items`;
                            }
                        }
                    }
                }
            },
            scales: {
                y: {
                    type: 'linear',
                    display: true,
                    position: 'left',
                    title: {
                        display: true,
                        text: 'Revenue ($)'
                    }
                },
                y1: {
                    type: 'linear',
                    display: true,
                    position: 'right',
                    title: {
                        display: true,
                        text: 'Quantity Sold'
                    },
                    grid: {
                        drawOnChartArea: false,
                    },
                }
            }
        }
    });
}

function createGenderChart(genderData) {
    const ctx = document.getElementById('genderChart').getContext('2d');
    
    const labels = genderData.map(item => item.Gender);
    const revenues = genderData.map(item => item.Total);
    
    new Chart(ctx, {
        type: 'polarArea',
        data: {
            labels: labels,
            datasets: [{
                data: revenues,
                backgroundColor: ['#FF6384', '#36A2EB'],
                borderWidth: 2,
                borderColor: '#fff'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        padding: 20,
                        usePointStyle: true
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = ((context.parsed / total) * 100).toFixed(1);
                            return `${context.label}: $${context.parsed.toLocaleString()} (${percentage}%)`;
                        }
                    }
                }
            }
        }
    });
}

function getFallbackData() {
    // Fallback data in case JSON loading fails
    return {
        kpis: {
            total_revenue: 322966.74,
            total_transactions: 1000,
            avg_transaction_value: 322.97,
            total_quantity_sold: 5510,
            avg_rating: 7.0
        },
        branch_data: [
            {Branch: 'A', City: 'Yangon', Total: 110568.71, Quantity: 1859},
            {Branch: 'B', City: 'Mandalay', Total: 106197.67, Quantity: 1820},
            {Branch: 'C', City: 'Naypyitaw', Total: 106200.37, Quantity: 1831}
        ],
        product_data: [
            {'Product line': 'Food and beverages', Total: 56144.84, Quantity: 952},
            {'Product line': 'Sports and travel', Total: 55122.83, Quantity: 920},
            {'Product line': 'Electronic accessories', Total: 54337.53, Quantity: 971},
            {'Product line': 'Fashion accessories', Total: 54305.90, Quantity: 902},
            {'Product line': 'Home and lifestyle', Total: 53861.91, Quantity: 911},
            {'Product line': 'Health and beauty', Total: 49193.74, Quantity: 854}
        ],
        customer_type_data: [
            {'Customer type': 'Member', Total: 164223.44, Quantity: 2785},
            {'Customer type': 'Normal', Total: 158743.30, Quantity: 2725}
        ],
        gender_data: [
            {Gender: 'Female', Total: 167882.93, Quantity: 2864},
            {Gender: 'Male', Total: 155083.81, Quantity: 2646}
        ],
        payment_data: [
            {Payment: 'Ewallet', Total: 111661.97, Quantity: 1906},
            {Payment: 'Cash', Total: 112206.57, Quantity: 1859},
            {Payment: 'Credit card', Total: 99098.20, Quantity: 1745}
        ],
        monthly_data: [
            {Month: '2019-01', Total: 116291.87, Quantity: 1987},
            {Month: '2019-02', Total: 97219.37, Quantity: 1666},
            {Month: '2019-03', Total: 109455.51, Quantity: 1857}
        ]
    };
}