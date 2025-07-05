import type { ReactNode } from 'react';

interface Props {
    children: ReactNode;                 // “John (lvl 3) — #1”
    primaryAction: ReactNode;            // Rest / Activate
    dangerAction: ReactNode;             // Delete
    bg?: string;                         // optional background override
}

export function EntityListItem({
    children,
    primaryAction,
    dangerAction,
    bg = 'bg-gray-100',
}: Props) {
    return (
        <li
            className={`flex items-center justify-between rounded px-3 py-1 ${bg}`}
        >
            <span>{children}</span>
            <div className="space-x-2">
                {primaryAction}
                {dangerAction}
            </div>
        </li>
    );
}