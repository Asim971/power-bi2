/**
 * BMD Sales Report Builder - Power BI Embedded Report Authoring
 * 
 * Uses Power BI Report Authoring APIs to programmatically create visuals:
 * - powerbi-client: Embed and interact with Power BI reports
 * - powerbi-report-authoring: Create/edit visuals programmatically
 * 
 * Dataset ID: 3477f170-bf61-42a4-b7a6-4414d7bf8881
 */

// Global state
let powerbi;
let report;
let currentPage;
let selectedVisualType = null;
const DATASET_ID = '3477f170-bf61-42a4-b7a6-4414d7bf8881';

// Visual specifications from report_design.md
const VISUAL_SPECS = {
    // Executive Dashboard KPIs
    executiveKPIs: [
        { type: 'card', x: 40, y: 160, width: 340, height: 150, title: 'VISITS', table: 'Fact_Visit', measure: 'Total Visits' },
        { type: 'card', x: 400, y: 160, width: 340, height: 150, title: 'ORDERS', table: 'Fact_Order', measure: 'Total Orders' },
        { type: 'card', x: 760, y: 160, width: 340, height: 150, title: 'CONVERSIONS', table: 'Fact_ProjectConversion', measure: 'Total Conversions' },
        { type: 'kpi', x: 1120, y: 160, width: 340, height: 150, title: 'CONV RATE 60D', table: 'Fact_Visit', measure: 'Conversion Rate 60D %' },
        { type: 'card', x: 1480, y: 160, width: 380, height: 150, title: 'REVENUE YTD', table: 'Fact_Order', measure: 'Order Amount YTD' }
    ],
    // Funnel stages
    funnelStages: [
        { name: 'Site Visits', table: 'Measures', measure: 'Site Visits' },
        { name: 'Project Conversions', table: 'Fact_ProjectConversion', measure: 'Total Conversions' },
        { name: 'Orders', table: 'Fact_Order', measure: 'Total Orders' },
        { name: 'Delivered', table: 'Measures', measure: 'Completed Orders' }
    ],
    // Quality gauges
    qualityGauges: [
        { title: 'PHOTO RATE', table: 'Fact_Visit', measure: 'Photo Capture %', target: 0.70, x: 40, y: 80 },
        { title: 'GPS RATE', table: 'Fact_Visit', measure: 'GPS Capture %', target: 0.80, x: 640, y: 80 },
        { title: 'FEEDBACK RATE', table: 'Fact_Visit', measure: 'Feedback Rate %', target: 0.75, x: 1240, y: 80 }
    ]
};

// Theme colors from BMD_Sales_Theme.json
const THEME_COLORS = {
    primary: '#0066CC',
    success: '#2ECC71',
    warning: '#F39C12',
    danger: '#E74C3C',
    site: '#1ABC9C',
    engineer: '#3498DB',
    contractor: '#9B59B6',
    dealer: '#E67E22',
    retailer: '#E91E63',
    ihb: '#00BCD4',
    factoryDN: '#2C3E50',
    generalDelivery: '#8E44AD'
};

// Initialize PowerBI
function initPowerBI() {
    powerbi = new window['powerbi-client'].service.Service(
        window['powerbi-client'].factories.hpmFactory,
        window['powerbi-client'].factories.wpmpFactory,
        window['powerbi-client'].factories.routerFactory
    );
    log('PowerBI client initialized');
}

// Logging utility
function log(message, type = 'info') {
    const console = document.getElementById('console');
    const timestamp = new Date().toLocaleTimeString();
    const colors = { info: '#2ecc71', error: '#e74c3c', warn: '#f39c12' };
    console.innerHTML += `<div style="color: ${colors[type] || colors.info}">[${timestamp}] ${message}</div>`;
    console.scrollTop = console.scrollHeight;
}

// Update connection status
function updateStatus(connected) {
    const status = document.getElementById('connectionStatus');
    if (connected) {
        status.className = 'status connected';
        status.textContent = '● Connected';
    } else {
        status.className = 'status disconnected';
        status.textContent = '● Disconnected';
    }
}

// Connect to dataset and create new report
async function createNewReport() {
    const accessToken = document.getElementById('accessToken').value.trim();
    const datasetId = document.getElementById('datasetId').value.trim();
    const workspaceId = document.getElementById('workspaceId').value.trim();

    if (!accessToken) {
        log('Please provide an access token', 'error');
        alert('Access token is required. Run:\naz account get-access-token --resource https://analysis.windows.net/powerbi/api --query accessToken -o tsv');
        return;
    }

    log('Creating new report from dataset...');

    try {
        // Get embed URL for dataset
        const embedUrl = workspaceId 
            ? `https://app.powerbi.com/reportEmbed?groupId=${workspaceId}`
            : 'https://app.powerbi.com/reportEmbed';

        const embedCreateConfig = {
            type: 'report',
            tokenType: window['powerbi-client'].models.TokenType.Aad,
            accessToken: accessToken,
            embedUrl: embedUrl,
            datasetId: datasetId,
            permissions: window['powerbi-client'].models.Permissions.All,
            viewMode: window['powerbi-client'].models.ViewMode.Edit,
            settings: {
                panes: {
                    filters: { visible: true },
                    pageNavigation: { visible: true },
                    visualizations: { visible: true, expanded: true },
                    fields: { visible: true, expanded: true }
                },
                bars: {
                    actionBar: { visible: true },
                    statusBar: { visible: true }
                }
            }
        };

        const reportContainer = document.getElementById('reportContainer');
        
        // Create the report
        report = powerbi.createReport(reportContainer, embedCreateConfig);

        // Handle report events
        report.on('loaded', async function() {
            log('Report created and loaded!', 'info');
            updateStatus(true);
            await refreshPageList();
        });

        report.on('rendered', function() {
            log('Report rendered', 'info');
        });

        report.on('error', function(event) {
            log(`Error: ${event.detail.message}`, 'error');
        });

        report.on('saved', function(event) {
            log(`Report saved: ${event.detail.reportObjectId}`, 'info');
        });

    } catch (error) {
        log(`Failed to create report: ${error.message}`, 'error');
    }
}

// Connect to existing dataset
async function connectToDataset() {
    await createNewReport();
}

// Refresh page list
async function refreshPageList() {
    if (!report) return;

    try {
        const pages = await report.getPages();
        const pageList = document.getElementById('pageList');
        pageList.innerHTML = '';

        pages.forEach((page, index) => {
            const li = document.createElement('li');
            li.className = page.isActive ? 'active' : '';
            li.innerHTML = `
                <span>${index + 1}. ${page.displayName || page.name}</span>
                <button onclick="deletePage('${page.name}')" style="border:none;background:none;cursor:pointer;">🗑️</button>
            `;
            li.onclick = () => navigateToPage(page.name);
            pageList.appendChild(li);

            if (page.isActive) {
                currentPage = page;
            }
        });

        log(`Found ${pages.length} page(s)`);
    } catch (error) {
        log(`Error listing pages: ${error.message}`, 'error');
    }
}

// Navigate to page
async function navigateToPage(pageName) {
    if (!report) return;
    
    try {
        const pages = await report.getPages();
        const page = pages.find(p => p.name === pageName);
        if (page) {
            await page.setActive();
            currentPage = page;
            log(`Navigated to page: ${page.displayName || page.name}`);
            await refreshPageList();
        }
    } catch (error) {
        log(`Error navigating: ${error.message}`, 'error');
    }
}

// Add new page
async function addPage() {
    if (!report) {
        log('No report loaded', 'error');
        return;
    }

    const pageName = prompt('Enter page name:', 'New Page');
    if (!pageName) return;

    try {
        // Note: Page creation requires the report to be in edit mode
        // The API will add a new page
        log(`Adding page: ${pageName}`);
        
        // Switch to edit mode if needed
        await report.switchMode('edit');
        
        // Power BI doesn't have direct addPage API - we need to use the UI or clone
        // For programmatic page creation, we can save and reload
        log('Page creation requires Power BI Desktop or Service UI', 'warn');
        
    } catch (error) {
        log(`Error adding page: ${error.message}`, 'error');
    }
}

// Delete page
async function deletePage(pageName) {
    if (!confirm(`Delete page "${pageName}"?`)) return;
    
    log('Page deletion requires Power BI UI', 'warn');
}

// Select visual type
function selectVisualType(type) {
    // Deselect all
    document.querySelectorAll('.visual-type-btn').forEach(btn => {
        btn.classList.remove('selected');
    });
    
    // Select clicked
    const btn = document.querySelector(`.visual-type-btn[data-type="${type}"]`);
    if (btn) {
        btn.classList.add('selected');
        selectedVisualType = type;
        document.getElementById('addVisualBtn').disabled = false;
        log(`Selected visual type: ${type}`);
    }
}

// Add selected visual to current page
async function addSelectedVisual() {
    if (!report || !currentPage || !selectedVisualType) {
        log('No report, page, or visual type selected', 'error');
        return;
    }

    try {
        log(`Creating ${selectedVisualType} visual...`);
        
        // Default layout
        const layout = {
            x: 100,
            y: 100,
            width: 400,
            height: 300
        };

        // Create the visual
        const response = await currentPage.createVisual(selectedVisualType, layout, true);
        const visual = response.visual;
        
        log(`Created visual: ${visual.name} (${visual.type})`);
        
        // Return visual reference for data binding
        return visual;
        
    } catch (error) {
        log(`Error creating visual: ${error.message}`, 'error');
    }
}

// Create visual with data binding
async function createVisualWithData(type, layout, dataConfig) {
    if (!currentPage) {
        log('No active page', 'error');
        return;
    }

    try {
        log(`Creating ${type} with data...`);
        
        // Create visual
        const response = await currentPage.createVisual(type, layout, false);
        const visual = response.visual;
        
        // Bind data if provided
        if (dataConfig) {
            // Add data fields based on visual type
            if (dataConfig.category) {
                const categoryField = {
                    $schema: 'http://powerbi.com/product/schema#column',
                    table: dataConfig.category.table,
                    column: dataConfig.category.column
                };
                await visual.addDataField('Category', categoryField);
            }
            
            if (dataConfig.value) {
                const valueField = {
                    $schema: 'http://powerbi.com/product/schema#measure',
                    table: dataConfig.value.table,
                    measure: dataConfig.value.measure
                };
                await visual.addDataField('Values', valueField);
            }
            
            if (dataConfig.series) {
                const seriesField = {
                    $schema: 'http://powerbi.com/product/schema#column',
                    table: dataConfig.series.table,
                    column: dataConfig.series.column
                };
                await visual.addDataField('Series', seriesField);
            }
        }
        
        log(`Visual created and data bound: ${visual.name}`);
        return visual;
        
    } catch (error) {
        log(`Error creating visual: ${error.message}`, 'error');
    }
}

// Build Executive Dashboard (Page 1)
async function buildExecutiveDashboard() {
    if (!report) {
        log('No report loaded. Create report first.', 'error');
        return;
    }

    log('Building Executive Command Center dashboard...');
    
    try {
        // Ensure we're on the first page
        const pages = await report.getPages();
        if (pages.length > 0) {
            await pages[0].setActive();
            currentPage = pages[0];
        }
        
        // Create header text box
        await createVisualWithData('textbox', { x: 0, y: 0, width: 1920, height: 60 }, null);
        
        // Create KPI Cards
        for (const kpi of VISUAL_SPECS.executiveKPIs) {
            const layout = { x: kpi.x, y: kpi.y, width: kpi.width, height: kpi.height };
            const dataConfig = {
                value: { table: kpi.table, measure: kpi.measure }
            };
            await createVisualWithData(kpi.type, layout, dataConfig);
            await sleep(500); // Rate limiting
        }
        
        // Create Performance Trend Line Chart
        await createVisualWithData('lineChart', 
            { x: 40, y: 340, width: 900, height: 350 },
            {
                category: { table: 'Dim_Date', column: 'Date' },
                value: { table: 'Fact_Visit', measure: 'Total Visits' }
            }
        );
        
        // Create Zone Heatmap (Filled Map)
        await createVisualWithData('filledMap',
            { x: 960, y: 340, width: 900, height: 350 },
            {
                category: { table: 'Dim_Territory', column: 'ZoneName' },
                value: { table: 'Fact_Visit', measure: 'Conversion Rate 60D %' }
            }
        );
        
        // Create Client Mix Donut
        await createVisualWithData('donutChart',
            { x: 40, y: 710, width: 580, height: 330 },
            {
                category: { table: 'Dim_Client', column: 'ClientType' },
                value: { table: 'Fact_Visit', measure: 'Total Visits' }
            }
        );
        
        // Create Role Performance Bar Chart
        await createVisualWithData('clusteredBarChart',
            { x: 640, y: 710, width: 620, height: 330 },
            {
                category: { table: 'Dim_User', column: 'RoleName' },
                value: { table: 'Measures', measure: 'Role Target Achievement %' }
            }
        );
        
        // Create Quick Funnel
        await createVisualWithData('funnel',
            { x: 1280, y: 710, width: 580, height: 330 },
            {
                category: { table: 'Measures', column: 'Funnel Stage' },
                value: { table: 'Measures', measure: 'Stage Count' }
            }
        );
        
        // Add slicers
        await createVisualWithData('slicer',
            { x: 40, y: 1040, width: 200, height: 40 },
            { category: { table: 'Dim_Date', column: 'Date' } }
        );
        
        await createVisualWithData('slicer',
            { x: 260, y: 1040, width: 200, height: 40 },
            { category: { table: 'Dim_Territory', column: 'ZoneName' } }
        );
        
        log('Executive Dashboard built successfully! 🎉', 'info');
        
    } catch (error) {
        log(`Error building dashboard: ${error.message}`, 'error');
    }
}

// Build Conversion Funnel (Page 4)
async function buildConversionFunnel() {
    if (!report) {
        log('No report loaded', 'error');
        return;
    }

    log('Building Conversion Funnel page...');
    
    try {
        // Create 7 KPI cards at top
        const kpiConfigs = [
            { title: 'SITE VISITS', measure: 'Site Visits', x: 40 },
            { title: 'CONVERSIONS', measure: 'Total Conversions', x: 310 },
            { title: 'ORDERS', measure: 'Total Orders', x: 580 },
            { title: 'DELIVERED', measure: 'Completed Orders', x: 850 },
            { title: 'CONV RATE', measure: 'Conversion Rate 60D %', x: 1120 },
            { title: 'AVG DAYS', measure: 'Avg Days to Conversion', x: 1390 },
            { title: 'COMPLETE %', measure: 'Order Completion Rate', x: 1660 }
        ];
        
        for (const kpi of kpiConfigs) {
            await createVisualWithData('card',
                { x: kpi.x, y: 80, width: 250, height: 120 },
                { value: { table: 'Measures', measure: kpi.measure } }
            );
            await sleep(300);
        }
        
        // Main Funnel
        await createVisualWithData('funnel',
            { x: 40, y: 220, width: 900, height: 400 },
            {
                category: { table: 'Measures', column: 'Funnel Stage' },
                value: { table: 'Measures', measure: 'Stage Count' }
            }
        );
        
        // Reward Eligibility Stacked Bar
        await createVisualWithData('stackedBarChart',
            { x: 960, y: 220, width: 450, height: 200 },
            {
                category: { table: 'Measures', column: 'Reward Type' },
                value: { table: 'Fact_Order', measure: 'Reward Eligible Orders' }
            }
        );
        
        // Delivery Method Comparison
        await createVisualWithData('clusteredColumnChart',
            { x: 1430, y: 220, width: 450, height: 200 },
            {
                category: { table: 'Fact_Order', column: 'DeliveryMethod' },
                value: { table: 'Fact_Order', measure: 'Total Orders' }
            }
        );
        
        // Days Distribution Histogram (using column chart)
        await createVisualWithData('clusteredColumnChart',
            { x: 960, y: 440, width: 920, height: 180 },
            {
                category: { table: 'Measures', column: 'Days to Convert Bin' },
                value: { table: 'Measures', measure: 'Conversion Count' }
            }
        );
        
        // Timeline Trend
        await createVisualWithData('lineChart',
            { x: 40, y: 640, width: 1840, height: 380 },
            {
                category: { table: 'Dim_Date', column: 'Date' },
                value: { table: 'Measures', measure: 'Site Visits' },
                series: { table: 'Measures', column: 'Metric Name' }
            }
        );
        
        log('Conversion Funnel page built! 🎉', 'info');
        
    } catch (error) {
        log(`Error: ${error.message}`, 'error');
    }
}

// Build Quality Scorecard (Page 3)
async function buildQualityScorecard() {
    if (!report) {
        log('No report loaded', 'error');
        return;
    }

    log('Building Quality Scorecard page...');
    
    try {
        // Create 3 gauge visuals
        for (const gauge of VISUAL_SPECS.qualityGauges) {
            await createVisualWithData('gauge',
                { x: gauge.x, y: gauge.y, width: 580, height: 250 },
                { value: { table: gauge.table, measure: gauge.measure } }
            );
            await sleep(300);
        }
        
        // Quality by Client Type bar chart
        await createVisualWithData('clusteredBarChart',
            { x: 40, y: 350, width: 900, height: 300 },
            {
                category: { table: 'Dim_Client', column: 'ClientType' },
                value: { table: 'Fact_Visit', measure: 'Quality Score' }
            }
        );
        
        // Top Performers table
        await createVisualWithData('tableEx',
            { x: 960, y: 350, width: 920, height: 300 },
            {
                category: { table: 'Dim_User', column: 'EmployeeName' },
                value: { table: 'Fact_Visit', measure: 'Quality Score' }
            }
        );
        
        // Quality Trend line chart
        await createVisualWithData('lineChart',
            { x: 40, y: 670, width: 1840, height: 300 },
            {
                category: { table: 'Dim_Date', column: 'MonthYear' },
                value: { table: 'Fact_Visit', measure: 'Photo Capture %' },
                series: { table: 'Measures', column: 'Quality Metric' }
            }
        );
        
        log('Quality Scorecard page built! 🎉', 'info');
        
    } catch (error) {
        log(`Error: ${error.message}`, 'error');
    }
}

// Build all 6 pages
async function buildAllPages() {
    if (!report) {
        log('No report loaded. Create report first.', 'error');
        return;
    }

    log('Building all 6 pages...', 'info');
    
    try {
        // Page 1: Executive Command Center
        log('Building Page 1: Executive Command Center...');
        await buildExecutiveDashboard();
        await sleep(1000);
        
        // Page 2: Territory Intelligence (would need additional page)
        log('Page 2: Territory Intelligence - Create page in Power BI first', 'warn');
        
        // Page 3: Quality Scorecard
        log('Building Page 3: Quality Scorecard...');
        await buildQualityScorecard();
        await sleep(1000);
        
        // Page 4: Conversion Funnel
        log('Building Page 4: Conversion Funnel...');
        await buildConversionFunnel();
        await sleep(1000);
        
        // Pages 5 & 6 would follow same pattern
        log('Pages 5 & 6 require additional page creation', 'warn');
        
        log('Report build complete! Save to preserve changes.', 'info');
        
    } catch (error) {
        log(`Build error: ${error.message}`, 'error');
    }
}

// Save report
async function saveReport() {
    if (!report) {
        log('No report to save', 'error');
        return;
    }

    try {
        log('Saving report...');
        await report.save();
        log('Report saved successfully! 💾', 'info');
    } catch (error) {
        log(`Save error: ${error.message}`, 'error');
    }
}

// Utility: Sleep
function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

// Initialize on load
document.addEventListener('DOMContentLoaded', function() {
    initPowerBI();
    log('Ready. Enter access token and click "Create New Report" to begin.');
});
