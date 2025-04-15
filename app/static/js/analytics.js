// Add loading overlay
const loadingOverlay = document.createElement('div');
loadingOverlay.className = 'loading-overlay';
loadingOverlay.innerHTML = '<div class="loading-spinner"></div>';
document.body.appendChild(loadingOverlay);

// Show loading overlay
function showLoading() {
    loadingOverlay.classList.add('active');
}

// Hide loading overlay
function hideLoading() {
    loadingOverlay.classList.remove('active');
}

// Animate elements on scroll
function animateOnScroll() {
    const elements = document.querySelectorAll('.chart-container, .stats-card');
    elements.forEach(element => {
        const elementTop = element.getBoundingClientRect().top;
        const elementBottom = element.getBoundingClientRect().bottom;
        
        if (elementTop < window.innerHeight && elementBottom > 0) {
            element.classList.add('visible');
        }
    });
}

// Initialize timeline interactions
document.addEventListener('DOMContentLoaded', () => {
    const timelineSteps = document.querySelectorAll('.timeline-content');
    
    timelineSteps.forEach(step => {
        // Add click handler for expanding/collapsing
        step.addEventListener('click', (e) => {
            // Don't expand if clicking on a link or button inside the step
            if (e.target.tagName === 'A' || e.target.tagName === 'BUTTON') {
                return;
            }
            
            // Remove expanded class from all steps
            timelineSteps.forEach(s => {
                if (s !== step) {
                    s.classList.remove('expanded');
                }
            });
            
            // Toggle expanded class on clicked step
            step.classList.toggle('expanded');
            
            // Scroll the expanded step into view if needed
            if (step.classList.contains('expanded')) {
                step.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }
        });
        
        // Add hover effect for step details
        const stepDetails = step.querySelector('.step-details');
        if (stepDetails) {
            stepDetails.addEventListener('mouseenter', () => {
                if (!step.classList.contains('expanded')) {
                    stepDetails.style.backgroundColor = '#f8f9fa';
                }
            });
            
            stepDetails.addEventListener('mouseleave', () => {
                if (!step.classList.contains('expanded')) {
                    stepDetails.style.backgroundColor = 'transparent';
                }
            });
        }
    });
    
    // Optimize performance by debouncing scroll events
    let scrollTimeout;
    window.addEventListener('scroll', () => {
        clearTimeout(scrollTimeout);
        scrollTimeout = setTimeout(() => {
            animateOnScroll();
        }, 100);
    });
});

// Optimize data loading
function loadData() {
    showLoading();
    
    // Load all data in parallel
    Promise.all([
        fetch('/api/analytics/chart-data').then(r => r.json()),
        fetch('/api/analytics/stats').then(r => r.json()),
        fetch('/api/analytics/journeys').then(r => r.json())
    ])
    .then(([chartData, statsData, journeysData]) => {
        updateChart(chartData);
        updateStats(statsData);
        updateJourneys(journeysData);
        hideLoading();
    })
    .catch(error => {
        console.error('Error loading data:', error);
        hideLoading();
    });
}

// Optimize chart updates
function updateChart(data) {
    const chartContainer = document.querySelector('.chart-container');
    if (!chartContainer) return;
    
    // Use requestAnimationFrame for smooth animations
    requestAnimationFrame(() => {
        // Update chart data
        // ... existing chart update code ...
        
        // Add visible class for animation
        chartContainer.classList.add('visible');
    });
}

// Optimize stats updates
function updateStats(data) {
    const statsCards = document.querySelectorAll('.stats-card');
    if (!statsCards.length) return;
    
    // Use requestAnimationFrame for smooth animations
    requestAnimationFrame(() => {
        // Update stats data
        // ... existing stats update code ...
        
        // Add visible class for animation
        statsCards.forEach(card => {
            card.classList.add('visible');
        });
    });
}

document.addEventListener('DOMContentLoaded', function() {
    // Fetch chart data from the static JSON file
    fetch('/static/js/chart-data.json')
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            // Initialize charts once data is loaded
            initCharts(data);
        })
        .catch(error => {
            console.error('Error loading chart data from static file:', error);
            // Try fetching from API endpoint as fallback
            console.log('Trying API endpoint as fallback...');
            fetch('/api/analytics/chart-data')
                .then(response => response.json())
                .then(data => {
                    initCharts(data);
                })
                .catch(apiError => {
                    console.error('Error loading chart data from API:', apiError);
                    // Initialize with empty data if both fetches fail
                    initCharts({
                        upgrade: {labels: [], values: []},
                        cancel: {labels: [], values: []}
                    });
                });
        });
    
    // Function to initialize charts with the loaded data
    function initCharts(chartData) {
        // Create Upgrade Chart
        const upgradeCtx = document.getElementById('upgradeChart').getContext('2d');
        new Chart(upgradeCtx, {
            type: 'bar',
            data: {
                labels: chartData.upgrade.labels,
                datasets: [{
                    label: 'Upgrade Reasons',
                    data: chartData.upgrade.values,
                    backgroundColor: '#10B981',
                    borderColor: '#059669',
                    borderWidth: 1,
                    borderRadius: 4,
                    barThickness: 30
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: {
                            display: true,
                            color: 'rgba(0, 0, 0, 0.1)'
                        }
                    },
                    x: {
                        grid: {
                            display: false
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
        
        // Create Cancellation Chart
        const cancelCtx = document.getElementById('cancelChart').getContext('2d');
        new Chart(cancelCtx, {
            type: 'bar',
            data: {
                labels: chartData.cancel.labels,
                datasets: [{
                    label: 'Cancellation Reasons',
                    data: chartData.cancel.values,
                    backgroundColor: '#EF4444',
                    borderColor: '#DC2626',
                    borderWidth: 1,
                    borderRadius: 4,
                    barThickness: 30
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: {
                            display: true,
                            color: 'rgba(0, 0, 0, 0.1)'
                        }
                    },
                    x: {
                        grid: {
                            display: false
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
}); 