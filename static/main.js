console.log("cookies:", document.cookie);
let user = getCookie("USER");
let activeSocket = { Id: 0 };
let selectingWaypoint = false;
let chosenMarker = null;

function clearCookies() {
  // get all the cookies as a string
  let cookies = document.cookie;
  // split the string by semicolons into an array
  let cookieArray = cookies.split(";");
  // loop through the array
  for (let i = 0; i < cookieArray.length; i++) {
    // get the current cookie name by trimming any whitespace and removing the value
    let cookieName = cookieArray[i].trim().split("=")[0];
    // set the expiration date to a past date
    document.cookie = cookieName + "=; expires=Thu, 01 Jan 1970 00:00:00 GMT";
  }
}

const tallinnCenter = [59.4270, 24.7256];
// Create a map object and set the view to a given center and zoom level
let map = L.map('map').setView(tallinnCenter, 13);

// Add a tile layer from OpenStreetMap
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
  attribution: '© <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors'
}).addTo(map);

async function login(username, password) {
  let data = {
    Username: username,
    Password: password
  };
  // convert the data to a string
  let body = JSON.stringify(data);
  // create an options object with the headers and body
  let options = {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: body
  };
  // use fetch to send the request to the api endpoint
  document.cookie = "";
  let result = await (await fetch('/api/user/login', options)).json();
  document.cookie = "USER="+result.Id+";";

  console.log("cookies after login:", document.cookie);

  return result;
}

async function register(username, email, password) {
  let data = {
    Username: username,
    Email: email,
    Password: password
  };
  // convert the data to a string
  let body = JSON.stringify(data);
  // create an options object with the headers and body
  let options = {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: body
  };
  // use fetch to send the request to the api endpoint
  document.cookie = "";
  let result = await (await fetch('/api/user/register', options)).json();
  document.cookie = "USER="+result.Id+";";

  return result;
}

async function updateActive() {
  // create an options object with the headers and body
  let options = {
    method: 'GET'
  };
  // use fetch to send the request to the api endpoint
  let result = await (await fetch('/api/socket?Id='+activeSocket.Id, options)).json();

  activeSocket = result;
  showSocket(activeSocket);
}

async function rate(socketID, rating, description) {
  let data = {
    BelongsTo: socketID,
    Author: parseInt(user, 10),
    Content: description,
    Rating: rating,
  };
  // convert the data to a string
  let body = JSON.stringify(data);
  // create an options object with the headers and body
  let options = {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: body
  };
  // use fetch to send the request to the api endpoint
  let result = await (await fetch('/api/review', options)).json();

  return result;
}

async function create(coords, address, description) {
  let data = {
    Latitude: coords.lat,
    Longitude: coords.lng,
    Address: address,
    Description: description
  };
  // convert the data to a string
  let body = JSON.stringify(data);
  // create an options object with the headers and body
  let options = {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: body
  };
  // use fetch to send the request to the api endpoint
  let result = await (await fetch('/api/socket', options)).json();

  return result;
}

async function edit(socketID, address, description) {
  let data = {
    SocketId: socketID,
    NewAddress: address,
    NewDescription: description
  };
  // convert the data to a string
  let body = JSON.stringify(data);
  // create an options object with the headers and body
  let options = {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json'
    },
    body: body
  };
  // use fetch to send the request to the api endpoint
  let result = await (await fetch('/api/socket', options)).json();

  return result;
}

async function socketDelete(socketID) {
  let data = {
    SocketId: socketID
  };
  // convert the data to a string
  let body = JSON.stringify(data);
  // create an options object with the headers and body
  let options = {
    method: 'DELETE',
    headers: {
      'Content-Type': 'application/json'
    },
    body: body
  };
  // use fetch to send the request to the api endpoint
  let result = await (await fetch('/api/socket', options)).json();
  console.log(result)

  return result;
}

async function logout() {
  clearCookies();
}

function addReview(review) {
  let reviewsListElement = document.getElementById("reviews");

  let reviewsElement = document.createElement("div");
  reviewsElement.classList.add("review", "column", "g8", "p8");
  reviewsElement.innerHTML = `
    <span class="rating"><b>${review.Rating.toFixed(1)}</b> / 5</span>
    ${
      review.Content ? (
        `<p class="description width100">${review.Content}</p>`
      ) : (
        `<i class="description width100">Kirjeldus puudub</i>`
      )
    }
  `;
  
  reviewsListElement.appendChild(reviewsElement);
}

function showSocket(socket) {
  activeSocket = socket;

  let viewElements = document.getElementById("view").children;
  for(let i = 0; i < viewElements.length; i++) {
    viewElements[i].style.display = "none";
  }
  
  let viewElement = document.getElementById("socket-view");
  viewElement.style.display = "flex";

  // Add information

  viewElement.querySelector(".address").innerHTML = socket.Address;
  viewElement.querySelector(".rating").innerHTML = `<span class="rating"><b>${socket.AverageRating.toFixed(1)}</b> / 5</span>`;
  viewElement.querySelector(".description").innerHTML = socket.Description;

  // Add reviews

  let reviewsListElement = document.getElementById("reviews");
  reviewsListElement.innerHTML = "";

  if(Array.isArray(socket.Reviews)) for(let review of socket.Reviews) {
    addReview(review);
  }
}

let markerGroup = L.layerGroup().addTo(map);

function socketListClear() {
  document.getElementById("list-view").querySelector(".locations").innerHTML = "";
}

function addSocketToList(socket) {
  let socketElement = document.createElement("div");
  socketElement.classList.add("location");
  socketElement.innerHTML = `
    <div class="line center-cross">
      <b class="name">${socket.Address}</b>
      <span class="rating"><b>&nbsp;•&nbsp;${socket.AverageRating.toFixed(1)}</b> / 5</span>
    </div>
    <p class="description width100 truncate">${socket.Description}</p>
    <button class="open">Vaata</button>
  `;

  socketElement.querySelector("button").onclick = () => showSocket(socket);

  document.getElementById("list-view").querySelector(".locations").appendChild(socketElement);
}

// add an event listener for the moveend event
async function onMove() {
  // get the bounding coordinates of the current map view
  let bounds = map.getBounds();
  let southWest = bounds.getSouthWest();
  let northEast = bounds.getNorthEast();

  // fetch waypoints from api using the bounding coordinates as parameters
  let data = await (await fetch(`/api/socket?BottomLeftLatitude=${southWest.lat}&BottomLeftLongitude=${southWest.lng}&TopRightLatitude=${northEast.lat}&TopRightLongitude=${northEast.lng}`)).json();
  
  markerGroup.clearLayers();
  socketListClear();

  if(Array.isArray(data)) for (let socket of data) {
    let marker = L.marker([socket.Latitude, socket.Longitude]).addTo(map).on('click', function() {
      showSocket(socket);
    });
    addSocketToList(socket);
    addSocketToList(socket);
    addSocketToList(socket);
    markerGroup.addLayer(marker);
  }
}

onMove();
map.on('moveend', onMove);

async function onClick(e) {
  if(!selectingWaypoint) return;

  let lat = e.latlng.lat;
  let lng = e.latlng.lng;

  chosenMarker = L.marker([lat, lng]);
  markerGroup.addLayer(chosenMarker);

  document.getElementById("add-dialog").style.display = "flex";

  selectingWaypoint = false;
}
map.on('click', onClick);

document.getElementById("show-login").onclick = async () => {
  document.getElementById("login-dialog").style.display = "flex";
}

document.getElementById("login-submit").onclick = async () => {
  await login(
    document.getElementById("login-username").value,
    document.getElementById("login-password").value
  );

  document.getElementById("login-dialog").style.display = "none";
  window.location.reload();
};

document.getElementById("show-register").onclick = async () => {
  document.getElementById("register-dialog").style.display = "flex";
}

document.getElementById("register-submit").onclick = async () => {
  await register(
    document.getElementById("register-username").value,
    document.getElementById("register-email").value,
    document.getElementById("register-password").value
  );

  document.getElementById("register-dialog").style.display = "none";
  window.location.reload();
};

document.getElementById("logout").onclick = async () => {
  await logout();
  window.location.reload();
}

document.getElementById("socket-back").onclick = async () => {
  let viewElements = document.getElementById("view").children;
  for(let i = 0; i < viewElements.length; i++) {
    viewElements[i].style.display = "none";
  }
  
  let viewElement = document.getElementById("list-view");
  viewElement.style.display = "flex";
}

document.getElementById("reviews-back").onclick = async () => {
  let viewElements = document.getElementById("view").children;
  for(let i = 0; i < viewElements.length; i++) {
    viewElements[i].style.display = "none";
  }
  
  let viewElement = document.getElementById("socket-view");
  viewElement.style.display = "flex";
}

document.getElementById("reviews-show").onclick = async () => {
  let viewElements = document.getElementById("view").children;
  for(let i = 0; i < viewElements.length; i++) {
    viewElements[i].style.display = "none";
  }
  
  let viewElement = document.getElementById("reviews-view");
  viewElement.style.display = "flex";
}

document.getElementById("rate-close").onclick = async () => {
  document.getElementById("rate-dialog").style.display = "none";
}

document.getElementById("rate-show").onclick = async () => {
  if(!user) {  
    document.getElementById("login-dialog").style.display = "flex";

    return;
  }

  document.getElementById("rate-dialog").style.display = "flex";
}

document.getElementById("rate-submit").onclick = async () => {
  addReview(await rate(
    activeSocket.Id,
    parseInt(document.getElementById("rate-rating").value),
    document.getElementById("rate-content").value
  ));
  await updateActive();

  document.getElementById("rate-dialog").style.display = "none";
}

document.getElementById("add-back").onclick = async () => {
  let viewElements = document.getElementById("view").children;
  for(let i = 0; i < viewElements.length; i++) {
    viewElements[i].style.display = "none";
  }
  
  let viewElement = document.getElementById("list-view");
  viewElement.style.display = "flex";
  selectingWaypoint = false;
}

document.getElementById("add-show").onclick = async () => {
  if(!user) {  
    document.getElementById("login-dialog").style.display = "flex";

    return;
  }

  let viewElements = document.getElementById("view").children;
  for(let i = 0; i < viewElements.length; i++) {
    viewElements[i].style.display = "none";
  }

  document.getElementById("add-view").style.display = "flex";
  selectingWaypoint = true;
}

document.getElementById("add-close").onclick = async () => {
  document.getElementById("add-dialog").style.display = "none";

  let viewElements = document.getElementById("view").children;
  for(let i = 0; i < viewElements.length; i++) {
    viewElements[i].style.display = "none";
  }

  document.getElementById("list-view").style.display = "flex";
}

document.getElementById("add-submit").onclick = async () => {
  let socket = await create(
    chosenMarker.getLatLng(),
    document.getElementById("add-address").value,
    document.getElementById("add-description").value
  );
  activeSocket = socket;
  showSocket(activeSocket);

  let marker = L.marker([socket.Latitude, socket.Longitude]).addTo(map).on('click', function() {
    showSocket(socket);
  });
  addSocketToList(socket);
  markerGroup.addLayer(marker);
  chosenMarker = null;

  document.getElementById("add-dialog").style.display = "none";
}

document.getElementById("login-close").onclick = async () => {
  document.getElementById("login-dialog").style.display = "none";
}

document.getElementById("register-close").onclick = async () => {
  document.getElementById("register-dialog").style.display = "none";
}

document.getElementById("edit-show").onclick = async () => {
  if(!user) {  
    document.getElementById("login-dialog").style.display = "flex";

    return;
  }

  document.getElementById("edit-dialog").style.display = "flex";
  document.getElementById("edit-address").value = activeSocket.Address;
  document.getElementById("edit-description").value = activeSocket.Description;
}

document.getElementById("edit-close").onclick = async () => {
  document.getElementById("edit-dialog").style.display = "none";
}

document.getElementById("edit-submit").onclick = async () => {
  let socket = await edit(
    activeSocket.Id,
    document.getElementById("edit-address").value,
    document.getElementById("edit-description").value
  );

  await updateActive();
  
  onMove();

  document.getElementById("edit-dialog").style.display = "none";
}

document.getElementById("delete").onclick = async () => {
  if(!user) {  
    document.getElementById("login-dialog").style.display = "flex";

    return;
  }

  await socketDelete(activeSocket.Id);
  onMove();
}

function getCookie(name) {
  // append an equal sign to the name
  let nameEQ = name + "=";
  // split the cookie string by semicolons into an array
  let cookies = document.cookie.split(";");
  // loop through the array
  for (let i = 0; i < cookies.length; i++) {
    // trim any whitespace from the current cookie
    let cookie = cookies[i].trim();
    // check if the current cookie starts with the name we want
    if (cookie.startsWith(nameEQ)) {
      // return the value after the equal sign
      return cookie.substring(nameEQ.length);
    }
  }
  // return null if no cookie is found
  return null;
}

if(user) {
  console.log("Logged in");
  document.getElementById("logged-in").style.display = "flex";
  document.getElementById("logged-out").style.display = "none";
}







// Add a routing control with two waypoints
// L.Routing.control({
//   waypoints: [
//     L.latLng(59.4370, 24.7536),
//     L.latLng(59.4349, 24.7281)
//   ]
// }).addTo(map);

// Generate 10 random waypoints within the map bounds
/* let waypoints = [];
let bounds = map.getBounds();
let southWest = bounds.getSouthWest();
let northEast = bounds.getNorthEast();
for (let i = 0; i < 80; i++) {
  let lat = tallinnCenter[0] + (Math.random() * 0.03 - 0.015);
  let lng = tallinnCenter[1] + (Math.random() * 0.08 - 0.04);
  L.marker([ lat, lng ]).addTo(map);
  // waypoints.push(L.latLng(lat, lng));
} */

// Create a marker cluster group and add the waypoints to it
// let markers = L.markerClusterGroup();
// for (let i = 0; i < waypoints.length; i++) {
//   markers.addLayer(L.marker(waypoints[i]));
// }
// map.addLayer(markers);
