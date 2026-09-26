import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { VideoSearchResult } from "../../domain/models/video-search.model";
import { Badge } from "@/components/ui/badge";

interface VideoSearchResultCardProps {
    result: VideoSearchResult;
}

function formatTimestamp(timestampMs: number): string {
    const totalSeconds = Math.floor(timestampMs / 1000);
    const hours = Math.floor(totalSeconds / 3600);
    const minutes = Math.floor((totalSeconds % 3600) / 60);
    const seconds = totalSeconds % 60;

    return [hours, minutes, seconds].map((value) => value.toString().padStart(2, "0")).join(":");
}

export function VideoSearchResultCard({
    result,
}: VideoSearchResultCardProps) {
    return (
        <Card className="overflow-hidden">
            <div className="aspect-video overflow-hidden bg-muted">
                {result.imageUrl ? (
                    <img
                        src={result.imageUrl}
                        alt={`Keyframe ${result.keyframeId}`}
                        className="h-full w-full object-cover"
                    />
                ) : (
                    <div className="flex h-full w-full items-center justify-center text-xs text-muted-foreground">
                        No preview
                    </div>
                )}
            </div>

            <CardHeader>
                <div className="flex items-start justify-between gap-4">
                    <CardTitle className="text-base">
                        {result.videoId}
                    </CardTitle>

                    <Badge variant="secondary">
                        {(result.score * 100).toFixed(1)}%
                    </Badge>
                </div>
            </CardHeader>

            <CardContent className="space-y-3 text-sm">
                <div className="grid grid-cols-2 gap-2 text-muted-foreground">
                    <span>Keyframe</span>
                    <span>{result.keyframeId}</span>

                    <span>Frame</span>
                    <span>{result.frameNumber}</span>

                    <span>Timestamp</span>
                    <span>{formatTimestamp(result.timestampMs)}</span>
                </div>

                {result.matchesObjects.length > 0 && (
                    <div className="flex flex-wrap gap-2">
                        {result.matchesObjects.map((object) => (
                            <Badge
                                key={object}
                                variant="outline"
                            >
                                {object}
                            </Badge>
                        ))}
                    </div>
                )}
            </CardContent>
        </Card>
    );
}
