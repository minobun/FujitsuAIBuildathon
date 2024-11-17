import React from "react";
import { CheckIcon } from "lucide-react";
import { useRouter } from "next/router";

export default function Tag(props: { label: string; link: string }) {
  const router = useRouter();
  return (
    <button
      style={{
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        borderRadius: "0.5rem",
        color: "#005821",
        fontSize: "0.75rem",
        backgroundColor: "#E5FFEFCF", // 緑色
        padding: "0.25rem 0.5rem",
        width: "fit-content",
      }}
      onClick={() => router.push(props.link)}
    >
      {props.label}
      <CheckIcon
        style={{
          marginLeft: "0.5rem",
          width: "1rem",
          height: "1rem",
        }}
      />
    </button>
  );
}
