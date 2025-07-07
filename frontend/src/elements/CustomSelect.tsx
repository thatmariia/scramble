import { useState, useRef } from 'react';
import { useFloating, autoUpdate, offset, flip, shift } from '@floating-ui/react';
import styles from './CustomSelect.module.css';
import Portal from './Portal';

interface Option<T> {
    label: string;
    value: T;
    color?: string;
}

interface Props<T> {
    value: T;
    options: Option<T>[];
    onChange: (val: T) => void;
}

export function CustomSelect<T>({ value, options, onChange }: Props<T>) {
    const [open, setOpen] = useState(false);

    const selected = options.find((opt) => opt.value === value);

    // Floating UI setup
    const {
        refs,
        floatingStyles,
        update,
        placement,
    } = useFloating({
        open,
        onOpenChange: setOpen,
        middleware: [offset(8), flip(), shift()],
        whileElementsMounted: autoUpdate,
        placement: 'bottom-end', // align right edges
    });

    return (
        <div className={styles.wrapper} ref={refs.setReference}>
            <button
                ref={refs.setReference}
                type="button"
                className="trigger"
                style={{
                    backgroundColor: selected?.color || 'transparent',
                }}
                onClick={() => setOpen((v) => !v)}
            >
                {selected?.label.slice(0, 3) || 'n/a'}
            </button>

            {open && (
                <Portal>
                    <ul
                        ref={refs.setFloating}
                        className={`card dropdown ${styles.dropdown}`}
                        style={{
                            ...floatingStyles,
                            zIndex: 999,
                        }}
                    >
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
                </Portal>
            )}
        </div>
    );
}
