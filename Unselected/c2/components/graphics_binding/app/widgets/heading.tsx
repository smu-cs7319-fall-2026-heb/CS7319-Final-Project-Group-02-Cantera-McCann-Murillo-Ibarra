import type { Widget } from "../widgets-provider";
import { COLORS } from "./colors";

export default function Heading({ widget }: { widget: Widget }) {
    return (
        <span className="text-2xl">
            {widget.parts?.map((part, iii) => (
                <span
                    key={iii}
                    style={{ color: part.color && COLORS[part.color] }}
                >
                    {part.value}
                </span>
            ))}
        </span>
    );
}
