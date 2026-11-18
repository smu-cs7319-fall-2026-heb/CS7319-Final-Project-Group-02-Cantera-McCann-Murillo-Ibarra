"use client";

import { createContext, useContext, useEffect, useRef, useState } from "react";
import mqtt, { type MqttClient } from "mqtt";

const CONNECTOR_LAYOUT = "ws://localhost:9001";
const LAYOUT_MANAGER = "c2/connector-layout/layout_manager/bottom_domain";
const REQUEST_OBJECTS = `${LAYOUT_MANAGER}/requests/request_objects`;
const REQUEST_CLICK = `${LAYOUT_MANAGER}/requests/request_click`;
const REQUEST_HOVER = `${LAYOUT_MANAGER}/requests/request_hover`;
const NOTIFY_OBJECTS = `${LAYOUT_MANAGER}/notifications/notify_objects`;
const NOTIFY_OBJECTS_CHANGE = `${LAYOUT_MANAGER}/notifications/notify_objects_change`;

type Color = "red" | "yellow" | "green" | "gray" | "blue" | "white";

export type Widget = {
    type:
        | "text"
        | "heading"
        | "caption"
        | "badge"
        | "button"
        | "bar"
        | "rectangle"
        | "circle";
    value?: string | number;
    color?: Color;
    opacity?: number;
    parts?: { value: string; color?: Color }[];
    x: number;
    y: number;
    width?: number;
    height?: number;
};

type Widgets = Record<string, Widget>;

const WidgetsContext = createContext<Widgets>({});

const OnClickContext = createContext<(name: string) => void>(() => {});

const OnHoverContext = createContext<(name: string | null) => void>(() => {});

export function useWidgets() {
    return useContext(WidgetsContext);
}

export function useOnClick() {
    return useContext(OnClickContext);
}

export function useOnHover() {
    return useContext(OnHoverContext);
}

export default function WidgetsProvider({
    children,
}: {
    children: React.ReactNode;
}) {
    const [widgets, setWidgets] = useState<Widgets>({});
    const clientRef = useRef<MqttClient | null>(null);

    useEffect(() => {
        const client = mqtt.connect(CONNECTOR_LAYOUT);
        clientRef.current = client;

        client.on("connect", () => {
            client.subscribe([NOTIFY_OBJECTS, NOTIFY_OBJECTS_CHANGE]);
            client.publish(REQUEST_OBJECTS, "");
        });

        client.on("message", (topic, payload) => {
            const received = JSON.parse(payload.toString());
            setWidgets(received);
        });

        return () => {
            client.end(true);
        };
    }, []);

    function onClick(name: string) {
        clientRef.current?.publish(REQUEST_CLICK, JSON.stringify({ name }));
    }

    function onHover(name: string | null) {
        clientRef.current?.publish(REQUEST_HOVER, JSON.stringify({ name }));
    }

    return (
        <WidgetsContext.Provider value={widgets}>
            <OnClickContext.Provider value={onClick}>
                <OnHoverContext.Provider value={onHover}>
                    {children}
                </OnHoverContext.Provider>
            </OnClickContext.Provider>
        </WidgetsContext.Provider>
    );
}
