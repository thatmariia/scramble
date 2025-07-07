import styles from './PlayerStamp.module.css';

interface Props {
    tag: string;
    color: string;
}

export function PlayerStamp({ tag, color }: Props) {
    return (
        <span 
            className={styles.stamp}
            style={{ backgroundColor: color }}
        >
                {tag}
        </span>
    );
}