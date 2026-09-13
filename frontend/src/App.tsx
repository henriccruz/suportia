import { useState, useEffect } from "react";
import { NavLink, Route, Routes, useNavigate } from "react-router-dom";
import { isAuthenticated, clearToken } from "./lib/auth";
import Login from "./components/Login";
import DashboardPage from "./pages/index";
import TicketPage from "./pages/tickets";
import AnalyticsPage from "./pages/analytics";
import SettingsPage from "./pages/settings";

function AppContent() {
  const [authenticated, setAuthenticated] = useState(isAuthenticated());
  const navigate = useNavigate();

  useEffect(() => {
    setAuthenticated(isAuthenticated());
  }, []);

  function handleLoginSuccess() {
    setAuthenticated(true);
    navigate("/dashboard");
  }

  function handleLogout() {
    clearToken();
    setAuthenticated(false);
    navigate("/");
  }

  if (!authenticated) {
    return <Login onLoginSuccess={handleLoginSuccess} />;
  }

  return (
    <>
      <nav className="topnav">
        <span className="brand">SuportIA</span>
        <NavLink to="/dashboard" className={({ isActive }) => (isActive ? "active" : "")}>
          Dashboard
        </NavLink>
        <NavLink to="/analytics" className={({ isActive }) => (isActive ? "active" : "")}>
          Analytics
        </NavLink>
        <NavLink to="/settings" className={({ isActive }) => (isActive ? "active" : "")}>
          Configurações
        </NavLink>
        <button
          className="btn btn-secondary"
          style={{ marginLeft: "auto" }}
          onClick={handleLogout}
        >
          Sair
        </button>
      </nav>
      <div className="container">
        <Routes>
          <Route path="/" element={<DashboardPage />} />
          <Route path="/dashboard" element={<DashboardPage />} />
          <Route path="/tickets/:id" element={<TicketPage />} />
          <Route path="/analytics" element={<AnalyticsPage />} />
          <Route path="/settings" element={<SettingsPage />} />
        </Routes>
      </div>
    </>
  );
}

export default AppContent;
