"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";

interface User {
  id: string;
  username: string;
  is_active: boolean;
  last_login: string | null;
  created_at: string;
}

export function useAuth() {
  const router = useRouter();
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    checkAuth();
  }, []);

  const checkAuth = async () => {
    const token = localStorage.getItem("access_token");
    if (!token) {
      setLoading(false);
      return;
    }

    try {
      const response = await api.get<User>("/auth/me");
      setUser(response.data);
    } catch (err) {
      localStorage.removeItem("access_token");
      setUser(null);
    } finally {
      setLoading(false);
    }
  };

  const login = async (username: string, password: string): Promise<boolean> => {
    setError(null);
    setLoading(true);

    try {
      const response = await api.post<{ access_token: string; expires_in: number }>(
        "/auth/login/json",
        { username, password }
      );

      localStorage.setItem("access_token", response.data.access_token);

      // Fetch user info
      const userResponse = await api.get<User>("/auth/me");
      setUser(userResponse.data);

      router.push("/dashboard");
      return true;
    } catch (err: any) {
      const message = err.response?.data?.detail || "Login failed";
      setError(message);
      return false;
    } finally {
      setLoading(false);
    }
  };

  const logout = () => {
    localStorage.removeItem("access_token");
    setUser(null);
    router.push("/login");
  };

  const isAuthenticated = !!user;

  return { user, loading, error, isAuthenticated, login, logout, checkAuth };
}
