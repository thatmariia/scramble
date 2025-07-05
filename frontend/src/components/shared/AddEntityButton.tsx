import { useState } from 'react';
import type { ReactNode } from 'react';

interface Props {
    buttonLabel: string;
    renderForm: (close: () => void) => ReactNode;
    color?: 'blue' | 'emerald';
}

export function AddEntityButton({
    buttonLabel,
    renderForm,
    color = 'blue',
}: Props) {
    const [open, setOpen] = useState(false);

    const close = () => setOpen(false);

    return (
        <div className="pt-4">
            {open ? (
                renderForm(close)
            ) : (
                <button
                    className={`px-4 py-2 bg-${color}-500 text-white rounded`}
                    onClick={() => setOpen(true)}
                >
                    {buttonLabel}
                </button>
            )}
            {open && (
                <button
                    className="ml-2 px-3 py-1 bg-gray-300 rounded"
                    onClick={close}
                >
                    Cancel
                </button>
            )}
        </div>
    );
}