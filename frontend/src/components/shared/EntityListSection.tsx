import type { ReactNode } from 'react';

interface Props<T> {
    title: string;
    items: T[];
    render: (item: T) => ReactNode;
}

export function EntityListSection<T>({ title, items, render }: Props<T>) {
    return (
        <section>
            <h2 className="text-xl font-semibold mb-2">{title}</h2>
            <ul className="space-y-1">{items.map(render)}</ul>
        </section>
    );
}