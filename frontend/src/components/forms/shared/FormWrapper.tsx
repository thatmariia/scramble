import type { ReactNode, FormEvent, KeyboardEvent } from 'react';
import styles from './FormWrapper.module.css'; 
import { X } from 'lucide-react';

interface Props {
    onSubmit: () => void;
    onCancel: () => void;
    isSubmitting?: boolean;
    submitLabel?: string;
    children: ReactNode;
}

export function EntityFormWrapper({
    onSubmit,
    onCancel,
    isSubmitting = false,
    submitLabel = '+',
    children,
}: Props) {
    const handleSubmit = (e: FormEvent) => {
        e.preventDefault();
        onSubmit();
    };

    const handleKeyDown = (e: KeyboardEvent) => {
        if (e.key === 'Escape') {
            e.preventDefault();
            onCancel();
        }
    };

    return (
        <div className={styles.wrapper}>
            <form
                className={styles.formInline}
                onSubmit={handleSubmit}
                onKeyDown={handleKeyDown}
            >
                {children}
                {/* <button
                    type="submit"
                    className="button primary"
                    disabled={isSubmitting}
                >
                    {submitLabel}
                </button> */}
                <button
                    type="button"
                    className="button cancel"
                    onClick={onCancel}
                >
                    <X className="icon" />
                </button>
            </form>
        </div>
    );
}