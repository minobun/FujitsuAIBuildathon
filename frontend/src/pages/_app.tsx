import { CssBaseline } from "@mui/material";
import { AppCacheProvider } from "@mui/material-nextjs/v14-pagesRouter";
import type { AppProps } from "next/app";
import Head from "next/head";
import "../styles/globals.css";

export default function App(props: AppProps) {
  const { Component, pageProps } = props;
  return (
    <AppCacheProvider {...props}>
      <Head>
        <title>Yorimichi Magazine</title>
        <meta name="description" content="Very Intersting Geo Game" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href="/favicon.ico" />
      </Head>
      <CssBaseline />
      <div className="flex justify-center items-center">
        <img src="/Title.svg" alt="logo" />
      </div>

      <Component {...pageProps} />
    </AppCacheProvider>
  );
}
