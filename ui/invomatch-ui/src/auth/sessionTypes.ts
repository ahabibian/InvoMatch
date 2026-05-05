import type { AuthSessionResponse } from "../services/api";

export type AuthSessionStatus = "loading" | "authenticated" | "unauthenticated" | "error";

export type AuthSessionContextValue = {
  session: AuthSessionResponse | null;
  status: AuthSessionStatus;
  loading: boolean;
  error: string | null;
  user: AuthSessionResponse["user"] | null;
  permissions: string[];
  hasPermission: (permission: string) => boolean;
  reloadSession: () => Promise<void>;
};