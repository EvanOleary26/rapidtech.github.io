document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('routeForm');
    const calculateBtn = document.getElementById('calculateBtn');
    const spinner = calculateBtn.querySelector('.spinner-border');
    const resultsDiv = document.getElementById('results');
    const errorDiv = document.getElementById('error');
    const mapForm = document.getElementById('mapForm');
    const advancedResultsDiv = document.getElementById('advancedResults');
    const advancedResultsBtn = document.getElementById('advancedResultsBtn');

    let konamiCode = [38, 38, 40, 40, 37, 39, 37, 39, 66, 65]; // Up, Up, Down, Down, Left, Right, Left, Right, B, A
    let keyPresses = []; 
    
    

    document.addEventListener('keydown', function(e) {
      keyPresses.push(e.keyCode);
      if (keyPresses.slice(-konamiCode.length).join('') === konamiCode.join('')) {
          window.location.href = "https://www.youtube.com/watch?v=dQw4w9WgXcQ";
        keyPresses = []; // Reset the sequence
      }
    });

    advancedResultsBtn.addEventListener('click', function(e) {
        e.preventDefault();
        advancedResultsDiv.classList.toggle('d-none');
    });

    resultsDiv.addEventListener('submit', async function(e) {
        e.preventDefault();
        advancedResultsDiv.classList.remove('d-none');
    });

    // Utility function to format large numbers
    function formatNumber(value) {
        if (value >= 1e9) {
            return `${(value / 1e9).toFixed(2)} Billion`;
        } else if (value >= 1e6) {
            return `${(value / 1e6).toFixed(2)} Million`;
        } else if (value >= 1e3) {
            return `${(value / 1e3).toFixed(2)} Thousand`;
        }
        return value.toString();
    }

    // Utility function to format time
    function formatTime(minutes) {
        if (minutes >= 60) {
            const hours = Math.floor(minutes / 60);
            const remainingMinutes = minutes % 60;
            return `${hours}h ${remainingMinutes}m`;
        }
        return `${minutes} Minutes`;
    }

    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        // Form validation
        if (!form.checkValidity()) {
            e.stopPropagation();
            form.classList.add('was-validated');
            return;
        }

        // Show loading state
        calculateBtn.disabled = true;
        spinner.classList.remove('d-none');
        resultsDiv.classList.add('d-none');
        errorDiv.classList.add('d-none');

        try {
            const formData = new FormData(form);
            const response = await fetch('/calculate', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || 'An error occurred');
            }
            
            // Update results with formatted values
            document.getElementById('estimatedCost').textContent = `$${formatNumber(data.estimated_cost)}`;
            document.getElementById('ridership').textContent = `${formatNumber(data.ridership)}`;
            document.getElementById('roadDistance').textContent = `${data.road_distance} Km`;
            document.getElementById('travelTime').textContent = formatTime(data.travel_time);
            document.getElementById('yearlyCost').textContent = `$${formatNumber(data.yearly_cost)}`;
            document.getElementById('yearsToEven').textContent = `${data.years_to_even} Years`;
            document.getElementById('profit').textContent = `$${formatNumber(data.profit)}`;
            document.getElementById('population1').textContent = `${formatNumber(data.populationA)}`;
            document.getElementById('population2').textContent = `${formatNumber(data.populationB)}`;

            resultsDiv.classList.remove('d-none');
        } catch (error) {
            errorDiv.textContent = error.message;
            errorDiv.classList.remove('d-none');
        } finally {
            // Reset loading state
            calculateBtn.disabled = false;
            spinner.classList.add('d-none');
        }
    });

    mapForm.addEventListener('submit', function(e) {
        e.preventDefault();
        const populationRadius = document.getElementById('populationRadius').value;
        const ticketPrice = document.getElementById('ticketPrice').value;
        const maxSpeed = document.getElementById('maxSpeed').value;

        // Handle the slider values as needed
        console.log(`Population Radius: ${populationRadius} km`);
        console.log(`Ticket Price: $${ticketPrice}`);
        console.log(`Max Speed: ${maxSpeed} km/h`);
    });

    initMap();
});

function initMap() {
    const map = new google.maps.Map(document.getElementById("map"), {
        zoom: 7,
        center: { lat: 0, lng: 0 }, // Default center
    });

    const directionsService = new google.maps.DirectionsService();
    const directionsRenderer = new google.maps.DirectionsRenderer();
    directionsRenderer.setMap(map);

    const form = document.getElementById("routeForm");
    form.addEventListener("submit", function (e) {
        e.preventDefault();
        const origin = document.getElementById("origin").value;
        const destination = document.getElementById("destination").value;

        directionsService.route(
            {
                origin: origin,
                destination: destination,
                travelMode: google.maps.TravelMode.DRIVING,
            },
            (response, status) => {
                if (status === "OK") {
                    directionsRenderer.setDirections(response);
                } else {
                    alert("Directions request failed due to " + status);
                }
            }
        );
    });
}

function openTab(evt, tabName) {
  // Declare all variables
  var i, tabcontent, tablinks;

  // Get all elements with class="tabcontent" and hide them
  tabcontent = document.getElementsByClassName("tabcontent");
  for (i = 0; i < tabcontent.length; i++) {
    tabcontent[i].style.display = "none";
  }

  // Get all elements with class="tablinks" and remove the class "active"
  tablinks = document.getElementsByClassName("tablinks");
  for (i = 0; i < tablinks.length; i++) {
    tablinks[i].className = tablinks[i].className.replace(" active", "");
  }

  // Show the current tab, and add an "active" class to the button that opened the tab
  document.getElementById(tabName).style.display = "block";
  evt.currentTarget.className += " active";
}

function loadGoogleMapsAPI(apiKey, callbackName) {
    const script = document.createElement('script');
    script.src = `https://maps.googleapis.com/maps/api/js?key=${apiKey}&callback=${callbackName}`;
    script.async = true;
    script.defer = true;
    document.head.appendChild(script);
}

// Initialize Google Maps API
fetch("/get-api-key")
  .then(response => response.json())
  .then(data => {
    const apiKey = data.apiKey;
    loadGoogleMapsAPI(apiKey, 'initMap'); // Pass the key to your function
  })
  .catch(error => console.error("Error fetching API key:", error));