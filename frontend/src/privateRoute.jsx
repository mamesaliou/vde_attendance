import { useContext } from "react";
import { AuthContext } from "./AuthProvider";
import { Navigate } from "react-router-dom";

const PrivateRoute = ({ children }) => {
  const { isLoggedIn } = useContext(AuthContext);
  const hasToken = !!localStorage.getItem("access_token"); // fallback très minimal

  return (isLoggedIn || hasToken) ? children : <Navigate to="/login" replace />;
};

export default PrivateRoute;