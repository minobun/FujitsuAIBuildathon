import { Button } from "@mui/material";
import { Input } from "../ui/input";
import { SearchIcon } from "lucide-react";

export default function ChatInput() {
  return (
    <div className="flex items-center border border-gray-300 rounded-md">
      <Input className="flex-1" />
      <Button>
        <SearchIcon className="w-5 h-5 text-gray-500" />
      </Button>
    </div>
  );
}
