const isLocalFrontend = window.location.port === "5500"
  || ["localhost", "127.0.0.1", "::1"].includes(window.location.hostname);

window.APP_CONFIG = {
  API_URL: isLocalFrontend ? "http://127.0.0.1:8000" : "https://linearlab.onrender.com"
};
