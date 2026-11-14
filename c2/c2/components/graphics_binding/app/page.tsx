"use client";

import {
    useOnClick,
    useOnHover,
    useWidgets,
    type Widget,
} from "./widgets-provider";
import Badge from "./widgets/badge";
import Bar from "./widgets/bar";
import Button from "./widgets/button";
import Caption from "./widgets/caption";
import Circle from "./widgets/circle";
import Heading from "./widgets/heading";
import Rectangle from "./widgets/rectangle";
import Text from "./widgets/text";

const COMPONENTS = {
    text: Text,
    heading: Heading,
    caption: Caption,
    badge: Badge,
    button: Button,
    bar: Bar,
    rectangle: Rectangle,
    circle: Circle,
};

function viewportTransform(widget: Widget) {
    const style: React.CSSProperties = {
        left: `${((widget.x + 1) / 2) * 100}%`,
        top: `${((1 - widget.y) / 2) * 100}%`,
        transform: "translate(-50%, -50%)",
    };

    if (widget.width !== undefined && widget.height !== undefined) {
        style.width = `${(widget.width / 2) * 100}%`;
        style.height = `${(widget.height / 2) * 100}%`;
    }

    return style;
}

export default function Home() {
    const widgets = useWidgets();
    const onClick = useOnClick();
    const onHover = useOnHover();

    return (
        <main className="flex flex-1 items-center justify-center bg-linear-to-br from-sky-100 to-slate-100">
            <div className="rounded-lg bg-white text-neutral-700 shadow-lg">
                <h1 className="border-b border-neutral-200 py-4 text-center text-3xl">
                    Connect Four
                </h1>
                <div className="relative h-[650px] w-[500px]">
                    {Object.entries(widgets).map(([name, widget]) => {
                        const Component = COMPONENTS[widget.type];

                        return (
                            <div
                                key={name}
                                className="absolute whitespace-nowrap"
                                style={viewportTransform(widget)}
                                onClick={() => onClick(name)}
                                onMouseEnter={() => onHover(name)}
                                onMouseLeave={() => onHover(null)}
                            >
                                <Component widget={widget} />
                            </div>
                        );
                    })}
                </div>
            </div>
        </main>
    );
}
