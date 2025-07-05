import type { ReactNode } from 'react';
import styles from './EntityListItem.module.css';

interface Props {
    children: ReactNode;
    primaryAction: ReactNode;
    dangerAction: ReactNode;  
}

export function EntityListItem({
    children,
    primaryAction,
    dangerAction,
}: Props) {
    return (
        <li className={styles.item}>
            <span className={styles.label}>{children}</span>
            <div className={styles.actions}>
                {primaryAction}
                {dangerAction}
            </div>
        </li>
    );
}