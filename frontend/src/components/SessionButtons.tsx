import { useSessionName } from '../context/SessionContext';
import { useSession } from '../hooks/session';
import SessionLoading from './session/SessionLoading';
import Settings from './session/Settings';
import Goals from './session/Goals';
import styles from './SessionButtons.module.css';
import { ChevronLeft, ChevronRight } from 'lucide-react';


export default function SessionButtons(
    { collapsed, setCollapsed }: { collapsed: boolean; setCollapsed: (collapsed: boolean) => void; }
) {
    const { name: active, setName } = useSessionName();
    const { isLoading } = active ? useSession(active) : { isLoading: false }; 

    if (!active) {
        return (
            <header className={styles.sessionHeader}>
                <div className={styles.sessionInfo}>
                    <span className={styles.name}>No active session</span>
                </div>
            </header>
        );
    }

    if (isLoading) {
        return <div className={styles.loading}>Loading session…</div>;
    }

    return (
        <div className={styles.sessionButtons}>
            <SessionLoading />
            <Goals />
            <Settings />
            
            <button
                className={`button ghost ${styles.chevronButton}`}
                onClick={() => setCollapsed(!collapsed)}
                aria-label={collapsed ? 'Open sidebar' : 'Close sidebar'}
            >
                {collapsed ? <ChevronLeft className='icon' /> : <ChevronRight className='icon' />}
            </button> 
        </div>
    );
}