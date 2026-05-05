"use client";

import { useEffect, useState } from "react";
import { DashboardLayout } from "@/components/layout/dashboard-layout";
import { Card, CardHeader, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { useIntegrations } from "@/hooks/use-integrations";

interface YouTubeAccount {
  id: string;
  account_name: string;
  channel_id: string;
  is_connected: boolean;
  connected_at: string | null;
}

export default function SettingsPage() {
  const {
    loading,
    error,
    getYouTubeStatus,
    connectYouTube,
    disconnectYouTube,
    getChannelInfo,
  } = useIntegrations();

  const [ytConfigured, setYtConfigured] = useState(false);
  const [ytAccounts, setYtAccounts] = useState<YouTubeAccount[]>([]);
  const [brandId, setBrandId] = useState("");
  const [channelDetails, setChannelDetails] = useState<Record<string, any> | null>(null);

  useEffect(() => {
    loadYouTubeStatus();
  }, []);

  const loadYouTubeStatus = async () => {
    const status = await getYouTubeStatus();
    if (status) {
      setYtConfigured(status.configured);
      setYtAccounts(status.connected_accounts);
    }
  };

  const handleConnect = async () => {
    if (!brandId) return;
    const authUrl = await connectYouTube(brandId);
    if (authUrl) {
      // Redirect to YouTube OAuth
      window.location.href = authUrl;
    }
  };

  const handleDisconnect = async (accountId: string) => {
    const success = await disconnectYouTube(accountId);
    if (success) {
      await loadYouTubeStatus();
      setChannelDetails(null);
    }
  };

  const handleViewChannel = async (accountId: string) => {
    const info = await getChannelInfo(accountId);
    setChannelDetails(info);
  };

  return (
    <DashboardLayout>
      <div className="max-w-4xl">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-2xl font-bold text-gray-900">Settings</h1>
          <p className="text-sm text-gray-500 mt-1">
            Platform integrations dan konfigurasi
          </p>
        </div>

        {/* YouTube Integration */}
        <Card className="mb-6">
          <CardHeader>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-lg bg-red-100 flex items-center justify-center">
                  <svg className="w-6 h-6 text-red-600" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z" />
                  </svg>
                </div>
                <div>
                  <h2 className="text-lg font-semibold text-gray-900">YouTube</h2>
                  <p className="text-sm text-gray-500">
                    Upload dan scheduled publish ke YouTube
                  </p>
                </div>
              </div>
              {ytConfigured ? (
                <Badge variant="success">Configured</Badge>
              ) : (
                <Badge variant="warning">Not Configured</Badge>
              )}
            </div>
          </CardHeader>
          <CardContent>
            {!ytConfigured ? (
              <div className="p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
                <p className="text-sm text-yellow-800">
                  YouTube OAuth belum dikonfigurasi. Set <code className="bg-yellow-100 px-1 rounded">YOUTUBE_CLIENT_ID</code> dan{" "}
                  <code className="bg-yellow-100 px-1 rounded">YOUTUBE_CLIENT_SECRET</code> di file .env
                </p>
                <p className="text-xs text-yellow-600 mt-2">
                  Dapatkan credentials dari Google Cloud Console &gt; APIs &amp; Services &gt; Credentials
                </p>
              </div>
            ) : (
              <div className="space-y-4">
                {/* Connected Accounts */}
                {ytAccounts.length > 0 && (
                  <div>
                    <h3 className="text-sm font-medium text-gray-700 mb-3">Connected Channels</h3>
                    <div className="space-y-3">
                      {ytAccounts.map((account) => (
                        <div
                          key={account.id}
                          className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
                        >
                          <div className="flex items-center gap-3">
                            <div className="w-8 h-8 rounded-full bg-red-100 flex items-center justify-center">
                              <span className="text-xs font-medium text-red-700">YT</span>
                            </div>
                            <div>
                              <p className="text-sm font-medium text-gray-900">
                                {account.account_name}
                              </p>
                              <p className="text-xs text-gray-500">
                                {account.channel_id}
                                {account.connected_at && (
                                  <> &middot; Connected {new Date(account.connected_at).toLocaleDateString("id-ID")}</>
                                )}
                              </p>
                            </div>
                          </div>
                          <div className="flex items-center gap-2">
                            {account.is_connected ? (
                              <Badge variant="success">Connected</Badge>
                            ) : (
                              <Badge variant="error">Disconnected</Badge>
                            )}
                            <Button
                              size="sm"
                              variant="ghost"
                              onClick={() => handleViewChannel(account.id)}
                            >
                              Info
                            </Button>
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() => handleDisconnect(account.id)}
                            >
                              Disconnect
                            </Button>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Channel Details */}
                {channelDetails && (
                  <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
                    <h4 className="text-sm font-medium text-blue-900 mb-2">Channel Details</h4>
                    <div className="grid grid-cols-2 gap-2 text-sm">
                      <div>
                        <span className="text-blue-600">Title:</span>{" "}
                        <span className="text-blue-900">{channelDetails.title}</span>
                      </div>
                      <div>
                        <span className="text-blue-600">Subscribers:</span>{" "}
                        <span className="text-blue-900">{channelDetails.subscriber_count || "Hidden"}</span>
                      </div>
                      <div>
                        <span className="text-blue-600">Videos:</span>{" "}
                        <span className="text-blue-900">{channelDetails.video_count || "0"}</span>
                      </div>
                      <div>
                        <span className="text-blue-600">ID:</span>{" "}
                        <span className="text-blue-900 font-mono text-xs">{channelDetails.channel_id}</span>
                      </div>
                    </div>
                  </div>
                )}

                {/* Connect New */}
                <div className="border-t border-gray-200 pt-4">
                  <h3 className="text-sm font-medium text-gray-700 mb-3">Connect New Channel</h3>
                  <div className="flex items-end gap-3">
                    <Input
                      label="Brand ID"
                      placeholder="UUID of the brand to connect"
                      value={brandId}
                      onChange={(e) => setBrandId(e.target.value)}
                      className="flex-1"
                    />
                    <Button
                      onClick={handleConnect}
                      loading={loading}
                      disabled={!brandId}
                    >
                      Connect YouTube
                    </Button>
                  </div>
                  {error && (
                    <p className="text-sm text-red-600 mt-2">{error}</p>
                  )}
                </div>
              </div>
            )}
          </CardContent>
        </Card>

        {/* TikTok Integration (Coming Soon) */}
        <Card className="mb-6 opacity-60">
          <CardHeader>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-lg bg-gray-100 flex items-center justify-center">
                  <span className="text-lg">🎵</span>
                </div>
                <div>
                  <h2 className="text-lg font-semibold text-gray-900">TikTok</h2>
                  <p className="text-sm text-gray-500">Auto-publish ke TikTok</p>
                </div>
              </div>
              <Badge>Coming Soon</Badge>
            </div>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-gray-500">
              TikTok autopost integration akan tersedia setelah validasi API dan platform constraints.
              Saat ini, konten TikTok bisa di-generate dan di-export secara manual.
            </p>
          </CardContent>
        </Card>

        {/* X Integration (Coming Soon) */}
        <Card className="opacity-60">
          <CardHeader>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-lg bg-gray-100 flex items-center justify-center">
                  <span className="text-lg font-bold">𝕏</span>
                </div>
                <div>
                  <h2 className="text-lg font-semibold text-gray-900">X (Twitter)</h2>
                  <p className="text-sm text-gray-500">Auto-publish ke X</p>
                </div>
              </div>
              <Badge>Coming Soon</Badge>
            </div>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-gray-500">
              X autopost integration akan tersedia setelah validasi API, biaya, dan kebijakan platform.
              Saat ini, konten X bisa di-generate dan di-copy secara manual.
            </p>
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  );
}
