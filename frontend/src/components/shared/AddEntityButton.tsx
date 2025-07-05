// src/components/common/AddEntityButton.tsx
import { useState } from 'react';
import type { ReactNode } from 'react';

interface Props {
    buttonLabel: string;     // e.g. “+ Add player”
    form: ReactNode;         // the actual form element
}

export function AddEntityButton({ buttonLabel, form }: Props) {
    const [open, setOpen] = useState(false);
    return (
        <div className="pt-4">
            {open ? (
                form
            ) : (
                <button
                    className="px-4 py-2 bg-blue-500 text-white rounded"
                    onClick={() => setOpen(true)}
                >
                    {buttonLabel}
                </button>
            )}
            {open && (
                <button
                    className="ml-2 px-3 py-1 bg-gray-300 rounded"
                    onClick={() => setOpen(false)}
                >
                    Cancel
                </button>
            )}
        </div>
    );
}