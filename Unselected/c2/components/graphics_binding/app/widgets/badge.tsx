import type { Widget } from "../widgets-provider";
import { COLORS } from "./colors";

export default function Badge({ widget }: { widget: Widget }) {
    return (
        <span
            className="rounded-full px-3 py-1 font-bold text-white"
            style={{ backgroundColor: widget.color && COLORS[widget.color] }}
        >
            {widget.value}
        </span>
    );
}
