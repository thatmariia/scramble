import {
    useFloating,
    offset,
    flip,
    shift,
    autoUpdate,
} from '@floating-ui/react';
import {
    useRef,
    useEffect,
    useState,
    type ReactNode,
    type RefObject,
} from 'react';
import Portal from './Portal';

interface HoverTooltipProps {
    triggerRef: RefObject<HTMLElement | null>;
    children: ReactNode;
    placement?: 'top' | 'bottom' | 'left' | 'right';
    delayMs?: number;
}

export default function HoverTooltip({
    triggerRef,
    children,
    placement = 'top',
    delayMs = 300,
}: HoverTooltipProps) {
    const [open, setOpen] = useState(false);
    const timeoutId = useRef<number | null>(null);

    const { refs, floatingStyles } = useFloating({
        open,
        placement,
        middleware: [offset(8), flip(), shift()],
        whileElementsMounted: autoUpdate,
    });

    useEffect(() => {
        if (triggerRef.current) {
            refs.setReference(triggerRef.current);
        }
    }, [triggerRef, refs]);

    useEffect(() => {
        if (!triggerRef.current) return;

        const show = () => {
            timeoutId.current = window.setTimeout(() => {
                setOpen(true);
            }, delayMs);
        };

        const hide = () => {
            if (timeoutId.current !== null) {
                clearTimeout(timeoutId.current);
                timeoutId.current = null;
            }
            setOpen(false);
        };

        const node = triggerRef.current;
        node.addEventListener('mouseenter', show);
        node.addEventListener('mouseleave', hide);

        return () => {
            node.removeEventListener('mouseenter', show);
            node.removeEventListener('mouseleave', hide);
            if (timeoutId.current !== null) clearTimeout(timeoutId.current);
        };
    }, [triggerRef, delayMs]);

    if (!open) return null;

    return (
        <Portal>
            <div
                ref={refs.setFloating}
                className="card tooltip"
                style={{
                    ...floatingStyles,
                }}
            >
                {children}
            </div>
        </Portal>
    );
}