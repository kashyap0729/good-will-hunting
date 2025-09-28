/**
 * Geofencing and Location-Based Rewards System
 * Pokemon Go-style location tracking and proximity rewards
 */

class GeofencingRewardSystem {
    constructor() {
        this.map = null;
        this.geofences = new Map();
        this.userRewards = new Map();
        this.userLocation = null;
        this.trackingInterval = null;
        this.proximityThreshold = 50; // meters
        
        // Reward multipliers by zone type
        this.zoneMultipliers = {
            'hotspot': 2.0,
            'community': 1.5,
            'business': 1.3,
            'residential': 1.0,
            'special_event': 3.0
        };
    }

    setMap(map) {
        this.map = map;
    }

    createDonationHotspot(center, radius, config = {}) {
        const hotspotId = config.id || `hotspot_${Date.now()}`;
        
        // Default configuration
        const defaultConfig = {
            type: 'hotspot',
            rewardMultiplier: 2.0,
            name: 'Donation Hotspot',
            description: 'High-impact donation area',
            color: '#FF4444',
            pulseAnimation: true,
            entryBonus: 100,
            proximityBonus: 50
        };
        
        const hotspotConfig = { ...defaultConfig, ...config };
        
        // Create visual representation with animated circles
        const outerCircle = new google.maps.Circle({
            strokeColor: hotspotConfig.color,
            strokeOpacity: 0.8,
            strokeWeight: 2,
            fillColor: hotspotConfig.color,
            fillOpacity: 0.15,
            map: this.map,
            center: center,
            radius: radius,
            clickable: true
        });

        const innerCircle = new google.maps.Circle({
            strokeColor: hotspotConfig.color,
            strokeOpacity: 0,
            fillColor: hotspotConfig.color,
            fillOpacity: 0.35,
            map: this.map,
            center: center,
            radius: radius * 0.6,
            clickable: false
        });

        // Add pulsing animation if enabled
        if (hotspotConfig.pulseAnimation) {
            this.animateCirclePulse(innerCircle, radius * 0.6, radius * 0.8);
        }

        // Add info window
        const infoWindow = new google.maps.InfoWindow({
            content: this.createHotspotInfoContent(hotspotConfig),
            position: center
        });

        // Click handler for outer circle
        outerCircle.addListener('click', () => {
            infoWindow.open(this.map);
        });

        // Create geofence object
        const geofence = {
            id: hotspotId,
            center: center,
            radius: radius,
            config: hotspotConfig,
            visualElements: {
                outer: outerCircle,
                inner: innerCircle,
                infoWindow: infoWindow
            },
            active: true,
            enteredUsers: new Set(),
            onEnter: (userId, location) => this.handleHotspotEntry(userId, hotspotId, location),
            onExit: (userId, location) => this.handleHotspotExit(userId, hotspotId, location),
            onProximity: (userId, distance) => this.handleProximityReward(userId, hotspotId, distance)
        };

        this.geofences.set(hotspotId, geofence);
        console.log(`Created hotspot: ${hotspotId} at (${center.lat}, ${center.lng})`);
        
        return geofence;
    }

    createHotspotInfoContent(config) {
        return `
            <div class="hotspot-info pokemon-style">
                <div class="hotspot-header">
                    <h3>${config.name}</h3>
                    <span class="hotspot-type">${config.type.toUpperCase()}</span>
                </div>
                <div class="hotspot-details">
                    <p>${config.description}</p>
                    <div class="reward-info">
                        <div class="multiplier">
                            <span class="label">Points Multiplier:</span>
                            <span class="value">${config.rewardMultiplier}x</span>
                        </div>
                        <div class="entry-bonus">
                            <span class="label">Entry Bonus:</span>
                            <span class="value">+${config.entryBonus} points</span>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    animateCirclePulse(circle, minRadius, maxRadius) {
        let growing = true;
        let currentRadius = minRadius;
        const step = (maxRadius - minRadius) / 30; // 30 steps for smooth animation
        
        const animate = () => {
            if (growing) {
                currentRadius += step;
                if (currentRadius >= maxRadius) {
                    growing = false;
                }
            } else {
                currentRadius -= step;
                if (currentRadius <= minRadius) {
                    growing = true;
                }
            }
            
            circle.setRadius(currentRadius);
            
            // Continue animation
            setTimeout(animate, 50); // 20 FPS
        };
        
        animate();
    }

    startTracking(userLocation) {
        this.userLocation = userLocation;
        
        // Check geofences immediately
        this.checkGeofences();
        
        // Start continuous tracking
        this.trackingInterval = setInterval(() => {
            this.checkGeofences();
        }, 5000); // Check every 5 seconds
        
        console.log('Geofencing tracking started');
    }

    updateUserLocation(newLocation) {
        const oldLocation = this.userLocation;
        this.userLocation = newLocation;
        
        // Immediate geofence check on location change
        if (this.distanceBetween(oldLocation, newLocation) > 10) { // Moved more than 10 meters
            this.checkGeofences();
        }
    }

    checkGeofences() {
        if (!this.userLocation) return;
        
        for (const [geofenceId, geofence] of this.geofences) {
            if (!geofence.active) continue;
            
            const distance = this.distanceBetween(this.userLocation, geofence.center);
            const isInside = distance <= geofence.radius;
            const wasInside = geofence.enteredUsers.has('current_user');
            
            // Handle entry
            if (isInside && !wasInside) {
                geofence.enteredUsers.add('current_user');
                geofence.onEnter('current_user', this.userLocation);
            }
            
            // Handle exit
            if (!isInside && wasInside) {
                geofence.enteredUsers.delete('current_user');
                geofence.onExit('current_user', this.userLocation);
            }
            
            // Handle proximity rewards (within hotspot but not at center)
            if (isInside && distance > 0) {
                geofence.onProximity('current_user', distance);
            }
        }
    }

    async handleHotspotEntry(userId, hotspotId, location) {
        const geofence = this.geofences.get(hotspotId);
        const config = geofence.config;
        
        console.log(`User entered hotspot: ${hotspotId}`);
        
        // Award entry achievement
        const achievement = {
            type: 'location_discovery',
            name: 'Hotspot Hunter',
            description: `Discovered: ${config.name}`,
            points: config.entryBonus,
            multiplier: config.rewardMultiplier,
            timestamp: new Date(),
            location: location
        };

        // Send to backend
        await this.awardAchievement(userId, achievement);

        // Show AR-style notification
        this.showARNotification(
            '🔥 Hotspot Discovered!', 
            `${config.name}\n+${config.entryBonus} points\n${config.rewardMultiplier}x multiplier active`
        );

        // Activate multiplier for future donations in this area
        this.activateLocationMultiplier(userId, hotspotId, config.rewardMultiplier);
    }

    async handleHotspotExit(userId, hotspotId, location) {
        const geofence = this.geofences.get(hotspotId);
        console.log(`User exited hotspot: ${hotspotId}`);
        
        // Deactivate location multiplier
        this.deactivateLocationMultiplier(userId, hotspotId);
        
        // Show exit notification
        this.showExitNotification(geofence.config.name);
    }

    async handleProximityReward(userId, hotspotId, distance) {
        const geofence = this.geofences.get(hotspotId);
        const config = geofence.config;
        
        // Calculate proximity bonus (closer = more bonus)
        const proximityRatio = 1 - (distance / geofence.radius);
        const proximityBonus = Math.floor(config.proximityBonus * proximityRatio);
        
        // Award proximity bonus every minute (prevent spam)
        const lastProximityReward = this.userRewards.get(`${userId}_${hotspotId}_proximity`);
        const now = Date.now();
        
        if (!lastProximityReward || (now - lastProximityReward) > 60000) { // 1 minute cooldown
            this.userRewards.set(`${userId}_${hotspotId}_proximity`, now);
            
            if (proximityBonus > 0) {
                await this.awardProximityBonus(userId, proximityBonus, distance);
            }
        }
    }

    activateLocationMultiplier(userId, hotspotId, multiplier) {
        const activeMultipliers = this.userRewards.get(`${userId}_multipliers`) || {};
        activeMultipliers[hotspotId] = multiplier;
        this.userRewards.set(`${userId}_multipliers`, activeMultipliers);
        
        // Update UI to show active multipliers
        this.updateMultiplierDisplay(activeMultipliers);
    }

    deactivateLocationMultiplier(userId, hotspotId) {
        const activeMultipliers = this.userRewards.get(`${userId}_multipliers`) || {};
        delete activeMultipliers[hotspotId];
        this.userRewards.set(`${userId}_multipliers`, activeMultipliers);
        
        this.updateMultiplierDisplay(activeMultipliers);
    }

    updateMultiplierDisplay(activeMultipliers) {
        const maxMultiplier = Math.max(...Object.values(activeMultipliers), 1.0);
        
        // Update multiplier indicator in UI
        const multiplierDisplay = document.querySelector('.multiplier-display');
        if (multiplierDisplay) {
            multiplierDisplay.textContent = `${maxMultiplier.toFixed(1)}x`;
            multiplierDisplay.className = `multiplier-display ${maxMultiplier > 1 ? 'active' : ''}`;
        }
    }

    showARNotification(title, message) {
        const notification = document.createElement('div');
        notification.className = 'ar-notification pokemon-style';
        notification.innerHTML = `
            <div class="notification-content">
                <div class="notification-icon">🎯</div>
                <h3>${title}</h3>
                <p>${message.replace(/\n/g, '<br>')}</p>
                <div class="sparkle-effect"></div>
                <div class="notification-timer"></div>
            </div>
        `;
        
        document.body.appendChild(notification);
        
        // Add entrance animation
        setTimeout(() => notification.classList.add('show'), 100);
        
        // Add sparkle effects
        this.addSparkleEffects(notification.querySelector('.sparkle-effect'));
        
        // Progress timer
        this.animateTimer(notification.querySelector('.notification-timer'), 4000);
        
        // Remove after animation
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => notification.remove(), 300);
        }, 4000);
    }

    showExitNotification(locationName) {
        const notification = document.createElement('div');
        notification.className = 'exit-notification pokemon-style';
        notification.innerHTML = `
            <div class="exit-content">
                <div class="exit-icon">👋</div>
                <p>Left ${locationName}</p>
                <span class="multiplier-off">Multiplier deactivated</span>
            </div>
        `;
        
        document.body.appendChild(notification);
        setTimeout(() => notification.classList.add('show'), 100);
        setTimeout(() => notification.remove(), 2000);
    }

    addSparkleEffects(container) {
        for (let i = 0; i < 15; i++) {
            const sparkle = document.createElement('div');
            sparkle.className = 'sparkle';
            sparkle.style.left = Math.random() * 100 + '%';
            sparkle.style.top = Math.random() * 100 + '%';
            sparkle.style.animationDelay = Math.random() * 2 + 's';
            container.appendChild(sparkle);
        }
    }

    animateTimer(timerElement, duration) {
        timerElement.style.width = '100%';
        timerElement.style.transition = `width ${duration}ms linear`;
        
        setTimeout(() => {
            timerElement.style.width = '0%';
        }, 50);
    }

    async awardAchievement(userId, achievement) {
        try {
            const response = await fetch('/api/v1/achievements/location', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.getAuthToken()}`
                },
                body: JSON.stringify({
                    user_id: userId,
                    achievement: achievement
                })
            });
            
            const result = await response.json();
            
            if (result.success) {
                console.log('Location achievement awarded:', achievement.name);
            }
            
        } catch (error) {
            console.error('Error awarding achievement:', error);
        }
    }

    async awardProximityBonus(userId, bonus, distance) {
        try {
            const response = await fetch('/api/v1/points/proximity', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.getAuthToken()}`
                },
                body: JSON.stringify({
                    user_id: userId,
                    points: bonus,
                    distance: distance,
                    source: 'proximity_bonus'
                })
            });
            
            const result = await response.json();
            
            if (result.success) {
                // Show mini notification
                this.showMiniNotification(`+${bonus} proximity bonus!`);
            }
            
        } catch (error) {
            console.error('Error awarding proximity bonus:', error);
        }
    }

    showMiniNotification(message) {
        const mini = document.createElement('div');
        mini.className = 'mini-notification';
        mini.textContent = message;
        
        document.body.appendChild(mini);
        setTimeout(() => mini.classList.add('show'), 50);
        setTimeout(() => mini.remove(), 2000);
    }

    distanceBetween(pos1, pos2) {
        const R = 6371e3; // Earth's radius in meters
        const φ1 = pos1.lat * Math.PI/180;
        const φ2 = pos2.lat * Math.PI/180;
        const Δφ = (pos2.lat-pos1.lat) * Math.PI/180;
        const Δλ = (pos2.lng-pos1.lng) * Math.PI/180;

        const a = Math.sin(Δφ/2) * Math.sin(Δφ/2) +
                Math.cos(φ1) * Math.cos(φ2) *
                Math.sin(Δλ/2) * Math.sin(Δλ/2);
        const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));

        return R * c; // Distance in meters
    }

    getAuthToken() {
        return localStorage.getItem('authToken') || 'demo-token';
    }

    stopTracking() {
        if (this.trackingInterval) {
            clearInterval(this.trackingInterval);
            this.trackingInterval = null;
            console.log('Geofencing tracking stopped');
        }
    }

    // Special event zones (temporary hotspots)
    createSpecialEventZone(center, radius, eventConfig) {
        const eventId = `event_${Date.now()}`;
        
        const specialConfig = {
            ...eventConfig,
            type: 'special_event',
            rewardMultiplier: eventConfig.multiplier || 3.0,
            color: '#9C27B0', // Purple for special events
            pulseAnimation: true,
            entryBonus: eventConfig.entryBonus || 500
        };
        
        const geofence = this.createDonationHotspot(center, radius, {
            id: eventId,
            ...specialConfig
        });
        
        // Auto-remove after event duration
        if (eventConfig.duration) {
            setTimeout(() => {
                this.removeGeofence(eventId);
            }, eventConfig.duration);
        }
        
        return geofence;
    }

    removeGeofence(geofenceId) {
        const geofence = this.geofences.get(geofenceId);
        if (geofence) {
            // Remove visual elements
            geofence.visualElements.outer.setMap(null);
            geofence.visualElements.inner.setMap(null);
            geofence.visualElements.infoWindow.close();
            
            // Remove from tracking
            this.geofences.delete(geofenceId);
            
            console.log(`Removed geofence: ${geofenceId}`);
        }
    }

    // Get user's current active multipliers
    getCurrentMultipliers(userId) {
        return this.userRewards.get(`${userId}_multipliers`) || {};
    }

    // Get the highest active multiplier
    getMaxActiveMultiplier(userId) {
        const multipliers = this.getCurrentMultipliers(userId);
        return Math.max(...Object.values(multipliers), 1.0);
    }
}

// Achievement System integration
class AchievementSystem {
    constructor() {
        this.locationAchievements = {
            'first_hotspot': {
                name: 'Hotspot Hunter',
                description: 'Entered your first donation hotspot',
                points: 100,
                emoji: '🎯'
            },
            'hotspot_master': {
                name: 'Hotspot Master',
                description: 'Visited 10 different hotspots',
                points: 1000,
                emoji: '🏆'
            },
            'neighborhood_explorer': {
                name: 'Neighborhood Explorer',
                description: 'Donated in 5 different neighborhoods',
                points: 500,
                emoji: '🗺️'
            },
            'proximity_champion': {
                name: 'Proximity Champion',
                description: 'Earned 100 proximity bonuses',
                points: 750,
                emoji: '📍'
            }
        };
    }

    checkLocationAchievements(userStats, newLocation) {
        const unlockedAchievements = [];
        
        // Check various location-based achievements
        if (userStats.hotspots_visited === 1) {
            unlockedAchievements.push(this.locationAchievements.first_hotspot);
        }
        
        if (userStats.hotspots_visited === 10) {
            unlockedAchievements.push(this.locationAchievements.hotspot_master);
        }
        
        if (userStats.unique_neighborhoods === 5) {
            unlockedAchievements.push(this.locationAchievements.neighborhood_explorer);
        }
        
        if (userStats.proximity_bonuses === 100) {
            unlockedAchievements.push(this.locationAchievements.proximity_champion);
        }
        
        return unlockedAchievements;
    }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { GeofencingRewardSystem, AchievementSystem };
} else if (typeof window !== 'undefined') {
    window.GeofencingRewardSystem = GeofencingRewardSystem;
    window.AchievementSystem = AchievementSystem;
}