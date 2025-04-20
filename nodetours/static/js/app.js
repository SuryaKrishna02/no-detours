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
    
        // Detect content type
        const isItinerary = text.includes('Itinerary') || text.includes('Day 1:');
        const isPackingList = text.includes('List');
        const isBudget = text.includes('Budget');
    
        let formattedContent = '';
        if (isItinerary) {
            formattedContent = formatItinerary(text);
            
            
        } else if (isPackingList) {
            formattedContent = formatPackingList(text);
        } else if (isBudget) {
            formattedContent = formatBudget(text);
        } else {
            formattedContent = formatDefault(text);
        }
    
        // Styles — unified block
        const styles = `
        <style>
            .formatted-content h1, .formatted-content h2, .formatted-content h3 {
                color: #5a2a82;
                margin-top: 15px;
                margin-bottom: 10px;
                font-weight: 600;
            }
            .formatted-content h1 {
                font-size: 26px;
                border-bottom: 2px solid #5a2a82;
                padding-bottom: 8px;
                margin-bottom: 20px;
            }
            .formatted-content h2 {
                font-size: 22px;
                border-bottom: 1px solid rgba(90, 42, 130, 0.3);
                padding-bottom: 6px;
                margin-top: 25px;
            }
            .formatted-content h3 {
                font-size: 18px;
                color: #5a2a82;
                margin-top: 20px;
            }
            .formatted-content p, .formatted-content li, .formatted-content div {
                line-height: 1.6;
            }
            .formatted-content ul {
                padding-left: 20px;
            }
            .formatted-content strong {
                color: #5a2a82;
            }
    
            /* Itinerary */
            .day-section {
                margin-bottom: 25px;
                border-bottom: 1px solid #e0e0e0;
                padding-bottom: 15px;
            }
            .day-title {
                border-left: 4px solid #5a2a82;
                padding-left: 10px;
            }
            .time-block {
                margin: 15px 0 10px;
            }
            .activity-item {
                margin-left: 20px;
            }
    
            /* Packing List */
            .packing-category {
                font-size: 20px;
                border-bottom: 1px solid rgba(90, 42, 130, 0.3);
            }
            .packing-checkbox {
                margin-right: 10px;
            }
            .packing-note {
                font-style: italic;
                padding: 12px 15px;
                background-color: #f9f9f9;
                border-left: 3px solid #5a2a82;
            }
    
            /* Budget */
            .budget-title {
                font-size: 24px;
            }
            .budget-category {
                background-color: rgba(90, 42, 130, 0.05);
                padding: 15px;
            }
            .budget-item {
                display: flex;
                justify-content: space-between;
                border-bottom: 1px dashed #e0e0e0;
                padding: 8px 0;
            }
            .budget-note {
                font-style: italic;
            }
        </style>
        `;
    
        return `<div class="formatted-content">${styles}${formattedContent}</div>`;
    }
    

// Format itinerary content
function formatItinerary(text) {
    // Format the title
    let formatted = text.replace(/# (.*?)(?:\n|$)/, '<h1>$1</h1>');
    
    // Split the content into day sections
    const dayMatches = formatted.match(/## Day \d+:[\s\S]*?(?=## Day \d+:|$)/g) || [];
    
    if (dayMatches.length > 0) {
        // Remove the original day sections from the formatted text
        dayMatches.forEach(match => {
            formatted = formatted.replace(match, '');
        });
        
        // Format each day section
        let formattedDays = '';
        dayMatches.forEach(daySection => {
            // Extract day title
            const dayTitleMatch = daySection.match(/## (Day \d+:)/);
            const dayTitle = dayTitleMatch ? dayTitleMatch[1] : 'Day';
            
            // Start the day section
            let formattedDay = `<div class="day-section"><div class="day-title">${dayTitle}</div>`;
            
            // Format morning, afternoon, evening sections
            const timeBlocks = daySection.match(/- \*\*(Morning|Afternoon|Evening):\*\*[\s\S]*?(?=- \*\*|###|$)/g) || [];
            
            timeBlocks.forEach(block => {
                const timeMatch = block.match(/- \*\*(Morning|Afternoon|Evening):\*\*/);
                const time = timeMatch ? timeMatch[1] : '';
                
                if (time) {
                    formattedDay += `<div class="time-block"><span class="time-label">${time}:</span></div>`;
                    
                    // Extract and format activities
                    const activities = block.match(/  - (.*?)(?=\n|$)/g) || [];
                    activities.forEach(activity => {
                        // Highlight attraction names
                        const formattedActivity = activity.replace(/  - (.*?)(?=\n|$)/, '$1')
                                                        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
                        
                        formattedDay += `<div class="activity-item">${formattedActivity}</div>`;
                    });
                }
            });
            
            // Format additional information sections
            const infoSections = daySection.match(/### (.*?):([\s\S]*?)(?=### |$)/g) || [];
            
            infoSections.forEach(section => {
                const titleMatch = section.match(/### (.*?):/);
                const title = titleMatch ? titleMatch[1] : '';
                
                if (title) {
                    formattedDay += `<div class="info-section"><h3>${title}:</h3>`;
                    
                    // Format list items
                    let content = section.replace(/### .*?:/, '').trim();
                    content = content.replace(/- (.*?)(?=\n|$)/g, '<div>• $1</div>')
                                    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
                    
                    formattedDay += content + '</div>';
                }
            });
            
            // Close the day section
            formattedDay += '</div>';
            formattedDays += formattedDay;
        });
        
        // Add the formatted days back to the content
        formatted += formattedDays;
    }
    
    // Format any trailing content
    formatted = formatted.replace(/\n/g, '<br>');

    document.getElementById("download-ics-btn").addEventListener("click", () => {
        generateICSFromFormattedItinerary(formatted);
    });
    
    return formatted;
}

// Format packing list content
function formatPackingList(text) {
    // Format the title
    let formatted = text.replace(/# (.*?)(?:\n|$)/, '<h1>$1</h1>');
    
    // Split into sections by ## headers
    const sections = formatted.split(/## /);
    let header = sections[0];
    const categories = sections.slice(1);
    
    // Format categories
    let formattedSections = '';
    for (const section of categories) {
        const titleMatch = section.match(/^(.*?)(?:\n|$)/);
        const title = titleMatch ? titleMatch[1] : '';
        
        if (title) {
            formattedSections += `<div class="packing-section"><h2 class="packing-category">${title}</h2>`;
            
            // Format list items with checkboxes
            let content = section.replace(/^.*?\n/, '').trim();
            content = content.replace(/- (.*?)(?=\n|$)/g, 
                                      '<div class="packing-item"><input type="checkbox" class="packing-checkbox"><span>$1</span></div>')
                             .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
            
            formattedSections += content + '</div>';
        }
    }
    
    // Format note section if present
    const noteMatch = formatted.match(/## Note([\s\S]*?)(?=$)/);
    let noteSection = '';
    
    if (noteMatch) {
        noteSection = `<div class="packing-note"><h3>Note</h3>${noteMatch[1].replace(/- (.*?)(?=\n|$)/g, '<p>• $1</p>')}</div>`;
    }
    
    return header + formattedSections + noteSection;
}

// Format budget content
function formatBudget(text) {
    // Format the title
    let formatted = text.replace(/## (Budget Estimate.*?)(?:\n|$)/, '<h1 class="budget-title">$1</h1>');
    
    // Split into categories
    const categories = formatted.match(/### (.*?)[\s\S]*?(?=### |#### |$)/g) || [];
    
    let formattedCategories = '';
    for (const category of categories) {
        const titleMatch = category.match(/### (.*?)(?:\n|$)/);
        const title = titleMatch ? titleMatch[1] : '';
        
        // Skip the "Total Estimated Budget" section for special formatting
        if (title && !title.includes("Total Estimated Budget")) {
            formattedCategories += `<div class="budget-category"><h3 class="category-title">${title}</h3>`;
            
            // Format budget items
            const items = category.match(/- \*\*(.*?)\*\*:(.*?)(?=\n|$)/g) || [];
            for (const item of items) {
                const parts = item.match(/- \*\*(.*?)\*\*:(.*?)(?=\n|$)/);
                if (parts) {
                    const description = parts[1];
                    const value = parts[2].trim();
                    
                    formattedCategories += `
                        <div class="budget-item">
                            <div class="item-desc">${description}</div>
                            <div class="item-value">${value}</div>
                        </div>
                    `;
                }
            }
            
            formattedCategories += '</div>';
        }
    }
    
    // Format total section
    const totalMatch = formatted.match(/### Total Estimated Budget[\s\S]*?(?=#### |$)/);
    let totalSection = '';
    
    if (totalMatch) {
        totalSection = '<div class="total-section">';
        totalSection += `<h3 class="category-title">${totalMatch[0].match(/### (.*?)(?:\n|$)/)[1]}</h3>`;
        
        const totalItems = totalMatch[0].match(/- \*\*(.*?)\*\*:(.*?)(?=\n|$)/g) || [];
        for (const item of totalItems) {
            const parts = item.match(/- \*\*(.*?)\*\*:(.*?)(?=\n|$)/);
            if (parts) {
                totalSection += `
                    <div class="budget-item">
                        <div class="item-desc">${parts[1]}</div>
                        <div class="item-value">${parts[2].trim()}</div>
                    </div>
                `;
            }
        }
        
        totalSection += '</div>';
    }
    
    // Format note section
    const noteMatch = formatted.match(/#### Note:[\s\S]*?$/);
    let noteSection = '';
    
    if (noteMatch) {
        noteSection = `<div class="budget-note">${noteMatch[0].replace(/#### Note:/, '<h3>Note:</h3>')}</div>`;
    }
    
    return formatted.split(/### /)[0] + formattedCategories + totalSection + noteSection;
}



// Default formatter for unknown content types
function formatDefault(text) {
    return text
        .replace(/# (.*?)(?:\n|$)/g, '<h1>$1</h1>')
        .replace(/## (.*?)(?:\n|$)/g, '<h2>$1</h2>')
        .replace(/### (.*?)(?:\n|$)/g, '<h3>$1</h3>')
        .replace(/#### (.*?)(?:\n|$)/g, '<h4>$1</h4>')
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.*?)\*/g, '<em>$1</em>')
        .replace(/- (.*?)(?=\n|$)/g, '<div class="list-item">• $1</div>')
        .replace(/\n/g, '<br>');
}
    
    logDebug('NoDetours app initialized');

    function generateICSFromFormattedItinerary(itineraryText) {
        const lines = itineraryText.split('\n');
        let icsContent = "BEGIN:VCALENDAR\nVERSION:2.0\nPRODID:-//NoDetours Trip Planner//EN\n";
    
        const timeBlocks = {
            "Morning": { start: "09:00", end: "11:00" },
            "Afternoon": { start: "13:00", end: "16:00" },
            "Evening": { start: "18:00", end: "21:00" }
        };
    
        let currentDate = new Date(); // Start from today
        let parsingDay = false;
        let timeOfDay = null;
    
        lines.forEach((line, i) => {
            const trimmed = line.trim();
    
            // Match day headers
            const dayMatch = trimmed.match(/^## Day (\d+): (.+)$/);
            if (dayMatch) {
                const dayOffset = parseInt(dayMatch[1]) - 1;
                currentDate = new Date();
                currentDate.setDate(currentDate.getDate() + dayOffset);
                parsingDay = true;
            }
    
            // Match time-of-day block
            const timeMatch = trimmed.match(/^\- \*\*(Morning|Afternoon|Evening)\*\*:/);
            if (timeMatch) {
                timeOfDay = timeMatch[1];
            }
    
            // Match activity lines (e.g., "  - Visit...")
            if (trimmed.startsWith('- ') && timeOfDay) {
                const activityMatch = trimmed.match(/^- (.*)/);
                if (activityMatch) {
                    const title = activityMatch[1].replace(/\*\*/g, '').trim();
                    const { start, end } = timeBlocks[timeOfDay];
    
                    const startICS = getICSDateTime(currentDate, start);
                    const endICS = getICSDateTime(currentDate, end);
    
                    icsContent += "BEGIN:VEVENT\n";
                    icsContent += `SUMMARY:${title}\n`;
                    icsContent += `DTSTART:${startICS}\n`;
                    icsContent += `DTEND:${endICS}\n`;
                    icsContent += `DESCRIPTION:${timeOfDay} activity in Chicago itinerary\n`;
                    icsContent += "END:VEVENT\n";
                }
            }
        });
    
        icsContent += "END:VCALENDAR";
    
        // Trigger file download
        const blob = new Blob([icsContent], { type: "text/calendar" });
        const url = URL.createObjectURL(blob);
        const link = document.createElement("a");
        link.href = url;
        link.download = "chicago-itinerary.ics";
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    }
    
    // Helper: Format date and time as YYYYMMDDTHHMMSS
    function getICSDateTime(date, timeStr) {
        const [hh, mm] = timeStr.split(":");
        const dt = new Date(date);
        dt.setHours(parseInt(hh), parseInt(mm), 0);
        return `${dt.getFullYear()}${String(dt.getMonth() + 1).padStart(2, '0')}${String(dt.getDate()).padStart(2, '0')}T${String(dt.getHours()).padStart(2, '0')}${String(dt.getMinutes()).padStart(2, '0')}00`;
    }
    


    
});
