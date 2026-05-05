"use client";

import { useState } from "react";
import { useAuth } from "@/hooks/use-auth";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

export default function LoginPage() {
  const { login, loading, error } = useAuth();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await login(username, password);
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 px-4">
      <div className="w-full max-w-sm">
        {/* Logo */}
        <div className="text-center mb-8">
          <h1 className="text-2xl font-bold text-gray-900">AI Content Studio</h1>
          <p className="text-sm text-gray-500 mt-1">Internal Content Automation Tool</p>
        </div>

        {/* Login Form */}
        <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-6">Login</h2>

          <form onSubmit={handleSubmit} className="space-y-4">
            <Input
              label="Username"
              placeholder="admin"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
              autoFocus
            />
            <Input
              label="Password"
              type="password"
              placeholder="Enter password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />

            {error && (
              <div className="p-3 bg-red-50 border border-red-200 rounded-lg">
                <p className="text-sm text-red-700">{error}</p>
              </div>
            )}

            <Button type="submit" loading={loading} className="w-full" size="lg">
              Login
            </Button>
          </form>
        </div>

        <p className="text-xs text-gray-400 text-center mt-6">
          Self-hosted internal tool. Single-user access.
        </p>
      </div>
    </div>
  );
}
