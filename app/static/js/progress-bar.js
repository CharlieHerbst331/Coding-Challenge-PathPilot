document.addEventListener('DOMContentLoaded', function() {
    // Initialize progress bars
    initProgressBars();
    
    // Set up modal functionality
    setupModal();
    
    // Setup collapsible summary card
    setupJourneySummaryCard();
    
    // Fix persona icons display
    fixPersonaIcons();
    
    // Adjust card heights
    adjustCardHeights();
});

/**
 * Initialize all progress bars on the page
 */
function initProgressBars() {
    const progressBars = document.querySelectorAll('.progress-bar');
    
    progressBars.forEach(bar => {
        const confidence = parseFloat(bar.getAttribute('data-confidence')) || 0;
        const prediction = bar.getAttribute('data-prediction') || '';
        
        // Set the color based on prediction type
        if (prediction === 'upgrade') {
            bar.classList.add('bg-green-500');
        } else if (prediction === 'cancel') {
            bar.classList.add('bg-red-500');
        } else {
            bar.classList.add('bg-yellow-500');
        }
        
        // Animate the width after a short delay
        setTimeout(() => {
            bar.style.width = `${confidence}%`;
        }, 300);
    });
}

/**
 * Fix persona icons to display side by side
 */
function fixPersonaIcons() {
    // Get all persona icon containers in the modal
    const personaContainer = document.querySelector('.bg-neutral-50.p-6.rounded-lg.text-center');
    
    if (personaContainer) {
        // Get the SVG icon elements
        const iconContainer = personaContainer.querySelector('.h-24.w-24');
        
        if (iconContainer) {
            // Clear the existing icon container
            const originalIconColor = iconContainer.classList[3]; // Store color class
            const originalTextColor = iconContainer.classList[4]; // Store text color class
            const originalSvg = iconContainer.innerHTML;
            
            // Parse the SVG to get the different paths
            const pathMatches = originalSvg.match(/<path[^>]*>/g);
            
            if (pathMatches && pathMatches.length > 1) {
                iconContainer.innerHTML = '';
                
                // Create separate circles for each icon
                const mainIconPath = pathMatches[0];
                const secondaryIconPath = pathMatches[1];
                
                // Create first icon (user)
                const firstIcon = document.createElement('div');
                firstIcon.className = `h-12 w-12 mx-1 ${originalIconColor} ${originalTextColor} rounded-full flex items-center justify-center`;
                firstIcon.innerHTML = `<svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">${mainIconPath}</svg>`;
                
                // Create second icon (status)
                const secondIcon = document.createElement('div');
                secondIcon.className = `h-12 w-12 mx-1 ${originalIconColor} ${originalTextColor} rounded-full flex items-center justify-center`;
                secondIcon.innerHTML = `<svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">${secondaryIconPath}</svg>`;
                
                // Create a container for both icons
                const iconGroup = document.createElement('div');
                iconGroup.className = 'flex justify-center';
                iconGroup.appendChild(firstIcon);
                iconGroup.appendChild(secondIcon);
                
                // Replace the original container with the new layout
                iconContainer.parentNode.replaceChild(iconGroup, iconContainer);
            }
        }
    }
}

/**
 * Adjust heights of the cards to be shorter
 */
function adjustCardHeights() {
    // Journey Summary Card
    const summaryCar = document.querySelector('.col-span-2.bg-white.shadow.rounded-lg.p-6.fadeIn');
    const predictionCard = document.getElementById('prediction-card');
    
    if (summaryCar) {
        summaryCar.style.maxHeight = '440px';
        summaryCar.style.overflow = 'hidden';
    }
    
    if (predictionCard) {
        predictionCard.style.maxHeight = '440px'; 
        predictionCard.style.overflow = 'hidden';
        
        // Remove excess whitespace
        const paragraphElement = predictionCard.querySelector('p.text-xs.text-neutral-400.text-center.mt-2');
        if (paragraphElement) {
            paragraphElement.style.marginTop = '0';
            paragraphElement.style.marginBottom = '0';
        }
        
        // Adjust spacing in the prediction card
        const spaceDivs = predictionCard.querySelectorAll('.space-y-4');
        spaceDivs.forEach(div => {
            div.classList.remove('space-y-4');
            div.classList.add('space-y-3');
        });
    }
}

/**
 * Set up modal open/close functionality
 */
function setupModal() {
    // Modal elements
    const modal = document.getElementById('prediction-modal');
    
    // If the modal doesn't exist, don't proceed
    if (!modal) return;
}

/**
 * Set up the journey summary card to be expandable
 */
function setupJourneySummaryCard() {
    const summaryCard = document.querySelector('.col-span-2.bg-white.shadow.rounded-lg.p-6.fadeIn');
    
    if (summaryCard) {
        // Add expand icon
        const titleElement = summaryCard.querySelector('h2');
        
        if (titleElement) {
            // Create the expand icon
            const expandIcon = document.createElement('div');
            expandIcon.className = 'absolute top-3 right-3 text-neutral-400';
            expandIcon.innerHTML = `
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                </svg>
            `;
            
            // Make the card position relative
            summaryCard.style.position = 'relative';
            
            // Add cursor pointer to the entire card
            summaryCard.classList.add('cursor-pointer', 'hover:shadow-lg', 'transition-all', 'duration-300');
            
            // Add the expand icon to the card
            summaryCard.appendChild(expandIcon);
            
            // Add event listener for expanding the card
            summaryCard.addEventListener('click', function() {
                openSummaryModal();
            });
            
            // Create the modal for summary
            createSummaryModal();
            
            // Apply truncation to text content
            const textContainers = summaryCard.querySelectorAll('p, li');
            textContainers.forEach(container => {
                container.classList.add('truncate');
            });
        }
    }
}

/**
 * Create a modal for the summary card
 */
function createSummaryModal() {
    // Check if modal already exists
    if (document.getElementById('summary-modal')) {
        return;
    }
    
    // Get the original content
    const analysisContainer = document.getElementById('analysis-container');
    if (!analysisContainer) return;
    
    // Create the modal element
    const modal = document.createElement('div');
    modal.id = 'summary-modal';
    modal.className = 'fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center hidden fadeIn';
    
    // Create the modal content
    modal.innerHTML = `
        <div class="bg-white rounded-lg w-11/12 max-w-4xl h-5/6 overflow-y-auto relative">
            <button onclick="closeSummaryModal()" class="absolute top-4 right-4 text-neutral-500 hover:text-neutral-700">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
            </button>
            
            <div class="p-8">
                <h2 class="text-2xl font-bold mb-6">Journey Summary</h2>
                <div id="modal-analysis-container">
                    ${analysisContainer.innerHTML}
                </div>
            </div>
        </div>
    `;
    
    // Add the modal to the document
    document.body.appendChild(modal);
    
    // Remove truncation from text in the modal
    const textContainers = modal.querySelectorAll('p, li');
    textContainers.forEach(container => {
        container.classList.remove('truncate');
    });
}

/**
 * Open the summary modal
 */
function openSummaryModal() {
    const modal = document.getElementById('summary-modal');
    if (modal) {
        modal.classList.remove('hidden');
    }
}

/**
 * Close the summary modal
 */
function closeSummaryModal() {
    const modal = document.getElementById('summary-modal');
    if (modal) {
        modal.classList.add('hidden');
    }
}

/**
 * Open the prediction modal
 */
function openPredictionModal() {
    const modal = document.getElementById('prediction-modal');
    if (modal) {
        modal.classList.remove('hidden');
        
        // Initialize progress bars inside the modal
        const modalProgressBars = modal.querySelectorAll('.progress-bar');
        modalProgressBars.forEach(bar => {
            const confidence = parseFloat(bar.getAttribute('data-confidence')) || 0;
            const prediction = bar.getAttribute('data-prediction') || '';
            
            // Set the color based on prediction type
            if (prediction === 'upgrade') {
                bar.classList.add('bg-green-500');
            } else if (prediction === 'cancel') {
                bar.classList.add('bg-red-500');
            } else {
                bar.classList.add('bg-yellow-500');
            }
            
            // Animate the width
            setTimeout(() => {
                bar.style.width = `${confidence}%`;
            }, 300);
        });
    }
}

/**
 * Close the prediction modal
 */
function closePredictionModal() {
    const modal = document.getElementById('prediction-modal');
    if (modal) {
        modal.classList.add('hidden');
    }
} 