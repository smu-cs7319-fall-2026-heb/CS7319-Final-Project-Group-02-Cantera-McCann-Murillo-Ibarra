import type { Widget } from "../widgets-provider";
import { COLORS } from "./colors";

export default function Text({ widget }: { widget: Widget }) {
    return (
        <span
            className="font-bold"
            style={{ color: widget.color && COLORS[widget.color] }}
        >
            {widget.value}
        </span>
    );
}
