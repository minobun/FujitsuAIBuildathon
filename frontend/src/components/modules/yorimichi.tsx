import { useState, useEffect } from "react";
import ReactStars from "react-rating-stars-component";
import Masonry from "react-masonry-css";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import {
  APIProvider,
  Map,
  useMapsLibrary,
  useMap,
} from "@vis.gl/react-google-maps";

import {
  MapPin,
  Utensils,
  Coffee,
  Beer,
  ShoppingBag,
  SearchIcon,
} from "lucide-react";
import { nanoid } from "nanoid";
import ChatInput from "@/components/modules/chatInput";
import ChatMessage from "@/components/modules/chatMessage";
import Tag from "@/components/modules/tag";
import { CircularProgress, Link } from "@mui/material";
import { Swiper, SwiperSlide, useSwiper } from "swiper/react";

// This would typically come from your backend or a config file
const GOOGLE_MAPS_API_KEY = process.env
  .NEXT_PUBLIC_GOOGLE_MAPS_API_KEY as string;

const startTemplates = [
  "Find me Dango makers with EC site",
  "I want to experience making Washi paper and have the opportunity",
  "I want to experience traditional craftsmanship and explore handmade products unique to the Amami area.",
];
const routeTemplates = [
  "Create a fun route for me that includes other enjoyable activities in the same neighborhood.",
];
const backTemplates = ["I want to go back to the previous page"];

function App(props: { station: any; locationNames: any }) {
  const { station, locationNames } = props;
  return (
    <APIProvider apiKey={GOOGLE_MAPS_API_KEY}>
      <Map
        defaultCenter={{ lat: station.location.lat, lng: station.location.lng }}
        defaultZoom={9}
        gestureHandling={"greedy"}
        fullscreenControl={false}
      >
        <Directions station={station} locationNames={locationNames} />
      </Map>
    </APIProvider>
  );
}

function Directions(props: { station: any; locationNames: any }) {
  const { station, locationNames } = props;
  const map = useMap();
  const routesLibrary = useMapsLibrary("routes");
  const [directionsService, setDirectionsService] =
    useState<google.maps.DirectionsService>();
  const [directionsRenderer, setDirectionsRenderer] =
    useState<google.maps.DirectionsRenderer>();
  const [route, setRoute] = useState<google.maps.DirectionsRoute[]>();
  const [routeIndex, setRouteIndex] = useState(0);
  // Initialize directions service and renderer
  useEffect(() => {
    if (!routesLibrary || !map) return;
    setDirectionsService(new routesLibrary.DirectionsService());
    setDirectionsRenderer(new routesLibrary.DirectionsRenderer({ map }));
  }, [routesLibrary, map]);

  // Use directions service
  useEffect(() => {
    if (!directionsService || !directionsRenderer) return;
    directionsService
      .route({
        origin: station.name,
        destination: station.name,
        waypoints: locationNames,
        travelMode: google.maps.TravelMode.DRIVING,
        provideRouteAlternatives: true,
      })
      .then((response) => {
        console.log(response);
        directionsRenderer.setDirections(response);
        setRoute(response.routes);
      });
    return () => directionsRenderer.setMap(null);
  }, [directionsService, directionsRenderer, locationNames, station]);

  // Update direction route
  useEffect(() => {
    if (!directionsRenderer) return;
    directionsRenderer.setRouteIndex(routeIndex);
  }, [routeIndex, directionsRenderer]);

  return <></>;
}

export default function Yorimichi() {
  const [messages, setMessages] = useState<{ role: string; content: string }[]>(
    []
  );

  const [locations, setLocations] = useState<any[]>([]);
  const [stores, setStores] = useState<any[]>([]);
  const [station, setStation] = useState<any>();
  const [waypoints, setWaypoints] = useState<any[]>([]);

  const threadId = nanoid();
  const [isLoading, setIsLoading] = useState(false);
  const [chatInput, setChatInput] = useState("");
  const [mode, setMode] = useState<string>("start");

  const [routes, setRoutes] = useState<google.maps.DirectionsRoute[]>([]);

  const chatRequest = async (message: string) => {
    setMessages((cur) => [...cur, { role: "user", content: message }]);
    setChatInput("");
    setIsLoading(true);
    try {
      const result = await fetch(
        `http://127.0.0.1:8000/generate_response?prompt=${message}&thread_id=${threadId}`,
        {
          method: "POST",
          headers: {},
        }
      );
      if (!result.ok) {
        throw new Error(`HTTP error! status: ${result.status}`);
      }
      const resultJson = await result.json();
      console.log(resultJson);
      if (resultJson.response_message)
        setMessages((cur) => [
          ...cur,
          { role: "bot", content: resultJson.response_message as string },
        ]);
      if (resultJson.location_names) setLocations(resultJson.location_names);
      if (resultJson.stores) setStores(resultJson.stores);
      if (resultJson.route) {
        setRoutes(resultJson.route.routes);
      }
      if (resultJson.station) setStation(resultJson.station);
      if (resultJson.waypoints) setWaypoints(resultJson.waypoints);
    } catch (error) {
      console.error("Fetch error:", error);
      setMessages((cur) => {
        if (cur && cur.length > 0) cur.pop();
        return cur;
      });
      setChatInput(message);
    }
    setIsLoading(false);
  };

  const handleSendButton = async (event: React.KeyboardEvent) => {
    if (event.ctrlKey && event.key === "Enter") {
      event.preventDefault();
      await chatRequest(chatInput);
    }
  };

  return (
    <div className="flex h-screen" style={{ backgroundColor: "white" }}>
      <div className="w-screen p-4 overflow-auto">
        <div className="mb-4">
          <CardHeader>
            <CardTitle>Start Chatting to Create Your first Journal!</CardTitle>
          </CardHeader>
          <CardContent className="flex flex-col">
            {messages.map((message, index) => (
              <ChatMessage
                key={index}
                message={message.content}
                sender={message.role}
              />
            ))}
          </CardContent>
          <CardContent>
            <div className="flex items-center border border-gray-300 rounded-md">
              <Input
                className="flex-1"
                placeholder="Search for anything you'd like to do, buy, or enjoy in Japan"
                value={chatInput}
                onChange={(event) => setChatInput(event.target.value)}
              />
              <Button
                onClick={() => chatRequest(chatInput)}
                onKeyDown={handleSendButton}
                disabled={isLoading}
              >
                <SearchIcon className="w-5 h-5 text-gray-500" />
              </Button>
            </div>
          </CardContent>
          <CardContent>
            {routes.length === 0 &&
              stores.length === 0 &&
              startTemplates.map((template, index) => (
                <Button
                  key={index}
                  variant="ghost"
                  className="w-full h-full justify-start mb-2 whitespace-pre-wrap text-wrap text-left"
                  onClick={() => chatRequest(template)}
                  style={{ backgroundColor: "#f1f5f9" }}
                  disabled={isLoading}
                >
                  <img
                    src="/icon-prompt.svg"
                    alt="prompt"
                    style={{ borderRadius: "10px" }}
                  />
                  {template}
                </Button>
              ))}
            {routes.length > 0 &&
              mode === "start" &&
              routeTemplates.map((template, index) => (
                <Button
                  key={index}
                  variant="ghost"
                  className="w-full h-full justify-start mb-2 whitespace-pre-wrap text-wrap text-left"
                  onClick={() => setMode("route")}
                  style={{ backgroundColor: "#f1f5f9" }}
                  disabled={isLoading}
                >
                  <img
                    src="/icon-prompt.svg"
                    alt="prompt"
                    style={{ borderRadius: "10px" }}
                  />
                  {template}
                </Button>
              ))}
            {routes.length > 0 &&
              mode === "route" &&
              backTemplates.map((template, index) => (
                <Button
                  key={index}
                  variant="ghost"
                  className="w-full h-full justify-start mb-2 whitespace-pre-wrap text-wrap text-left"
                  onClick={() => setMode("start")}
                  style={{ backgroundColor: "#f1f5f9" }}
                  disabled={isLoading}
                >
                  <img
                    src="/icon-prompt.svg"
                    alt="prompt"
                    style={{ borderRadius: "10px" }}
                  />
                  {template}
                </Button>
              ))}
          </CardContent>
        </div>

        {isLoading && (
          <div className="flex items-center justify-center grow m-2">
            <CircularProgress />
            <p className="ml-4">Loading...</p>
          </div>
        )}

        {mode === "start" && stores && stores.length > 0 && (
          <Masonry breakpointCols={1} className="flex -p-2">
            {stores.map((store: any) => {
              console.log(store);
              return (
                <Card key={store.name} className="flex m-2">
                  <CardContent className="flex m-2 p-2">
                    <img
                      src={store.photo}
                      alt={store.name}
                      className="w-1/3"
                      style={{ borderRadius: "10px" }}
                    />

                    <div className="flex flex-col p-4 w-2/3 m-2">
                      <CardTitle>{store.name}</CardTitle>
                      <div className="flex mt-1">
                        <p style={{ fontSize: "12px" }}>{store.rating}</p>
                        <ReactStars
                          value={store.rating}
                          size={12}
                          edit={false}
                        />
                      </div>
                      <CardTitle className="mt-2">Location</CardTitle>
                      <CardDescription>{store.address}</CardDescription>
                      <CardTitle className="mt-2">Shop</CardTitle>
                      <Tag label="website" link={store.website} />
                      <CardDescription>
                        <Link href={store.website}>{store.website}</Link>
                      </CardDescription>
                    </div>
                  </CardContent>
                </Card>
              );
            })}
          </Masonry>
        )}
        {mode === "route" && (
          <div className="p-4">
            <div className="flex">
              <div className="w-12 flex flex-col items-center mr-4">
                <div className={"w-5 h-10"}>
                  <MapPin />
                </div>
                <div className={"w-2 h-full bg-primary"}></div>
              </div>
              <div className="flex-1">
                <p>{station.name}</p>
              </div>
            </div>
            {waypoints.map((waypoint) => {
              const isStore = locations.some((location) =>
                location.name.includes(waypoint)
              );
              const store = stores.find((store) => store.name === waypoint);
              return (
                <div key={waypoint} className="flex">
                  <div className="w-12 flex flex-col items-center mr-4">
                    <div className={"w-5 h-10"}>
                      <MapPin color={isStore ? undefined : "red"} />
                    </div>
                    <div className={"w-2 h-full bg-primary"}></div>
                  </div>
                  <div className="flex-1">
                    <p>{waypoint}</p>
                    {store && (
                      <Card key={store.name} className="flex m-2">
                        <CardContent className="flex m-2 p-2">
                          <img
                            src={store.photo}
                            alt={store.name}
                            className="w-1/3"
                            style={{ borderRadius: "10px" }}
                          />
                          <div className="flex flex-col p-4 w-2/3 m-2">
                            <CardTitle>{store.name}</CardTitle>
                            <div className="flex mt-1">
                              <p style={{ fontSize: "12px" }}>{store.rating}</p>
                              <ReactStars
                                value={store.rating}
                                size={12}
                                edit={false}
                              />
                            </div>
                            <CardTitle className="mt-2">Location</CardTitle>
                            <CardDescription>{store.address}</CardDescription>
                            <CardTitle className="mt-2">Shop</CardTitle>
                            <Tag label="website" link={store.website} />
                            <CardDescription>
                              <Link href={store.website}>{store.website}</Link>
                            </CardDescription>
                          </div>
                        </CardContent>
                      </Card>
                    )}
                  </div>
                </div>
              );
            })}
            <div className="flex">
              <div className="w-12 flex flex-col items-center mr-4">
                <div className={"w-5 h-10"}>
                  <MapPin />
                </div>
              </div>
              <div className="flex-1">
                <p>{station.name}</p>
              </div>
            </div>
          </div>
        )}
        {mode === "route" && station && waypoints && (
          <App
            station={station}
            locationNames={locations.map((location) => ({
              location: location.location,
            }))}
          />
        )}
      </div>
    </div>
  );
}
