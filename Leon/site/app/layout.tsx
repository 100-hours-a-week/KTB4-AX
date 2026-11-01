import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "PAIR | 카테부 실시간 모의면접 매칭",
  description: "닉네임, 팀, 부서만 입력하고 매칭 시작. 같은 부서의 모의면접 파트너와 실시간으로 연결됩니다.",
  other: {
    "codex-preview": "development",
  },
  icons: {
    icon: "/favicon.svg",
    shortcut: "/favicon.svg",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="ko">
      <body className="antialiased">{children}</body>
    </html>
  );
}
