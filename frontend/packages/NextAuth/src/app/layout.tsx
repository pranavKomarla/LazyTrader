import React from "react";
import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./css/globals.css";
import { ThemeProvider, ThemeModeScript } from "flowbite-react";
import customTheme from "@/utils/theme/custom-theme";
import { CustomizerContextProvider } from "@/app/context/customizerContext";
import "../utils/i18n";
import SessionProviderComp from "./components/nextauth/SessionProvider";
import { createTheme } from "flowbite-react";

const theme = createTheme(customTheme);

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "MaterialM - Nextjs",
};

export default function RootLayout({
  children,
  session,
}: {
  children: React.ReactNode;
  session: any;
}) {
  return (
    <>
      <html lang="en">
        <head>
          <link rel="icon" href="/favicon.svg" type="image/svg+xml" />
          <ThemeModeScript />
        </head>
        <body className={`${inter.className}`}>
          <ThemeProvider theme={theme}>
            <SessionProviderComp session={session}>
              <CustomizerContextProvider>{children}</CustomizerContextProvider>
            </SessionProviderComp>
          </ThemeProvider>
        </body>
      </html>
    </>
  );
}
