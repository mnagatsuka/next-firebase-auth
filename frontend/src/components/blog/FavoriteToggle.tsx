"use client";

import { useState } from "react";
import { Star } from "lucide-react";
import { Button } from "@/components/ui/button";
import { toast } from "sonner";
import { useAuth } from "@/hooks/useAuth";
import { useFavoritePost, useUnfavoritePost } from "@/lib/api/generated/client";

interface FavoriteToggleProps {
  postId: string;
  initialFavorited?: boolean;
}

export function FavoriteToggle({ postId, initialFavorited = false }: FavoriteToggleProps) {
  const { user, isAuthenticated, signInAnonymously } = useAuth();
  const [isFavorited, setIsFavorited] = useState<boolean>(initialFavorited);
  const [loading, setLoading] = useState<boolean>(false);

  const favMutation = useFavoritePost();
  const unfavMutation = useUnfavoritePost();

  const toggleFavorite = async () => {
    try {
      setLoading(true);
      if (!isAuthenticated || !user) {
        await signInAnonymously();
      }

      if (!isFavorited) {
        favMutation.mutate(
          { id: postId },
          {
            onSuccess: () => {
              setIsFavorited(true);
              toast.success("Added to Favorites");
            },
            onError: (e: any) => {
              toast.error(e?.message || "Failed to add favorite");
            },
            onSettled: () => setLoading(false),
          },
        );
      } else {
        unfavMutation.mutate(
          { id: postId },
          {
            onSuccess: () => {
              setIsFavorited(false);
              toast.success("Removed from Favorites");
            },
            onError: (e: any) => {
              toast.error(e?.message || "Failed to remove favorite");
            },
            onSettled: () => setLoading(false),
          },
        );
      }
    } catch (err: any) {
      const message = err?.message || "Failed to update favorite";
      toast.error(message);
      setLoading(false);
    }
  };

  return (
    <Button
      type="button"
      variant={isFavorited ? "default" : "outline"}
      size="sm"
      onClick={toggleFavorite}
      disabled={loading}
      aria-pressed={isFavorited}
      aria-label={isFavorited ? "Remove from favorites" : "Add to favorites"}
      title={isFavorited ? "Remove from favorites" : "Add to favorites"}
      className="gap-2"
    >
      <Star className="h-4 w-4" fill={isFavorited ? "currentColor" : "none"} />
      {isFavorited ? "Favorited" : "Favorite"}
    </Button>
  );
}
