import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { AgentResult } from "../../domain/models/agent-search.model";

interface AgentResultCardProps {
    result: AgentResult;
    onSelect?: (videoUrl: string, timestampMs: number) => void;
}

function formatTimestamp(ms: number): string {
    const totalSeconds = Math.floor(ms / 1000);
    const hours = Math.floor(totalSeconds / 3600);
    const minutes = Math.floor((totalSeconds % 3600) / 60);
    const seconds = totalSeconds % 60;
    return [hours, minutes, seconds]
        .map((v) => v.toString().padStart(2, "0"))
        .join(":");
}

export function AgentResultCard({ result, onSelect }: AgentResultCardProps) {
    const handleClick = () => {
        if (result.videoUrl && onSelect) {
            onSelect(result.videoUrl, result.timestampMs);
        }
    };

    const canPlay = Boolean(result.videoUrl) && Boolean(onSelect);

    return (
        <Card
            className={
                canPlay
                    ? "overflow-hidden cursor-pointer transition hover:ring-2 hover:ring-primary/40"
                    : "overflow-hidden"
            }
            onClick={canPlay ? handleClick : undefined}
            role={canPlay ? "button" : undefined}
            tabIndex={canPlay ? 0 : undefined}
            onKeyDown={
                canPlay
                    ? (event) => {
                          if (event.key === "Enter" || event.key === " ") {
                              event.preventDefault();
                              handleClick();
                          }
                      }
                    : undefined
            }
        >
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

                {result.matchedObjects.length > 0 && (
                    <div className="flex flex-wrap gap-2">
                        {result.matchedObjects.map((object) => (
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