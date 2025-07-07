// src/components/Dropdown.tsx
import {
    useFloating,
    autoUpdate,
    offset,
    flip,
    shift,
} from '@floating-ui/react';
import {
    useRef,
    useState,
    useEffect,
    type ReactNode,
    type RefObject,
} from 'react';
import Portal from './Portal';

interface DropdownProps {
    triggerRef: RefObject<HTMLElement | null>;
    open: boolean;
    onClose: () => void;
    children: ReactNode;
    placement?: 'bottom-start' | 'bottom-end' | 'top-start' | 'top-end';
}

export default function Dropdown({
    triggerRef,
    open,
    onClose,
    children,
    placement = 'bottom-end',
}: DropdownProps) {
    const [dropdownRef, setDropdownRef] = useState<HTMLDivElement | null>(null);

    const { refs, floatingStyles, update } = useFloating({
        open,
        middleware: [offset(8), flip(), shift()],
        placement,
        whileElementsMounted: autoUpdate,
    });

    // Link trigger and floating elements
    useEffect(() => {
        refs.setReference(triggerRef.current);
        refs.setFloating(dropdownRef);
    }, [triggerRef, dropdownRef, refs]);

    // Close on outside click
    useEffect(() => {
        if (!open) return;
        const handleClick = (e: MouseEvent) => {
            if (
                !triggerRef.current?.contains(e.target as Node) &&
                !dropdownRef?.contains(e.target as Node)
            ) {
                onClose();
            }
        };
        document.addEventListener('mousedown', handleClick);
        return () => document.removeEventListener('mousedown', handleClick);
    }, [open, triggerRef, dropdownRef, onClose]);

    if (!open) return null;

    return (
        <Portal>
            <div
                ref={setDropdownRef}
                className="card dropdown"
                style={{
                    ...floatingStyles,
                    zIndex: 999,
                }}
            >
                {children}
            </div>
        </Portal>
    );
}