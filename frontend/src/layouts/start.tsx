import { Button } from "@/components/ui/button";
import { Card } from "@mui/material";
import React from "react";
import { useSwiper } from "swiper/react";

export default function Start() {
  const swiper = useSwiper();
  return (
    <Card
      style={{
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        width: "100vw",
        height: "90vh",
        backgroundImage: `url("Cover.svg")`,
        backgroundSize: "contain",
        backgroundPosition: "center",
        backgroundRepeat: "no-repeat",
        border: "none",
        boxShadow: "none",
        backgroundColor: "transparent",
      }}
    >
      <p
        style={{
          position: "absolute",
          top: "11rem",
          left: "1rem",
        }}
      >
        VOL 001 | Your Story with Japan
      </p>
      <h1
        style={{
          position: "absolute",
          top: "16rem",
          left: "1.5rem",
          fontSize: "3rem",
          fontWeight: "bold",
        }}
      >
        寄り道 Magazine
      </h1>
      <p
        style={{
          width: "80%",
        }}
      >
        Value proposition goes here, find the hidden gems in Japan in your own
        way.
      </p>
      <Button
        onClick={() => swiper.slideNext()}
        style={{
          position: "absolute",
          bottom: "15rem",
          left: "3rem",
          backgroundColor: "transparent",
          backgroundImage: `url("button.png")`,
          backgroundSize: "contain",
          backgroundPosition: "center",
          backgroundRepeat: "no-repeat",
          width: "10rem",
          border: "none",
        }}
      />
    </Card>
  );
}
