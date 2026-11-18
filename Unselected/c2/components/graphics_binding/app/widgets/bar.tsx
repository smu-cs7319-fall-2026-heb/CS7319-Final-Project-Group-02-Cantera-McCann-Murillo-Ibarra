import type { Widget } from "../widgets-provider";
import { COLORS } from "./colors";

export default function Bar({ widget }: { widget: Widget }) {
    return (
        <div className="h-full w-full bg-neutral-200">
            <div
                className="h-full"
                style={{
                    width: `${Number(widget.value) * 100}%`,
                    backgroundColor: widget.color && COLORS[widget.color],
                }}
            />
        </div>
    );
}
