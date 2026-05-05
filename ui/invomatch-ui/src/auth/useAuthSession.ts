import { useContext } from "react";
import { AuthSessionContext } from "./AuthSessionContext";
import type { AuthSessionContextValue } from "./sessionTypes";

export function useAuthSession(): AuthSessionContextValue {
  const context = useContext(AuthSessionContext);

  if (!context) {
    throw new Error("useAuthSession must be used within AuthSessionProvider.");
  }

  return context;
}