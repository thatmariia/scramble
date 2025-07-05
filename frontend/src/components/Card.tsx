import { useState } from 'react';
import styles from './Card.module.css';
import { ChevronDown, ChevronUp } from 'lucide-react';

interface Props {
    title: string;
    children: React.ReactNode;
    defaultOpen?: boolean;
}

export function Card({ title, children, defaultOpen = true }: Props) {
    const [open, setOpen] = useState(defaultOpen);

    return (
        <div className={styles.card}>
            <button className={styles.header} onClick={() => setOpen(!open)}>
                <span className={styles.title}>{title}</span>
                {open ? <ChevronUp className='icon' /> : <ChevronDown className='icon' />}
            </button>

            {open && <div className={styles.content}>{children}</div>}
        </div>
    );
}