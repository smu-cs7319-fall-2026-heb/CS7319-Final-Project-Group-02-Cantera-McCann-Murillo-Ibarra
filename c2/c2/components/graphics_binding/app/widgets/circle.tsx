import type { Widget } from "../widgets-provider";
import { COLORS } from "./colors";

export default function Circle({ widget }: { widget: Widget }) {
    return (
        <div
            className="h-full w-full scale-90 rounded-full"
            style={{ backgroundColor: COLORS.white }}
        >
            <div
                className="h-full w-full rounded-full inset-shadow-sm inset-shadow-black/25"
                style={{
                    backgroundColor: widget.color && COLORS[widget.color],
                    opacity: widget.opacity,
                }}
            />
        </div>
    );
}
