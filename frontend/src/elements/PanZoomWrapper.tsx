import React, { useRef, useState, useEffect } from 'react';
import styles from './PanZoomWrapper.module.css';
import { Crosshair } from 'lucide-react';

interface Props {
    children: React.ReactNode;
    minScale?: number;
    maxScale?: number;
    initialScale?: number;
}

export function PanZoomWrapper({
    children,
    minScale = 0.5,
    maxScale = 2,
    initialScale = 1
}: Props) {
    const containerRef = useRef<HTMLDivElement>(null);
    const [scale, setScale] = useState(initialScale);
    const [offset, setOffset] = useState({ x: 0, y: 0 });
    const [isDragging, setIsDragging] = useState(false);
    const lastPos = useRef({ x: 0, y: 0 });

    const resetView = () => {
        setScale(initialScale);
        setOffset({ x: 0, y: 0 });
    };

    const handleMouseDown = (e: React.MouseEvent) => {
        e.preventDefault();
        setIsDragging(true);
        document.documentElement.classList.add('no-select');
        lastPos.current = { x: e.clientX, y: e.clientY };
    };

    const handleMouseMove = (e: MouseEvent) => {
        if (!isDragging) return;
        const dx = e.clientX - lastPos.current.x;
        const dy = e.clientY - lastPos.current.y;
        setOffset((prev) => ({ x: prev.x + dx, y: prev.y + dy }));
        lastPos.current = { x: e.clientX, y: e.clientY };
    };

    const handleMouseUp = () => {
        setIsDragging(false);
        document.documentElement.classList.remove('no-select');
    }

    const handleWheel = (e: React.WheelEvent) => {
        e.preventDefault();
        const delta = -e.deltaY;
        const zoomFactor = 1 + delta * 0.001;
        setScale((prev) => {
            const newScale = Math.min(maxScale, Math.max(minScale, prev * zoomFactor));
            return newScale;
        });
    };

    useEffect(() => {
        window.addEventListener('mousemove', handleMouseMove);
        window.addEventListener('mouseup', handleMouseUp);
        return () => {
            window.removeEventListener('mousemove', handleMouseMove);
            window.removeEventListener('mouseup', handleMouseUp);
            document.documentElement.classList.remove('no-select');
        };
    }, [isDragging]);

    return (
        <div
            ref={containerRef}
            className={styles.panZoomContainer}
            onMouseDown={handleMouseDown}
            onWheel={handleWheel}
        >
            <button
                onClick={resetView}
                className={`${styles.resetButton} button ghost `}
            >
                <Crosshair className='icon' />
            </button>
            <div className={styles.roundContentWrapper}>  
                <div
                    className={`${styles.content} ${isDragging ? 'no-select' : ''}`}
                    style={{
                        transform: `translate(${offset.x}px, ${offset.y}px) scale(${scale})`
                    }}
                >
                    {children}
                </div>
            </div>
        </div>
    );
}