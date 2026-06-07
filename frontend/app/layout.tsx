import type { Metadata } from "next";
import "./globals.scss";

export const metadata: Metadata = {
  title: "DomPrice | Оценка стоимости недвижимости в Казахстане",
  description: "Платформа для оценки рыночной стоимости квартир в Казахстане с использованием AI",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="ru">
      <body>{children}</body>
    </html>
  );
}