import { createPortal } from 'react-dom';
import { type ReactNode } from 'react';

interface PortalProps {
    children: ReactNode;
}

export default function Portal({ children }: PortalProps) {
    const mount = document.getElementById('ui-portal');
    return mount ? createPortal(children, mount) : null;
}