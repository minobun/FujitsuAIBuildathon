import { Card, CardContent } from "../ui/card";

export default function ChatMessage(props: {
  message: string;
  sender: string;
}) {
  const { message, sender } = props;
  return (
    <Card
      className={`my-2 ${
        sender === "user"
          ? "bg-blue-500 text-white self-end"
          : "bg-gray-200 text-black self-start"
      }`}
    >
      <CardContent className="p-2">{message}</CardContent>
    </Card>
  );
}
