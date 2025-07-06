import { useState, useRef, useEffect } from 'react';
import styles from './CustomSelect.module.css';

interface Option<T> {
    label: string;
    value: T;
    color?: string; // optional color for the option
}

interface Props<T> {
    value: T;
    options: Option<T>[];
    onChange: (val: T) => void;
}

export function CustomSelect<T>({ value, options, onChange }: Props<T>) {
    const [open, setOpen] = useState(false);
    const ref = useRef<HTMLDivElement>(null);

    useEffect(() => {
        const close = (e: MouseEvent) => {
            if (ref.current && !ref.current.contains(e.target as Node)) {
                setOpen(false);
            }
        };
        document.addEventListener('mousedown', close);
        return () => document.removeEventListener('mousedown', close);
    }, []);

    const selected = options.find((opt) => opt.value === value);

    return (
        <div className={styles.wrapper} ref={ref}>
            <button
                type="button"
                className="trigger"
                style={{
                    backgroundColor: selected?.color || 'transparent',
                }}
                onClick={() => setOpen(!open)}
            >
                {selected?.label.slice(0, 3) || 'n/a'}
                {/* <span className={styles.chevron}>▾</span> */}
            </button>
            {open && (
                <ul className={`card ${styles.dropdown}`}>
                    {options.map((opt) => (
                        <li
                            key={String(opt.value)}
                            className={styles.option}
                            style={{
                                backgroundColor: opt.color || 'transparent',
                            }}
                            onClick={() => {
                                onChange(opt.value);
                                setOpen(false);
                            }}
                        >
                            {opt.label}
                        </li>
                    ))}
                </ul>
            )}
        </div>
    );
}