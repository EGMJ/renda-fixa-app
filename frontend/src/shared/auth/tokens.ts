export function getToken() {
  if (typeof window === "undefined") return null;
  return localStorage.getItem("auth_token");
}

export function isAuthenticated() {
  return !!getToken();
}