import Yorimichi from "@/components/modules/yorimichi";
import Start from "@/layouts/start";
import React from "react";
import { Swiper, SwiperSlide } from "swiper/react";
import { Navigation, Pagination, Scrollbar, A11y } from "swiper/modules";

import "swiper/css";

export default function Home() {
  return (
    <Swiper
      slidesPerView={1}
      effect="coverflow"
      centeredSlides
      coverflowEffect={{
        rotate: 50,
        stretch: 0,
        depth: 100,
        modifier: 1,
        slideShadows: true,
      }}
      style={{
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        height: "100vh",
        width: "100vw",
        justifyContent: "center",
        backgroundImage: `url("frame.png")`,
      }}
    >
      <SwiperSlide>
        <Start />
      </SwiperSlide>
      <SwiperSlide>
        <Yorimichi />
      </SwiperSlide>
    </Swiper>
  );
}
