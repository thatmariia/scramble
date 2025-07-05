import { useState } from 'react';
import type { ReactNode } from 'react';
import styles from './AddEntityButton.module.css';

interface Props {
    entity: string; // e.g. "player", "court"
    renderForm: (close: () => void) => ReactNode;
}

export function AddEntityButton({
    entity,
    renderForm
}: Props) {
    const [open, setOpen] = useState(false);
    const close = () => setOpen(false);

    const label = `+ add ${entity}`;

    return (
        <div className={styles.wrapper}>
            {open ? (
                <>
                    {renderForm(close)}
                </>
            ) : (
                <button
                    className="button primary"
                    onClick={() => setOpen(true)}
                >
                    {label}
                </button>
            )}
        </div>
    );
}