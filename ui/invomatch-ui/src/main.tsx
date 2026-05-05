import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { AuthSessionProvider } from "./auth/AuthSessionProvider";
import "./index.css";
import App from "./App.tsx";

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <AuthSessionProvider>
      <App />
    </AuthSessionProvider>
  </StrictMode>,
);