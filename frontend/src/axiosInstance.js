import axios from "axios";

const baseURL = import.meta.env.VITE_BACKEND_BASE_API; // ex: "http://127.0.0.1:8000/api/v1/"
const apiBase = baseURL.endsWith("/") ? baseURL : baseURL + "/";
console.log("API Base URL:", baseURL);

const ance = axios.create({
  baseURL: apiBase,
  headers: {
    "Content-Type": "application/json",
  },
});

// Request interceptor
ance.interceptors.request.use(
  function (config) {
    const accessToken = localStorage.getItem("access_token");
    if (accessToken) {
      // s'assure que headers existe
      config.headers = config.headers || {};
      config.headers["Authorization"] = `Bearer ${accessToken}`;
    }
    return config;
  },
  function (error) {
    return Promise.reject(error);
  }
);

// Response interceptor
ance.interceptors.response.use(
  function (response) {
    return response;
  },
  async function (error) {
    const originalRequest = error.config || {};

    // Garde-fous: pas de response (CORS/réseau), ou déjà retenté, ou endpoint refresh
    if (
      !error.response ||
      originalRequest._retry ||
      (originalRequest.url && originalRequest.url.includes("token/refresh/"))
    ) {
      return Promise.reject(error);
    }

    // 401 => essayer de rafraîchir
    if (error.response.status === 401) {
      originalRequest._retry = true;

      const refreshToken = localStorage.getItem("refresh_token");
      if (!refreshToken) {
        // pas de refresh -> nettoyage + redirection
        localStorage.removeItem("access_token");
        localStorage.removeItem("refresh_token");
        window.location.href = "/login";
        return Promise.reject(error);
      }

      try {
        // Utiliser l'instance axios "globale" pour éviter l'interceptor et boucles
        const resp = await axios.post(`${apiBase}token/refresh/`, {
          refresh: refreshToken,
        });

        const newAccess = resp.data?.access;
        if (!newAccess) {
          throw new Error("No access token in refresh response");
        }

        localStorage.setItem("access_token", newAccess);
        // Réessayer la requête initiale avec le nouveau token
        originalRequest.headers = originalRequest.headers || {};
        originalRequest.headers["Authorization"] = `Bearer ${newAccess}`;
        return ance(originalRequest);
      } catch (e) {
        // refresh échoué -> cleanup + redirection
        localStorage.removeItem("access_token");
        localStorage.removeItem("refresh_token");
         window.location.href = "/login";
        return Promise.reject(e);
      }
    }

    return Promise.reject(error);
  }
);

export default ance;