import type { Widget } from "../widgets-provider";

export default function Caption({ widget }: { widget: Widget }) {
    return <span className="text-sm text-neutral-500">{widget.value}</span>;
}
