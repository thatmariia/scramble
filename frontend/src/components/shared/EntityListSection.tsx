import type { ReactNode } from 'react';
import styles from './EntityListSection.module.css';

interface Props<T> {
    title?: string;
    items: T[];
    render: (item: T) => ReactNode;
}

export function EntityListSection<T>({ title, items, render }: Props<T>) {
    return (
        <section className={styles.section}>
            {title && <span className={styles.title}>{title}</span>}
            <ul className={styles.list}>{items.map(render)}</ul>
        </section>
    );
}