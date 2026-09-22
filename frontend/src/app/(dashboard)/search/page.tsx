import { PageHeader } from "@/components/layout/page-header";
import { VideoSearch } from "@/features/video-search/presentation/components/video-search";

export default function SearchPage() {
    return (
        <>
            <PageHeader
                title="Video Search Agent"
                description="Tìm kiếm nội dung video bằng ngôn ngữ tự nhiên"
            />
            <VideoSearch />
        </>
    );
}
