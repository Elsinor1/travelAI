/**
 * Shows offers that match selected profile, hide other
 * @returns None
 */
function showOffers() {
  const travelProfileSelect = document.getElementById("travel-profiles-select");
  const profileId = travelProfileSelect.value;

  if (profileId === "disabled") {
    return;
  }

  const displayedOffers = document.getElementsByClassName(
    "custom-offer-container"
  );

  for (const offer of displayedOffers) {
    if (offer.dataset.profile === profileId) {
      offer.style.display = "block";
    } else {
      offer.style.display = "none";
    }
    console.log("Showing offers");
  }
}

/**
 * Redirection to editing profiles. Useed for edit profile button
 */
function redirectToProfiles() {
  // Redirect to the travel_profile page
  window.location.href = "/travel_profile";
}

/**
 * Creates new container and displayes new travel offer
 * @param {json} offerJson -Json with travel offer data
 */
function displayTravelOffer(offerJson) {
  // Check offerJson is valid
  if (offerJson.itinerary === null) {
    alert("Cannot generate further offers for selected profile");
    return false;
  }
  let container = document.createElement("div");
  container.classList.add("container", "custom-offer-container");
  container.dataset.profile = offerJson.travel_profile;
  container.dataset.id = offerJson.id;
  container.style.display = "block";

  // Array to store image URLs
  let imagesHTML = "";

  // Images carousel HTML preparation
  // Prepare variable for the loop
  let isActive = "";
  // Iterate over each image
  for (let x in offerJson.image) {
    // If it is a first element, add active class
    if (x === "0") {
      isActive = "active";
    } else {
      isActive = "";
    }

    // Fill the html with name and url
    let html = `
        <div class="carousel-item ${isActive}">
          <img src="${offerJson.image[x].url}" class="d-block carousel-image" alt="${offerJson.image[x].name}">
        </div>`;
    // Append it to the images html
    imagesHTML += html;
  }

  // Calculate ticket cost
  let ticketCost =
    parseInt(offerJson.return_routes[0].price) +
    parseInt(offerJson.departure_routes[0].price);

  // Populate container with offer details
  container.innerHTML = `
    <div class="row">
    <div class="col-md-8">
        <div class="offer-details">
            <a href="/display_offer/${offerJson.id}">
                <h3 class="offer-title">${offerJson.itinerary.Label}</h3>
            </a> 
            <p class="offer-description">${offerJson.itinerary.Description}</p>
            <p class="offer-route">From: ${offerJson.origin_airport.name} To: ${offerJson.destination_airport.name}</p>
            <p class="offer-price">Flight tickets ~${ticketCost}$</p>
        </div>
    </div>
    <div class="col-md-4">
        <div id="carousel-${offerJson.id}" class="carousel slide" data-bs-ride="carousel">
            <div class="carousel-inner">
                ${imagesHTML}
            </div>
            <button class="carousel-control-prev" type="button" data-bs-target="#carousel-${offerJson.id}" data-bs-slide="prev">
                <span class="carousel-control-prev-icon" aria-hidden="true"></span>
                <span class="visually-hidden">Previous</span>
            </button>
            <button class="carousel-control-next" type="button" data-bs-target="#carousel-${offerJson.id}" data-bs-slide="next">
                <span class="carousel-control-next-icon" aria-hidden="true"></span>
                <span class="visually-hidden">Next</span>
            </button>
        </div>
    </div>
  </div>
  `;

  // Append container to the custom-offer-list div
  const offerList = document.getElementById("custom-offer-list");
  offerList.insertBefore(container, offerList.lastChild.previousSibling);
  return true;
}

/**
 * Fetches new offer using get_new_offer API, displays loader animation during fetching
 * @returns None
 */
function generateNewOffer() {
  const travelProfileSelect = document.getElementById("travel-profiles-select");
  const profileId = travelProfileSelect.value;

  if (profileId === "disabled") {
    alert("Choose travel profile before generating new offers");
    return;
  }

  // Hide button and show loader animation
  const generateOfferButton = document.getElementById("generate-offer-button");
  generateOfferButton.style.display = "none";

  const loaderAnimation = document.getElementById("customTripLoader");
  loaderAnimation.style.display = "block";

  // API URL
  const API_URL = `/get_new_offer?travel_profile_id=${profileId}`;
  // Fetch new offer
  fetch(API_URL)
    .then((response) => {
      if (!response.ok) {
        console.error("Fetch of travel offer failed");
        throw new Error("Network response was not ok.");
      }
      return response.json();
    })
    .then((data) => {
      displayTravelOffer(data);
      // Show button and hide loader animation
      generateOfferButton.style.display = "block";
      loaderAnimation.style.display = "none";
    })
    .catch((error) => {
      console.error("Error fetching travel offer:", error);
    });
}
