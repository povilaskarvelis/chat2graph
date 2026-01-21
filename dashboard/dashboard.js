// Dashboard JavaScript for Chat2Graph
let currentData = null;
let charts = {};
let graphNetwork = null;
let graphData = { nodes: [], edges: [] };

// Initialize dashboard
document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('refreshBtn').addEventListener('click', loadData);
    document.getElementById('queryBtn').addEventListener('click', handleGraphQuery);
    document.getElementById('clearGraphBtn').addEventListener('click', clearGraph);
    document.getElementById('graphQuery').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            handleGraphQuery();
        }
    });
    initializeGraph();
    loadData();
});

// Load data from JSON file or API
async function loadData() {
    const dataSource = document.getElementById('dataSource').value;
    const loadingEl = document.getElementById('loading');
    const errorEl = document.getElementById('error');
    
    loadingEl.classList.remove('hidden');
    errorEl.classList.add('hidden');
    
    try {
        if (dataSource === 'api') {
            await loadFromAPI();
        } else {
            await loadFromJSON();
        }
    } catch (error) {
        console.error('Error loading data:', error);
        errorEl.textContent = `Error loading data: ${error.message}`;
        errorEl.classList.remove('hidden');
    } finally {
        loadingEl.classList.add('hidden');
    }
}

// Load data from JSON file
async function loadFromJSON() {
    // Try multiple possible paths
    const paths = [
        '../results/analysis_latest.json',
        'results/analysis_latest.json',
        './results/analysis_latest.json'
    ];
    
    let lastError = null;
    
    for (const path of paths) {
        try {
            const response = await fetch(path);
            if (!response.ok) {
                continue;
            }
            currentData = await response.json();
            renderDashboard();
            return; // Success!
        } catch (error) {
            lastError = error;
            continue;
        }
    }
    
    // If all paths failed
    throw new Error('Could not load analysis data. Make sure analysis_latest.json exists in the results/ directory. ' +
                   'If opening directly from file system, use a web server (see dashboard/README.md).');
}

// Load data from API
async function loadFromAPI() {
    try {
        const response = await fetch('http://localhost:8080/stats');
        if (!response.ok) {
            throw new Error('API server not available');
        }
        // For now, fall back to JSON if API doesn't have full analysis
        await loadFromJSON();
    } catch (error) {
        throw new Error('API server not available. Please use JSON data source or start the API server.');
    }
}

// Render the entire dashboard
function renderDashboard() {
    if (!currentData) return;
    
    renderOverallStats();
    renderCharts();
    renderDisorderCards();
    renderEpisodes();
}

// Render overall statistics
function renderOverallStats() {
    const stats = currentData.overall;
    const container = document.getElementById('overallStats');
    
    const clinicalRatio = stats.total_entities > 0 
        ? (stats.clinical_entities / stats.total_entities * 100).toFixed(1) 
        : 0;
    
    container.innerHTML = `
        <div class="stat-card">
            <div class="stat-value">${stats.total_entities}</div>
            <div class="stat-label">Total Entities</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">${stats.clinical_entities}</div>
            <div class="stat-label">Clinical Entities</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">${stats.semantic_entities}</div>
            <div class="stat-label">Semantic Entities</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">${clinicalRatio}%</div>
            <div class="stat-label">Clinical Ratio</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">${stats.total_relationships}</div>
            <div class="stat-label">Relationships</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">${stats.episodes}</div>
            <div class="stat-label">Episodes</div>
        </div>
    `;
}

// Render charts
function renderCharts() {
    renderClinicalRatioChart();
    renderEntityCountsChart();
    renderDensityChart();
    renderRelationshipsChart();
}

// Clinical Ratio Chart
function renderClinicalRatioChart() {
    const ctx = document.getElementById('clinicalRatioChart').getContext('2d');
    const disorders = Object.keys(currentData.by_disorder);
    const ratios = disorders.map(d => currentData.by_disorder[d].avg_clinical_ratio * 100);
    
    if (charts.clinicalRatio) {
        charts.clinicalRatio.destroy();
    }
    
    charts.clinicalRatio = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: disorders,
            datasets: [{
                label: 'Clinical Ratio (%)',
                data: ratios,
                backgroundColor: [
                    'rgba(74, 144, 226, 0.8)',
                    'rgba(123, 104, 238, 0.8)',
                    'rgba(231, 76, 60, 0.8)'
                ],
                borderColor: [
                    'rgba(74, 144, 226, 1)',
                    'rgba(123, 104, 238, 1)',
                    'rgba(231, 76, 60, 1)'
                ],
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100,
                    ticks: {
                        callback: function(value) {
                            return value + '%';
                        }
                    }
                }
            },
            plugins: {
                legend: {
                    display: false
                }
            }
        }
    });
}

// Entity Counts Chart
function renderEntityCountsChart() {
    const ctx = document.getElementById('entityCountsChart').getContext('2d');
    const disorders = Object.keys(currentData.by_disorder);
    const clinical = disorders.map(d => currentData.by_disorder[d].avg_clinical_entities);
    const semantic = disorders.map(d => currentData.by_disorder[d].avg_semantic_entities);
    
    if (charts.entityCounts) {
        charts.entityCounts.destroy();
    }
    
    charts.entityCounts = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: disorders,
            datasets: [
                {
                    label: 'Clinical Entities',
                    data: clinical,
                    backgroundColor: 'rgba(74, 144, 226, 0.8)',
                    borderColor: 'rgba(74, 144, 226, 1)',
                    borderWidth: 2
                },
                {
                    label: 'Semantic Entities',
                    data: semantic,
                    backgroundColor: 'rgba(123, 104, 238, 0.8)',
                    borderColor: 'rgba(123, 104, 238, 1)',
                    borderWidth: 2
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
}

// Density Chart
function renderDensityChart() {
    const ctx = document.getElementById('densityChart').getContext('2d');
    const disorders = Object.keys(currentData.by_disorder);
    const clinicalDens = disorders.map(d => currentData.by_disorder[d].avg_clinical_density);
    const semanticDens = disorders.map(d => currentData.by_disorder[d].avg_semantic_density);
    const crossDens = disorders.map(d => currentData.by_disorder[d].avg_cross_density);
    
    if (charts.density) {
        charts.density.destroy();
    }
    
    charts.density = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: disorders,
            datasets: [
                {
                    label: 'Clinical Density',
                    data: clinicalDens,
                    backgroundColor: 'rgba(74, 144, 226, 0.8)',
                    borderColor: 'rgba(74, 144, 226, 1)',
                    borderWidth: 2
                },
                {
                    label: 'Semantic Density',
                    data: semanticDens,
                    backgroundColor: 'rgba(123, 104, 238, 0.8)',
                    borderColor: 'rgba(123, 104, 238, 1)',
                    borderWidth: 2
                },
                {
                    label: 'Cross-type Density',
                    data: crossDens,
                    backgroundColor: 'rgba(231, 76, 60, 0.8)',
                    borderColor: 'rgba(231, 76, 60, 1)',
                    borderWidth: 2
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
}

// Relationships Chart
function renderRelationshipsChart() {
    const ctx = document.getElementById('relationshipsChart').getContext('2d');
    const episodes = Object.keys(currentData.by_episode);
    const relationships = episodes.map(ep => currentData.by_episode[ep].metrics.relationships);
    
    if (charts.relationships) {
        charts.relationships.destroy();
    }
    
    charts.relationships = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: episodes.map(ep => ep.replace(/_/g, ' ')),
            datasets: [{
                label: 'Relationships',
                data: relationships,
                backgroundColor: 'rgba(80, 200, 120, 0.8)',
                borderColor: 'rgba(80, 200, 120, 1)',
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            scales: {
                y: {
                    beginAtZero: true
                }
            },
            plugins: {
                legend: {
                    display: false
                }
            }
        }
    });
}

// Render disorder cards
function renderDisorderCards() {
    const container = document.getElementById('disorderCards');
    const disorders = currentData.by_disorder;
    
    container.innerHTML = Object.keys(disorders).map(disorder => {
        const data = disorders[disorder];
        const disorderClass = disorder.toLowerCase().replace(/\s+/g, '');
        const ratio = (data.avg_clinical_ratio * 100).toFixed(1);
        
        return `
            <div class="disorder-card ${disorderClass}">
                <h3>${disorder}</h3>
                <div class="metric-row">
                    <span class="metric-label">Episodes:</span>
                    <span class="metric-value">${data.episode_count}</span>
                </div>
                <div class="metric-row">
                    <span class="metric-label">Meets Criteria:</span>
                    <span class="metric-value">${data.meets_criteria_count}</span>
                </div>
                <div class="metric-row">
                    <span class="metric-label">Avg Clinical Entities:</span>
                    <span class="metric-value">${data.avg_clinical_entities}</span>
                </div>
                <div class="metric-row">
                    <span class="metric-label">Avg Semantic Entities:</span>
                    <span class="metric-value">${data.avg_semantic_entities}</span>
                </div>
                <div class="metric-row">
                    <span class="metric-label">Clinical Ratio:</span>
                    <span class="metric-value">${ratio}%</span>
                </div>
                <div class="metric-row">
                    <span class="metric-label">Avg Relationships:</span>
                    <span class="metric-value">${data.avg_relationships}</span>
                </div>
                <div class="metric-row">
                    <span class="metric-label">Clinical Density:</span>
                    <span class="metric-value">${data.avg_clinical_density.toFixed(4)}</span>
                </div>
                <div class="metric-row">
                    <span class="metric-label">Semantic Density:</span>
                    <span class="metric-value">${data.avg_semantic_density.toFixed(4)}</span>
                </div>
                <div class="metric-row">
                    <span class="metric-label">Cross-type Density:</span>
                    <span class="metric-value">${data.avg_cross_density.toFixed(4)}</span>
                </div>
            </div>
        `;
    }).join('');
}

// Render episodes
function renderEpisodes() {
    const tabsContainer = document.getElementById('episodeTabs');
    const contentContainer = document.getElementById('episodeContent');
    const episodes = Object.keys(currentData.by_episode);
    
    // Create tabs
    tabsContainer.innerHTML = episodes.map((ep, index) => `
        <button class="tab ${index === 0 ? 'active' : ''}" data-episode="${ep}">
            ${ep.replace(/_/g, ' ')}
        </button>
    `).join('');
    
    // Create content
    contentContainer.innerHTML = episodes.map((ep, index) => {
        const episodeData = currentData.by_episode[ep];
        const metrics = episodeData.metrics;
        const clinicalRatio = metrics.total > 0 
            ? (metrics.clinical / metrics.total * 100).toFixed(1) 
            : 0;
        
        return `
            <div class="episode-details ${index === 0 ? 'active' : ''}" data-episode="${ep}">
                <div class="episode-metrics">
                    <div class="metric-box">
                        <div class="value">${metrics.clinical}</div>
                        <div class="label">Clinical Entities</div>
                    </div>
                    <div class="metric-box">
                        <div class="value">${metrics.semantic}</div>
                        <div class="label">Semantic Entities</div>
                    </div>
                    <div class="metric-box">
                        <div class="value">${metrics.total}</div>
                        <div class="label">Total Entities</div>
                    </div>
                    <div class="metric-box">
                        <div class="value">${clinicalRatio}%</div>
                        <div class="label">Clinical Ratio</div>
                    </div>
                    <div class="metric-box">
                        <div class="value">${metrics.relationships}</div>
                        <div class="label">Relationships</div>
                    </div>
                    <div class="metric-box">
                        <div class="value">${episodeData.disorder || 'N/A'}</div>
                        <div class="label">Disorder</div>
                    </div>
                    <div class="metric-box">
                        <div class="value">${episodeData.meets_criteria ? '✓' : '✗'}</div>
                        <div class="label">Meets Criteria</div>
                    </div>
                </div>
                
                <div class="entities-section">
                    <div class="entities-grid">
                        <div class="entity-list">
                            <h4>Clinical Entities (${episodeData.clinical_entities.length})</h4>
                            ${episodeData.clinical_entities.map(entity => `
                                <div class="entity-item">
                                    <span class="entity-name">${entity.name}</span>
                                    <span class="entity-type">(${entity.type})</span>
                                </div>
                            `).join('')}
                        </div>
                        
                        <div class="entity-list">
                            <h4>Semantic Entities (${episodeData.semantic_entities.length})</h4>
                            ${episodeData.semantic_entities.map(entity => `
                                <div class="entity-item">
                                    <span class="entity-name">${entity.name}</span>
                                    <span class="entity-type">(${entity.type})</span>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                    
                    <div class="relationships-list">
                        <h4>Relationships (${episodeData.relationships.length})</h4>
                        ${episodeData.relationships.map(rel => `
                            <div class="relationship-item">
                                <div class="relationship-path">
                                    ${rel.from}
                                    <span class="relationship-type">--[${rel.type}]--></span>
                                    ${rel.to}
                                </div>
                                ${rel.description ? `
                                    <div class="relationship-description">"${rel.description}"</div>
                                ` : ''}
                            </div>
                        `).join('')}
                    </div>
                </div>
            </div>
        `;
    }).join('');
    
    // Add tab click handlers
    document.querySelectorAll('.tab').forEach(tab => {
        tab.addEventListener('click', () => {
            const episode = tab.dataset.episode;
            
            // Update active tab
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            tab.classList.add('active');
            
            // Update active content
            document.querySelectorAll('.episode-details').forEach(d => d.classList.remove('active'));
            document.querySelector(`.episode-details[data-episode="${episode}"]`).classList.add('active');
        });
    });
}

// Initialize graph visualization
function initializeGraph() {
    const container = document.getElementById('graphNetwork');
    const options = {
        nodes: {
            shape: 'dot',
            size: 20,
            font: {
                size: 14,
                face: 'Arial'
            },
            borderWidth: 2,
            shadow: true
        },
        edges: {
            width: 2,
            color: { inherit: 'from' },
            smooth: {
                type: 'continuous',
                roundness: 0.5
            },
            arrows: {
                to: { enabled: true, scaleFactor: 1 }
            },
            font: {
                size: 12,
                align: 'middle'
            }
        },
        physics: {
            enabled: true,
            stabilization: {
                enabled: true,
                iterations: 100
            },
            barnesHut: {
                gravitationalConstant: -2000,
                centralGravity: 0.3,
                springLength: 200,
                springConstant: 0.04,
                damping: 0.09
            }
        },
        interaction: {
            hover: true,
            tooltipDelay: 200,
            zoomView: true,
            dragView: true
        }
    };
    
    graphNetwork = new vis.Network(container, graphData, options);
    
    // Add click handler to show node details
    graphNetwork.on('click', (params) => {
        if (params.nodes.length > 0) {
            const nodeId = params.nodes[0];
            const node = graphData.nodes.find(n => n.id === nodeId);
            if (node) {
                showNodeDetails(node);
            }
        }
    });
}

// Handle graph query
function handleGraphQuery() {
    if (!currentData) {
        alert('Please load data first');
        return;
    }
    
    const query = document.getElementById('graphQuery').value.trim();
    const mode = document.getElementById('queryMode').value;
    
    if (!query) {
        alert('Please enter a query');
        return;
    }
    
    let results = null;
    
    switch (mode) {
        case 'search':
            results = searchEntities(query);
            break;
        case 'episode':
            results = getEpisodeGraph(query);
            break;
        case 'relationship':
            results = filterByRelationship(query);
            break;
        case 'disorder':
            results = filterByDisorder(query);
            break;
    }
    
    if (results && results.nodes.length > 0) {
        renderGraph(results);
    } else {
        document.getElementById('graphInfo').textContent = 'No results found for your query.';
        clearGraph();
    }
}

// Helper function to get node ID
function getNodeId(entityName, isClinical) {
    return `${isClinical ? 'clinical' : 'semantic'}_${entityName}`;
}

// Helper function to find entity in episode data
function findEntity(episodeData, name) {
    const clinical = episodeData.clinical_entities.find(e => e.name === name);
    if (clinical) return { ...clinical, isClinical: true };
    const semantic = episodeData.semantic_entities.find(e => e.name === name);
    if (semantic) return { ...semantic, isClinical: false };
    return null;
}

// Search entities by name
function searchEntities(query) {
    const queryLower = query.toLowerCase();
    const nodes = new Map();
    const edges = [];
    
    // Search through all episodes
    for (const [episodeName, episodeData] of Object.entries(currentData.by_episode)) {
        // Search clinical entities
        for (const entity of episodeData.clinical_entities) {
            if (entity.name.toLowerCase().includes(queryLower)) {
                const nodeId = getNodeId(entity.name, true);
                if (!nodes.has(nodeId)) {
                    nodes.set(nodeId, {
                        id: nodeId,
                        label: entity.name,
                        group: 'clinical',
                        type: entity.type,
                        episodes: [episodeName]
                    });
                } else {
                    if (!nodes.get(nodeId).episodes.includes(episodeName)) {
                        nodes.get(nodeId).episodes.push(episodeName);
                    }
                }
            }
        }
        
        // Search semantic entities
        for (const entity of episodeData.semantic_entities) {
            if (entity.name.toLowerCase().includes(queryLower)) {
                const nodeId = getNodeId(entity.name, false);
                if (!nodes.has(nodeId)) {
                    nodes.set(nodeId, {
                        id: nodeId,
                        label: entity.name,
                        group: 'semantic',
                        type: entity.type,
                        episodes: [episodeName]
                    });
                } else {
                    if (!nodes.get(nodeId).episodes.includes(episodeName)) {
                        nodes.get(nodeId).episodes.push(episodeName);
                    }
                }
            }
        }
        
        // Add relationships for matching entities and their connections
        for (const rel of episodeData.relationships) {
            const fromMatches = rel.from.toLowerCase().includes(queryLower);
            const toMatches = rel.to.toLowerCase().includes(queryLower);
            
            if (fromMatches || toMatches) {
                // Add from node if it matches
                if (fromMatches) {
                    const fromEntity = findEntity(episodeData, rel.from);
                    if (fromEntity) {
                        const fromId = getNodeId(rel.from, fromEntity.isClinical);
                        if (!nodes.has(fromId)) {
                            nodes.set(fromId, {
                                id: fromId,
                                label: rel.from,
                                group: fromEntity.isClinical ? 'clinical' : 'semantic',
                                type: fromEntity.type,
                                episodes: [episodeName]
                            });
                        }
                    }
                }
                
                // Add to node if it matches
                if (toMatches) {
                    const toEntity = findEntity(episodeData, rel.to);
                    if (toEntity) {
                        const toId = getNodeId(rel.to, toEntity.isClinical);
                        if (!nodes.has(toId)) {
                            nodes.set(toId, {
                                id: toId,
                                label: rel.to,
                                group: toEntity.isClinical ? 'clinical' : 'semantic',
                                type: toEntity.type,
                                episodes: [episodeName]
                            });
                        }
                    }
                }
                
                // Add edge if both nodes exist (or if one matches and we want to show connections)
                const fromEntity = findEntity(episodeData, rel.from);
                const toEntity = findEntity(episodeData, rel.to);
                
                if (fromEntity && toEntity) {
                    const fromId = getNodeId(rel.from, fromEntity.isClinical);
                    const toId = getNodeId(rel.to, toEntity.isClinical);
                    
                    // Add edge if at least one node matches the query
                    if (nodes.has(fromId) || nodes.has(toId)) {
                        // Make sure both nodes are in the graph
                        if (!nodes.has(fromId) && fromEntity) {
                            nodes.set(fromId, {
                                id: fromId,
                                label: rel.from,
                                group: fromEntity.isClinical ? 'clinical' : 'semantic',
                                type: fromEntity.type,
                                episodes: [episodeName]
                            });
                        }
                        if (!nodes.has(toId) && toEntity) {
                            nodes.set(toId, {
                                id: toId,
                                label: rel.to,
                                group: toEntity.isClinical ? 'clinical' : 'semantic',
                                type: toEntity.type,
                                episodes: [episodeName]
                            });
                        }
                        
                        // Add edge
                        if (nodes.has(fromId) && nodes.has(toId)) {
                            edges.push({
                                from: fromId,
                                to: toId,
                                label: rel.type,
                                title: rel.description || rel.type
                            });
                        }
                    }
                }
            }
        }
    }
    
    return { nodes: Array.from(nodes.values()), edges };
}

// Get graph for a specific episode
function getEpisodeGraph(episodeName) {
    // Try exact match first
    let episodeData = currentData.by_episode[episodeName];
    
    // Try partial match
    if (!episodeData) {
        const matchingKey = Object.keys(currentData.by_episode).find(
            key => key.toLowerCase().includes(episodeName.toLowerCase())
        );
        if (matchingKey) {
            episodeData = currentData.by_episode[matchingKey];
            episodeName = matchingKey;
        }
    }
    
    if (!episodeData) {
        return null;
    }
    
    const nodes = new Map();
    const edges = [];
    
    // Add all entities from episode
    for (const entity of episodeData.clinical_entities) {
        const nodeId = getNodeId(entity.name, true);
        nodes.set(nodeId, {
            id: nodeId,
            label: entity.name,
            group: 'clinical',
            type: entity.type,
            episodes: [episodeName]
        });
    }
    
    for (const entity of episodeData.semantic_entities) {
        const nodeId = getNodeId(entity.name, false);
        nodes.set(nodeId, {
            id: nodeId,
            label: entity.name,
            group: 'semantic',
            type: entity.type,
            episodes: [episodeName]
        });
    }
    
    // Add all relationships
    for (const rel of episodeData.relationships) {
        const fromEntity = findEntity(episodeData, rel.from);
        const toEntity = findEntity(episodeData, rel.to);
        
        if (fromEntity && toEntity) {
            const fromId = getNodeId(rel.from, fromEntity.isClinical);
            const toId = getNodeId(rel.to, toEntity.isClinical);
            
            if (nodes.has(fromId) && nodes.has(toId)) {
                edges.push({
                    from: fromId,
                    to: toId,
                    label: rel.type,
                    title: rel.description || rel.type
                });
            }
        }
    }
    
    return { nodes: Array.from(nodes.values()), edges };
}

// Filter by relationship type
function filterByRelationship(relType) {
    const nodes = new Map();
    const edges = [];
    const relTypeUpper = relType.toUpperCase();
    
    for (const [episodeName, episodeData] of Object.entries(currentData.by_episode)) {
        for (const rel of episodeData.relationships) {
            if (rel.type.toUpperCase().includes(relTypeUpper)) {
                const fromEntity = findEntity(episodeData, rel.from);
                const toEntity = findEntity(episodeData, rel.to);
                
                if (fromEntity && toEntity) {
                    const fromId = getNodeId(rel.from, fromEntity.isClinical);
                    const toId = getNodeId(rel.to, toEntity.isClinical);
                    
                    // Add nodes
                    if (!nodes.has(fromId)) {
                        nodes.set(fromId, {
                            id: fromId,
                            label: rel.from,
                            group: fromEntity.isClinical ? 'clinical' : 'semantic',
                            type: fromEntity.type,
                            episodes: [episodeName]
                        });
                    } else {
                        if (!nodes.get(fromId).episodes.includes(episodeName)) {
                            nodes.get(fromId).episodes.push(episodeName);
                        }
                    }
                    
                    if (!nodes.has(toId)) {
                        nodes.set(toId, {
                            id: toId,
                            label: rel.to,
                            group: toEntity.isClinical ? 'clinical' : 'semantic',
                            type: toEntity.type,
                            episodes: [episodeName]
                        });
                    } else {
                        if (!nodes.get(toId).episodes.includes(episodeName)) {
                            nodes.get(toId).episodes.push(episodeName);
                        }
                    }
                    
                    // Add edge
                    edges.push({
                        from: fromId,
                        to: toId,
                        label: rel.type,
                        title: rel.description || rel.type
                    });
                }
            }
        }
    }
    
    return { nodes: Array.from(nodes.values()), edges };
}

// Filter by disorder
function filterByDisorder(disorderQuery) {
    const disorderLower = disorderQuery.toLowerCase();
    const nodes = new Map();
    const edges = [];
    
    for (const [episodeName, episodeData] of Object.entries(currentData.by_episode)) {
        const disorder = episodeData.disorder || '';
        if (disorder.toLowerCase().includes(disorderLower)) {
            // Add all entities
            for (const entity of episodeData.clinical_entities) {
                const nodeId = getNodeId(entity.name, true);
                if (!nodes.has(nodeId)) {
                    nodes.set(nodeId, {
                        id: nodeId,
                        label: entity.name,
                        group: 'clinical',
                        type: entity.type,
                        episodes: [episodeName]
                    });
                } else {
                    if (!nodes.get(nodeId).episodes.includes(episodeName)) {
                        nodes.get(nodeId).episodes.push(episodeName);
                    }
                }
            }
            
            for (const entity of episodeData.semantic_entities) {
                const nodeId = getNodeId(entity.name, false);
                if (!nodes.has(nodeId)) {
                    nodes.set(nodeId, {
                        id: nodeId,
                        label: entity.name,
                        group: 'semantic',
                        type: entity.type,
                        episodes: [episodeName]
                    });
                } else {
                    if (!nodes.get(nodeId).episodes.includes(episodeName)) {
                        nodes.get(nodeId).episodes.push(episodeName);
                    }
                }
            }
            
            // Add relationships
            for (const rel of episodeData.relationships) {
                const fromEntity = findEntity(episodeData, rel.from);
                const toEntity = findEntity(episodeData, rel.to);
                
                if (fromEntity && toEntity) {
                    const fromId = getNodeId(rel.from, fromEntity.isClinical);
                    const toId = getNodeId(rel.to, toEntity.isClinical);
                    
                    if (nodes.has(fromId) && nodes.has(toId)) {
                        edges.push({
                            from: fromId,
                            to: toId,
                            label: rel.type,
                            title: rel.description || rel.type
                        });
                    }
                }
            }
        }
    }
    
    return { nodes: Array.from(nodes.values()), edges };
}

// Render graph
function renderGraph(data) {
    graphData.nodes = data.nodes.map(node => ({
        id: node.id,
        label: node.label,
        group: node.group,
        title: `${node.label}\nType: ${node.type}\nEpisodes: ${node.episodes.join(', ')}`,
        color: node.group === 'clinical' ? 
            { background: '#4a90e2', border: '#357abd' } : 
            { background: '#7b68ee', border: '#5a4fcf' }
    }));
    
    graphData.edges = data.edges.map(edge => ({
        from: edge.from,
        to: edge.to,
        label: edge.label,
        title: edge.title || edge.label,
        color: { color: '#888', highlight: '#333' }
    }));
    
    graphNetwork.setData(graphData);
    
    // Update info
    document.getElementById('graphInfo').innerHTML = `
        <strong>Graph loaded:</strong> ${data.nodes.length} nodes, ${data.edges.length} edges
        <br><small>Click on nodes to see details. Drag to move, scroll to zoom.</small>
    `;
}

// Clear graph
function clearGraph() {
    graphData.nodes = [];
    graphData.edges = [];
    graphNetwork.setData(graphData);
    document.getElementById('graphInfo').textContent = '';
    document.getElementById('graphQuery').value = '';
}

// Show node details
function showNodeDetails(node) {
    const episodes = node.episodes || [];
    const episodeList = episodes.map(ep => {
        const epData = currentData.by_episode[ep];
        return `${ep} (${epData.disorder || 'Unknown'})`;
    }).join('\n');
    
    alert(`Entity: ${node.label}\nType: ${node.type}\nGroup: ${node.group}\n\nAppears in:\n${episodeList}`);
}

