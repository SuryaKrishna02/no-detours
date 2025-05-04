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
    const downloadIcsBtn = document.getElementById('download-ics-btn');
    
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
                // Special handling for validation errors with missing required info
                if (response.status === 400 && data.missing_info) {
                    const missingInfo = data.missing_info;
                    let validationMessage = `<div class="validation-error">
                        <h3><i class="fas fa-exclamation-circle"></i> Please provide more details</h3>
                        <p>Your travel plan requires additional information:</p>
                        <ul>`;
                    
                    missingInfo.forEach(info => {
                        validationMessage += `<li>Please specify your <strong>${info}</strong></li>`;
                    });
                    
                    validationMessage += `</ul>
                        <p>${data.example || "Example: 'I want to visit Chicago for 3 days in June with my family.'"}</p>
                        <button class="try-again-btn">Try Again</button>
                    </div>`;
                    
                    // Display validation error
                    itineraryText.innerHTML = validationMessage;
                    
                    // Hide loading, show only the itinerary tab with error
                    loadingIndicator.style.display = 'none';
                    document.querySelector('.tabs').style.display = 'flex';
                    document.querySelector('.tab-content').style.display = 'block';
                    
                    // Make sure the itinerary tab is active
                    tabButtons.forEach(btn => btn.classList.remove('active'));
                    tabPanes.forEach(pane => pane.classList.remove('active'));
                    document.querySelector('[data-tab="itinerary"]').classList.add('active');
                    document.getElementById('itinerary-content').classList.add('active');
                    
                    // Add event listener to the "Try Again" button
                    setTimeout(() => {
                        document.querySelector('.try-again-btn')?.addEventListener('click', () => {
                            userInput.focus();
                            resultsSection.style.display = 'none';
                        });
                    }, 100);
                    
                    // Scroll to results
                    resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
                    
                    return; // Exit early
                }
                
                throw new Error(data.error || 'Failed to generate travel plan');
            }
            
            // Store trip details if provided
            if (data.trip_details) {
                window.tripDetails = data.trip_details;
                console.log("Received trip details:", data.trip_details);
            }
            
            // Display results (with fallbacks if any component is missing)
            itineraryText.innerHTML = formatContent(data.itinerary || 'No itinerary generated. Please try again with more specific details about your trip.');
            packingText.innerHTML = formatContent(data.packing_list || 'No packing list generated. Please try again with more specific details about your trip.');
            budgetText.innerHTML = formatContent(data.estimated_budget || 'No budget estimate generated. Please try again with more specific details about your trip.');
            
            // Hide loading, show tabs and content
            loadingIndicator.style.display = 'none';
            document.querySelector('.tabs').style.display = 'flex';
            document.querySelector('.tab-content').style.display = 'block';
            
            // Check for calendar button
            if (data.trip_details && data.trip_details.daily_dates) {
                window.tripDetails = data.trip_details;
                showDownloadButton();
            }
            
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
        
        // Log content details for debugging
        console.log("Content length:", text.length);
        console.log("Content start:", text.substring(0, 100));
        console.log("Content type determination:");
        console.log("- Contains 'Itinerary':", text.includes('Itinerary'));
        console.log("- Contains 'Day 1':", text.includes('Day 1'));
        console.log("- Contains 'List':", text.includes('List'));
        console.log("- Contains 'Budget':", text.includes('Budget'));
        console.log("- Contains 'Estimated Budget':", text.includes('Estimated Budget'));
    
        // Fix issue with duplicated content by detecting and removing markdown delimiters
        if (text.includes("```markdown") || text.includes("```")) {
            const codeBlockPattern = /```(?:markdown)?\s*([\s\S]*?)```/;
            const match = text.match(codeBlockPattern);
            if (match) {
                // Extract just the content within the code block
                text = match[1].trim();
                console.log("Extracted content from markdown code block");
            }
        }
        
        // Improved content type detection
        const isItinerary = text.includes('Itinerary') || text.includes('Day 1') || text.match(/## Day \d+/);
        const isPackingList = text.includes('List') || text.includes('Packing');
        const isBudget = text.includes('Budget') || text.includes('Estimated Budget');
        
        console.log("Content type decision:", isItinerary ? "Itinerary" : (isPackingList ? "Packing List" : (isBudget ? "Budget" : "Unknown")));
    
        let formattedContent = '';
        try {
            if (isItinerary) {
                formattedContent = formatItinerary(text);
            } else if (isPackingList) {
                formattedContent = formatPackingList(text);
            } else if (isBudget) {
                formattedContent = formatBudget(text);
            } else {
                formattedContent = formatDefault(text);
            }
        } catch (error) {
            console.error("Error formatting content:", error);
            // Fallback to default formatting if specific formatter fails
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
                margin-bottom: 15px;
                border-radius: 6px;
            }
            .budget-item {
                display: flex;
                justify-content: space-between;
                border-bottom: 1px dashed #e0e0e0;
                padding: 8px 0;
            }
            .total-item {
                font-weight: bold;
                color: #5a2a82;
            }
            .budget-note {
                font-style: italic;
                padding: 12px 15px;
                background-color: #f9f9f9;
                border-left: 3px solid #5a2a82;
                margin-top: 15px;
                border-radius: 4px;
            }
        </style>
        `;
    
        return `<div class="formatted-content">${styles}${formattedContent}</div>`;
    }
    

// Format itinerary content
function formatItinerary(text) {
    console.log("Formatting itinerary:", text.substring(0, 100) + "...");
    
    if (!text || text.includes("I apologize") || text.length < 50) {
        // Hide download button for invalid itineraries
        hideDownloadButton();
        
        return `<div class="error-message">
            <p><i class="fas fa-exclamation-triangle"></i> Unable to generate an itinerary.</p>
            <p>Please try again with more specific details about your trip, including destination and dates.</p>
        </div>`;
    }
    
    // Validate that we have the expected number of days if trip_details is available
    if (window.tripDetails && window.tripDetails.duration_days) {
        const expectedDays = parseInt(window.tripDetails.duration_days);
        
        // Count day headers in the text
        const dayMatches = [...text.matchAll(/## Day \d+/g)];
        const dayCount = dayMatches.length;
        
        console.log(`Expected ${expectedDays} days, found ${dayCount} days`);
        
        // If we're missing days and have at least 2 days, try to fix it
        if (dayCount < expectedDays && dayCount >= 2) {
            console.warn(`Itinerary is missing days. Expected: ${expectedDays}, Found: ${dayCount}`);
        }
    }
    
    // Preprocessing step: Clean up the text to remove duplicate content
    
    // Step 1: Fix issue with markdown code blocks
    // This can happen if the LLM outputs something like ```markdown (content) ```
    if (text.includes("```markdown") || text.includes("```")) {
        const codeBlockPattern = /```(?:markdown)?\s*([\s\S]*?)```/;
        const match = text.match(codeBlockPattern);
        if (match) {
            // Extract just the content within the code block
            text = match[1].trim();
            console.log("Extracted content from markdown code block");
        }
    }
    
    // Step 2: Handle case where the raw markdown and rendered content appear together
    // This happens when the model tries to output both the raw format and the display format
    
    // First, detect if there are two copies of the same day sections
    const dayHeaders = [...text.matchAll(/## Day \d+/g)];
    if (dayHeaders.length > 3) { // If there are more day headers than expected
        console.log("Detected potential duplicate content, cleaning up...");
        
        // Extract just the cleaned markdown section without duplication
        const cleanedText = [];
        const lines = text.split('\n');
        let inDaySection = false;
        let dayPattern = /^## Day \d+/;
        
        for (let i = 0; i < lines.length; i++) {
            const line = lines[i].trim();
            
            // Check if this is a day header
            if (dayPattern.test(line)) {
                inDaySection = true;
                cleanedText.push(line);
                continue;
            }
            
            // Check if this is a special section header (not a day)
            if (line.startsWith('## ') && !line.includes('Day')) {
                inDaySection = false;
            }
            
            // Only add lines that are in day sections or not duplicated
            if (inDaySection || !cleanedText.includes(line)) {
                cleanedText.push(line);
            }
        }
        
        text = cleanedText.join('\n');
        console.log("Cleaned text length:", text.length);
    }
    
    try {
        // Create the formatted HTML container
        let formattedHTML = '<div class="itinerary-container">';
        
        // Format the title
        const titleMatch = text.match(/# (.*?)(?=\n|$)/);
        let destination = "Travel";
        if (titleMatch) {
            destination = titleMatch[1].replace(" Travel Itinerary", "");
            formattedHTML += `<h1 class="itinerary-title">${titleMatch[1]}</h1>`;
        } else {
            formattedHTML += `<h1 class="itinerary-title">Travel Itinerary</h1>`;
        }
        
        // Format the overview section
        const overviewMatch = text.match(/## Overview\s+([\s\S]*?)(?=##|$)/);
        if (overviewMatch) {
            formattedHTML += `<div class="overview-section">
                <p>${overviewMatch[1].trim().replace(/\n/g, '<br>')}</p>
            </div>`;
        }
        
        // We no longer extract dates from the itinerary text since we're not showing them
        // Instead, rely on the trip_details data passed from the backend
        
        // Parse and store the destination
        window.tripDestination = destination;
        
        // Always show the download button if we have trip details data
        // This will ensure the calendar feature works even though dates aren't visible in the UI
        if (window.tripDetails && window.tripDetails.daily_dates && 
            Object.keys(window.tripDetails.daily_dates).length > 0) {
            // Store dates from backend data
            const backendDates = [];
            Object.values(window.tripDetails.daily_dates).forEach(date => {
                if (date.match(/\d{4}-\d{2}-\d{2}/)) {
                    backendDates.push(date);
                }
            });
            window.tripDates = backendDates;
            
            console.log("Using backend dates for calendar:", backendDates);
            showDownloadButton();
        } else {
            // Fallback: try to extract dates from the text
            const datePattern = /## Day \d+(?::)?\s*(?:.*?)?(\d{4}-\d{2}-\d{2})/g;
            const dates = [];
            let dateMatch;
            while ((dateMatch = datePattern.exec(text)) !== null) {
                dates.push(dateMatch[1]);
            }
            
            window.tripDates = dates;
            
            // Only show download button if we found dates or have backend dates
            if (dates.length > 0) {
                showDownloadButton();
            } else {
                hideDownloadButton();
            }
        }
        
        // Extract and format day sections
        const daySections = [];
        // Updated pattern to better match "## Day X" format without any extra info
        const dayPattern = /## Day (\d+)(?::)?\s*(.*?)(?=## Day \d+|## Accommodation|$)/gs;
        let dayMatch;
        
        while ((dayMatch = dayPattern.exec(text)) !== null) {
            // Get the day number
            const dayNum = dayMatch[1];
            
            // Get the title and date (if any)
            let title = dayMatch[2] ? dayMatch[2].trim() : '';
            
            // Check if title contains a date (format: YYYY-MM-DD)
            let date = '';
            const dateMatch = title.match(/(\d{4}-\d{2}-\d{2})/);
            if (dateMatch) {
                date = dateMatch[1];
                // Remove the date from the title if there's other text
                title = title.replace(dateMatch[1], '').trim();
                // Remove any leading dash or colon
                title = title.replace(/^[-:]\s*/, '').trim();
            }
            
            daySections.push({
                day: dayNum,
                title: title,
                date: date,
                content: dayMatch[0]
            });
        }
        
        // Format each day section
        formattedHTML += '<div class="days-container">';
        
        daySections.forEach(day => {
            // Clean up day.content to remove any raw markdown
            let content = day.content.trim();
            
            formattedHTML += `<div class="day-section">
                <h2 class="day-title">Day ${day.day}</h2>`;
            
            // Format time blocks (Morning, Afternoon, Evening)
            const timeBlocks = ['Morning', 'Afternoon', 'Evening'];
            
            timeBlocks.forEach(timeBlock => {
                // More flexible pattern to handle various formats
                const timeBlockPatterns = [
                    // Pattern for "- **Morning**:" format
                    new RegExp(`- \\*\\*${timeBlock}\\*\\*:?(.*?)(?=- \\*\\*|$)`, 's'),
                    // Pattern for just "**Morning**:" format without the leading dash
                    new RegExp(`\\*\\*${timeBlock}\\*\\*:?(.*?)(?=\\*\\*|$)`, 's')
                ];
                
                let timeBlockMatch = null;
                // Try each pattern until we find a match
                for (const pattern of timeBlockPatterns) {
                    timeBlockMatch = day.content.match(pattern);
                    if (timeBlockMatch) break;
                }
                
                if (timeBlockMatch) {
                    formattedHTML += `<div class="time-block">
                        <h3 class="time-title">${timeBlock}</h3>
                        <div class="activities">`;
                    
                    // Extract activities
                    let activitiesText = timeBlockMatch[1];
                    
                    // Clean up the activities text - remove any markdown sections
                    // This helps with the duplicate content issue
                    if (activitiesText.includes('```') || activitiesText.includes('```markdown')) {
                        const codeBlockMatch = activitiesText.match(/```(?:markdown)?\s*([\s\S]*?)```/);
                        if (codeBlockMatch) {
                            activitiesText = codeBlockMatch[1].trim();
                        }
                    }
                    
                    // Handle different possible formats:
                    // 1. A list with each item on a new line starting with -
                    // 2. Direct text without list markers
                    let activities = [];
                    
                    // First try to extract as a list
                    activities = activitiesText.match(/- (.*?)(?=\n|$)/g) || [];
                    
                    // If no list items found, just use the whole text split by lines
                    if (activities.length === 0 && activitiesText.trim()) {
                        activities = activitiesText.split('\n')
                            .filter(line => line.trim())
                            .map(line => line.trim());
                    }
                    
                    // Clean up each activity and add it
                    activities.forEach(activity => {
                        // Skip if activity is just the header text
                        if (activity.includes(`**${timeBlock}**`)) return;
                        
                        // Remove leading dash, stars, and spaces
                        const formattedActivity = activity
                            .replace(/^[-*•]\s*/g, '')  // Remove -, *, or • followed by optional spaces
                            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>') // Bold markdown to <strong>
                            .trim();
                        
                        // Only add if it's non-empty and not just the timeblock
                        if (formattedActivity && 
                            !formattedActivity.includes(`**${timeBlock}**`) && 
                            formattedActivity !== timeBlock) {
                            formattedHTML += `<div class="activity-item">${formattedActivity}</div>`;
                        }
                    });
                    
                    formattedHTML += `</div></div>`;
                }
            });
            
            formattedHTML += '</div>'; // close day-section
        });
        
        formattedHTML += '</div>'; // close days-container
        
        // Format additional sections
        const additionalSections = [
            { title: 'Accommodation', icon: 'fa-hotel' },
            { title: 'Transportation', icon: 'fa-car' },
            { title: 'Dining Recommendations', icon: 'fa-utensils' },
            { title: 'Estimated Costs', icon: 'fa-money-bill' },
            { title: 'Tips', icon: 'fa-lightbulb' }
        ];
        
        formattedHTML += '<div class="additional-info">';
        
        additionalSections.forEach(section => {
            const sectionPattern = new RegExp(`## ${section.title}\\s+(([\\s\\S]*?)(?=##|$))`, 'i');
            const sectionMatch = text.match(sectionPattern);
            
            if (sectionMatch) {
                formattedHTML += `<div class="info-section">
                    <h2 class="section-title"><i class="fas ${section.icon}"></i> ${section.title}</h2>
                    <div class="section-content">`;
                
                let content = sectionMatch[1].trim();
                
                // Format bullet points
                content = content.replace(/-(.*?)(?=\n|$)/g, '<div class="info-item"><span>$1</span></div>');
                // Bold text
                content = content.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
                // Line breaks
                content = content.replace(/\n/g, '<br>');
                
                formattedHTML += content;
                formattedHTML += `</div></div>`;
            }
        });
        
        formattedHTML += '</div>'; // close additional-info
        
        // Add download button event listener
        if (downloadIcsBtn) {
            downloadIcsBtn.addEventListener("click", () => {
                generateICSFromItinerary();
            });
        }
        
        // Add custom CSS directly in the component
        formattedHTML += `
        <style>
            .itinerary-container {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                color: #333;
                max-width: 100%;
                padding: 0 10px;
            }
            .itinerary-title {
                color: #5a2a82;
                font-size: 28px;
                border-bottom: 3px solid #5a2a82;
                padding-bottom: 12px;
                margin-bottom: 25px;
                text-align: center;
            }
            .overview-section {
                background-color: rgba(90, 42, 130, 0.05);
                padding: 20px;
                border-radius: 10px;
                margin-bottom: 30px;
                font-size: 16px;
                line-height: 1.6;
                box-shadow: 0 2px 10px rgba(0,0,0,0.05);
                border: 1px solid rgba(90, 42, 130, 0.1);
            }
            .days-container {
                display: flex;
                flex-direction: column;
                gap: 30px;
                margin-bottom: 35px;
            }
            .day-section {
                background-color: transparent;
                overflow: hidden;
                position: relative;
                margin-bottom: 20px;
                padding-bottom: 10px;
                border-bottom: 1px solid #e8e8e8;
            }
            .day-title {
                background-color: transparent;
                color: #5a2a82;
                padding: 15px 20px;
                margin: 0;
                font-size: 20px;
                position: relative;
                display: flex;
                align-items: center;
                border-bottom: 1px solid #e0e0e0;
            }
            .day-title::before {
                content: "";
                margin-right: 5px;
            }
            .day-date {
                background-color: rgba(90, 42, 130, 0.1);
                color: #5a2a82;
                font-weight: bold;
                padding: 10px 20px;
                font-size: 16px;
                border-bottom: 1px solid rgba(90, 42, 130, 0.2);
                display: block;
                margin-top: -5px;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            }
            .time-block {
                padding: 18px 20px;
                position: relative;
                margin-bottom: 10px;
            }
            .time-title {
                margin: 0 0 15px 0;
                color: #5a2a82;
                font-size: 18px;
                display: flex;
                align-items: center;
                font-weight: 600;
            }
            .time-title::before {
                content: "•";
                margin-right: 10px;
                font-size: 24px;
                line-height: 0;
                position: relative;
                top: 4px;
                color: #5a2a82;
            }
            .activities {
                padding-left: 24px;
            }
            .activity-item {
                margin-bottom: 12px;
                line-height: 1.5;
                position: relative;
                padding-left: 18px;
            }
            .activity-item::before {
                content: "•";
                position: absolute;
                left: 0;
                color: #5a2a82;
                font-size: 1.2em;
            }
            .additional-info {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
                gap: 25px;
                margin-top: 30px;
            }
            .info-section {
                background-color: transparent;
                overflow: hidden;
                margin-bottom: 20px;
                height: 100%;
                display: flex;
                flex-direction: column;
            }
            .section-title {
                color: #5a2a82;
                padding: 15px 0;
                margin: 0;
                font-size: 18px;
                display: flex;
                align-items: center;
                gap: 10px;
                border-bottom: 1px solid #e0e0e0;
            }
            .section-content {
                padding: 18px;
                line-height: 1.6;
                flex: 1;
            }
            .info-item {
                margin-bottom: 10px;
                position: relative;
                padding-left: 15px;
            }
            .info-item::before {
                content: "•";
                position: absolute;
                left: 0;
                color: #5a2a82;
            }
            strong {
                color: #5a2a82;
                font-weight: 600;
            }
            
            /* Responsive adjustments */
            @media (max-width: 768px) {
                .additional-info {
                    grid-template-columns: 1fr;
                }
                .day-title, .section-title {
                    font-size: 16px;
                }
                .time-title {
                    font-size: 16px;
                }
                .time-block, .section-content {
                    padding: 15px;
                }
            }
        </style>`;
        
        // Close the container
        formattedHTML += '</div>';
        
        return formattedHTML;
    } catch (error) {
        console.error("Error formatting itinerary:", error);
        
        // Hide download button on error
        hideDownloadButton();
        
        // Fallback to simple formatting
        let formatted = text
            .replace(/# (.*?)(?=\n|$)/, '<h1>$1</h1>')
            .replace(/## (.*?)(?=\n|$)/g, '<h2>$1</h2>')
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/- (.*?)(?=\n|$)/g, '<div class="list-item">$1</div>')
            .replace(/\n/g, '<br>');
            
        return formatted;
    }
}

// Helper functions for download button
function showDownloadButton() {
    const downloadBtn = document.getElementById("download-ics-btn");
    if (downloadBtn) {
        console.log("Showing calendar download button");
        downloadBtn.style.display = "block";
        downloadBtn.classList.add("active");
    } else {
        console.error("Calendar download button not found");
    }
}

function hideDownloadButton() {
    const downloadBtn = document.getElementById("download-ics-btn");
    if (downloadBtn) {
        console.log("Hiding calendar download button");
        downloadBtn.style.display = "none";
        downloadBtn.classList.remove("active");
    }
}

// Format packing list content
function formatPackingList(text) {
    // Fix issue with duplicated content by detecting and removing markdown delimiters
    if (text.includes("```markdown") || text.includes("```")) {
        const codeBlockPattern = /```(?:markdown)?\s*([\s\S]*?)```/;
        const match = text.match(codeBlockPattern);
        if (match) {
            // Extract just the content within the code block
            text = match[1].trim();
            console.log("Extracted content from markdown code block");
        }
    }
    
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
    console.log("Budget text:", text); // Debug log
    
    // Check if there's any content
    if (!text || text.includes("I apologize")) {
        return `<div class="error-message">
            <p><i class="fas fa-exclamation-triangle"></i> Unable to generate a budget estimate.</p>
            <p>Please try again with more specific details about your trip.</p>
        </div>`;
    }
    
    // Fix issue with duplicated content by detecting and removing markdown delimiters
    if (text.includes("```markdown") || text.includes("```")) {
        const codeBlockPattern = /```(?:markdown)?\s*([\s\S]*?)```/;
        const match = text.match(codeBlockPattern);
        if (match) {
            // Extract just the content within the code block
            text = match[1].trim();
            console.log("Extracted content from markdown code block");
        }
    }
    
    // Format the title
    let formatted = text;
    const titleMatch = text.match(/### Budget Estimate for (.*?)(?:\n|$)/);
    if (titleMatch) {
        const destination = titleMatch[1];
        formatted = formatted.replace(titleMatch[0], `<h1 class="budget-title">Budget Estimate for ${destination}</h1>`);
    }
    
    // Support both ### and #### headings for categories
    const categoryPattern = /(####) (\d+\. [\w\s]+):/g;
    const categories = [];
    let match;
    
    while ((match = categoryPattern.exec(text)) !== null) {
        const start = match.index;
        const categoryName = match[2];
        
        // Find the end of this section (next #### or end of text)
        const nextSectionMatch = text.slice(start + match[0].length).match(/(####)/);
        const end = nextSectionMatch 
            ? start + match[0].length + nextSectionMatch.index 
            : text.length;
        
        categories.push({
            name: categoryName,
            content: text.slice(start, end)
        });
    }
    
    // Format each category
    let formattedCategories = '';
    
    categories.forEach(category => {
        // Skip the "Total Estimated Budget" section for special formatting
        if (!category.name.includes("Total Estimated Budget")) {
            formattedCategories += `<div class="budget-category">
                <h3 class="category-title">${category.name}</h3>`;
            
            // Extract all bullet points
            const items = [...category.content.matchAll(/- \*\*(.*?)\*\*:? (.*?)(?=\n|$)/g)];
            
            items.forEach(item => {
                const label = item[1];
                const value = item[2].trim();
                
                formattedCategories += `
                    <div class="budget-item">
                        <div class="item-desc">${label}</div>
                        <div class="item-value">${value}</div>
                    </div>
                `;
            });
            
            formattedCategories += '</div>';
        }
    });
    
    // Format total section
    let totalSection = '';
    const totalMatch = text.match(/#### Total Estimated Budget Range:([\s\S]*?)(?=\*Note|\*\*Note|$)/);
    
    if (totalMatch) {
        totalSection = `<div class="total-section budget-category">
            <h3 class="category-title">Total Estimated Budget Range</h3>`;
        
        const items = [...totalMatch[1].matchAll(/- \*\*(.*?)\*\*:? (.*?)(?=\n|$)/g)];
        
        items.forEach(item => {
            const label = item[1];
            const value = item[2].trim();
            
            totalSection += `
                <div class="budget-item total-item">
                    <div class="item-desc">${label}</div>
                    <div class="item-value">${value}</div>
                </div>
            `;
        });
        
        totalSection += '</div>';
    }
    
    // Format note section
    let noteSection = '';
    const noteMatch = text.match(/\*Note:([\s\S]*?)$/);
    
    if (noteMatch) {
        noteSection = `<div class="budget-note">
            <p><i class="fas fa-info-circle"></i> <strong>Note:</strong> ${noteMatch[1].trim()}</p>
        </div>`;
    }
    
    // Add some styling specific to the budget
    const styles = `
    <style>
        .budget-category {
            background-color: rgba(90, 42, 130, 0.05);
            padding: 15px;
            margin-bottom: 15px;
            border-radius: 8px;
        }
        .budget-item {
            display: flex;
            justify-content: space-between;
            border-bottom: 1px dashed #e0e0e0;
            padding: 8px 0;
        }
        .total-item {
            font-weight: bold;
            color: #5a2a82;
        }
        .budget-note {
            font-style: italic;
            margin-top: 20px;
            padding: 15px;
            background-color: #f9f9f9;
            border-left: 3px solid #5a2a82;
            border-radius: 4px;
        }
    </style>
    `;
    
    // If we couldn't properly parse the budget, just format it simply
    if (categories.length === 0) {
        return `<div class="formatted-content">${styles}
            <div class="budget-category">
                ${text.replace(/\n/g, '<br>')}
            </div>
        </div>`;
    }
    
    return `<div class="formatted-content">${styles}
        ${formattedCategories}
        ${totalSection}
        ${noteSection}
    </div>`;
}



// Default formatter for unknown content types
function formatDefault(text) {
    // Fix issue with duplicated content by detecting and removing markdown delimiters
    if (text.includes("```markdown") || text.includes("```")) {
        const codeBlockPattern = /```(?:markdown)?\s*([\s\S]*?)```/;
        const match = text.match(codeBlockPattern);
        if (match) {
            // Extract just the content within the code block
            text = match[1].trim();
            console.log("Extracted content from markdown code block");
        }
    }
    
    return text
        .replace(/# (.*?)(?:\n|$)/g, '<h1>$1</h1>')
        .replace(/## (.*?)(?:\n|$)/g, '<h2>$1</h2>')
        .replace(/### (.*?)(?:\n|$)/g, '<h3>$1</h3>')
        .replace(/#### (.*?)(?:\n|$)/g, '<h4>$1</h4>')
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.*?)\*/g, '<em>$1</em>')
        .replace(/- (.*?)(?=\n|$)/g, '<div class="list-item">$1</div>')
        .replace(/\n/g, '<br>');
}
    
    // Init download button
    if (downloadIcsBtn) {
        downloadIcsBtn.addEventListener("click", function() {
            generateICSFromItinerary();
        });
        console.log("Calendar download button initialized");
    } else {
        console.error("Calendar download button not found in DOM");
    }
    
    logDebug('NoDetours app initialized');

    // New calendar generation function that uses stored dates and content from DOM
    function generateICSFromItinerary() {
        console.log("Generating ICS calendar from displayed itinerary");
        
        // First, try to get the tripDetails from the window object
        // These are passed from the backend with precise dates
        let allDates = {};
        if (window.tripDetails && window.tripDetails.daily_dates) {
            allDates = window.tripDetails.daily_dates;
            console.log("Using backend dates:", allDates);
        }
        
        // Backup extraction method - get dates from the tripDates array
        if (Object.keys(allDates).length === 0 && window.tripDates && window.tripDates.length > 0) {
            window.tripDates.forEach((dateStr, index) => {
                allDates[index + 1] = dateStr;
            });
            console.log("Using extracted dates:", allDates);
        }
        
        // If we still don't have dates, check for date elements in the DOM
        if (Object.keys(allDates).length === 0) {
            const dayDates = document.querySelectorAll('.day-date');
            if (dayDates.length > 0) {
                dayDates.forEach((dateEl, index) => {
                    const dateText = dateEl.textContent;
                    const dateMatch = dateText.match(/\d{4}-\d{2}-\d{2}/);
                    if (dateMatch) {
                        allDates[index + 1] = dateMatch[0];
                    }
                });
                console.log("Using DOM-extracted dates:", allDates);
            }
        }
        
        // If we still have no dates, create some default dates starting from today + 2 weeks
        if (Object.keys(allDates).length === 0) {
            // Find how many days we have in the itinerary
            const daySections = document.querySelectorAll('.day-section');
            const numDays = daySections.length || 3; // Default to 3 days if no day sections found
            
            // Create dates starting 2 weeks from now
            const startDate = new Date();
            startDate.setDate(startDate.getDate() + 14); // Start 2 weeks from now
            
            for (let i = 1; i <= numDays; i++) {
                const date = new Date(startDate);
                date.setDate(startDate.getDate() + (i - 1));
                const dateStr = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`;
                allDates[i] = dateStr;
            }
            console.log("Using generated default dates:", allDates);
        }
        
        // Final check - do we have any dates?
        if (Object.keys(allDates).length === 0) {
            alert("Cannot generate calendar: No valid dates found in the itinerary. Please regenerate your itinerary with specific dates.");
            return;
        }
        
        const destination = window.tripDestination || "Trip";
        
        let icsContent = "BEGIN:VCALENDAR\nVERSION:2.0\nPRODID:-//NoDetours Trip Planner//EN\n";
    
        // Standard time blocks - customized for better distribution
        const timeBlocks = {
            "Morning": { start: "09:00", end: "12:00" },
            "Afternoon": { start: "13:00", end: "17:00" },
            "Evening": { start: "18:00", end: "21:00" }
        };
        
        // Extract day sections from the displayed itinerary
        const daySections = document.querySelectorAll('.day-section');
        
        // Validate that we have day sections
        if (daySections.length === 0) {
            alert("Cannot generate calendar: No day sections found in the itinerary.");
            return;
        }
        
        // Process each day section
        daySections.forEach((daySection, index) => {
            // Get the day number from the title or use index+1
            const dayNum = index + 1;
            let dayNumFromTitle = null;
            const titleText = daySection.querySelector('.day-title').textContent;
            const dayMatch = titleText.match(/Day (\d+):/);
            if (dayMatch) {
                dayNumFromTitle = parseInt(dayMatch[1]);
            }
            
            // Use the correct day number
            const actualDayNum = dayNumFromTitle || dayNum;
            
            // Get date for this day
            const dateStr = allDates[actualDayNum];
            if (!dateStr) {
                console.warn(`No date found for day ${actualDayNum}`);
                return; // Skip this day
            }
            
            // Parse date
            const currentDate = new Date(dateStr);
            if (isNaN(currentDate.getTime())) {
                console.warn(`Invalid date for day ${actualDayNum}: ${dateStr}`);
                return; // Skip this day
            }
            
            // Format day info
            console.log(`Processing Day ${actualDayNum}: ${dateStr}`);
            
            // Get day title
            const dayTitle = daySection.querySelector('.day-title').textContent.replace(/Day \d+: /, '').trim();
            
            // Process time blocks
            const timeBlockElements = daySection.querySelectorAll('.time-block');
            timeBlockElements.forEach((blockEl, timeIndex) => {
                // Get time block type (Morning, Afternoon, Evening)
                const timeBlockTitle = blockEl.querySelector('.time-title').textContent.trim();
                let timeBlockConfig = timeBlocks[timeBlockTitle];
                
                if (!timeBlockConfig) {
                    console.warn(`Unknown time block: ${timeBlockTitle}, using default times`);
                    // Use default times based on position
                    if (timeIndex === 0) {
                        timeBlockConfig = timeBlocks["Morning"];
                    } else if (timeIndex === 1) {
                        timeBlockConfig = timeBlocks["Afternoon"];
                    } else {
                        timeBlockConfig = timeBlocks["Evening"];
                    }
                }
                
                // Get activities
                const activityElements = blockEl.querySelectorAll('.activity-item');
                activityElements.forEach((activityEl, actIndex) => {
                    const activityText = activityEl.textContent.replace(/^• /, '').trim();
                    
                    // Create calendar event with staggered times to avoid overlaps
                    const { start, end } = timeBlockConfig;
                    
                    // Stagger activity start times by 30 minutes within each time block
                    const [startHour, startMin] = start.split(':').map(Number);
                    const staggeredStart = `${startHour}:${String(startMin + (actIndex * 30) % 60).padStart(2, '0')}`;
                    const staggeredEnd = `${startHour + Math.floor((startMin + (actIndex * 30)) / 60)}:${String((startMin + (actIndex * 30) + 30) % 60).padStart(2, '0')}`;
                    
                    // Only create event if we have activity text
                    if (activityText && activityText.length > 2) {
                        const startICS = getICSDateTime(currentDate, staggeredStart);
                        const endICS = getICSDateTime(currentDate, staggeredEnd);
                        
                        icsContent += "BEGIN:VEVENT\n";
                        icsContent += `SUMMARY:${activityText}\n`;
                        icsContent += `DTSTART:${startICS}\n`;
                        icsContent += `DTEND:${endICS}\n`;
                        icsContent += `DESCRIPTION:${timeBlockTitle} activity on Day ${actualDayNum} (${dayTitle}) of your ${destination} itinerary\n`;
                        icsContent += `LOCATION:${destination}\n`;
                        icsContent += "END:VEVENT\n";
                    }
                });
            });
            
            // Add a full-day event for the day itself (with nextday for end)
            const dayStartICS = getICSDate(currentDate);
            
            // For the end date, use the next day (per iCalendar spec)
            const nextDate = new Date(currentDate);
            nextDate.setDate(nextDate.getDate() + 1);
            const dayEndICS = getICSDate(nextDate);
            
            icsContent += "BEGIN:VEVENT\n";
            icsContent += `SUMMARY:Day ${actualDayNum}: ${dayTitle} - ${destination}\n`;
            icsContent += `DTSTART;VALUE=DATE:${dayStartICS}\n`;
            icsContent += `DTEND;VALUE=DATE:${dayEndICS}\n`;
            icsContent += `DESCRIPTION:Day ${actualDayNum} of your ${destination} itinerary\n`;
            icsContent += "TRANSP:TRANSPARENT\n";  // Doesn't block time
            icsContent += "END:VEVENT\n";
        });
        
        icsContent += "END:VCALENDAR";
        
        // Trigger file download
        const blob = new Blob([icsContent], { type: "text/calendar" });
        const url = URL.createObjectURL(blob);
        const link = document.createElement("a");
        link.href = url;
        link.download = `${destination.toLowerCase().replace(/\s+/g, '-')}-itinerary.ics`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        
        console.log("ICS file generated for", destination);
    }
    
    // Helper: Format date and time as YYYYMMDDTHHMMSS
    function getICSDateTime(date, timeStr) {
        try {
            const [hh, mm] = timeStr.split(":");
            const dt = new Date(date);
            dt.setHours(parseInt(hh), parseInt(mm), 0);
            return `${dt.getFullYear()}${String(dt.getMonth() + 1).padStart(2, '0')}${String(dt.getDate()).padStart(2, '0')}T${String(dt.getHours()).padStart(2, '0')}${String(dt.getMinutes()).padStart(2, '0')}00`;
        } catch (error) {
            console.error("Error formatting ICS date:", error);
            return "20250101T120000"; // Fallback date
        }
    }
    
    // Helper: Format date as YYYYMMDD for all-day events
    function getICSDate(date) {
        try {
            return `${date.getFullYear()}${String(date.getMonth() + 1).padStart(2, '0')}${String(date.getDate()).padStart(2, '0')}`;
        } catch (error) {
            console.error("Error formatting ICS date:", error);
            return "20250101"; // Fallback date
        }
    }
    


    
});
