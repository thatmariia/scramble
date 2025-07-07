import styles from './PlayerStamp.module.css';
import type { Player } from '../api/models/Player';
import { useRef } from 'react';
import HoverTooltip from './HoverTooltip';
import { LEVELS } from '../constants/levels';

interface Props {
    tag: string;
    color: string;
    player?: Player;
}

export function PlayerStamp({ tag, color, player }: Props) {
    const ref = useRef<HTMLSpanElement>(null);

    return (
        <div className={styles.wrapper}>
            <span 
                className={styles.stamp}
                style={{ backgroundColor: color }}
                ref={ref}
            >
                    {tag}
            </span>

            {player && (
                <HoverTooltip triggerRef={ref} delayMs={1000}>
                    <strong>{player.name}</strong>
                    <br />
                    {LEVELS[player.level]}
                    <br />
                </HoverTooltip>
            )}
        </div>
    );
}