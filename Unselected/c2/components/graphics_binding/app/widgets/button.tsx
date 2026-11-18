import type { Widget } from "../widgets-provider";
import { COLORS } from "./colors";

export default function Button({ widget }: { widget: Widget }) {
    return (
        <button
            className="cursor-pointer rounded px-4 py-1.5 text-sm font-bold text-white"
            style={{ backgroundColor: widget.color && COLORS[widget.color] }}
        >
            {widget.value}
        </button>
    );
}
