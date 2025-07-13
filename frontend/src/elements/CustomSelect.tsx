import { useState, useRef, useEffect } from 'react';
import { useFloating, autoUpdate, offset, flip, shift } from '@floating-ui/react';
import { FloatingPortal } from '@floating-ui/react';
import styles from './CustomSelect.module.css';
import Portal from './Portal';
import { toast } from 'sonner';

interface Option<T> {
    label: string;
    value: T;
    color?: string;
    slice?: number; // Optional, for slicing label
}

interface Props<T> {
    value: T;
    options: Option<T>[];
    onChange: (val: T) => void;
    fixedWidth?: string | number; // e.g., "10rem", 200, etc.
}

export function CustomSelect<T>({ value, options, onChange, fixedWidth }: Props<T>) {
    const [open, setOpen] = useState(false);

    const selected = options.find((opt) => String(opt.value) === String(value));
    const displayLabel =
        selected?.slice
            ? selected.label.slice(0, selected.slice)
            : selected?.label ?? 'n/a';

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

    const [visibleLabel, setVisibleLabel] = useState(displayLabel);
    const [fading, setFading] = useState(false);

    // when displayLabel changes, animate the transition
    useEffect(() => {
        if (displayLabel !== visibleLabel) {
            setFading(true);
            const timeout = setTimeout(() => {
                setVisibleLabel(displayLabel);
                setFading(false);
            }, 200); // match your fade duration
            return () => clearTimeout(timeout);
        }
    }, [displayLabel]);

    return (
        <div className={styles.wrapper} ref={refs.setReference}>
            <button
                ref={refs.setReference}
                type="button"
                className={`trigger ${styles.trigger}`}
                style={{
                    backgroundColor: selected?.color || 'transparent',
                    width: fixedWidth ?? 'auto',
                }}
                onClick={() => setOpen((v) => !v)}
            >
                <span className={`${styles.label} ${fading ? styles.fading : ''}`}>
                    {visibleLabel}
                </span>
            </button>

            {open && (
                <Portal>
                    <ul
                        ref={refs.setFloating}
                        className={`card dropdown ${styles.dropdown}`}
                        style={{
                            ...floatingStyles,
                            zIndex: 1001,
                            position: 'absolute', // important
                            pointerEvents: 'auto',
                        }}
                    >
                        {options.map((opt) => (
                            <li
                                key={String(opt.value)}
                                className={styles.option}
                                style={{
                                    backgroundColor: opt.color,
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
