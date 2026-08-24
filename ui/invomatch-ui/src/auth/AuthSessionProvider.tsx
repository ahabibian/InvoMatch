import { useCallback, useEffect, useMemo, useState } from "react";
import type { ReactNode } from "react";
import { getAuthSession, loginAuthSession, logoutAuthSession } from "../services/api";
import type { ApiError, AuthSessionResponse } from "../services/api";
import { AuthSessionContext } from "./AuthSessionContext";
import type { AuthSessionContextValue, AuthSessionStatus } from "./sessionTypes";

type AuthSessionProviderProps = {
  children: ReactNode;
};

type SessionLoadResult =
  | {
      session: AuthSessionResponse;
      status: "authenticated";
      error: null;
    }
  | {
      session: null;
      status: "unauthenticated" | "error";
      error: string;
    };

function getSessionErrorMessage(err: unknown): string {
  const apiError = err as Partial<ApiError>;

  if (apiError?.status === 401) {
    return "Authentication is required or the configured token is missing, expired, or revoked.";
  }

  if (apiError?.status === 403) {
    return "The authenticated user is not allowed to access the application session.";
  }

  return apiError?.message ?? "Failed to load the authenticated session.";
}

function getSessionErrorStatus(err: unknown): "unauthenticated" | "error" {
  const apiError = err as Partial<ApiError>;

  if (apiError?.status === 401) {
    return "unauthenticated";
  }

  return "error";
}

async function loadAuthSession(): Promise<SessionLoadResult> {
  try {
    const response = await getAuthSession();

    return {
      session: response,
      status: "authenticated",
      error: null,
    };
  } catch (err: unknown) {
    return {
      session: null,
      status: getSessionErrorStatus(err),
      error: getSessionErrorMessage(err),
    };
  }
}

export function AuthSessionProvider({ children }: AuthSessionProviderProps) {
  const [session, setSession] = useState<AuthSessionResponse | null>(null);
  const [status, setStatus] = useState<AuthSessionStatus>("loading");
  const [error, setError] = useState<string | null>(null);

  const applySessionResult = useCallback((result: SessionLoadResult) => {
    setSession(result.session);
    setStatus(result.status);
    setError(result.error);
  }, []);

  const reloadSession = useCallback(async () => {
    setStatus("loading");
    setError(null);

    const result = await loadAuthSession();
    applySessionResult(result);
  }, [applySessionResult]);

  useEffect(() => {
    let cancelled = false;

    async function loadInitialSession() {
      const result = await loadAuthSession();

      if (!cancelled) {
        applySessionResult(result);
      }
    }

    void loadInitialSession();

    return () => {
      cancelled = true;
    };
  }, [applySessionResult]);

  const value = useMemo<AuthSessionContextValue>(() => {
    const permissions = session?.permissions ?? [];

    return {
      session,
      status,
      loading: status === "loading",
      error,
      user: session?.user ?? null,
      permissions,
      hasPermission: (permission: string) => permissions.includes(permission),
      reloadSession,
      login: async (credential: string) => {
        await loginAuthSession(credential);
        await reloadSession();
      },
      logout: async () => {
        await logoutAuthSession();
        await reloadSession();
      },
    };
  }, [error, reloadSession, session, status]);

  return (
    <AuthSessionContext.Provider value={value}>
      {children}
    </AuthSessionContext.Provider>
  );
}
