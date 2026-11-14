import type { Widget } from "../widgets-provider";
import { COLORS } from "./colors";

export default function Rectangle({ widget }: { widget: Widget }) {
    return (
        <div
            className="h-full w-full rounded-xl border-b-4 border-black/25"
            style={{ backgroundColor: widget.color && COLORS[widget.color] }}
        />
    );
}
