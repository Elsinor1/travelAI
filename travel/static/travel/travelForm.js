/**
 * Module for autocomplete suggestions and display of suggestions
 */
const AutocompleteModule = (function () {
  /**
   * Activates autocomplete functionality for location input
   */
  function autocomplete() {
    const input = document.getElementById("locationInput");
    const locationLongitude = document.getElementById("longitude");
    const locationLatitude = document.getElementById("latitude");
    const suggestionsDropdown = document.getElementById("suggestions-dropdown");
    const triggerAmount = 2; // Amount of letters that trigger autocomplete
    let timer;

    // Event listener for autocomplete trigger
    input.addEventListener("input", function () {
      clearTimeout(timer); // Clearing old timer
      const letters = input.value;
      locationLongitude.value = "";
      locationLatitude.value = "";

      // If trigger amount of letters is written, after 0.3s timer fetch suggestions
      if (letters.length >= triggerAmount) {
        timer = setTimeout(() => {
          fetchSuggestions(letters);
        }, 300);
      } else {
        suggestionsDropdown.innerHTML = ""; // Delete suggestions if less than trigger amount
      }
    });
  }

  /**
   * Fetches suggestions from, API
   * @param {string} letters - string for autocomplete of location
   */
  function fetchSuggestions(letters) {
    fetch(`/location_autocomplete/?letters=${letters}`)
      .then((response) => {
        if (!response.ok) {
          console.log("Autocomplete response was not ok");
        }
        return response.json();
      })
      .then((data) => {
        displaySuggestions(data);
      })
      .catch((error) => {
        console.error("Error fetching suggestions:", error);
      });
  }
  /**
   *Displays suggestions in suggestion dropdown box
   * @param {Array} suggestions - array of suggested locations from DB
   */
  function displaySuggestions(suggestions) {
    const input = document.getElementById("locationInput");
    const suggestionsDropdown = document.getElementById("suggestions-dropdown");
    const locationLongitude = document.getElementById("longitude");
    const locationLatitude = document.getElementById("latitude");
    suggestionsDropdown.innerHTML = "";
    console.log("Displaying suggestions");
    // Hint
    let hint = document.createElement("option");
    hint.textContent = "Confirm your location";
    hint.disabled = true;
    suggestionsDropdown.appendChild(hint);

    // Display suggestions in the dropdown
    suggestions.forEach((location) => {
      const option = document.createElement("div");
      option.textContent = location.name;
      option.classList.add("suggestion-item");
      option.addEventListener("click", function () {
        input.value = location.name; // Set input value to selected location
        suggestionsDropdown.innerHTML = ""; // Clear suggestions
        // Setting longitude and latitude hidden inputs
        locationLongitude.value = location.longitude;
        locationLatitude.value = location.latitude;
      });
      suggestionsDropdown.appendChild(option);
    });
  }

  // Return the function to make it accessible outside the module
  return {
    autocomplete: autocomplete,
    fetchSuggestions: fetchSuggestions,
  };
})();

/**
 * Module for getting nearest airport from DB based on given locatioin in input
 */
const NearestAirportsModule = (function () {
  function initiate() {
    const suggestionsDropdown = document.getElementById("suggestions-dropdown");
    suggestionsDropdown.addEventListener("click", nearestAirports);
  }

  /**
   * Gets cookie from document, used for getting a csrf token
   * @param {string} name - "csrftoken"
   * @returns string csrftoken
   */
  function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(";").shift();
  }

  /**
   * Fetches nearest airports for location in the form
   */
  function nearestAirports() {
    const locationLongitude = document.getElementById("longitude").value;
    const locationLatitude = document.getElementById("latitude").value;
    const requestedAmount = 5; //Amount of airports fetched
    const apiURL = "/nearest_airport/";
    const csrftoken = getCookie("csrftoken");

    const requestData = {
      // profile: 'your_profile_value',  // Replace with the actual profile value
      latitude: locationLatitude,
      longitude: locationLongitude,
      req_amount: requestedAmount,
    };

    // Stops submit, fetches nearest airports, displays destinations recomendations

    // Fetch nearest airports
    console.log("fetching");
    fetch(apiURL, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": csrftoken,
      },
      body: JSON.stringify(requestData),
    })
      .then((response) => {
        if (!response.ok) {
          console.error("Fetch nearest airport failed");
          throw new Error("Network response was not ok.");
        }

        return response.json();
      })
      .then((data) => {
        displayNearestAirports(data);
      })
      .catch((error) => {
        console.error("Error fetching nearest airports:", error);
      });
  }

  /**
   * Displays airports in the airportSelect element
   * @param {json} data - json of airport data
   */
  function displayNearestAirports(data) {
    console.log(data);
    // Get select element
    const airportSelect = document.getElementById("airportSelect");
    // Remove old options
    while (airportSelect.childElementCount > 1) {
      airportSelect.removeChild(airportSelect.lastChild);
    }

    // For each airport in the array
    data.nearest_airports.forEach((airport) => {
      // Create new option
      const airportOption = document.createElement("option");
      airportOption.textContent = airport.name;
      airportOption.dataset.id = airport.id;
      airportSelect.appendChild(airportOption);
    });
  }

  // Return functions to be accessible outside the module
  return {
    initiate: initiate,
  };
})();

/**
 * Module for travel form functionality
 */
const TravelProfileModule = (function () {
  function initiate() {
    const editProfileButton = document.getElementById("edit-profile-button");
    if (editProfileButton) {
      editProfileButton.addEventListener("click", editProfile);
    }

    const newProfileButton = document.getElementById("new-profile-button");
    newProfileButton.addEventListener("click", createNewProfile);

    const findAirportsButton = document.getElementById("find-airports-button");
    findAirportsButton.addEventListener("click", () => {
      const input = document.getElementById("locationInput").value;
      AutocompleteModule.fetchSuggestions(input);
    });
  }

  /**
   * Submits travel form to the /update_profile/
   */
  function submitTravelProfile() {
    form = document.getElementById("travelProfileForm");
    // Show loading animation
    document.getElementById("loaderSection").style.display = "block";

    // Serialize form data
    const formData = new FormData(form);

    console.log(formData);

    // Fetch API to send form data
    fetch("/update_profile/", {
      method: "POST",
      body: formData,
    })
      .then((response) => response.json())
      .then((data) => {
        data_json = JSON.parse(data);
        let message = data_json.message;
        let profile_data = data_json.profile_data;
        console.log(message, profile_data);

        // Redirect to cusatom trip page
        document.getElementById("loaderSection").style.display = "none";
        window.location.replace("/custom_trip");
      })
      .catch((error) => {
        console.error("Error when updating profile:", error);
        document.getElementById("loader").style.display = "none";
      });
  }

  /**
   * Prefils the form when a profile is selected, uses travelProfilesJSON variable accessed from django form template
   * @param {number} selectedProfileId - Selected profile ID
   */
  function fillProfileForm(selectedProfileId) {
    console.log("Travel profiles: ", travelProfilesJSON);

    // Form inputs
    const travelProfileId = document.getElementById("travelProfileId");
    const adultAmount = document.getElementById("adultAmount");
    const childrenAmount = document.getElementById("childrenAmount");
    const vacationType = document.getElementById("vacationType");
    const activityPreference = document.getElementById("activityPreference");
    const diningPreference = document.getElementById("diningPreference");
    const locationInput = document.getElementById("locationInput");
    const airportSelect = document.getElementById("airportSelect");

    // Set the hidden input value to "new" or to ID number of edited profile
    travelProfileId.value = selectedProfileId;

    // Check if the "New profile" option is selected
    if (selectedProfileId === "new") {
      // Clear all input fields except for profileName
      adultAmount.value = 1;
      childrenAmount.value = 0;
      vacationType.value = "";
      locationInput.value = "";
      airportSelect.value = "";
      activityPreference.value = "";
      diningPreference.value = "";
    }
    // Editing existing profile
    else {
      // Fetch the profile data based on the selected profile ID
      let selectedProfile = travelProfilesJSON.find(
        (profile) => profile.id == selectedProfileId
      );

      console.log("Filling profile", selectedProfile);
      // Update the input fields
      adultAmount.value = selectedProfile.adults;
      childrenAmount.value = selectedProfile.children;
      locationInput.value = selectedProfile.autocomplete_city.name;
      activityPreference.value = selectedProfile.activity_preference.name;
      diningPreference.value = selectedProfile.dining_preference.name;
      // IF Vacationi type does not exist
      try {
        vacationType.value = selectedProfile.vacation_type.name;
      } catch (error) {
        vacationType.value = "";
      }
      fillOptions(selectedProfile.preffered_airports, airportSelect);

      /**
       * Displays options in an select element
       * @param {*} optionArray - Array of options for display
       * @param {*} selectElement - Select element to which should options be added
       */
      function fillOptions(optionArray, selectElement) {
        // Creates options for given select object based on given option array
        console.log("array: ", optionArray);
        optionArray.forEach((item) => {
          // Check if option with the same id already exists
          console.log(selectElement.options);
          Array.from(selectElement.options).forEach((option) => {
            console.log(`ID: ${option.dataset.id}`);
          });
          const existingOption = Array.from(selectElement.options).find(
            (option) => option.dataset.id === item.id.toString()
          );
          console.log(existingOption);
          if (!existingOption) {
            let option = document.createElement("option");
            option.textContent = item.name;
            option.value = item.name;
            option.selected = true;
            option.dataset.id = item.id;
            selectElement.appendChild(option);
          }
        });
      }
    }
  }
  // Function for "New profile" button.
  function createNewProfile() {
    fillProfileForm("new");
    nextPrev(1);
  }

  // Function for the "Edit profile" button.
  function editProfile() {
    // Get the selected profile ID from the dropdown
    const select = document.getElementById("travelProfileSelect");
    var selectedProfileId = document.getElementById("travelProfileSelect")
      .options[select.selectedIndex].value;

    console.log(`Filling for with profile: ${selectedProfileId}`);
    fillProfileForm(selectedProfileId);
    nextPrev(1);
  }

  return {
    initiate: initiate,
    submitTravelProfile: submitTravelProfile,
  };
})();

function showTab(n) {
  // This function will display the specified tab of the form ...
  var x = document.getElementsByClassName("tab");
  x[n].style.display = "block";
  // ... and fix the Previous/Next buttons:
  if (n == 0) {
    document.getElementById("prevBtn").style.display = "none";
    document.getElementById("nextBtn").style.display = "none";
  } else {
    document.getElementById("prevBtn").style.display = "inline";
    document.getElementById("nextBtn").style.display = "inline";
  }
  if (n == x.length - 1) {
    document.getElementById("nextBtn").innerHTML = "Save profile";
  } else {
    document.getElementById("nextBtn").innerHTML = "Next";
  }
  // ... and run a function that displays the correct step indicator:
  fixStepIndicator(n);
}

function nextPrev(n) {
  // This function will figure out which tab to display
  var x = document.getElementsByClassName("tab");
  // Exit the function if any field in the current tab is invalid:
  if (n == 1 && !validateForm()) return false;

  // Hide the current tab:
  x[currentTab].style.display = "none";
  // Increase or decrease the current tab by 1:
  currentTab = currentTab + n;
  console.log(`currentTab changed to ${currentTab}`);

  // if you have reached the end of the form... :
  if (currentTab >= x.length) {
    //...the form gets submitted:
    TravelProfileModule.submitTravelProfile();
    return false;
  }
  // Otherwise, display the correct tab:
  showTab(currentTab);
}

function validateForm() {
  // This function deals with validation of the form fields
  var x,
    y,
    i,
    valid = true;
  x = document.getElementsByClassName("tab");

  y = x[currentTab].getElementsByTagName("input");
  // A loop that checks every input field in the current tab:
  for (i = 0; i < y.length; i++) {
    // If a field is empty...
    if (y[i].value == "") {
      // add an "invalid" class to the field:
      y[i].className += " invalid";
      // and set the current valid status to false:
      valid = false;
    }
  }
  // If the valid status is true, mark the step as finished and valid:
  if (valid) {
    document.getElementsByClassName("step")[currentTab].className += " finish";
  }
  return valid; // return the valid status
}

function fixStepIndicator(n) {
  // This function removes the "active" class of all steps...
  var i,
    x = document.getElementsByClassName("step");
  for (i = 0; i < x.length; i++) {
    x[i].className = x[i].className.replace(" active", "");
  }
  //... and adds the "active" class to the current step:
  x[n].className += " active";
}

// Setting up a currentTab variable, which stores displayed tab of travel form
var currentTab = 0;

// Initiate all tabs after DOM is loaded, show tab 0
document.addEventListener("DOMContentLoaded", function () {
  TravelProfileModule.initiate();
  AutocompleteModule.autocomplete();
  NearestAirportsModule.initiate();

  showTab(currentTab); // Display the current tab
  console.log("DOMContentLoaded", `${currentTab}`);
});
