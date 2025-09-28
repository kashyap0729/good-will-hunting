/**
 * Gamified Map Manager
 * Pokemon Go-style donation mapping with advanced markers, geofencing, and rewards
 */

class GamifiedMapManager {
    constructor(mapId, apiKey) {
        this.mapId = mapId;
        this.apiKey = apiKey;
        this.map = null;
        this.markers = new Map();
        this.userLocation = null;
        this.achievementManager = new AchievementSystem();
        this.geofencingSystem = new GeofencingRewardSystem();
        this.heatmapManager = null;
        
        // Initialize map styles
        this.pokemonGoStyle = this.getPokemonGoMapStyle();
        
        this.initializeMap();
    }

    async initializeMap() {
        try {
            // Load Google Maps libraries
            const { Map } = await google.maps.importLibrary("maps");
            const { AdvancedMarkerElement, PinElement } = await google.maps.importLibrary("marker");
            
            // Create map with Pokemon Go styling
            this.map = new Map(document.getElementById('map'), {
                center: { lat: 37.7749, lng: -122.4194 }, // San Francisco default
                zoom: 13,
                mapId: this.mapId,
                mapTypeId: 'roadmap',
                styles: this.pokemonGoStyle,
                gestureHandling: 'greedy',
                zoomControl: true,
                mapTypeControl: false,
                streetViewControl: false,
                fullscreenControl: true
            });

            // Initialize subsystems
            this.geofencingSystem.setMap(this.map);
            this.heatmapManager = new DonationHeatmapManager(this.map);
            
            // Setup user location tracking
            await this.setupLocationTracking();
            
            // Load initial donation hotspots
            await this.loadDonationHotspots();
            
            console.log('Gamified map initialized successfully');
            
        } catch (error) {
            console.error('Error initializing map:', error);
        }
    }

    async setupLocationTracking() {
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(
                (position) => {
                    this.userLocation = {
                        lat: position.coords.latitude,
                        lng: position.coords.longitude
                    };
                    
                    // Center map on user location
                    this.map.setCenter(this.userLocation);
                    
                    // Add user location marker
                    this.addUserLocationMarker();
                    
                    // Start geofencing
                    this.geofencingSystem.startTracking(this.userLocation);
                },
                (error) => {
                    console.warn('Geolocation error:', error);
                },
                { 
                    enableHighAccuracy: true,
                    timeout: 10000,
                    maximumAge: 300000 // 5 minutes
                }
            );

            // Watch position for real-time updates
            navigator.geolocation.watchPosition(
                (position) => {
                    this.userLocation = {
                        lat: position.coords.latitude,
                        lng: position.coords.longitude
                    };
                    this.geofencingSystem.updateUserLocation(this.userLocation);
                }
            );
        }
    }

    async addUserLocationMarker() {
        const { AdvancedMarkerElement, PinElement } = await google.maps.importLibrary("marker");
        
        const userPin = new PinElement({
            background: '#4285F4',
            borderColor: '#FFFFFF',
            scale: 1.2,
            glyph: '👤'
        });

        const userMarker = new AdvancedMarkerElement({
            map: this.map,
            position: this.userLocation,
            content: userPin.element,
            title: "Your Location",
            zIndex: 10000
        });

        return userMarker;
    }

    async createGymLeaderPin(location, donationData) {
        const { AdvancedMarkerElement, PinElement } = await google.maps.importLibrary("marker");
        
        // Create animated gym leader marker with tier-based styling
        const pinElement = new PinElement({
            scale: donationData.isTopDonor ? 2.2 : 1.8,
            background: this.getTierColor(donationData.tier),
            borderColor: '#FFFFFF',
            borderWidth: 3,
            glyphColor: '#FFFFFF',
            glyph: this.getTierEmoji(donationData.tier)
        });

        // Create custom marker content with Pokemon Go styling
        const markerContent = this.createCustomMarkerContent(donationData);

        const marker = new AdvancedMarkerElement({
            map: this.map,
            position: location,
            content: markerContent,
            title: `${donationData.organizationName} - Level ${donationData.level}`,
            zIndex: donationData.isTopDonor ? 1000 : 100
        });

        // Add pulsing animation for top donors
        if (donationData.isTopDonor) {
            this.addPulsingAnimation(markerContent);
        }

        // Interactive features
        marker.addListener('click', () => {
            this.handleDonationInteraction(marker, donationData);
        });

        // Store marker reference
        this.markers.set(donationData.id, marker);

        return marker;
    }

    createCustomMarkerContent(donationData) {
        const container = document.createElement('div');
        container.className = 'gym-leader-marker';
        container.innerHTML = `
            <div class="marker-container ${donationData.tier.toLowerCase()}" data-tier="${donationData.tier}">
                <div class="marker-level">Lv.${donationData.level}</div>
                <div class="marker-icon">${this.getTierEmoji(donationData.tier)}</div>
                <div class="marker-points">+${donationData.points}</div>
                <div class="marker-name">${donationData.organizationName}</div>
                ${donationData.hasBonus ? '<div class="bonus-indicator">2X</div>' : ''}
                ${donationData.isHotspot ? '<div class="hotspot-indicator">🔥</div>' : ''}
                <div class="marker-pulse ${donationData.isTopDonor ? 'active' : ''}"></div>
            </div>
        `;
        
        return container;
    }

    getTierColor(tier) {
        const colors = {
            'Bronze': '#CD7F32',
            'Silver': '#C0C0C0', 
            'Gold': '#FFD700',
            'Platinum': '#E5E4E2',
            'Diamond': '#B9F2FF'
        };
        return colors[tier] || '#FF6B35';
    }

    getTierEmoji(tier) {
        const emojis = {
            'Bronze': '🥉',
            'Silver': '🥈',
            'Gold': '🥇',
            'Platinum': '💎',
            'Diamond': '💠'
        };
        return emojis[tier] || '🎁';
    }

    addPulsingAnimation(element) {
        element.classList.add('pulsing-marker');
        
        // CSS animation will be defined in stylesheet
        const style = document.createElement('style');
        style.textContent = `
            @keyframes pulse {
                0% { transform: scale(1); opacity: 1; }
                50% { transform: scale(1.1); opacity: 0.8; }
                100% { transform: scale(1); opacity: 1; }
            }
            
            .pulsing-marker {
                animation: pulse 2s infinite ease-in-out;
            }
        `;
        document.head.appendChild(style);
    }

    async handleDonationInteraction(marker, donationData) {
        // Create Pokemon Go-style info popup
        const infoContent = this.createInfoPopup(donationData);
        
        // Show donation interface
        this.showDonationInterface(donationData);
        
        // Track interaction
        await this.trackInteraction('marker_click', donationData);
    }

    createInfoPopup(donationData) {
        return `
            <div class="pokemon-style-info">
                <div class="info-header">
                    <h3>${donationData.organizationName}</h3>
                    <span class="tier-badge ${donationData.tier.toLowerCase()}">${donationData.tier}</span>
                </div>
                <div class="info-stats">
                    <div class="stat">
                        <span class="label">Level:</span>
                        <span class="value">${donationData.level}</span>
                    </div>
                    <div class="stat">
                        <span class="label">Points:</span>
                        <span class="value">+${donationData.points}</span>
                    </div>
                    <div class="stat">
                        <span class="label">Items Needed:</span>
                        <span class="value">${donationData.itemsNeeded.join(', ')}</span>
                    </div>
                </div>
                <div class="info-actions">
                    <button class="donate-btn" onclick="openDonationModal('${donationData.id}')">
                        Donate Now 🎁
                    </button>
                    <button class="directions-btn" onclick="getDirections(${donationData.location.lat}, ${donationData.location.lng})">
                        Get Directions 🗺️
                    </button>
                </div>
            </div>
        `;
    }

    showDonationInterface(donationData) {
        // Create modal interface for donations
        const modal = document.createElement('div');
        modal.className = 'donation-modal pokemon-style';
        modal.innerHTML = `
            <div class="modal-content">
                <div class="modal-header">
                    <h2>${donationData.organizationName}</h2>
                    <button class="close-btn" onclick="this.closest('.donation-modal').remove()">&times;</button>
                </div>
                <div class="modal-body">
                    <div class="organization-info">
                        <img src="${donationData.image}" alt="${donationData.organizationName}" class="org-image">
                        <div class="org-details">
                            <p class="description">${donationData.description}</p>
                            <div class="needs-list">
                                <h4>Items Currently Needed:</h4>
                                <ul>
                                    ${donationData.itemsNeeded.map(item => `<li>${item}</li>`).join('')}
                                </ul>
                            </div>
                        </div>
                    </div>
                    <div class="donation-form">
                        <h3>Make a Donation</h3>
                        <form id="donationForm">
                            <div class="donation-type-selector">
                                <label>
                                    <input type="radio" name="donationType" value="monetary" checked>
                                    <span class="radio-custom">💰 Monetary</span>
                                </label>
                                <label>
                                    <input type="radio" name="donationType" value="items">
                                    <span class="radio-custom">📦 Items</span>
                                </label>
                            </div>
                            <div class="amount-input">
                                <label for="amount">Amount ($):</label>
                                <input type="number" id="amount" name="amount" min="1" step="0.01" required>
                            </div>
                            <button type="submit" class="submit-donation">
                                Donate & Earn Points! ⭐
                            </button>
                        </form>
                    </div>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        // Setup form handler
        document.getElementById('donationForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            await this.processDonation(donationData, new FormData(e.target));
            modal.remove();
        });
    }

    async processDonation(donationData, formData) {
        try {
            const donationType = formData.get('donationType');
            const amount = parseFloat(formData.get('amount'));
            
            // Show processing animation
            this.showProcessingAnimation();
            
            // Submit donation to API
            const response = await fetch('/api/v1/donations', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.getAuthToken()}`
                },
                body: JSON.stringify({
                    amount: amount,
                    donation_type: donationType,
                    charity_id: donationData.id,
                    location: donationData.location
                })
            });
            
            const result = await response.json();
            
            if (result.success) {
                // Show success animation with points
                this.showSuccessAnimation(result.points);
                
                // Update marker to show recent donation
                this.updateMarkerAfterDonation(donationData.id);
                
                // Check for location-based achievements
                await this.checkLocationAchievements(donationData.location);
                
            } else {
                this.showErrorMessage('Donation failed. Please try again.');
            }
            
        } catch (error) {
            console.error('Donation processing error:', error);
            this.showErrorMessage('Network error. Please check your connection.');
        }
    }

    showProcessingAnimation() {
        const processingOverlay = document.createElement('div');
        processingOverlay.className = 'processing-overlay';
        processingOverlay.innerHTML = `
            <div class="processing-content">
                <div class="pokeball-spinner"></div>
                <p>Processing your donation...</p>
            </div>
        `;
        document.body.appendChild(processingOverlay);
        
        // Remove after 2 seconds
        setTimeout(() => {
            processingOverlay.remove();
        }, 2000);
    }

    showSuccessAnimation(pointsData) {
        const successOverlay = document.createElement('div');
        successOverlay.className = 'success-overlay pokemon-style';
        successOverlay.innerHTML = `
            <div class="success-content">
                <div class="success-icon">🎉</div>
                <h2>Donation Successful!</h2>
                <div class="points-earned">
                    <span class="points-text">+${pointsData.points_awarded} Points!</span>
                    ${pointsData.new_tier ? `<div class="tier-up">Tier Up! ${pointsData.new_tier} 🏆</div>` : ''}
                </div>
                <div class="sparkle-effects"></div>
            </div>
        `;
        document.body.appendChild(successOverlay);
        
        // Add sparkle effects
        this.createSparkleEffect(successOverlay);
        
        // Remove after 3 seconds
        setTimeout(() => {
            successOverlay.remove();
        }, 3000);
    }

    createSparkleEffect(container) {
        const sparkles = container.querySelector('.sparkle-effects');
        
        for (let i = 0; i < 20; i++) {
            const sparkle = document.createElement('div');
            sparkle.className = 'sparkle';
            sparkle.style.left = Math.random() * 100 + '%';
            sparkle.style.animationDelay = Math.random() * 2 + 's';
            sparkles.appendChild(sparkle);
        }
    }

    async loadDonationHotspots() {
        try {
            // Fetch hotspots from API
            const response = await fetch('/api/v1/hotspots/nearby', {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${this.getAuthToken()}`
                }
            });
            
            const hotspots = await response.json();
            
            if (hotspots.success) {
                // Create markers for each hotspot
                for (const hotspot of hotspots.data) {
                    await this.createGymLeaderPin(hotspot.location, hotspot);
                }
                
                // Update heatmap
                this.heatmapManager.updateDonationHeatmap(hotspots.data);
            }
            
        } catch (error) {
            console.error('Error loading hotspots:', error);
        }
    }

    async trackInteraction(type, data) {
        try {
            await fetch('/api/v1/analytics/interaction', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.getAuthToken()}`
                },
                body: JSON.stringify({
                    type: type,
                    data: data,
                    timestamp: new Date().toISOString(),
                    user_location: this.userLocation
                })
            });
        } catch (error) {
            console.error('Error tracking interaction:', error);
        }
    }

    getPokemonGoMapStyle() {
        return [
            {
                "featureType": "all",
                "elementType": "geometry.fill",
                "stylers": [{"saturation": -40}, {"lightness": 25}]
            },
            {
                "featureType": "all",
                "elementType": "labels.text.fill",
                "stylers": [{"saturation": 36}, {"color": "#000000"}, {"lightness": 40}]
            },
            {
                "featureType": "all",
                "elementType": "labels.text.stroke",
                "stylers": [{"visibility": "on"}, {"color": "#000000"}, {"lightness": 16}]
            },
            {
                "featureType": "all",
                "elementType": "labels.icon",
                "stylers": [{"visibility": "off"}]
            },
            {
                "featureType": "administrative",
                "elementType": "geometry.fill",
                "stylers": [{"color": "#000000"}, {"lightness": 20}]
            },
            {
                "featureType": "water",
                "elementType": "geometry",
                "stylers": [{"color": "#4A90E2"}, {"lightness": 17}]
            },
            {
                "featureType": "landscape",
                "elementType": "geometry",
                "stylers": [{"color": "#2ECC71"}, {"lightness": 20}]
            },
            {
                "featureType": "road.highway",
                "elementType": "geometry.fill",
                "stylers": [{"color": "#F39C12"}, {"lightness": 17}]
            },
            {
                "featureType": "road.arterial",
                "elementType": "geometry",
                "stylers": [{"color": "#E74C3C"}, {"lightness": 18}]
            }
        ];
    }

    getAuthToken() {
        // In production, get from secure storage
        return localStorage.getItem('authToken') || 'demo-token';
    }

    updateMarkerAfterDonation(markerId) {
        const marker = this.markers.get(markerId);
        if (marker) {
            // Add visual indication of recent donation
            const markerElement = marker.content;
            markerElement.classList.add('recent-donation');
            
            // Remove indicator after 30 seconds
            setTimeout(() => {
                markerElement.classList.remove('recent-donation');
            }, 30000);
        }
    }

    async checkLocationAchievements(location) {
        try {
            const response = await fetch('/api/v1/achievements/location-check', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.getAuthToken()}`
                },
                body: JSON.stringify({
                    location: location,
                    user_location: this.userLocation
                })
            });
            
            const result = await response.json();
            
            if (result.success && result.achievements.length > 0) {
                this.showAchievementNotifications(result.achievements);
            }
            
        } catch (error) {
            console.error('Error checking location achievements:', error);
        }
    }

    showAchievementNotifications(achievements) {
        achievements.forEach((achievement, index) => {
            setTimeout(() => {
                const notification = document.createElement('div');
                notification.className = 'achievement-notification pokemon-style';
                notification.innerHTML = `
                    <div class="achievement-content">
                        <div class="achievement-icon">${achievement.emoji}</div>
                        <div class="achievement-text">
                            <h3>Achievement Unlocked!</h3>
                            <p>${achievement.name}</p>
                            <span class="points">+${achievement.points} points</span>
                        </div>
                    </div>
                `;
                
                document.body.appendChild(notification);
                
                // Show animation
                setTimeout(() => notification.classList.add('show'), 100);
                
                // Remove after 4 seconds
                setTimeout(() => {
                    notification.classList.remove('show');
                    setTimeout(() => notification.remove(), 300);
                }, 4000);
                
            }, index * 500); // Stagger multiple achievements
        });
    }

    showErrorMessage(message) {
        const errorOverlay = document.createElement('div');
        errorOverlay.className = 'error-overlay';
        errorOverlay.innerHTML = `
            <div class="error-content">
                <div class="error-icon">⚠️</div>
                <p>${message}</p>
                <button onclick="this.closest('.error-overlay').remove()">OK</button>
            </div>
        `;
        document.body.appendChild(errorOverlay);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (errorOverlay.parentNode) {
                errorOverlay.remove();
            }
        }, 5000);
    }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = GamifiedMapManager;
} else if (typeof window !== 'undefined') {
    window.GamifiedMapManager = GamifiedMapManager;
}