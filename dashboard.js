// Dashboard JavaScript
class RealEstateDashboard {
    constructor() {
        this.apiBase = '/api';
        this.charts = {};
        this.currentSection = 'overview';
        this.dateRange = '30d';
        
        this.init();
    }
    
    init() {
        this.setupEventListeners();
        this.loadDashboard();
    }
    
    setupEventListeners() {
        // Navigation
        document.querySelectorAll('.nav-item').forEach(item => {
            item.addEventListener('click', (e) => {
                const section = e.currentTarget.dataset.section;
                this.switchSection(section);
            });
        });
        
        // Chart controls
        document.querySelectorAll('.chart-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const metric = e.target.dataset.metric;
                this.updateChart('revenueTrend', metric);
            });
        });
        
        // Forecast controls
        document.querySelectorAll('.forecast-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const metric = e.target.dataset.metric;
                this.updateForecastChart(metric);
            });
        });
        
        // Date range change
        document.getElementById('dateRange').addEventListener('change', (e) => {
            this.dateRange = e.target.value;
            this.updateDashboard();
        });
    }
    
    switchSection(section) {
        // Update navigation
        document.querySelectorAll('.nav-item').forEach(item => {
            item.classList.remove('active');
        });
        document.querySelector(`[data-section="${section}"]`).classList.add('active');
        
        // Update content
        document.querySelectorAll('.dashboard-section').forEach(sec => {
            sec.classList.remove('active');
        });
        document.getElementById(`${section}-section`).classList.add('active');
        
        this.currentSection = section;
        this.loadSectionData(section);
    }
    
    async loadDashboard() {
        this.showLoading();
        try {
            await this.loadOverviewData();
        } catch (error) {
            console.error('Error loading dashboard:', error);
        } finally {
            this.hideLoading();
        }
    }
    
    async updateDashboard() {
        await this.loadSectionData(this.currentSection);
    }
    
    async refreshDashboard() {
        const refreshBtn = document.querySelector('.refresh-btn i');
        refreshBtn.classList.add('fa-spin');
        
        try {
            await this.loadSectionData(this.currentSection);
        } finally {
            refreshBtn.classList.remove('fa-spin');
        }
    }
    
    async loadSectionData(section) {
        switch (section) {
            case 'overview':
                await this.loadOverviewData();
                break;
            case 'sales':
                await this.loadSalesData();
                break;
            case 'agents':
                await this.loadAgentsData();
                break;
            case 'properties':
                await this.loadPropertiesData();
                break;
            case 'market':
                await this.loadMarketData();
                break;
            case 'pipeline':
                await this.loadPipelineData();
                break;
            case 'forecasting':
                await this.loadForecastingData();
                break;
        }
    }
    
    async loadOverviewData() {
        try {
            const response = await fetch(`${this.apiBase}/dashboard/overview?range=${this.dateRange}`);
            const data = await response.json();
            
            if (data.success) {
                this.updateKPIs(data.data.kpis);
                this.updateCharts(data.data.charts_data);
            }
        } catch (error) {
            console.error('Error loading overview data:', error);
        }
    }
    
    async loadSalesData() {
        try {
            const response = await fetch(`${this.apiBase}/analytics/sales?range=${this.dateRange}`);
            const data = await response.json();
            
            if (data.success) {
                this.updateRevenueForecastChart(data.data.forecasting);
            }
        } catch (error) {
            console.error('Error loading sales data:', error);
        }
    }
    
    async loadAgentsData() {
        try {
            const response = await fetch(`${this.apiBase}/analytics/agents`);
            const data = await response.json();
            
            if (data.success) {
                this.updateAgentsGrid(data.data);
            }
        } catch (error) {
            console.error('Error loading agents data:', error);
        }
    }
    
    async loadPropertiesData() {
        try {
            const response = await fetch(`${this.apiBase}/analytics/properties`);
            const data = await response.json();
            
            if (data.success) {
                this.updatePropertyMetrics(data.data);
            }
        } catch (error) {
            console.error('Error loading properties data:', error);
        }
    }
    
    async loadMarketData() {
        try {
            const response = await fetch(`${this.apiBase}/analytics/market`);
            const data = await response.json();
            
            if (data.success) {
                this.updateMarketOverview(data.data);
            }
        } catch (error) {
            console.error('Error loading market data:', error);
        }
    }
    
    async loadPipelineData() {
        try {
            const response = await fetch(`${this.apiBase}/crm/pipeline`);
            const data = await response.json();
            
            if (data.success) {
                this.updatePipelineStages(data.data);
            }
        } catch (error) {
            console.error('Error loading pipeline data:', error);
        }
    }
    
    async loadForecastingData() {
        try {
            const response = await fetch(`${this.apiBase}/forecasting/revenue`);
            const data = await response.json();
            
            if (data.success) {
                this.updateForecastChart('revenue', data.data);
            }
        } catch (error) {
            console.error('Error loading forecasting data:', error);
        }
    }
    
    updateKPIs(kpis) {
        // Update KPI values
        document.getElementById('totalRevenue').textContent = this.formatCurrency(kpis.total_revenue.value);
        document.getElementById('dealsClosedValue').textContent = kpis.deals_closed.value;
        document.getElementById('leadsGenerated').textContent = kpis.leads_generated.value;
        document.getElementById('conversionRate').textContent = kpis.conversion_rate.value.toFixed(1) + '%';
        document.getElementById('avgDealSize').textContent = this.formatCurrency(kpis.avg_deal_size.value);
        document.getElementById('propertyViews').textContent = kpis.property_views.value;
        
        // Update changes
        this.updateKPIChange('revenueChange', kpis.total_revenue.change, kpis.total_revenue.trend);
        this.updateKPIChange('dealsChange', kpis.deals_closed.change, kpis.deals_closed.trend);
        this.updateKPIChange('leadsChange', kpis.leads_generated.change, kpis.leads_generated.trend);
        this.updateKPIChange('conversionChange', kpis.conversion_rate.change, kpis.conversion_rate.trend);
        this.updateKPIChange('dealSizeChange', kpis.avg_deal_size.change, kpis.avg_deal_size.trend);
        this.updateKPIChange('viewsChange', kpis.property_views.change, kpis.property_views.trend);
    }
    
    updateKPIChange(elementId, change, trend) {
        const element = document.getElementById(elementId);
        const icon = trend === 'up' ? 'fa-arrow-up' : 'fa-arrow-down';
        const className = trend === 'up' ? 'positive' : 'negative';
        
        element.innerHTML = `<i class="fas ${icon}"></i> ${Math.abs(change).toFixed(1)}%`;
        element.className = `kpi-change ${className}`;
    }
    
    updateCharts(chartsData) {
        this.createRevenueTrendChart(chartsData.revenue_trend);
        this.createPipelineChart(chartsData.deals_pipeline);
        this.createLeadSourcesChart(chartsData.lead_sources);
        this.updatePropertyStats(chartsData.property_performance);
    }
    
    createRevenueTrendChart(data) {
        const ctx = document.getElementById('revenueTrendChart').getContext('2d');
        
        if (this.charts.revenueTrend) {
            this.charts.revenueTrend.destroy();
        }
        
        this.charts.revenueTrend = new Chart(ctx, {
            type: 'line',
            data: {
                labels: data.map(item => item.week),
                datasets: [{
                    label: 'Revenue',
                    data: data.map(item => item.revenue),
                    borderColor: '#667eea',
                    backgroundColor: 'rgba(102, 126, 234, 0.1)',
                    borderWidth: 3,
                    fill: true,
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: function(value) {
                                return '€' + (value / 1000).toFixed(0) + 'K';
                            }
                        }
                    }
                }
            }
        });
    }
    
    createPipelineChart(data) {
        const ctx = document.getElementById('pipelineChart').getContext('2d');
        
        if (this.charts.pipeline) {
            this.charts.pipeline.destroy();
        }
        
        this.charts.pipeline = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: data.stages.map(stage => stage.name),
                datasets: [{
                    label: 'Deal Count',
                    data: data.stages.map(stage => stage.count),
                    backgroundColor: [
                        '#667eea',
                        '#764ba2',
                        '#f093fb',
                        '#f5576c',
                        '#4facfe'
                    ],
                    borderRadius: 6
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    }
    
    createLeadSourcesChart(data) {
        const ctx = document.getElementById('leadSourcesChart').getContext('2d');
        
        if (this.charts.leadSources) {
            this.charts.leadSources.destroy();
        }
        
        this.charts.leadSources = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: data.map(item => item.source),
                datasets: [{
                    data: data.map(item => item.count),
                    backgroundColor: [
                        '#667eea',
                        '#764ba2',
                        '#f093fb',
                        '#f5576c',
                        '#4facfe',
                        '#00f2fe'
                    ],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
    }
    
    updatePropertyStats(data) {
        document.getElementById('avgDaysMarket').textContent = Math.round(data.avg_days_on_market);
        document.getElementById('totalViews').textContent = data.total_views.toLocaleString();
        document.getElementById('inquiryRate').textContent = data.inquiry_rate.toFixed(1) + '%';
        
        // Update top properties
        const topPropertiesContainer = document.getElementById('topProperties');
        topPropertiesContainer.innerHTML = '';
        
        data.top_performing.forEach(property => {
            const propertyItem = document.createElement('div');
            propertyItem.className = 'property-item';
            propertyItem.innerHTML = `
                <span class="property-name">${property.title}</span>
                <span class="property-views">${property.views} views</span>
            `;
            topPropertiesContainer.appendChild(propertyItem);
        });
    }
    
    updateRevenueForecastChart(data) {
        const ctx = document.getElementById('revenueForecastChart').getContext('2d');
        
        if (this.charts.revenueForecast) {
            this.charts.revenueForecast.destroy();
        }
        
        const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'];
        
        this.charts.revenueForecast = new Chart(ctx, {
            type: 'line',
            data: {
                labels: months,
                datasets: [
                    {
                        label: 'Historical',
                        data: data.historical,
                        borderColor: '#667eea',
                        backgroundColor: 'rgba(102, 126, 234, 0.1)',
                        borderWidth: 3,
                        fill: false
                    },
                    {
                        label: 'Forecast',
                        data: data.forecast,
                        borderColor: '#f5576c',
                        backgroundColor: 'rgba(245, 87, 108, 0.1)',
                        borderWidth: 3,
                        borderDash: [5, 5],
                        fill: false
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'top'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: function(value) {
                                return '€' + (value / 1000).toFixed(0) + 'K';
                            }
                        }
                    }
                }
            }
        });
    }
    
    updateAgentsGrid(agents) {
        const agentsGrid = document.getElementById('agentsGrid');
        agentsGrid.innerHTML = '';
        
        agents.forEach(agent => {
            const agentCard = document.createElement('div');
            agentCard.className = 'agent-card';
            agentCard.innerHTML = `
                <div class="agent-header">
                    <div class="agent-avatar">
                        ${agent.name.split(' ').map(n => n[0]).join('')}
                    </div>
                    <div class="agent-info">
                        <h4>${agent.name}</h4>
                        <div class="agent-rank">Rank #${agent.rank}</div>
                    </div>
                </div>
                <div class="agent-metrics">
                    <div class="agent-metric">
                        <div class="agent-metric-value">${agent.deals_closed}</div>
                        <div class="agent-metric-label">Deals Closed</div>
                    </div>
                    <div class="agent-metric">
                        <div class="agent-metric-value">${this.formatCurrency(agent.revenue_generated)}</div>
                        <div class="agent-metric-label">Revenue</div>
                    </div>
                    <div class="agent-metric">
                        <div class="agent-metric-value">${agent.conversion_rate.toFixed(1)}%</div>
                        <div class="agent-metric-label">Conversion Rate</div>
                    </div>
                    <div class="agent-metric">
                        <div class="agent-metric-value">${agent.rating.toFixed(1)}</div>
                        <div class="agent-metric-label">Rating</div>
                    </div>
                </div>
            `;
            agentsGrid.appendChild(agentCard);
        });
    }
    
    updateMarketOverview(data) {
        const marketOverview = document.getElementById('marketOverview');
        marketOverview.innerHTML = `
            <div class="market-card">
                <h3>Market Metrics</h3>
                <div class="market-metric">
                    <span class="metric-label">Average Price/m²</span>
                    <span class="metric-value">€${data.average_price_sqm.toLocaleString()}</span>
                </div>
                <div class="market-metric">
                    <span class="metric-label">Monthly Change</span>
                    <span class="metric-value">${data.price_change_monthly > 0 ? '+' : ''}${data.price_change_monthly}%</span>
                </div>
                <div class="market-metric">
                    <span class="metric-label">Inventory Levels</span>
                    <span class="metric-value">${data.inventory_levels}</span>
                </div>
                <div class="market-metric">
                    <span class="metric-label">Avg Days on Market</span>
                    <span class="metric-value">${data.days_on_market_avg} days</span>
                </div>
            </div>
            <div class="market-card">
                <h3>Market Health</h3>
                <div class="market-metric">
                    <span class="metric-label">Health Score</span>
                    <span class="metric-value">${data.trend_analysis.market_health_score}/100</span>
                </div>
                <div class="market-metric">
                    <span class="metric-label">Investment Rating</span>
                    <span class="metric-value">${data.trend_analysis.investment_rating}</span>
                </div>
                <div class="market-metric">
                    <span class="metric-label">Price Momentum</span>
                    <span class="metric-value">${data.trend_analysis.price_momentum}</span>
                </div>
            </div>
        `;
    }
    
    updatePipelineStages(data) {
        const pipelineStages = document.getElementById('pipelineStages');
        pipelineStages.innerHTML = '';
        
        data.stages.forEach(stage => {
            const stageElement = document.createElement('div');
            stageElement.className = 'pipeline-stage';
            stageElement.innerHTML = `
                <div class="stage-header">
                    <div class="stage-title">${stage.name}</div>
                    <div class="stage-count">${stage.count}</div>
                </div>
                <div class="stage-value">${this.formatCurrency(stage.value)}</div>
                <div class="deals-list">
                    ${data.deals ? data.deals.filter(deal => deal.stage === stage.name).map(deal => `
                        <div class="deal-item">
                            <div class="deal-client">${deal.client_name}</div>
                            <div class="deal-property">${deal.property}</div>
                            <div class="deal-value">${this.formatCurrency(deal.value)}</div>
                        </div>
                    `).join('') : ''}
                </div>
            `;
            pipelineStages.appendChild(stageElement);
        });
    }
    
    async updateForecastChart(metric) {
        try {
            const response = await fetch(`${this.apiBase}/forecasting/${metric}`);
            const data = await response.json();
            
            if (data.success) {
                this.createForecastChart(metric, data.data);
            }
        } catch (error) {
            console.error('Error updating forecast chart:', error);
        }
    }
    
    createForecastChart(metric, data) {
        const ctx = document.getElementById('forecastChart').getContext('2d');
        
        if (this.charts.forecast) {
            this.charts.forecast.destroy();
        }
        
        const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'];
        
        this.charts.forecast = new Chart(ctx, {
            type: 'line',
            data: {
                labels: months,
                datasets: [
                    {
                        label: 'Historical',
                        data: data.historical,
                        borderColor: '#667eea',
                        backgroundColor: 'rgba(102, 126, 234, 0.1)',
                        borderWidth: 3,
                        fill: false
                    },
                    {
                        label: 'Forecast',
                        data: data.forecast,
                        borderColor: '#f5576c',
                        backgroundColor: 'rgba(245, 87, 108, 0.1)',
                        borderWidth: 3,
                        borderDash: [5, 5],
                        fill: false
                    },
                    {
                        label: 'Upper Bound',
                        data: data.confidence_intervals.upper,
                        borderColor: 'rgba(245, 87, 108, 0.3)',
                        backgroundColor: 'rgba(245, 87, 108, 0.1)',
                        borderWidth: 1,
                        fill: '+1'
                    },
                    {
                        label: 'Lower Bound',
                        data: data.confidence_intervals.lower,
                        borderColor: 'rgba(245, 87, 108, 0.3)',
                        backgroundColor: 'rgba(245, 87, 108, 0.1)',
                        borderWidth: 1,
                        fill: false
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'top'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: function(value) {
                                if (metric === 'revenue') {
                                    return '€' + (value / 1000).toFixed(0) + 'K';
                                }
                                return value;
                            }
                        }
                    }
                }
            }
        });
    }
    
    formatCurrency(amount) {
        return new Intl.NumberFormat('it-IT', {
            style: 'currency',
            currency: 'EUR',
            minimumFractionDigits: 0,
            maximumFractionDigits: 0
        }).format(amount);
    }
    
    showLoading() {
        document.getElementById('loadingOverlay').classList.add('active');
    }
    
    hideLoading() {
        document.getElementById('loadingOverlay').classList.remove('active');
    }
}

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new RealEstateDashboard();
});

