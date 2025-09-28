/**
 * Donation Heatmap Manager
 * Advanced heat map visualization using deck.gl for high-performance rendering
 */

class DonationHeatmapManager {
    constructor(map) {
        this.map = map;
        this.overlay = null;
        this.heatmapData = [];
        this.currentLayers = [];
        
        // Configuration for different heatmap modes
        this.heatmapConfigs = {
            donation_amount: {
                colorRange: [
                    [255, 255, 178, 25],   // Low activity - Light Yellow
                    [254, 217, 118, 85],   // Low-Medium - Orange Yellow  
                    [254, 178, 76, 127],   // Medium - Orange
                    [253, 141, 60, 170],   // Medium-High - Dark Orange
                    [252, 78, 42, 212],    // High - Red Orange
                    [227, 26, 28, 255],    // Very High - Red
                    [189, 0, 38, 255]      // Extreme - Dark Red
                ],
                intensity: 1,
                threshold: 0.05,
                radiusPixels: 120
            },
            donation_frequency: {
                colorRange: [
                    [158, 202, 225, 25],   // Low frequency - Light Blue
                    [107, 174, 214, 85],   // Low-Medium - Medium Blue
                    [66, 146, 198, 127],   // Medium - Blue
                    [33, 113, 181, 170],   // Medium-High - Dark Blue
                    [8, 81, 156, 212],     // High - Navy Blue
                    [8, 48, 107, 255]      // Very High - Dark Navy
                ],
                intensity: 0.8,
                threshold: 0.03,
                radiusPixels: 100
            },
            user_density: {
                colorRange: [
                    [247, 252, 245, 25],   // Low density - Light Green
                    [199, 233, 192, 85],   // Low-Medium - Light Green
                    [161, 217, 155, 127],  // Medium - Green
                    [116, 196, 118, 170],  // Medium-High - Medium Green
                    [65, 171, 93, 212],    // High - Dark Green
                    [35, 139, 69, 255],    // Very High - Forest Green
                    [0, 90, 50, 255]       // Extreme - Dark Forest
                ],
                intensity: 1.2,
                threshold: 0.08,
                radiusPixels: 90
            },
            impact_score: {
                colorRange: [
                    [255, 245, 240, 25],   // Low impact - Light Pink
                    [254, 224, 210, 85],   // Low-Medium - Pink
                    [252, 187, 161, 127],  // Medium - Light Red
                    [252, 146, 114, 170],  // Medium-High - Orange Red
                    [251, 106, 74, 212],   // High - Red
                    [239, 59, 44, 255],    // Very High - Bright Red
                    [203, 24, 29, 255]     // Extreme - Dark Red
                ],
                intensity: 1.5,
                threshold: 0.1,
                radiusPixels: 110
            }
        };
        
        this.initializeDeckGL();
    }

    async initializeDeckGL() {
        try {
            // Import deck.gl modules
            const deckgl = await import('https://unpkg.com/deck.gl@latest/dist.min.js');
            
            // Create deck.gl overlay for Google Maps
            this.overlay = new deckgl.GoogleMapsOverlay({
                layers: [],
                getTooltip: ({ object, x, y }) => this.getTooltipContent(object, x, y)
            });
            
            this.overlay.setMap(this.map);
            console.log('Deck.gl overlay initialized');
            
        } catch (error) {
            console.error('Error initializing deck.gl:', error);
            // Fallback to basic heatmap if deck.gl fails
            this.initializeFallbackHeatmap();
        }
    }

    initializeFallbackHeatmap() {
        // Fallback to Google Maps native heatmap
        this.heatmapLayer = new google.maps.visualization.HeatmapLayer({
            data: [],
            map: this.map,
            radius: 50,
            opacity: 0.6
        });
        
        console.log('Fallback heatmap layer initialized');
    }

    updateDonationHeatmap(donationData, mode = 'donation_amount') {
        if (!donationData || !Array.isArray(donationData)) {
            console.warn('Invalid donation data provided');
            return;
        }
        
        this.heatmapData = donationData;
        
        if (this.overlay) {
            this.updateDeckGLHeatmap(mode);
        } else if (this.heatmapLayer) {
            this.updateFallbackHeatmap();
        }
    }

    updateDeckGLHeatmap(mode) {
        const config = this.heatmapConfigs[mode] || this.heatmapConfigs.donation_amount;
        
        // Create heatmap layer
        const heatmapLayer = new deck.HeatmapLayer({
            id: `heatmap-${mode}`,
            data: this.heatmapData,
            getPosition: d => [d.lng || d.longitude, d.lat || d.latitude],
            getWeight: d => this.getWeightForMode(d, mode),
            radiusPixels: config.radiusPixels,
            intensity: config.intensity,
            threshold: config.threshold,
            colorRange: config.colorRange,
            aggregation: 'SUM'
        });

        // Create hexagon layer for additional visualization
        const hexagonLayer = new deck.HexagonLayer({
            id: `hexagon-${mode}`,
            data: this.heatmapData,
            getPosition: d => [d.lng || d.longitude, d.lat || d.latitude],
            getElevationWeight: d => this.getWeightForMode(d, mode),
            elevationScale: 100,
            radius: 200,
            opacity: 0.3,
            coverage: 0.8,
            upperPercentile: 95,
            material: {
                ambient: 0.4,
                diffuse: 0.6,
                shininess: 32,
                specularColor: [255, 255, 255]
            }
        });

        // Create scatter plot layer for individual donations
        const scatterLayer = new deck.ScatterplotLayer({
            id: `scatter-${mode}`,
            data: this.heatmapData.filter(d => this.getWeightForMode(d, mode) > 0),
            getPosition: d => [d.lng || d.longitude, d.lat || d.latitude],
            getRadius: d => Math.sqrt(this.getWeightForMode(d, mode)) * 20,
            getFillColor: d => this.getColorForWeight(this.getWeightForMode(d, mode), config),
            getLineColor: [255, 255, 255],
            lineWidthMinPixels: 1,
            opacity: 0.6,
            radiusMinPixels: 3,
            radiusMaxPixels: 50,
            pickable: true,
            onHover: this.handleScatterHover.bind(this)
        });

        // Update overlay layers
        this.currentLayers = [heatmapLayer, hexagonLayer, scatterLayer];
        this.overlay.setProps({
            layers: this.currentLayers
        });

        console.log(`Updated heatmap with ${this.heatmapData.length} data points in ${mode} mode`);
    }

    updateFallbackHeatmap() {
        // Convert data for Google Maps heatmap
        const heatmapPoints = this.heatmapData.map(d => ({
            location: new google.maps.LatLng(d.lat || d.latitude, d.lng || d.longitude),
            weight: Math.log(this.getWeightForMode(d, 'donation_amount') + 1)
        }));
        
        this.heatmapLayer.setData(heatmapPoints);
    }

    getWeightForMode(dataPoint, mode) {
        switch (mode) {
            case 'donation_amount':
                return Math.log((dataPoint.amount || 0) + 1);
            
            case 'donation_frequency':
                return dataPoint.frequency || dataPoint.donation_count || 1;
            
            case 'user_density':
                return dataPoint.user_count || dataPoint.unique_donors || 1;
            
            case 'impact_score':
                // Calculate impact score based on multiple factors
                const amount = dataPoint.amount || 0;
                const frequency = dataPoint.frequency || 1;
                const uniqueDonors = dataPoint.unique_donors || 1;
                return Math.log((amount * frequency * uniqueDonors) + 1);
            
            default:
                return Math.log((dataPoint.amount || 0) + 1);
        }
    }

    getColorForWeight(weight, config) {
        const normalizedWeight = Math.min(weight / 10, 1); // Normalize to 0-1
        const colorIndex = Math.floor(normalizedWeight * (config.colorRange.length - 1));
        return config.colorRange[colorIndex] || config.colorRange[0];
    }

    handleScatterHover(info) {
        if (info.object) {
            const tooltip = document.getElementById('heatmap-tooltip');
            if (tooltip) {
                tooltip.style.display = 'block';
                tooltip.style.left = info.x + 'px';
                tooltip.style.top = info.y + 'px';
                tooltip.innerHTML = this.createTooltipContent(info.object);
            }
        } else {
            const tooltip = document.getElementById('heatmap-tooltip');
            if (tooltip) {
                tooltip.style.display = 'none';
            }
        }
    }

    getTooltipContent(object, x, y) {
        if (!object) return null;
        
        return {
            html: this.createTooltipContent(object),
            style: {
                backgroundColor: 'rgba(0, 0, 0, 0.8)',
                color: 'white',
                borderRadius: '8px',
                padding: '12px',
                fontSize: '14px',
                maxWidth: '250px'
            }
        };
    }

    createTooltipContent(dataPoint) {
        return `
            <div class="heatmap-tooltip-content">
                <h4>${dataPoint.name || 'Donation Point'}</h4>
                <div class="tooltip-stats">
                    <div class="stat">
                        <span class="label">Total Donated:</span>
                        <span class="value">$${(dataPoint.amount || 0).toLocaleString()}</span>
                    </div>
                    <div class="stat">
                        <span class="label">Donations:</span>
                        <span class="value">${dataPoint.frequency || dataPoint.donation_count || 0}</span>
                    </div>
                    <div class="stat">
                        <span class="label">Unique Donors:</span>
                        <span class="value">${dataPoint.unique_donors || 0}</span>
                    </div>
                    ${dataPoint.organization ? `
                        <div class="stat">
                            <span class="label">Organization:</span>
                            <span class="value">${dataPoint.organization}</span>
                        </div>
                    ` : ''}
                </div>
            </div>
        `;
    }

    // Advanced filtering and analysis
    filterDataByTimeRange(startDate, endDate) {
        const start = new Date(startDate);
        const end = new Date(endDate);
        
        return this.heatmapData.filter(d => {
            const donationDate = new Date(d.date || d.timestamp);
            return donationDate >= start && donationDate <= end;
        });
    }

    filterDataByAmount(minAmount, maxAmount = Infinity) {
        return this.heatmapData.filter(d => {
            const amount = d.amount || 0;
            return amount >= minAmount && amount <= maxAmount;
        });
    }

    filterDataByLocation(bounds) {
        return this.heatmapData.filter(d => {
            const lat = d.lat || d.latitude;
            const lng = d.lng || d.longitude;
            
            return lat >= bounds.south && lat <= bounds.north &&
                   lng >= bounds.west && lng <= bounds.east;
        });
    }

    // Analysis functions
    calculateHotspots(threshold = 0.8) {
        const sortedData = [...this.heatmapData]
            .sort((a, b) => this.getWeightForMode(b, 'impact_score') - this.getWeightForMode(a, 'impact_score'));
        
        const topPercentileCount = Math.ceil(sortedData.length * threshold);
        return sortedData.slice(0, topPercentileCount);
    }

    analyzeTrends(timeWindow = '7d') {
        const trends = {
            growth_rate: 0,
            peak_hours: [],
            peak_days: [],
            geographic_expansion: 0
        };
        
        // Calculate growth rate
        const recentData = this.filterDataByTimeRange(
            new Date(Date.now() - 7 * 24 * 60 * 60 * 1000),
            new Date()
        );
        
        const previousData = this.filterDataByTimeRange(
            new Date(Date.now() - 14 * 24 * 60 * 60 * 1000),
            new Date(Date.now() - 7 * 24 * 60 * 60 * 1000)
        );
        
        if (previousData.length > 0) {
            trends.growth_rate = (recentData.length - previousData.length) / previousData.length;
        }
        
        return trends;
    }

    // Export heatmap data
    exportHeatmapData(format = 'json') {
        switch (format) {
            case 'csv':
                return this.exportAsCSV();
            case 'geojson':
                return this.exportAsGeoJSON();
            default:
                return this.exportAsJSON();
        }
    }

    exportAsJSON() {
        return JSON.stringify(this.heatmapData, null, 2);
    }

    exportAsCSV() {
        if (this.heatmapData.length === 0) return '';
        
        const headers = Object.keys(this.heatmapData[0]);
        const csvContent = [
            headers.join(','),
            ...this.heatmapData.map(row => 
                headers.map(header => row[header] || '').join(',')
            )
        ].join('\n');
        
        return csvContent;
    }

    exportAsGeoJSON() {
        const features = this.heatmapData.map(d => ({
            type: 'Feature',
            geometry: {
                type: 'Point',
                coordinates: [d.lng || d.longitude, d.lat || d.latitude]
            },
            properties: {
                ...d,
                weight_amount: this.getWeightForMode(d, 'donation_amount'),
                weight_frequency: this.getWeightForMode(d, 'donation_frequency'),
                weight_density: this.getWeightForMode(d, 'user_density'),
                weight_impact: this.getWeightForMode(d, 'impact_score')
            }
        }));
        
        return JSON.stringify({
            type: 'FeatureCollection',
            features: features
        }, null, 2);
    }

    // Layer management
    toggleLayer(layerId, visible) {
        const layer = this.currentLayers.find(l => l.id === layerId);
        if (layer) {
            layer.props.visible = visible;
            this.overlay.setProps({
                layers: this.currentLayers
            });
        }
    }

    setLayerOpacity(layerId, opacity) {
        const layer = this.currentLayers.find(l => l.id === layerId);
        if (layer) {
            layer.props.opacity = opacity;
            this.overlay.setProps({
                layers: this.currentLayers
            });
        }
    }

    // Real-time updates
    addRealtimeDonation(donationData) {
        this.heatmapData.push(donationData);
        
        // Limit data size for performance
        if (this.heatmapData.length > 10000) {
            this.heatmapData = this.heatmapData.slice(-8000); // Keep last 8000 points
        }
        
        // Update visualization
        this.updateDonationHeatmap(this.heatmapData);
        
        // Show real-time indicator
        this.showRealtimeIndicator(donationData);
    }

    showRealtimeIndicator(donationData) {
        const indicator = document.createElement('div');
        indicator.className = 'realtime-donation-indicator';
        indicator.innerHTML = `
            <div class="indicator-content">
                <div class="pulse"></div>
                <span>New donation: $${donationData.amount}</span>
            </div>
        `;
        
        document.body.appendChild(indicator);
        
        setTimeout(() => {
            indicator.classList.add('show');
        }, 100);
        
        setTimeout(() => {
            indicator.remove();
        }, 3000);
    }

    // Performance optimization
    optimizeForPerformance() {
        // Reduce data density for better performance
        if (this.heatmapData.length > 5000) {
            // Sample data to reduce load
            const sampleRate = 5000 / this.heatmapData.length;
            this.heatmapData = this.heatmapData.filter(() => Math.random() < sampleRate);
        }
        
        // Update with optimized data
        this.updateDonationHeatmap(this.heatmapData);
    }

    destroy() {
        if (this.overlay) {
            this.overlay.setMap(null);
        }
        
        if (this.heatmapLayer) {
            this.heatmapLayer.setMap(null);
        }
        
        this.currentLayers = [];
        this.heatmapData = [];
    }
}

// Utility functions for heatmap configuration
class HeatmapControls {
    constructor(heatmapManager) {
        this.heatmapManager = heatmapManager;
        this.createControlPanel();
    }
    
    createControlPanel() {
        const controlPanel = document.createElement('div');
        controlPanel.className = 'heatmap-controls';
        controlPanel.innerHTML = `
            <div class="control-header">
                <h3>Heatmap Controls</h3>
            </div>
            <div class="control-group">
                <label>Display Mode:</label>
                <select id="heatmap-mode">
                    <option value="donation_amount">Donation Amount</option>
                    <option value="donation_frequency">Donation Frequency</option>
                    <option value="user_density">User Density</option>
                    <option value="impact_score">Impact Score</option>
                </select>
            </div>
            <div class="control-group">
                <label>Opacity: <span id="opacity-value">0.6</span></label>
                <input type="range" id="opacity-slider" min="0" max="1" step="0.1" value="0.6">
            </div>
            <div class="control-group">
                <label>Radius: <span id="radius-value">120</span>px</label>
                <input type="range" id="radius-slider" min="50" max="300" step="10" value="120">
            </div>
            <div class="control-actions">
                <button id="export-data">Export Data</button>
                <button id="reset-view">Reset View</button>
            </div>
        `;
        
        document.body.appendChild(controlPanel);
        this.attachEventListeners();
    }
    
    attachEventListeners() {
        document.getElementById('heatmap-mode').addEventListener('change', (e) => {
            this.heatmapManager.updateDonationHeatmap(
                this.heatmapManager.heatmapData, 
                e.target.value
            );
        });
        
        document.getElementById('opacity-slider').addEventListener('input', (e) => {
            const opacity = parseFloat(e.target.value);
            document.getElementById('opacity-value').textContent = opacity;
            this.heatmapManager.setLayerOpacity('heatmap-donation_amount', opacity);
        });
        
        document.getElementById('radius-slider').addEventListener('input', (e) => {
            const radius = parseInt(e.target.value);
            document.getElementById('radius-value').textContent = radius;
            // Update radius configuration
        });
        
        document.getElementById('export-data').addEventListener('click', () => {
            const data = this.heatmapManager.exportHeatmapData('csv');
            this.downloadData(data, 'heatmap-data.csv', 'text/csv');
        });
        
        document.getElementById('reset-view').addEventListener('click', () => {
            this.heatmapManager.map.setZoom(13);
            this.heatmapManager.map.setCenter({ lat: 37.7749, lng: -122.4194 });
        });
    }
    
    downloadData(data, filename, type) {
        const blob = new Blob([data], { type: type });
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = filename;
        link.click();
        URL.revokeObjectURL(url);
    }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { DonationHeatmapManager, HeatmapControls };
} else if (typeof window !== 'undefined') {
    window.DonationHeatmapManager = DonationHeatmapManager;
    window.HeatmapControls = HeatmapControls;
}