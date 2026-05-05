import { createContext } from "react";
import type { AuthSessionContextValue } from "./sessionTypes";

export const AuthSessionContext = createContext<AuthSessionContextValue | null>(null);