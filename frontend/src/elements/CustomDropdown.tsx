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
    // const [dropdownRef, setDropdownRef] = useState<HTMLDivElement | null>(null);
    const dropdownRef = useRef<HTMLDivElement | null>(null);

    const { refs, floatingStyles, update } = useFloating({
        open,
        middleware: [offset(8), flip(), shift()],
        placement,
        whileElementsMounted: autoUpdate,
    });

    // Link trigger and floating elements
    useEffect(() => {
        if (triggerRef.current) {
            refs.setReference(triggerRef.current);
        }
    }, [triggerRef, refs]);

    // Close on outside click
    useEffect(() => {
        if (!open) return;

        const handleClick = (e: MouseEvent) => {
            const target = e.target as Node;

            const clickedOutside =
                !triggerRef.current?.contains(target) &&
                !refs.floating.current?.contains(target) &&
                !(target instanceof HTMLElement && target.closest('.floating-escape'));

            if (clickedOutside) {
                onClose();
            }
        };

        document.addEventListener('mousedown', handleClick);
        return () => document.removeEventListener('mousedown', handleClick);
    }, [open, triggerRef, refs.floating, onClose]);
    

    if (!open) return null;

    return (
        <Portal>
            <div
                ref={refs.setFloating}
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