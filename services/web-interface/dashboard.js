// Dashboard JavaScript - Updated for Web Interface
class RealEstateDashboard {
  constructor() {
    this.apiBase = "http://localhost:5005/api"; // Dashboard analytics service
    this.charts = {};
    this.currentSection = "overview";
    this.dateRange = "30d";

    this.init();
  }

  init() {
    this.setupEventListeners();
    this.loadDashboard();
    this.setupMockData(); // For demo purposes
  }

  setupEventListeners() {
    // Navigation
    document.querySelectorAll(".nav-item").forEach((item) => {
      item.addEventListener("click", (e) => {
        e.preventDefault();
        const section = e.currentTarget.dataset.section;
        this.switchSection(section);
      });
    });

    // Chart controls
    document.querySelectorAll(".chart-btn").forEach((btn) => {
      btn.addEventListener("click", (e) => {
        const metric = e.target.dataset.metric;
        this.updateChart("revenueTrend", metric);
      });
    });

    // Date range change
    if (document.getElementById("dateRange")) {
      document.getElementById("dateRange").addEventListener("change", (e) => {
        this.dateRange = e.target.value;
        this.updateDashboard();
      });
    }

    // Chat functionality
    if (document.getElementById("sendChatBtn")) {
      document.getElementById("sendChatBtn").addEventListener("click", () => {
        this.sendChatMessage();
      });
    }

    if (document.getElementById("chatInput")) {
      document.getElementById("chatInput").addEventListener("keypress", (e) => {
        if (e.key === "Enter") {
          this.sendChatMessage();
        }
      });
    }
  }

  setupMockData() {
    // Mock data for demo purposes
    this.mockData = {
      kpis: {
        total_revenue: { value: 1250000, change: 12.5, trend: "up" },
        deals_closed: { value: 48, change: 8.3, trend: "up" },
        leads_generated: { value: 156, change: 15.2, trend: "up" },
        conversion_rate: { value: 18.5, change: 2.1, trend: "up" },
        avg_deal_size: { value: 26000, change: 5.8, trend: "up" },
        property_views: { value: 2340, change: 22.1, trend: "up" },
      },
      charts_data: {
        revenue_trend: [
          { week: "Week 1", revenue: 280000 },
          { week: "Week 2", revenue: 320000 },
          { week: "Week 3", revenue: 295000 },
          { week: "Week 4", revenue: 355000 },
        ],
        deals_pipeline: {
          stages: [
            { name: "Lead", count: 45 },
            { name: "Qualified", count: 32 },
            { name: "Proposal", count: 18 },
            { name: "Negotiation", count: 12 },
            { name: "Closed", count: 8 },
          ],
        },
        lead_sources: [
          { source: "Website", count: 85 },
          { source: "Social Media", count: 45 },
          { source: "Referrals", count: 38 },
          { source: "Advertising", count: 32 },
          { source: "Other", count: 15 },
        ],
        property_performance: {
          avg_days_on_market: 32,
          total_views: 12450,
          inquiry_rate: 8.7,
          top_performing: [
            { title: "Villa in Tuscany", views: 245 },
            { title: "Apartment in Milan", views: 198 },
            { title: "House in Rome", views: 156 },
          ],
        },
      },
    };
  }

  switchSection(section) {
    // Update page title
    const titles = {
      overview: "Dashboard Overview",
      properties: "Property Management",
      leads: "Lead Management",
      sales: "Sales Analytics",
      marketing: "Marketing Campaigns",
      analytics: "Advanced Analytics",
      "ai-chat": "AI Assistant",
    };

    document.getElementById("page-title").textContent =
      titles[section] || "Dashboard";

    // Update navigation
    document.querySelectorAll(".nav-item").forEach((item) => {
      item.classList.remove("active");
    });
    document
      .querySelector(`[data-section="${section}"]`)
      .classList.add("active");

    // Update content
    document.querySelectorAll(".dashboard-section").forEach((sec) => {
      sec.classList.remove("active");
    });
    document.getElementById(`${section}-section`).classList.add("active");

    this.currentSection = section;
    this.loadSectionData(section);
  }

  async loadDashboard() {
    this.showLoading();
    try {
      await this.loadOverviewData();
    } catch (error) {
      console.error("Error loading dashboard:", error);
      // Load mock data as fallback
      this.loadMockData();
    } finally {
      this.hideLoading();
    }
  }

  async updateDashboard() {
    await this.loadSectionData(this.currentSection);
  }

  async refreshDashboard() {
    const refreshBtn = document.querySelector(".refresh-btn i");
    if (refreshBtn) {
      refreshBtn.classList.add("fa-spin");
    }

    try {
      await this.loadSectionData(this.currentSection);
    } finally {
      if (refreshBtn) {
        refreshBtn.classList.remove("fa-spin");
      }
    }
  }

  async loadSectionData(section) {
    switch (section) {
      case "overview":
        await this.loadOverviewData();
        break;
      case "properties":
        await this.loadPropertiesData();
        break;
      case "leads":
        await this.loadLeadsData();
        break;
      case "sales":
        await this.loadSalesData();
        break;
      case "marketing":
        await this.loadMarketingData();
        break;
      case "analytics":
        await this.loadAnalyticsData();
        break;
      case "ai-chat":
        // Chat is already loaded
        break;
    }
  }

  async loadOverviewData() {
    try {
      // Try to load from API
      const response = await fetch(
        `${this.apiBase}/dashboard/overview?range=${this.dateRange}`
      );
      const data = await response.json();

      if (data.success) {
        this.updateKPIs(data.data.kpis);
        this.updateCharts(data.data.charts_data);
      } else {
        throw new Error("API response not successful");
      }
    } catch (error) {
      console.error("Error loading overview data:", error);
      // Use mock data
      this.loadMockData();
    }
  }

  loadMockData() {
    this.updateKPIs(this.mockData.kpis);
    this.updateCharts(this.mockData.charts_data);
  }

  async loadPropertiesData() {
    // Mock properties data
    const propertiesGrid = document.getElementById("propertiesGrid");
    if (propertiesGrid) {
      propertiesGrid.innerHTML =
        "<p>Properties data will be loaded here...</p>";
    }
  }

  async loadLeadsData() {
    // Mock leads data
    const leadsTableBody = document.getElementById("leadsTableBody");
    if (leadsTableBody) {
      leadsTableBody.innerHTML =
        '<tr><td colspan="8">Leads data will be loaded here...</td></tr>';
    }
  }

  async loadSalesData() {
    // Mock sales data
    console.log("Loading sales data...");
  }

  async loadMarketingData() {
    // Mock marketing data
    const campaignsGrid = document.getElementById("campaignsGrid");
    if (campaignsGrid) {
      campaignsGrid.innerHTML =
        "<p>Marketing campaigns data will be loaded here...</p>";
    }
  }

  async loadAnalyticsData() {
    // Mock analytics data
    console.log("Loading analytics data...");
  }

  updateKPIs(kpis) {
    // Update KPI values
    if (document.getElementById("totalRevenue")) {
      document.getElementById("totalRevenue").textContent = this.formatCurrency(
        kpis.total_revenue.value
      );
    }
    if (document.getElementById("dealsClosedValue")) {
      document.getElementById("dealsClosedValue").textContent =
        kpis.deals_closed.value;
    }
    if (document.getElementById("leadsGenerated")) {
      document.getElementById("leadsGenerated").textContent =
        kpis.leads_generated.value;
    }
    if (document.getElementById("conversionRate")) {
      document.getElementById("conversionRate").textContent =
        kpis.conversion_rate.value.toFixed(1) + "%";
    }

    // Update changes
    this.updateKPIChange(
      "revenueChange",
      kpis.total_revenue.change,
      kpis.total_revenue.trend
    );
    this.updateKPIChange(
      "dealsChange",
      kpis.deals_closed.change,
      kpis.deals_closed.trend
    );
    this.updateKPIChange(
      "leadsChange",
      kpis.leads_generated.change,
      kpis.leads_generated.trend
    );
    this.updateKPIChange(
      "conversionChange",
      kpis.conversion_rate.change,
      kpis.conversion_rate.trend
    );
  }

  updateKPIChange(elementId, change, trend) {
    const element = document.getElementById(elementId);
    if (element) {
      const icon = trend === "up" ? "fa-arrow-up" : "fa-arrow-down";
      const className = trend === "up" ? "positive" : "negative";

      element.innerHTML = `<i class="fas ${icon}"></i> ${Math.abs(
        change
      ).toFixed(1)}%`;
      element.className = `kpi-change ${className}`;
    }
  }

  updateCharts(chartsData) {
    this.createRevenueTrendChart(chartsData.revenue_trend);
    this.createPipelineChart(chartsData.deals_pipeline);
    this.createLeadSourcesChart(chartsData.lead_sources);
    this.updatePropertyStats(chartsData.property_performance);
  }

  createRevenueTrendChart(data) {
    const ctx = document.getElementById("revenueTrendChart");
    if (!ctx) return;

    if (this.charts.revenueTrend) {
      this.charts.revenueTrend.destroy();
    }

    this.charts.revenueTrend = new Chart(ctx, {
      type: "line",
      data: {
        labels: data.map((item) => item.week),
        datasets: [
          {
            label: "Revenue",
            data: data.map((item) => item.revenue),
            borderColor: "#667eea",
            backgroundColor: "rgba(102, 126, 234, 0.1)",
            borderWidth: 3,
            fill: true,
            tension: 0.4,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            display: false,
          },
        },
        scales: {
          y: {
            beginAtZero: true,
            ticks: {
              callback: function (value) {
                return "€" + (value / 1000).toFixed(0) + "K";
              },
            },
          },
        },
      },
    });
  }

  createPipelineChart(data) {
    const ctx = document.getElementById("pipelineChart");
    if (!ctx) return;

    if (this.charts.pipeline) {
      this.charts.pipeline.destroy();
    }

    this.charts.pipeline = new Chart(ctx, {
      type: "bar",
      data: {
        labels: data.stages.map((stage) => stage.name),
        datasets: [
          {
            label: "Deal Count",
            data: data.stages.map((stage) => stage.count),
            backgroundColor: [
              "#667eea",
              "#764ba2",
              "#f093fb",
              "#f5576c",
              "#4facfe",
            ],
            borderRadius: 6,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            display: false,
          },
        },
        scales: {
          y: {
            beginAtZero: true,
          },
        },
      },
    });
  }

  createLeadSourcesChart(data) {
    const ctx = document.getElementById("leadSourcesChart");
    if (!ctx) return;

    if (this.charts.leadSources) {
      this.charts.leadSources.destroy();
    }

    this.charts.leadSources = new Chart(ctx, {
      type: "doughnut",
      data: {
        labels: data.map((item) => item.source),
        datasets: [
          {
            data: data.map((item) => item.count),
            backgroundColor: [
              "#667eea",
              "#764ba2",
              "#f093fb",
              "#f5576c",
              "#4facfe",
              "#00f2fe",
            ],
            borderWidth: 0,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: "bottom",
          },
        },
      },
    });
  }

  updatePropertyStats(data) {
    if (document.getElementById("avgDaysMarket")) {
      document.getElementById("avgDaysMarket").textContent = Math.round(
        data.avg_days_on_market
      );
    }
    if (document.getElementById("totalViews")) {
      document.getElementById("totalViews").textContent =
        data.total_views.toLocaleString();
    }
    if (document.getElementById("inquiryRate")) {
      document.getElementById("inquiryRate").textContent =
        data.inquiry_rate.toFixed(1) + "%";
    }

    // Update top properties
    const topPropertiesContainer = document.getElementById("topProperties");
    if (topPropertiesContainer) {
      topPropertiesContainer.innerHTML = "";

      data.top_performing.forEach((property) => {
        const propertyItem = document.createElement("div");
        propertyItem.className = "property-item";
        propertyItem.innerHTML = `
                    <span class="property-name">${property.title}</span>
                    <span class="property-views">${property.views} views</span>
                `;
        topPropertiesContainer.appendChild(propertyItem);
      });
    }
  }

  sendChatMessage() {
    const chatInput = document.getElementById("chatInput");
    const chatMessages = document.getElementById("chatMessages");

    if (!chatInput || !chatMessages) return;

    const message = chatInput.value.trim();
    if (!message) return;

    // Add user message
    const userMessage = document.createElement("div");
    userMessage.className = "message user";
    userMessage.innerHTML = `
            <div class="message-content">
                <p>${message}</p>
            </div>
        `;
    chatMessages.appendChild(userMessage);

    // Clear input
    chatInput.value = "";

    // Simulate AI response
    setTimeout(() => {
      const aiMessage = document.createElement("div");
      aiMessage.className = "message assistant";
      aiMessage.innerHTML = `
                <div class="message-content">
                    <p>I understand you're asking about "${message}". Let me help you with that. This is a demo response - in the full system, this would connect to your Open WebUI instance for intelligent responses.</p>
                </div>
            `;
      chatMessages.appendChild(aiMessage);

      // Scroll to bottom
      chatMessages.scrollTop = chatMessages.scrollHeight;
    }, 1000);

    // Scroll to bottom
    chatMessages.scrollTop = chatMessages.scrollHeight;
  }

  formatCurrency(amount) {
    return new Intl.NumberFormat("it-IT", {
      style: "currency",
      currency: "EUR",
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount);
  }

  showLoading() {
    const loadingOverlay = document.getElementById("loadingOverlay");
    if (loadingOverlay) {
      loadingOverlay.classList.add("active");
    }
  }

  hideLoading() {
    const loadingOverlay = document.getElementById("loadingOverlay");
    if (loadingOverlay) {
      loadingOverlay.classList.remove("active");
    }
  }
}

// Initialize dashboard when DOM is loaded
document.addEventListener("DOMContentLoaded", () => {
  window.dashboard = new RealEstateDashboard();
});
