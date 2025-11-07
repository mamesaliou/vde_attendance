import { useContext } from "react"
import { AuthContext } from "./AuthProvider"
import { Navigate } from "react-router-dom"

const PublicRoute = ({children}) => {
  const { isLoggedIn } = useContext(AuthContext);
  const hasToken = !!localStorage.getItem("access_token");

  return !(isLoggedIn || hasToken) ?(
    children 
  ) : <Navigate to="/attendance" replace />;

}

export default PublicRoute