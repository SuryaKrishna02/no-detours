// static/js/app.js
document.addEventListener('DOMContentLoaded', function() {
    // DOM elements
    const travelForm = document.getElementById('travel-form');
    const userInput = document.getElementById('user-input');
    const submitBtn = document.getElementById('submit-btn');
    const resultsSection = document.getElementById('results');
    const loadingIndicator = document.getElementById('loading');
    const itineraryText = document.getElementById('itinerary-text');
    const packingText = document.getElementById('packing-text');
    const budgetText = document.getElementById('budget-text');
    const tabButtons = document.querySelectorAll('.tab-btn');
    const tabPanes = document.querySelectorAll('.tab-pane');
    
    // Debug mode to log events
    const DEBUG = true;
    
    function logDebug(message, data = null) {
        if (DEBUG) {
            if (data) {
                console.log(`[DEBUG] ${message}`, data);
            } else {
                console.log(`[DEBUG] ${message}`);
            }
        }
    }
    
    // Handle tab switching
    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            // Remove active class from all buttons and panes
            tabButtons.forEach(btn => btn.classList.remove('active'));
            tabPanes.forEach(pane => pane.classList.remove('active'));
            
            // Add active class to clicked button and corresponding pane
            button.classList.add('active');
            const tabId = button.getAttribute('data-tab') + '-content';
            document.getElementById(tabId).classList.add('active');
            
            logDebug(`Switched to tab: ${button.getAttribute('data-tab')}`);
        });
    });
    
    // Handle form submission
    travelForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const input = userInput.value.trim();
        if (!input) {
            alert('Please enter your travel plans!');
            return;
        }
        
        logDebug(`Processing input: ${input.substring(0, 50)}...`);
        
        // Show loading indicator
        resultsSection.style.display = 'block';
        loadingIndicator.style.display = 'flex';
        document.querySelector('.tabs').style.display = 'none';
        document.querySelector('.tab-content').style.display = 'none';
        
        // Disable submit button
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Creating Plan...';
        
        try {
            logDebug('Sending request to API');
            
            // Send request to API
            const response = await fetch('/api/plan', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ text: input })
            });
            
            logDebug(`API response status: ${response.status}`);
            
            let data;
            try {
                data = await response.json();
                logDebug('Parsed response data', data);
            } catch (parseError) {
                logDebug(`Error parsing JSON: ${parseError}`);
                throw new Error('Failed to parse response from server');
            }
            
            if (!response.ok || data.error) {
                throw new Error(data.error || 'Failed to generate travel plan');
            }
            
            // Display results (with fallbacks if any component is missing)
            itineraryText.innerHTML = formatContent(data.itinerary || 'No itinerary generated. Please try again with more specific details about your trip.');
            packingText.innerHTML = formatContent(data.packing_list || 'No packing list generated. Please try again with more specific details about your trip.');
            budgetText.innerHTML = formatContent(data.estimated_budget || 'No budget estimate generated. Please try again with more specific details about your trip.');
            
            // Hide loading, show tabs and content
            loadingIndicator.style.display = 'none';
            document.querySelector('.tabs').style.display = 'flex';
            document.querySelector('.tab-content').style.display = 'block';
            
            // Scroll to results
            resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
            
            logDebug('Successfully displayed results');
            
        } catch (error) {
            logDebug(`Error: ${error.message}`);
            console.error('Error:', error);
            
            // Display error in the itinerary section
            itineraryText.innerHTML = `<div class="error-message">
                <p><i class="fas fa-exclamation-triangle"></i> ${error.message || 'An error occurred while generating your travel plan.'}</p>
                <p>Please try again with more specific details about your destination, dates, and preferences.</p>
            </div>`;
            
            // Hide loading, show only the itinerary tab
            loadingIndicator.style.display = 'none';
            document.querySelector('.tabs').style.display = 'flex';
            document.querySelector('.tab-content').style.display = 'block';
            
            // Make sure the itinerary tab is active
            tabButtons.forEach(btn => btn.classList.remove('active'));
            tabPanes.forEach(pane => pane.classList.remove('active'));
            document.querySelector('[data-tab="itinerary"]').classList.add('active');
            document.getElementById('itinerary-content').classList.add('active');
            
            resultsSection.style.display = 'block';
            resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
        } finally {
            // Re-enable submit button
            submitBtn.disabled = false;
            submitBtn.innerHTML = '<i class="fas fa-paper-plane"></i> Create Travel Plan';
        }
    });
    
    // Function to format content with better styling
    function formatContent(text) {
        if (!text) return 'No content available.';
        
        logDebug(`Formatting content: ${text.substring(0, 50)}...`);
        
        // Convert plain text to HTML with some basic formatting
        let formatted = text
            // Convert newlines to <br>
            .replace(/\n/g, '<br>')
            // Bold headers (lines ending with : or starting with Day)
            .replace(/^(Day \d+:.*?)(<br>)/gm, '<strong>$1</strong>$2')
            .replace(/^(#+)\s+(.*?)(<br>)/gm, function(match, p1, p2) {
                const level = Math.min(p1.length, 6);
                return `<h${level}>${p2}</h${level}><br>`;
            })
            .replace(/(^|\<br\>)([^<>]+:)(\<br\>|$)/g, '$1<strong>$2</strong>$3')
            // Create lists
            .replace(/(\<br\>)- (.*?)(\<br\>|$)/g, '$1• $2$3')
            .replace(/(\<br\>)(\d+\.) (.*?)(\<br\>|$)/g, '$1<strong>$2</strong> $3$4');
        
        return formatted;
    }
    
    logDebug('NoDetours app initialized');
});