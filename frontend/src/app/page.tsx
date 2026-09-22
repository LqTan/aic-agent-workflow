import { VideoSearch } from "@/features/video-search/presentation/components/video-search";
import Image from "next/image";

export default function Home() {
  return (
    <main className="mx-auto w-full max-w-7xl px-6 py-10">
      <VideoSearch/>
    </main>
  );
}
