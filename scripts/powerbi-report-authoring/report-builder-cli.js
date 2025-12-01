#!/usr/bin/env node
/**
 * Power BI Report Builder - Server-Side Implementation
 * 
 * Creates Power BI reports programmatically using:
 * 1. Power BI REST API for report/dataset operations
 * 2. Power BI Embedded APIs for visual creation
 * 
 * Usage:
 *   node report-builder-cli.js create-report
 *   node report-builder-cli.js add-visual --type card --page 1
 *   node report-builder-cli.js build-dashboard
 */

const https = require('https');
const { execSync } = require('child_process');

// Configuration
const CONFIG = {
    datasetId: '3477f170-bf61-42a4-b7a6-4414d7bf8881',
    apiBase: 'https://api.powerbi.com/v1.0/myorg',
    embedBase: 'https://app.powerbi.com'
};

// Visual type mappings
const VISUAL_TYPES = {
    card: 'card',
    kpi: 'kpi', 
    gauge: 'gauge',
    funnel: 'funnel',
    line: 'lineChart',
    column: 'clusteredColumnChart',
    bar: 'clusteredBarChart',
    donut: 'donutChart',
    pie: 'pieChart',
    map: 'filledMap',
    table: 'tableEx',
    matrix: 'pivotTable',
    slicer: 'slicer',
    text: 'textbox',
    area: 'areaChart'
};

// Report page definitions
const REPORT_PAGES = [
    {
        name: 'ExecutiveCommandCenter',
        displayName: 'Executive Command Center',
        ordinal: 0,
        visuals: [
            { type: 'textbox', x: 0, y: 0, width: 1920, height: 60, title: 'Header' },
            { type: 'card', x: 40, y: 160, width: 340, height: 150, measure: 'Total Visits', table: 'Fact_Visit' },
            { type: 'card', x: 400, y: 160, width: 340, height: 150, measure: 'Total Orders', table: 'Fact_Order' },
            { type: 'card', x: 760, y: 160, width: 340, height: 150, measure: 'Total Conversions', table: 'Fact_ProjectConversion' },
            { type: 'kpi', x: 1120, y: 160, width: 340, height: 150, measure: 'Conversion Rate 60D %', table: 'Fact_Visit' },
            { type: 'card', x: 1480, y: 160, width: 380, height: 150, measure: 'Order Amount YTD', table: 'Fact_Order' },
            { type: 'lineChart', x: 40, y: 340, width: 900, height: 350, category: 'Date', series: ['Visits', 'Orders'] },
            { type: 'filledMap', x: 960, y: 340, width: 900, height: 350, location: 'ZoneName', value: 'Conversion Rate' },
            { type: 'donutChart', x: 40, y: 710, width: 580, height: 330, category: 'ClientType', value: 'Visits' },
            { type: 'clusteredBarChart', x: 640, y: 710, width: 620, height: 330, category: 'RoleName', value: 'Achievement' },
            { type: 'funnel', x: 1280, y: 710, width: 580, height: 330, stages: ['Visits', 'Conversions', 'Orders', 'Delivered'] }
        ]
    },
    {
        name: 'TerritoryIntelligence',
        displayName: 'Territory Intelligence',
        ordinal: 1,
        visuals: [
            { type: 'filledMap', x: 40, y: 80, width: 1840, height: 500, drilldown: true },
            { type: 'pivotTable', x: 40, y: 600, width: 1840, height: 420, hierarchy: ['Zone', 'Region', 'Area', 'ASM'] }
        ]
    },
    {
        name: 'QualityScorecard',
        displayName: 'Quality Scorecard',
        ordinal: 2,
        visuals: [
            { type: 'gauge', x: 40, y: 80, width: 580, height: 250, measure: 'Photo Rate', target: 0.70 },
            { type: 'gauge', x: 670, y: 80, width: 580, height: 250, measure: 'GPS Rate', target: 0.80 },
            { type: 'gauge', x: 1300, y: 80, width: 580, height: 250, measure: 'Feedback Rate', target: 0.75 },
            { type: 'clusteredBarChart', x: 40, y: 350, width: 900, height: 300, category: 'ClientType', value: 'Quality' },
            { type: 'tableEx', x: 960, y: 350, width: 920, height: 300, columns: ['Employee', 'Quality', 'Rank'] },
            { type: 'lineChart', x: 40, y: 670, width: 1840, height: 350, category: 'Month', series: ['Photo', 'GPS', 'Feedback'] }
        ]
    },
    {
        name: 'ConversionFunnel',
        displayName: 'Conversion Journey',
        ordinal: 3,
        visuals: [
            { type: 'card', x: 40, y: 80, width: 250, height: 120, measure: 'Site Visits' },
            { type: 'card', x: 310, y: 80, width: 250, height: 120, measure: 'Conversions' },
            { type: 'card', x: 580, y: 80, width: 250, height: 120, measure: 'Orders' },
            { type: 'card', x: 850, y: 80, width: 250, height: 120, measure: 'Delivered' },
            { type: 'kpi', x: 1120, y: 80, width: 250, height: 120, measure: 'Conv Rate' },
            { type: 'card', x: 1390, y: 80, width: 250, height: 120, measure: 'Avg Days' },
            { type: 'gauge', x: 1660, y: 80, width: 220, height: 120, measure: 'Complete %' },
            { type: 'funnel', x: 40, y: 220, width: 900, height: 400, stages: ['Visits', 'Conversions', 'Orders', 'Delivered'] },
            { type: 'stackedBarChart', x: 960, y: 220, width: 450, height: 200, category: 'Reward Type' },
            { type: 'clusteredColumnChart', x: 1430, y: 220, width: 450, height: 200, category: 'Delivery Method' },
            { type: 'clusteredColumnChart', x: 960, y: 440, width: 920, height: 180, category: 'Days Bin' },
            { type: 'lineChart', x: 40, y: 640, width: 1840, height: 380, category: 'Week', series: ['Visits', 'Conversions', 'Orders', 'Rate'] }
        ]
    },
    {
        name: 'OrderAnalytics',
        displayName: 'Order Analytics',
        ordinal: 4,
        visuals: [
            { type: 'card', x: 40, y: 80, width: 250, height: 120, measure: 'Total Orders' },
            { type: 'card', x: 310, y: 80, width: 250, height: 120, measure: 'Total Amount' },
            { type: 'card', x: 580, y: 80, width: 250, height: 120, measure: 'Avg Order' },
            { type: 'card', x: 850, y: 80, width: 250, height: 120, measure: 'Factory DN' },
            { type: 'card', x: 1120, y: 80, width: 250, height: 120, measure: 'General Delivery' },
            { type: 'kpi', x: 1390, y: 80, width: 250, height: 120, measure: 'Engineer Eligible %' },
            { type: 'kpi', x: 1660, y: 80, width: 220, height: 120, measure: 'Partner Eligible %' },
            { type: 'stackedAreaChart', x: 40, y: 220, width: 900, height: 350, category: 'Week', series: ['Factory DN', 'General'] },
            { type: 'donutChart', x: 960, y: 220, width: 450, height: 350, category: 'Order Status' },
            { type: 'clusteredBarChart', x: 1430, y: 220, width: 450, height: 350, category: 'Zone', value: 'Amount' },
            { type: 'tableEx', x: 40, y: 590, width: 1840, height: 400, columns: ['OrderID', 'Site', 'Amount', 'Method', 'Status', 'Engineer'] }
        ]
    },
    {
        name: 'MyPerformance',
        displayName: 'My Performance',
        ordinal: 5,
        visuals: [
            { type: 'card', x: 40, y: 80, width: 200, height: 100, title: 'Role Badge' },
            { type: 'card', x: 260, y: 80, width: 300, height: 100, measure: 'Territory' },
            { type: 'gauge', x: 580, y: 80, width: 250, height: 100, measure: 'Performance Score' },
            { type: 'bulletChart', x: 40, y: 620, width: 1840, height: 200, metrics: ['Visits', 'Conversions', 'Quality', 'Orders'] },
            { type: 'multiRowCard', x: 40, y: 840, width: 1840, height: 180, badges: ['Top Performer', 'Quality Star', 'Streak', 'Conversion King'] }
        ]
    }
];

// Get Azure AD access token
function getAccessToken() {
    try {
        const token = execSync(
            'az account get-access-token --resource https://analysis.windows.net/powerbi/api --query accessToken -o tsv',
            { encoding: 'utf8' }
        ).trim();
        return token;
    } catch (error) {
        console.error('Failed to get access token. Run: az login');
        process.exit(1);
    }
}

// Make HTTP request to Power BI API
function apiRequest(method, path, body = null) {
    return new Promise((resolve, reject) => {
        const token = getAccessToken();
        const url = new URL(CONFIG.apiBase + path);
        
        const options = {
            hostname: url.hostname,
            path: url.pathname + url.search,
            method: method,
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        };

        const req = https.request(options, (res) => {
            let data = '';
            res.on('data', chunk => data += chunk);
            res.on('end', () => {
                if (res.statusCode >= 200 && res.statusCode < 300) {
                    try {
                        resolve(data ? JSON.parse(data) : {});
                    } catch {
                        resolve(data);
                    }
                } else {
                    reject(new Error(`API Error ${res.statusCode}: ${data}`));
                }
            });
        });

        req.on('error', reject);
        
        if (body) {
            req.write(JSON.stringify(body));
        }
        
        req.end();
    });
}

// List workspaces
async function listWorkspaces() {
    console.log('\n📂 Power BI Workspaces:');
    const response = await apiRequest('GET', '/groups');
    response.value.forEach(ws => {
        console.log(`  ${ws.name}: ${ws.id}`);
    });
    return response.value;
}

// List datasets
async function listDatasets(workspaceId = null) {
    console.log('\n📊 Datasets:');
    const path = workspaceId ? `/groups/${workspaceId}/datasets` : '/datasets';
    const response = await apiRequest('GET', path);
    response.value.forEach(ds => {
        console.log(`  ${ds.name}: ${ds.id}`);
        if (ds.createReportEmbedURL) {
            console.log(`    Embed URL: ${ds.createReportEmbedURL}`);
        }
    });
    return response.value;
}

// List reports
async function listReports(workspaceId = null) {
    console.log('\n📑 Reports:');
    const path = workspaceId ? `/groups/${workspaceId}/reports` : '/reports';
    const response = await apiRequest('GET', path);
    response.value.forEach(rpt => {
        console.log(`  ${rpt.name}: ${rpt.id}`);
        console.log(`    Dataset: ${rpt.datasetId}`);
    });
    return response.value;
}

// Clone report as template
async function cloneReport(sourceReportId, name, workspaceId = null, datasetId = null) {
    console.log(`\n📋 Cloning report "${sourceReportId}" as "${name}"...`);
    
    const body = { name };
    if (workspaceId) body.targetWorkspaceId = workspaceId;
    if (datasetId) body.targetModelId = datasetId;
    
    const response = await apiRequest('POST', `/reports/${sourceReportId}/Clone`, body);
    console.log(`  New report created: ${response.id}`);
    return response;
}

// Get dataset info for embed token
async function getDatasetEmbedInfo(datasetId, workspaceId = null) {
    console.log(`\n🔍 Getting dataset embed info for ${datasetId}...`);
    const path = workspaceId 
        ? `/groups/${workspaceId}/datasets/${datasetId}` 
        : `/datasets/${datasetId}`;
    const response = await apiRequest('GET', path);
    console.log(`  Name: ${response.name}`);
    console.log(`  Web URL: ${response.webUrl}`);
    console.log(`  Create Report URL: ${response.createReportEmbedURL}`);
    return response;
}

// Generate embed token for creating a report
async function generateEmbedToken(datasetId, workspaceId = null) {
    console.log('\n🔐 Generating embed token...');
    
    const body = {
        datasets: [{ id: datasetId }],
        targetWorkspaces: workspaceId ? [{ id: workspaceId }] : []
    };
    
    const response = await apiRequest('POST', '/GenerateToken', body);
    console.log(`  Token expires: ${response.expiration}`);
    return response.token;
}

// Execute DAX query
async function executeDaxQuery(query, datasetId = CONFIG.datasetId, workspaceId = null) {
    console.log('\n🔢 Executing DAX query...');
    
    const path = workspaceId 
        ? `/groups/${workspaceId}/datasets/${datasetId}/executeQueries`
        : `/datasets/${datasetId}/executeQueries`;
    
    const body = {
        queries: [{ query }],
        serializerSettings: { includeNulls: true }
    };
    
    const response = await apiRequest('POST', path, body);
    return response;
}

// Generate report creation HTML
function generateReportCreationHTML(embedUrl, datasetId, token) {
    return `
<!DOCTYPE html>
<html>
<head>
    <title>BMD Sales Report Builder</title>
    <script src="https://cdn.jsdelivr.net/npm/powerbi-client@2.23.0/dist/powerbi.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/powerbi-report-authoring@3.0.0/dist/powerbi-report-authoring.min.js"></script>
</head>
<body>
    <div id="reportContainer" style="height: 100vh; width: 100vw;"></div>
    <script>
        const config = {
            type: 'report',
            tokenType: powerbi.models.TokenType.Aad,
            accessToken: '${token}',
            embedUrl: '${embedUrl}',
            datasetId: '${datasetId}',
            permissions: powerbi.models.Permissions.All,
            viewMode: powerbi.models.ViewMode.Edit,
            settings: {
                panes: {
                    filters: { visible: true },
                    pageNavigation: { visible: true }
                }
            }
        };
        
        const powerbiService = new powerbi.service.Service(
            powerbi.factories.hpmFactory,
            powerbi.factories.wpmpFactory,
            powerbi.factories.routerFactory
        );
        
        const container = document.getElementById('reportContainer');
        const report = powerbiService.createReport(container, config);
        
        report.on('loaded', async () => {
            console.log('Report loaded - ready for authoring');
            
            // Get active page
            const pages = await report.getPages();
            const page = pages.find(p => p.isActive);
            
            // Create visuals programmatically
            ${generateVisualCreationCode(REPORT_PAGES[0])}
        });
        
        report.on('error', (e) => console.error('Error:', e.detail));
    </script>
</body>
</html>`;
}

// Generate JavaScript code for visual creation
function generateVisualCreationCode(pageConfig) {
    const code = pageConfig.visuals.map(v => `
            // Create ${v.type}
            await page.createVisual('${v.type}', {
                x: ${v.x},
                y: ${v.y},
                width: ${v.width},
                height: ${v.height}
            });`).join('\n');
    
    return code;
}

// Print visual creation instructions
function printVisualInstructions() {
    console.log(`
╔═══════════════════════════════════════════════════════════════════════════════╗
║          POWER BI REPORT AUTHORING - VISUAL CREATION GUIDE                    ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║                                                                               ║
║  The Power BI Report Authoring API allows programmatic visual creation:      ║
║                                                                               ║
║  1. CREATE VISUAL:                                                            ║
║     const response = await page.createVisual('card', {                        ║
║         x: 100, y: 100, width: 300, height: 200                              ║
║     });                                                                       ║
║     const visual = response.visual;                                           ║
║                                                                               ║
║  2. ADD DATA FIELD:                                                           ║
║     await visual.addDataField('Values', {                                     ║
║         $schema: 'http://powerbi.com/product/schema#measure',                 ║
║         table: 'Fact_Visit',                                                  ║
║         measure: 'Total Visits'                                               ║
║     });                                                                       ║
║                                                                               ║
║  3. SET PROPERTIES:                                                           ║
║     await visual.setProperty(                                                 ║
║         { objectName: 'title', propertyName: 'titleText' },                   ║
║         { schema: 'text', value: 'VISITS' }                                   ║
║     );                                                                        ║
║                                                                               ║
║  AVAILABLE VISUAL TYPES:                                                      ║
║  card, kpi, gauge, funnel, lineChart, clusteredColumnChart,                   ║
║  clusteredBarChart, donutChart, pieChart, filledMap, tableEx,                 ║
║  pivotTable, slicer, textbox, areaChart, stackedAreaChart                     ║
║                                                                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝
`);
}

// Print report design summary
function printReportDesign() {
    console.log('\n📊 BMD SALES REPORT DESIGN\n');
    console.log('═'.repeat(80));
    
    REPORT_PAGES.forEach((page, i) => {
        console.log(`\nPage ${i + 1}: ${page.displayName}`);
        console.log('─'.repeat(40));
        page.visuals.forEach((v, j) => {
            console.log(`  ${j + 1}. ${v.type.padEnd(25)} @ (${v.x}, ${v.y}) ${v.width}x${v.height}`);
            if (v.measure) console.log(`     Measure: ${v.measure}`);
            if (v.category) console.log(`     Category: ${v.category}`);
        });
    });
    
    console.log('\n' + '═'.repeat(80));
}

// CLI handler
async function main() {
    const args = process.argv.slice(2);
    const command = args[0];
    
    console.log('╔═══════════════════════════════════════════════════════════════╗');
    console.log('║       BMD SALES - POWER BI REPORT BUILDER CLI                 ║');
    console.log('╚═══════════════════════════════════════════════════════════════╝');

    switch (command) {
        case 'workspaces':
            await listWorkspaces();
            break;
            
        case 'datasets':
            await listDatasets(args[1]);
            break;
            
        case 'reports':
            await listReports(args[1]);
            break;
            
        case 'dataset-info':
            await getDatasetEmbedInfo(args[1] || CONFIG.datasetId, args[2]);
            break;
            
        case 'clone':
            if (!args[1] || !args[2]) {
                console.log('Usage: clone <source-report-id> <new-name> [workspace-id]');
                break;
            }
            await cloneReport(args[1], args[2], args[3], CONFIG.datasetId);
            break;
            
        case 'dax':
            if (!args[1]) {
                console.log('Usage: dax "<query>"');
                console.log('Example: dax "EVALUATE SUMMARIZECOLUMNS(Dim_Territory[ZoneName], \\"Visits\\", COUNTROWS(Fact_Visit))"');
                break;
            }
            const result = await executeDaxQuery(args[1]);
            console.log(JSON.stringify(result, null, 2));
            break;
            
        case 'design':
            printReportDesign();
            break;
            
        case 'instructions':
            printVisualInstructions();
            break;
            
        case 'generate-html':
            const embedUrl = args[1] || `${CONFIG.embedBase}/reportEmbed`;
            const datasetId = args[2] || CONFIG.datasetId;
            const token = getAccessToken();
            const html = generateReportCreationHTML(embedUrl, datasetId, token);
            console.log(html);
            break;
            
        default:
            console.log(`
Usage: node report-builder-cli.js <command> [options]

Commands:
  workspaces              List available workspaces
  datasets [workspace]    List datasets
  reports [workspace]     List reports
  dataset-info [id] [ws]  Get dataset embed info
  clone <id> <name> [ws]  Clone a report
  dax "<query>"           Execute DAX query
  design                  Print report design specification
  instructions            Show visual creation API guide
  generate-html           Generate HTML for embedded report creation

Examples:
  node report-builder-cli.js workspaces
  node report-builder-cli.js datasets
  node report-builder-cli.js design
  node report-builder-cli.js dax "EVALUATE SUMMARIZECOLUMNS(Dim_Territory[ZoneName])"
            `);
    }
}

main().catch(console.error);
